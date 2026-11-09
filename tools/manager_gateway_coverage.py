"""Map Project7 manager gateway handlers to the stock client's request surface.

The manager (a separate offline server app) dispatches a fixed set of resource
RPCs: LocalGatewayServer builds literal String[] tables and matches method digests,
while week/story engines dispatch their own names. Auditing the manager by reading
one class at a time hides which client requests have no handler at all, so this
tool unions every `*.dis` table in the manager package and joins it with the
client request inventory produced by tools/rpc_cross_reference.py.

Static only: disassembly is read as text, nothing is executed. A name being
mentioned by an engine is evidence that the request is answered there, not proof
that its reply payload or state transition matches the original server.
"""
import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CONST = re.compile(r'const-string(?:/jumbo)?\s+v(\d+),\s*"([^"]+)"')
ARRAY = re.compile(r'filled-new-array/range v(\d+)\s*\.\.\.\s*v(\d+)')
IDENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]{2,}$')


def arrays_in(lines):
    """Literal String[] tables: contiguous const-string block matching the range."""
    found = []
    for index, line in enumerate(lines):
        match = ARRAY.search(line)
        if not match:
            continue
        low, high = int(match.group(1)), int(match.group(2))
        size = high - low + 1
        names = []
        cursor = index - 1
        while cursor >= 0 and len(names) < size:
            item = CONST.search(lines[cursor])
            if item and low <= int(item.group(1)) <= high:
                names.append(item.group(2))
            elif lines[cursor].strip():
                break
            cursor -= 1
        field = None
        for probe in lines[index + 1:index + 5]:
            match_field = re.search(r'sput-object\s+v\d+,\s*.+?->([A-Za-z0-9_]+)', probe)
            if match_field:
                field = match_field.group(1)
                break
        if field is None:
            # Inline table consumed immediately by digest/equals matching
            # (LocalGatewayServer builds no field; it scans the array in place).
            tail = '\n'.join(lines[index + 1:index + 20])
            if 'digest(' in tail or '->equals(' in tail:
                field = 'INLINE_DISPATCH'
        found.append({'line': index + 1, 'declared': size, 'field': field,
                      'names': sorted(set(names))})
    return found


def scan(dis_dir, client_names):
    engines = {}
    for path in sorted(dis_dir.glob('*.dis')):
        lines = path.read_text(encoding='utf-8', errors='replace').splitlines()
        tables = arrays_in(lines)
        strong = set()
        other = set()
        for table in tables:
            hits = {name for name in table['names'] if name in client_names}
            if table['field'] and ('METHOD' in table['field'].upper()
                                   or table['field'] == 'INLINE_DISPATCH'):
                strong.update(hits)
            else:
                other.update(hits)
        weak = set(other)
        for line in lines:
            item = CONST.search(line)
            if item and item.group(2) in client_names:
                weak.add(item.group(2))
        if strong or weak:
            engines[path.stem] = {
                'tables': [{'line': table['line'], 'declared': table['declared'],
                            'field': table['field'],
                            'names': [name for name in table['names']
                                      if name in client_names]}
                           for table in tables],
                'strong': sorted(strong), 'mentioned': sorted(weak - strong),
                'literals': sum(1 for line in lines if CONST.search(line))}
    return engines


def _area(path):
    marker = '/original-py-640/'
    if marker in path:
        tail = path.split(marker, 1)[1]
        if 'ActivityMembers' in tail:
            return 'activity'
        return tail.split('/')[0]
    return path.split('/')[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dis-dir', type=Path, default=ROOT / 'analysis/project7/manager')
    parser.add_argument('--matrix', type=Path, default=ROOT / 'reports/rpc-cross-reference.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/manager-gateway-coverage.json')
    parser.add_argument('--markdown', type=Path, default=ROOT / 'reports/manager-gateway-coverage.md')
    parser.add_argument('--top', type=int, default=40)
    args = parser.parse_args()

    matrix = json.loads(args.matrix.read_text(encoding='utf-8'))
    requests = matrix['requests']
    engines = scan(args.dis_dir, set(requests))

    handled = Counter()
    evidence = {}
    for engine, data in engines.items():
        for name in data['strong']:
            handled[name] += 1
            evidence.setdefault(name, []).append('%s:table' % engine)
        for name in data['mentioned']:
            evidence.setdefault(name, []).append('%s:literal' % engine)

    rows = {}
    for name, row in requests.items():
        sites = row.get('call_sites') or []
        if name in handled:
            status = 'manager_registered'
        elif name in evidence:
            status = 'manager_listed'
        else:
            status = 'absent'
        rows[name] = {'status': status, 'call_sites': len(sites),
                      'client_areas': dict(Counter(
                          _area(site['file']) for site in sites).most_common(4)),
                      'engines': evidence.get(name, [])}
    counts = Counter(row['status'] for row in rows.values())

    report = {'generated_at': datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(),
              'dis_dir': str(args.dis_dir.relative_to(ROOT)) if args.dis_dir.is_relative_to(ROOT) else str(args.dis_dir),
              'client_matrix': str(args.matrix.relative_to(ROOT)) if args.matrix.is_relative_to(ROOT) else str(args.matrix),
              'engines': engines,
              'status_counts': dict(counts),
              'requests': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    args.markdown.write_text(markdown(report, args.top), encoding='utf-8')
    print(json.dumps({'status_counts': dict(counts),
                      'engines_with_handlers': len(engines)}, ensure_ascii=False))
    print('json:', args.output)
    print('markdown:', args.markdown)


def markdown(report, top):
    rows = report['requests']
    lines = ['# Project7 管理器网关 ↔ 原客户端请求对照', '',
             '生成时间 %s。`manager_registered` = 落在某引擎注册的 METHODS 分派表（强证据）；'
             '`manager_listed` = 出现在内联 String[] 或散落的字符串常量里（可能是分派表，也可能是 ack/允许列表，语义需读该分支）；`absent` = 管理器完全没有该名。'
             % report['generated_at'], '',
             '| 状态 | 请求数 |', '|---|---|']
    for status, count in sorted(report['status_counts'].items()):
        lines.append('| %s | %d |' % (status, count))
    lines += ['', '## 分派表（每个引擎的字面量表）', '',
              '| 引擎 | 表行 | 声明长度 | 注册字段 | 命中客户端请求 |', '|---|---|---|---|---|']
    for engine, data in report['engines'].items():
        for table in data['tables']:
            if table['names']:
                lines.append('| %s | %d | %d | %s | %s |' % (
                    engine, table['line'], table['declared'], table['field'] or '—',
                    ', '.join(table['names'][:8]) + (' …' if len(table['names']) > 8 else '')))
    absent = [(name, row) for name, row in rows.items() if row['status'] == 'absent']
    absent.sort(key=lambda item: (-item[1]['call_sites'], item[0]))
    core = [item for item in absent if 'activity' not in ','.join(item[1]['client_areas'])]
    for label, subset in (('absent 且非活动模块（Top %d）' % top, core),
                          ('absent 全部（Top %d）' % top, absent)):
        lines += ['', '## %s' % label, '',
                  '| 请求 | 调用点 | 客户端区域 |', '|---|---|---|']
        for name, row in subset[:top]:
            lines.append('| `%s` | %d | %s |' % (
                name, row['call_sites'], ','.join(row['client_areas'])))
    return '\n'.join(lines) + '\n'


if __name__ == '__main__':
    main()
