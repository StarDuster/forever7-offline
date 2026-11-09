"""Maintainer-only static Python 2.7 literal decoder, derived from DeepSeek's
read_literal_marshal.py. No game imports/calls are evaluated. Fixed SHA is checked
by the producer before decoding. Requires existing bytecode27/xdis tooling.
"""
from pathlib import Path
from tools import bytecode27
from xdis.bytecode import Bytecode
from xdis.opcodes import opcode_27
from . import typed

MAX_BYTES = 32 * 1024 * 1024
MAX_INSTRUCTIONS = 4000000
MAX_STACK = 200000


def read(path):
    path = Path(path)
    if not 0 < path.stat().st_size <= MAX_BYTES:
        raise ValueError('marshal size limit')
    code = bytecode27.read(path)
    aliases = {'TD': '__literal_dict__', 'True': True, 'False': False, 'None': None}
    stack, started, returned = [], False, False
    for number, instruction in enumerate(Bytecode(code, opcode_27)):
        if number >= MAX_INSTRUCTIONS or len(stack) > MAX_STACK:
            raise ValueError('literal instruction/stack limit')
        op, count = instruction.opname, instruction.arg or 0
        if not started:
            if op == 'STORE_NAME' and instruction.argval == '_reload_all':
                started = True
            continue
        if op == 'LOAD_CONST':
            stack.append(instruction.argval)
        elif op == 'LOAD_NAME':
            stack.append(aliases[instruction.argval])
        elif op == 'STORE_NAME':
            aliases[instruction.argval] = stack.pop()
        elif op in ('BUILD_TUPLE', 'BUILD_LIST'):
            if count > len(stack):
                raise ValueError('truncated literal stack')
            values = stack[-count:] if count else []
            if count:
                del stack[-count:]
            stack.append(tuple(values) if op == 'BUILD_TUPLE' else list(values))
        elif op == 'BUILD_MAP':
            stack.append({})
        elif op == 'STORE_MAP':
            key, value = stack.pop(), stack.pop()
            if key in stack[-1]:
                raise ValueError('duplicate literal dictionary key')
            stack[-1][key] = value
        elif op == 'BINARY_SUBSCR':
            key, value = stack.pop(), stack.pop()
            stack.append(value[key])
        elif op == 'UNARY_NEGATIVE':
            value = stack.pop()
            if type(value) not in (int, float):
                raise ValueError('non-numeric negate')
            stack.append(-value)
        elif op == 'CALL_FUNCTION':
            if count != 1:
                raise ValueError('nonliteral call')
            value, function = stack.pop(), stack.pop()
            if function != '__literal_dict__' or not isinstance(value, dict):
                raise ValueError('nonliteral function')
            stack.append(dict(value))
        elif op == 'RETURN_VALUE':
            returned = True
            break
        else:
            raise ValueError('unsupported literal opcode %s at %s' % (op, instruction.offset))
    if not started or not returned or not isinstance(aliases.get('data'), dict):
        raise ValueError('no complete literal table')
    typed(aliases['data'])  # reject code objects, unsupported values and nonfinite numbers
    return aliases['data']
