"""Append an evidence-backed parsing result to the project's local journal."""
import argparse
from collections import Counter
from datetime import datetime
import json
import os
from pathlib import Path
import uuid
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
STATUSES = ('verified_static', 'verified_native', 'hypothesis', 'failed', 'pending')


def record(category, finding, status, evidence=(), details=None, next_steps=()):
    if status not in STATUSES:
        raise ValueError('Use an explicit verification status')
    references = []
    for filename in evidence:
        path = (ROOT / filename).resolve()
        if not path.is_relative_to(ROOT) or not path.exists():
            raise ValueError('Evidence must exist inside this project: %s' % filename)
        references.append(str(path.relative_to(ROOT)))
    item = {'id': uuid.uuid4().hex[:12],
            'recorded_at': datetime.now(ZoneInfo('Asia/Hong_Kong')).isoformat(),
            'category': category, 'status': status, 'finding': finding,
            'evidence': references, 'details': details or {}, 'next_steps': list(next_steps)}
    folder = ROOT / 'reports'
    folder.mkdir(exist_ok=True)
    journal = folder / 'analysis-findings.jsonl'
    with journal.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(item, ensure_ascii=False, allow_nan=False) + '\n')
        handle.flush()
        os.fsync(handle.fileno())
    entries = [json.loads(line) for line in journal.read_text().splitlines() if line.strip()]
    summary = {'updated_at': item['recorded_at'], 'records': len(entries),
               'status_definitions': {
                   'verified_static': '已对照文件、数据或构建结果验证，不代表游戏内可运行',
                   'verified_native': '已在原客户端引擎内验证，仅限记录中的范围',
                   'hypothesis': '待验证推测，不作为完成依据',
                   'failed': '已尝试但未达到预期，保留失败证据',
                   'pending': '尚未验证或尚未接入运行版'},
               'by_category': dict(Counter(entry['category'] for entry in entries)),
               'by_status': dict(Counter(entry['status'] for entry in entries)),
               'latest': item, 'journal': str(journal.relative_to(ROOT)),
               'goal_complete': False}
    temporary = folder / 'analysis-index.json.tmp'
    temporary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    os.replace(temporary, folder / 'analysis-index.json')
    return item['id']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--category', required=True)
    parser.add_argument('--finding', required=True)
    parser.add_argument('--status', choices=STATUSES, required=True)
    parser.add_argument('--evidence', nargs='*', default=[])
    parser.add_argument('--next', dest='next_steps', nargs='*', default=[])
    args = parser.parse_args()
    print(record(args.category, args.finding, args.status, args.evidence, next_steps=args.next_steps))


if __name__ == '__main__':
    main()
