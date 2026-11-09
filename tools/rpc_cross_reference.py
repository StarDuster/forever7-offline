"""Cross-reference original client RPC call sites against the offline runtime.

Each audit so far re-derived the same facts by hand: which requests the stock
client actually sends, where they are sent, what callback consumes the reply, and
whether runtime/local_gateway.py plus its adapters answer them at all. This tool
derives that matrix mechanically over the decompiled corpus
(analysis/original-py-640, produced by tools/decompile_corpus.py from the official
Android 640 script set the build ships) so a mechanism
review starts from a ranked gap list instead of a fresh search.

Static only: no decoded code is executed and no game state is touched. Coverage
here is request-name evidence, not proof that a reply's fields or state
transitions are correct; those still need the per-mechanism contract checks.
"""
import argparse
import ast
from collections import Counter
from datetime import datetime
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CALL_PATTERN = re.compile(
    r"callServerMethod(?:Seq|Reliable)?\(\s*(?:u)?(['\"])([A-Za-z_][A-Za-z0-9_]*)\1")
CALLBACK_PATTERN = re.compile(r"callback\s*=\s*([A-Za-z_][\w\.]*)")
REPLY_PATTERN = re.compile(r"^(\s*)def\s+(reply[A-Za-z0-9_]*|[A-Za-z0-9_]+Reply)\s*\(")
NAME_OPERANDS = {'name', 'request_name', 'method', 'methodname', 'operation', 'rpc_name'}
DISPATCH_OPS = (ast.Eq, ast.NotEq, ast.In, ast.NotIn)


def _string_constants(node):
    values = []
    for child in ast.walk(node):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            values.append(child.value)
    return values


def _module_string_sets(tree):
    """Module-level name -> string set, following `A | B` and tuple/list/set literals."""
    sets = {}
    assignments = [node for node in tree.body
                   if isinstance(node, (ast.Assign, ast.AnnAssign))]
    by_name = {}
    for node in assignments:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                by_name[target.id] = node.value
    resolving = set()

    def resolve(name):
        if name in sets:
            return sets[name]
        if name in resolving or name not in by_name:
            return None
        resolving.add(name)
        values = resolve_value(by_name[name])
        resolving.discard(name)
        if values is not None:
            sets[name] = values
        return values

    def resolve_value(value):
        if isinstance(value, (ast.Tuple, ast.List, ast.Set)):
            items = [child.value for child in value.elts
                     if isinstance(child, ast.Constant) and isinstance(child.value, str)]
            return set(items) if len(items) == len(value.elts) else None
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) \
                and value.func.id in ('frozenset', 'set', 'tuple', 'list') and value.args:
            return resolve_value(value.args[0])
        if isinstance(value, ast.BinOp) and isinstance(value.op, ast.BitOr):
            left, right = resolve_value(value.left), resolve_value(value.right)
            return None if left is None or right is None else left | right
        if isinstance(value, ast.Name):
            return resolve(value.id)
        return None

    for name in by_name:
        resolve(name)
    return sets


def _name_comparison(node):
    operands = [node.left] + list(node.comparators)
    if not any(isinstance(item, ast.Name) and item.id in NAME_OPERANDS for item in operands):
        return None
    names = set()
    for item in operands:
        if isinstance(item, ast.Name) and item.id in NAME_OPERANDS:
            continue
        names.update(_string_constants(item))
    return names or None


def runtime_index(runtime_dir):
    dispatch = {}
    registered = {}
    mentioned = {}

    def add(bucket, name, source):
        bucket.setdefault(name, [])
        if source not in bucket[name]:
            bucket[name].append(source)

    unparsed = []
    for path in sorted(runtime_dir.glob('*.py')):
        rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        text = path.read_text(encoding='utf-8')
        try:
            tree = ast.parse(text)
        except SyntaxError:
            # offline_bootstrap.py is injected into the stock Python 2.7 client
            # (`exec ... in globals()`), so keep its literals visible without AST.
            unparsed.append(rel)
            for lineno, line in enumerate(text.splitlines(), 1):
                for literal in re.findall(r"u?['\"]([^'\"\\]{1,120})['\"]", line):
                    add(mentioned, literal, '%s:%d' % (rel, lineno))
                for match in re.finditer(r"\bname\s*(?:==|in)\s*\(?([^):\n]+)", line):
                    for literal in re.findall(r"u?['\"]([^'\"]+)['\"]", match.group(1)):
                        add(dispatch, literal, '%s:%d' % (rel, lineno))
            continue
        sets = _module_string_sets(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                add(mentioned, node.value, rel)
            if isinstance(node, ast.Compare) and isinstance(node.ops[0], DISPATCH_OPS):
                names = _name_comparison(node)
                if names:
                    for name in names:
                        add(dispatch, name, '%s:%d' % (rel, node.lineno))
            if isinstance(node, ast.Dict):
                for key in node.keys:
                    if isinstance(key, ast.Constant) and isinstance(key.value, str):
                        add(registered, key.value, '%s:%d' % (rel, node.lineno))
        for name, values in sets.items():
            for value in values:
                add(registered, value, '%s:%s' % (rel, name))
    return dispatch, registered, mentioned, unparsed


def _scope_tracker():
    stack = []

    def track(line):
        match = re.match(r'^(\s*)(class|def)\s+([A-Za-z_][\w]*)', line)
        if match:
            indent = len(match.group(1))
            while stack and stack[-1][0] >= indent:
                stack.pop()
            stack.append((indent, match.group(3)))
        return '.'.join(item[1] for item in stack)

    return track


def _balanced(text):
    depth = 0
    for char in text:
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
    return depth <= 0


def corpus_index(corpus_dirs):
    requests = {}
    replies = {}
    files = sorted({path for corpus_dir in corpus_dirs for path in corpus_dir.rglob('*.py')})
    for path in files:
        rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        defs = {}
        for lineno, line in enumerate(lines, 1):
            match = re.match(r'^\s*def\s+([A-Za-z_][\w]*)\s*\(', line)
            if match:
                defs.setdefault(match.group(1), lineno)
        track = _scope_tracker()
        pending = ''
        pending_line = 0
        for lineno, line in enumerate(lines, 1):
            scope = track(line)
            if pending:
                pending += '\n' + line
                if _balanced(pending):
                    _record_call(pending, rel, pending_line, scope, requests, defs)
                    pending = ''
                continue
            if 'callServerMethod' in line:
                pending = line
                pending_line = lineno
                if not _balanced(line):
                    continue
                _record_call(line, rel, lineno, scope, requests, defs)
                pending = ''
            match = REPLY_PATTERN.match(line)
            if match:
                replies.setdefault(match.group(2), []).append(
                    {'file': rel, 'line': lineno, 'scope': scope})
    return files, requests, replies


def _record_call(text, rel, lineno, scope, requests, defs):
    for quote, name in CALL_PATTERN.findall(text):
        callback = CALLBACK_PATTERN.search(text)
        callback_name = callback.group(1) if callback else None
        requests.setdefault(name, []).append({
            'file': rel, 'line': lineno, 'scope': scope,
            'callback': callback_name,
            'callback_line': defs.get(callback_name.rsplit('.', 1)[-1])
            if callback_name else None})


def _classify(name, dispatch, registered, mentioned, rejected):
    if name in rejected:
        return 'rejected', rejected[name]
    if name in dispatch:
        return 'handled', dispatch[name]
    if name in registered:
        return 'registered', registered[name]
    if name in mentioned:
        return 'mentioned_only', mentioned[name]
    return 'unhandled', []


def log_evidence(log_dirs):
    """Name -> {count, files} for `RPC UNIMPLEMENTED <name>` lines already recorded.

    Logs may come from older bundled runtimes; the matrix status stays authoritative,
    this only marks names the real client was seen requesting in a native run.
    """
    pattern = re.compile(r'RPC UNIMPLEMENTED\s+([A-Za-z_][\w]*)')
    observed = {}
    seen_paths = set()
    for directory in log_dirs:
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob('*.log')):
            if path in seen_paths:
                continue
            seen_paths.add(path)
            rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
            try:
                text = path.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            for name in pattern.findall(text):
                entry = observed.setdefault(name, {'count': 0, 'files': []})
                entry['count'] += 1
                if rel not in entry['files'] and len(entry['files']) < 5:
                    entry['files'].append(rel)
    return observed


def _area(rel_path, corpus_dirs):
    rest = rel_path
    prefixes = []
    for corpus in corpus_dirs:
        prefixes.append(str(corpus).rstrip('/') + '/')
        if corpus.is_relative_to(ROOT):
            prefixes.append(str(corpus.relative_to(ROOT)).rstrip('/') + '/')
    for prefix in prefixes:
        if rel_path.startswith(prefix):
            rest = rel_path[len(prefix):]
            break
    if 'ActivityMembers' in rest:
        return 'activity'
    parts = rest.split('/')
    return parts[0] if len(parts) > 1 else '(root)'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, nargs='+',
                        default=[ROOT / 'analysis/original-py-640'])
    parser.add_argument('--runtime', type=Path, default=ROOT / 'runtime')
    parser.add_argument('--rejections', type=Path,
                        default=ROOT / 'runtime/offline_rpc_rejections.py')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/rpc-cross-reference.json')
    parser.add_argument('--markdown', type=Path, default=ROOT / 'reports/rpc-cross-reference.md')
    parser.add_argument('--top', type=int, default=60)
    parser.add_argument('--corpus-summary', type=Path,
                        default=ROOT / 'reports/original-corpus-640-summary.json',
                        help='decompile summary describing the corpus version/provenance')
    parser.add_argument('--logs', type=Path, nargs='*',
                        default=[ROOT / 'analysis', ROOT / 'reports'],
                        help='directories scanned for "RPC UNIMPLEMENTED <name>" runtime logs')
    args = parser.parse_args()

    for corpus in args.corpus:
        if not corpus.is_dir() or not any(corpus.rglob('*.py')):
            raise SystemExit('no decompiled corpus at %s; run tools/decompile_corpus.py' % corpus)

    dispatch, registered, mentioned, unparsed = runtime_index(args.runtime)
    rejection_tree = ast.parse(args.rejections.read_text(encoding='utf-8'))
    rejected = {}
    for name, values in _module_string_sets(rejection_tree).items():
        if name.startswith('RPC_') and 'REJECTION' in name:
            for value in values:
                rejected.setdefault(value, []).append('runtime/%s:%s' % (args.rejections.name, name))

    observed = log_evidence(args.logs)
    files, requests, replies = corpus_index(args.corpus)
    rows = {}
    for name, sites in requests.items():
        status, evidence = _classify(name, dispatch, registered, mentioned, rejected)
        areas = Counter(_area(site['file'], args.corpus) for site in sites)
        rows[name] = {'status': status, 'call_sites': sites,
                      'runtime_evidence': evidence[:8],
                      'client_areas': dict(areas.most_common(4)),
                      'observed_unimplemented': observed.get(name)}
    counts = {}
    for row in rows.values():
        counts[row['status']] = counts.get(row['status'], 0) + 1

    reply_rows = {name: sites for name, sites in replies.items()}
    missing_consumers = sorted(name for name in mentioned
                               if name.startswith('reply') and name not in reply_rows)

    report = {'generated_at': datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(),
              'corpus': {'dirs': [str(corpus.relative_to(ROOT))
                                  if corpus.is_relative_to(ROOT) else str(corpus)
                                  for corpus in args.corpus],
                         'files': len(files), 'call_sites': sum(len(v) for v in requests.values()),
                         'distinct_requests': len(requests),
                         'summary': _corpus_summary(args.corpus_summary)},
              'status_counts': counts,
              'runtime_unparsed_files': unparsed,
              'requests': rows,
              'client_reply_handlers': reply_rows,
              'runtime_reply_names_without_client_handler': missing_consumers}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    args.markdown.write_text(_markdown(report, args.top), encoding='utf-8')
    print(json.dumps({'status_counts': counts,
                      'call_sites': report['corpus']['call_sites'],
                      'distinct_requests': report['corpus']['distinct_requests'],
                      'corpus_files': len(files)}, ensure_ascii=False))
    print('json:', args.output)
    print('markdown:', args.markdown)


def _corpus_summary(path):
    if not path.is_file():
        return None
    summary = json.loads(path.read_text(encoding='utf-8'))
    keep = ('source_dir', 'output_dir', 'status_counts', 'total_bytes', 'finished_at')
    return {key: summary[key] for key in keep if key in summary}


def _markdown(report, top):
    rows = report['requests']
    lines = ['# 原客户端 RPC 调用面 ↔ 离线 runtime 对照', '',
             '生成时间 %s；语料 %d 个模块，%d 个调用点，%d 个不同请求名。' % (
                 report['generated_at'], report['corpus']['files'],
                 report['corpus']['call_sites'], report['corpus']['distinct_requests']),
             '', '语料出处：%s。' % (
                 (report['corpus'].get('summary') or {}).get('source_dir') or '未记录（缺 --corpus-summary）'),
             '', '口径：`handled` = runtime 有按 `name` 分派/比较；`registered` = 只出现在 `runtime/*.py` 的字符串集合或字典键（适配器入口）；`rejected` = 在 `offline_rpc_rejections.py` 里显式拒绝；`mentioned_only` = 只在其它字符串常量里出现；`unhandled` = runtime 完全未提及。名称级证据，不等于回包字段或状态迁移已对齐。',
             '', '| 状态 | 请求数 |', '|---|---|']
    for status, count in sorted(report['status_counts'].items()):
        lines.append('| %s | %d |' % (status, count))
    for status in ('unhandled', 'mentioned_only'):
        subset = [(name, row) for name, row in rows.items() if row['status'] == status]
        subset.sort(key=lambda item: (-len(item[1]['call_sites']), item[0]))
        lines += ['', '## %s（Top %d）' % (status, top), '',
                  '| 请求 | 调用点 | 客户端区域 | 首个调用位置 | 回调 |', '|---|---|---|---|---|']
        for name, row in subset[:top]:
            site = row['call_sites'][0]
            lines.append('| `%s` | %d | %s | %s:%d | %s |' % (
                name, len(row['call_sites']), ','.join(row['client_areas']),
                site['file'], site['line'], site['callback'] or '—'))
    exercised = [(name, row) for name, row in rows.items()
                 if row['observed_unimplemented'] and row['status'] in ('unhandled', 'mentioned_only')]
    exercised.sort(key=lambda item: (-item[1]['observed_unimplemented']['count'], item[0]))
    lines += ['', '## 实测日志出现过、runtime 未处理（Top %d）' % top, '',
              '来自既有原生运行日志里的 `RPC UNIMPLEMENTED` 行；日志可能出自更早的 bundled runtime，状态以本表矩阵列为准。',
              '', '| 请求 | 日志次数 | 调用点 | 客户端区域 | 首条日志 |', '|---|---|---|---|---|']
    for name, row in exercised[:top]:
        entry = row['observed_unimplemented']
        lines.append('| `%s` | %d | %d | %s | %s |' % (
            name, entry['count'], len(row['call_sites']),
            ','.join(row['client_areas']), entry['files'][0] if entry['files'] else '—'))
    lines += ['', '## 客户端 reply 处理器与 runtime 回复名', '',
              '客户端已定义 %d 个 reply 处理器；runtime 出现 %d 个 reply 名在客户端找不到同名处理器（可能是拼写/协议差异，或客户端在该分支不注册）。' % (
                  len(report['client_reply_handlers']),
                  len(report['runtime_reply_names_without_client_handler'])), '']
    for name in report['runtime_reply_names_without_client_handler'][:top]:
        lines.append('- `%s`' % name)
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    main()
