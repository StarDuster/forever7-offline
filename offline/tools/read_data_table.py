"""Read literal cdata assignments from a decompiled file, without exec/eval.

Only constants, containers, previously parsed aliases, and the data generator's
TD/dict/set wrappers are accepted. Imports, arbitrary calls, and game code are
never executed. An unsupported expression fails instead of guessing its value.
"""
import _bootstrap  # noqa: E402,F401
import argparse
import ast
import json
from pathlib import Path


def literal(node, aliases):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id in aliases:
        return aliases[node.id]
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        items = [literal(x, aliases) for x in node.elts]
        return tuple(items) if isinstance(node, ast.Tuple) else set(items) if isinstance(node, ast.Set) else items
    if isinstance(node, ast.Dict):
        return {literal(k, aliases): literal(v, aliases) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = literal(node.operand, aliases)
        if type(value) not in (int, float):
            raise ValueError('Expected a numeric literal')
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.Subscript):
        return literal(node.value, aliases)[literal(node.slice, aliases)]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and not node.keywords:
        if node.func.id in ('TD', 'dict', 'set', 'frozenset') and len(node.args) <= 1:
            value = literal(node.args[0], aliases) if node.args else []
            return {'TD': dict, 'dict': dict, 'set': set, 'frozenset': frozenset}[node.func.id](value)
    raise ValueError('Unsupported expression at line %s: %s' % (node.lineno, ast.dump(node)[:180]))


def read(path):
    tree = ast.parse(Path(path).read_text())
    aliases = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        name = node.targets[0].id
        if name == 'data' or name.startswith('l') and name[1:].isdigit():
            aliases[name] = literal(node.value, aliases)
    if 'data' not in aliases:
        raise ValueError('No literal data assignment')
    return aliases['data']


def serializable(value):
    if isinstance(value, (tuple, list, set, frozenset)):
        return [serializable(x) for x in value]
    if isinstance(value, dict):
        return {k: serializable(v) for k, v in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--keys', type=int, nargs='*')
    args = parser.parse_args()
    data = read(args.source)
    if args.keys:
        data = {key: data.get(key) for key in args.keys}
    result = json.dumps(serializable(data), ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result + '\n')
        print(args.output)
    else:
        print(result)


if __name__ == '__main__':
    main()
