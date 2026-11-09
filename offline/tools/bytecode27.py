"""Decode NeoX's Python 2.7 opcode permutation for static analysis only.

Reference table: https://github.com/yuanbi/NeteaseUnpackTools/blob/master/NeteasePycObject/netpyc.cpp
Cross-checked against the redirect.py bootstrap in the downloaded 1.96.455 APK.
No decoded code is executed. Unknown opcodes fail closed.
"""
import _bootstrap  # noqa: E402,F401
import argparse
import contextlib
import io
from pathlib import Path

from xdis.unmarshal import load_code
from xdis.bytecode import Bytecode
from xdis.opcodes import opcode_27

STANDARD_TO_NEOX = {
    0: 0, 1: 38, 2: 46, 3: 37, 4: 66, 5: 12, 10: 35, 11: 67, 12: 81,
    13: 32, 15: 9, 19: 63, 20: 70, 21: 44, 22: 36, 23: 39, 24: 57,
    25: 10, 26: 52, 28: 49, 30: 86, 31: 87, 32: 88, 33: 89, 40: 24,
    41: 25, 42: 26, 43: 27, 50: 14, 51: 15, 52: 16, 53: 17, 54: 8,
    55: 21, 56: 55, 57: 82, 58: 34, 59: 22, 60: 65, 61: 6, 62: 58,
    63: 71, 64: 43, 65: 30, 66: 19, 67: 5, 68: 60, 71: 53, 72: 42,
    73: 3, 74: 48, 75: 84, 76: 77, 77: 78, 78: 85, 79: 47, 80: 51,
    81: 54, 82: 50, 83: 83, 84: 74, 85: 64, 86: 31, 87: 72, 88: 45,
    89: 33, 90: 145, 91: 159, 92: 125, 93: 149, 94: 157, 95: 132,
    96: 95, 97: 113, 98: 111, 99: 138, 100: 153, 101: 101, 102: 135,
    103: 90, 104: 99, 105: 151, 106: 96, 107: 114, 108: 134, 109: 116,
    110: 156, 111: 105, 112: 130, 113: 137, 114: 148, 115: 172,
    116: 155, 119: 103, 120: 158, 121: 128, 122: 110, 124: 97,
    125: 104, 126: 118, 130: 93, 131: 131, 132: 136, 133: 115,
    134: 100, 135: 120, 136: 129, 137: 102, 140: 140, 141: 141,
    142: 142, 143: 94, 146: 109, 147: 123,
}
NEOX_TO_STANDARD = {value: key for key, value in STANDARD_TO_NEOX.items()}
NEOX_TO_STANDARD.update({13: 27, 160: 145})  # true division; extended argument


def decode(code):
    data = code.co_code
    position = 0
    instructions = []
    extended = 0
    aliases = []
    while position < len(data):
        value = data[position]
        if value not in NEOX_TO_STANDARD and value != 173:
            raise ValueError(f"Unknown opcode {value} in {code.co_filename}:{code.co_name} at {position}")
        opcode = NEOX_TO_STANDARD.get(value)
        width = 3 if value >= 90 else 1
        if position + width > len(data):
            raise ValueError("Truncated instruction")
        argument = int.from_bytes(data[position + 1:position + 3], "little") | extended if width == 3 else None
        aliases.append(position)
        if opcode == 145:
            extended = argument << 16
            position += width
            continue
        extended = 0
        if value == 173:
            # NeoX fused LOAD_FAST(0), LOAD_CONST(arg), inferred from independent
            # call sites (hasattr(self, literal), callback(0), data['latitude']).
            # Expand it, then relocate every absolute/relative jump and lnotab.
            if not code.co_varnames or argument >= len(code.co_consts):
                raise ValueError("Invalid fused LOAD_FAST0/LOAD_CONST argument")
            instructions.append({"old": aliases, "op": 124, "arg": 0, "width": 3})
            instructions.append({"old": [], "op": 100, "arg": argument, "width": 3})
        else:
            instructions.append({"old": aliases, "op": opcode, "arg": argument,
                                 "width": 3 if opcode >= 90 else 1})
        aliases = []
        position += width
    if aliases:
        raise ValueError("Dangling extended argument")
    for instruction in instructions:
        op, arg = instruction["op"], instruction["arg"]
        if op in opcode_27.hasjabs:
            instruction["target"] = arg
        elif op in opcode_27.hasjrel:
            instruction["target"] = instruction["old"][-1] + 3 + arg
    for _ in range(12):
        positions = {}
        size = 0
        for instruction in instructions:
            instruction["position"] = size
            for old in instruction["old"]:
                positions[old] = size
            size += instruction["width"]
        positions[len(data)] = size
        changed = False
        for instruction in instructions:
            arg = instruction["arg"]
            if "target" in instruction:
                target = positions[instruction["target"]]
                arg = target if instruction["op"] in opcode_27.hasjabs else target - instruction["position"] - instruction["width"]
                if arg < 0:
                    raise ValueError("Invalid relocated relative jump")
            instruction["encoded_arg"] = arg
            width = 1 if arg is None else max(1, (arg.bit_length() + 15) // 16) * 3
            if width != instruction["width"]:
                instruction["width"] = width
                changed = True
        if not changed:
            break
    else:
        raise ValueError("Jump relocation did not converge")
    result = bytearray()
    for instruction in instructions:
        op, arg = instruction["op"], instruction["encoded_arg"]
        if arg is not None:
            for shift in range((instruction["width"] // 3 - 1) * 16, 0, -16):
                result.append(145)
                result.extend(((arg >> shift) & 65535).to_bytes(2, "little"))
        result.append(op)
        if arg is not None:
            result.extend((arg & 65535).to_bytes(2, "little"))
    lnotab = bytearray()
    old_address = new_address = 0
    original_lnotab = code.co_lnotab.encode("latin1") if isinstance(code.co_lnotab, str) else code.co_lnotab
    for delta_address, delta_line in zip(original_lnotab[::2], original_lnotab[1::2]):
        old_address += delta_address
        # A zero-line-delta entry may land inside an instruction. Its address
        # merely extends the next delta and does not represent a source line.
        if not delta_line:
            continue
        if old_address not in positions:
            raise ValueError("Source line starts inside an instruction")
        delta = positions[old_address] - new_address
        while delta > 255:
            lnotab.extend((255, 0))
            delta -= 255
        lnotab.extend((delta, delta_line))
        new_address = positions[old_address]
    code.co_lnotab = bytes(lnotab)
    code.co_code = bytes(result)
    for value in code.co_consts:
        if hasattr(value, "co_code"):
            decode(value)
    return code


def read(path):
    return decode(load_code(io.BytesIO(Path(path).read_bytes()), 62211, code_objects={}))


def disassemble(code, out):
    out.write(f"\n# {code.co_filename}:{code.co_firstlineno} {code.co_name}\n")
    out.write(Bytecode(code, opcode_27).dis())
    for value in code.co_consts:
        if hasattr(value, "co_code"):
            disassemble(value, out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--decompile", action="store_true")
    args = parser.parse_args()
    code = read(args.module)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as out:
        if args.decompile:
            from uncompyle6.main import decompile
            # Parser diagnostics can be very large; keep them beside the artifact.
            with args.output.with_suffix(".diagnostics.txt").open("w") as diag:
                with contextlib.redirect_stdout(diag), contextlib.redirect_stderr(diag):
                    decompile(code, bytecode_version=(2, 7), out=out)
        else:
            disassemble(code, out)
    print(args.output)


if __name__ == "__main__":
    main()
