"""Write Python 2.7 marshal v2 objects parsed by xdis, without executing them.

xdis.marsh's legacy Python-2 path mixes str/bytes under current Python. This
small writer preserves Python-2 bytes/unicode and code objects explicitly.
It deliberately does not serialize arbitrary Python objects.
"""
import _bootstrap  # noqa: E402,F401
import struct

from xdis.cross_types import LongTypeForPython3, UnicodeForPython3


def raw(value):
    return value.encode("utf-8") if isinstance(value, str) else value


def dumps(value):
    if value is None:
        return b"N"
    if value is False:
        return b"F"
    if value is True:
        return b"T"
    if value is Ellipsis:
        return b"."
    if value is StopIteration:
        return b"S"
    if isinstance(value, int):
        if not isinstance(value, LongTypeForPython3) and -(1 << 31) <= value < 1 << 31:
            return b"i" + struct.pack("<i", value)
        number = abs(int(value))
        digits = []
        while number:
            digits.append(number & 32767)
            number >>= 15
        size = len(digits) * (-1 if value < 0 else 1)
        return b"l" + struct.pack("<i", size) + b"".join(struct.pack("<H", digit) for digit in digits)
    if isinstance(value, float):
        return b"g" + struct.pack("<d", value)
    if isinstance(value, complex):
        return b"y" + struct.pack("<dd", value.real, value.imag)
    if isinstance(value, UnicodeForPython3):
        data = value.value
        return b"u" + struct.pack("<i", len(data)) + data
    if isinstance(value, (str, bytes)):
        data = raw(value)
        return b"s" + struct.pack("<i", len(data)) + data
    if isinstance(value, (tuple, list, set, frozenset)):
        tag = {tuple: b"(", list: b"[", set: b"<", frozenset: b">"}[type(value)]
        return tag + struct.pack("<i", len(value)) + b"".join(dumps(item) for item in value)
    if isinstance(value, dict):
        return b"{" + b"".join(dumps(k) + dumps(v) for k, v in value.items()) + b"0"
    if hasattr(value, "co_code"):
        header = struct.pack("<4i", value.co_argcount, value.co_nlocals, value.co_stacksize, value.co_flags)
        parts = [dumps(item) for item in (value.co_code, value.co_consts, value.co_names,
                 value.co_varnames, value.co_freevars, value.co_cellvars, value.co_filename, value.co_name)]
        return b"c" + header + b"".join(parts) + struct.pack("<i", value.co_firstlineno) + dumps(value.co_lnotab)
    raise TypeError(f"Unsupported marshal constant: {type(value)}")
