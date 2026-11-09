"""Decompile a whole official script corpus into searchable source.

The offline build replaces the APK script with the official Android 640 script set
(README: script.check/script.data), so analysis/android640-scripts is the
build-authoritative corpus and the default here. The APK-embedded script from
analysis/assets/script.npk is a different version; point --source-dir at
analysis/scripts when comparing against it instead.

Agents currently decompile one NeoX Python 2.7 module at a time while auditing a
mechanism, so every comparison starts with the same expensive step and the result
is thrown away. This tool converts analysis/scripts once, in parallel, into
analysis/original-py/<module>.py plus a manifest, so original behavior can be
grepped, diffed and cross-referenced like ordinary source.

Decompilation is static only: no decoded code is executed. A module that fails
is recorded with its diagnostics and never silently treated as understood.
"""
import argparse
import contextlib
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import sys
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
MODULE_TIMEOUT_SECONDS = 60
if str(ROOT / 'tools') not in sys.path:
    sys.path.insert(0, str(ROOT / 'tools'))
import bytecode27  # noqa: E402  (NeoX opcode table lives beside this tool)
from uncompyle6.main import decompile  # noqa: E402


def _decompile_one(task):
    module, source, output, timeout = task
    started = os.times().elapsed
    data = Path(source).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    text = ''
    status = 'ok'
    error = None

    def _timeout(signum, frame):
        raise TimeoutError('decompile exceeded %ss' % timeout)

    previous = signal.signal(signal.SIGALRM, _timeout)
    signal.setitimer(signal.ITIMER_REAL, timeout)
    try:
        code = bytecode27.read(source)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            decompile(code, bytecode_version=(2, 7), out=buffer)
        text = buffer.getvalue()
    except Exception as exc:  # partial output is still evidence; failure stays explicit
        status = 'failed'
        error = '%s: %s' % (type(exc).__name__, exc)
        text = locals().get('buffer')
        text = text.getvalue() if isinstance(text, io.StringIO) else ''
        if text:
            status = 'partial'
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)

    output = Path(output)
    if text:
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix('.py.tmp')
        temporary.write_text(text, encoding='utf-8', errors='replace')
        os.replace(temporary, output)
    return {'module': module, 'source': source, 'source_sha256': digest,
            'output': str(output) if text else None, 'status': status,
            'bytes': len(text), 'seconds': round(os.times().elapsed - started, 3),
            'error': error}


def _load_manifest(path):
    entries = {}
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            entries[entry['module']] = entry
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path,
                        default=ROOT / 'analysis/android640-scripts')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'analysis/original-py-640')
    parser.add_argument('--manifest', type=Path,
                        default=ROOT / 'reports/original-corpus-640-manifest.jsonl')
    parser.add_argument('--summary', type=Path,
                        default=ROOT / 'reports/original-corpus-640-summary.json')
    parser.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--filter', help='substring match on module path')
    parser.add_argument('--force', action='store_true', help='redo finished modules')
    parser.add_argument('--timeout', type=int, default=MODULE_TIMEOUT_SECONDS,
                        help='per-module decompile timeout in seconds')
    args = parser.parse_args()

    source_dir = args.source_dir.resolve()
    output_dir = args.output_dir.resolve()
    if not source_dir.is_dir():
        parser.error('missing source directory: %s' % source_dir)
    if output_dir == source_dir:
        parser.error('output directory must differ from source')

    sources = sorted(source_dir.rglob('*.marshal'))
    if args.filter:
        sources = [path for path in sources if args.filter in path.as_posix()]
    if args.limit:
        sources = sources[:args.limit]
    if not sources:
        parser.error('no modules matched')

    entries = _load_manifest(args.manifest)
    tasks = []
    skipped = 0
    for source in sources:
        module = source.relative_to(source_dir).with_suffix('').as_posix()
        output = output_dir / (module + '.py')
        previous = entries.get(module)
        if not args.force and previous and previous['status'] in ('ok', 'partial') and output.exists():
            skipped += 1
            continue
        tasks.append((module, str(source), str(output), args.timeout))

    started = datetime.now(ZoneInfo('Asia/Hong_Kong'))
    results = []
    if tasks:
        with ProcessPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            for done, result in enumerate(pool.map(_decompile_one, tasks), 1):
                results.append(result)
                entries[result['module']] = result
                if done % 200 == 0 or done == len(tasks):
                    print('%d/%d modules decompiled' % (done, len(tasks)), flush=True)

    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    ordered = [entries[key] for key in sorted(entries)]
    temporary = args.manifest.with_suffix('.jsonl.tmp')
    with temporary.open('w', encoding='utf-8') as handle:
        for entry in ordered:
            handle.write(json.dumps(entry, ensure_ascii=False) + '\n')
    os.replace(temporary, args.manifest)

    counts = {}
    for entry in ordered:
        counts[entry['status']] = counts.get(entry['status'], 0) + 1
    last_run = {}
    for entry in results:
        last_run[entry['status']] = last_run.get(entry['status'], 0) + 1

    def display(path):
        return str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path)

    summary = {'finished_at': datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(),
               'started_at': started.isoformat(),
               'source_dir': display(source_dir),
               'output_dir': display(output_dir),
               'modules_matched': len(sources), 'skipped_existing': skipped,
               'processed': len(results),
               'status_counts': counts, 'last_run_status_counts': last_run,
               'total_bytes': sum(entry['bytes'] for entry in ordered),
               'failures': [{'module': entry['module'], 'status': entry['status'],
                             'error': entry['error']}
                            for entry in ordered if entry['status'] == 'failed']}
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary['status_counts'], ensure_ascii=False))
    print('manifest:', args.manifest)
    print('summary:', args.summary)


if __name__ == '__main__':
    main()
