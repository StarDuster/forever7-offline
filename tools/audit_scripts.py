"""Statically validate decoded opcode boundaries and relocated jump targets.

Passing this audit does not establish native runtime or gameplay compatibility.
"""
import argparse
import json
from pathlib import Path
import time

from bytecode27 import read


def count_code(code):
    return 1 + sum(count_code(value) for value in code.co_consts if hasattr(value, "co_code"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    total, functions, failures = 0, 0, []
    started = time.monotonic()
    for path in args.directory.rglob("*.marshal"):
        total += 1
        try:
            functions += count_code(read(path))
        except Exception as exc:
            failures.append({"path": str(path), "error": f"{type(exc).__name__}: {exc}"})
        if total % 2000 == 0:
            print(f"{total} modules, failures={len(failures)}", flush=True)
    report = {"directory": str(args.directory), "modules": total, "code_objects": functions,
              "failures": failures, "seconds": round(time.monotonic() - started, 1),
              "runtime_tested": False, "fused_opcode_semantics": "inferred from client call sites"}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "failures"}))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
