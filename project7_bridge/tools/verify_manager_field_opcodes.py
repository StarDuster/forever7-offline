"""Reject manager DEX field accesses whose opcode disagrees with the field type.

ART verifies these even when a JVM host or javac accepts the source. This is a
post-chain check over the final classes7.dex, not a generator-text scan.
"""
import _bootstrap  # noqa: E402,F401
from pathlib import Path
import logging
import sys

from androguard.core.dex import DEX

FIELD_OPS = {
    'iget': 'I', 'iput': 'I', 'sget': 'I', 'sput': 'I',
    'iget-object': 'L', 'iput-object': 'L', 'sget-object': 'L', 'sput-object': 'L',
    'iget-wide': 'W', 'iput-wide': 'W', 'sget-wide': 'W', 'sput-wide': 'W',
    'iget-boolean': 'Z', 'iput-boolean': 'Z', 'sget-boolean': 'Z', 'sput-boolean': 'Z',
    'iget-byte': 'B', 'iput-byte': 'B', 'sget-byte': 'B', 'sput-byte': 'B',
    'iget-char': 'C', 'iput-char': 'C', 'sget-char': 'C', 'sput-char': 'C',
    'iget-short': 'S', 'iput-short': 'S', 'sget-short': 'S', 'sput-short': 'S',
}


def expected_kind(descriptor):
    if descriptor == 'Z':
        return 'Z'
    if descriptor == 'B':
        return 'B'
    if descriptor == 'C':
        return 'C'
    if descriptor == 'S':
        return 'S'
    if descriptor in ('J', 'D'):
        return 'W'
    if descriptor.startswith(('L', '[')):
        return 'L'
    return 'I'


def verify(data, label='classes7.dex'):
    logging.disable(logging.CRITICAL)
    dex = DEX(data)
    bad = []
    for cls in dex.get_classes():
        for method in cls.get_methods():
            code = method.get_code()
            if code is None:
                continue
            for instruction in code.get_bc().get_instructions():
                opcode = instruction.get_name()
                kind = FIELD_OPS.get(opcode)
                if kind is None:
                    continue
                output = instruction.get_output()
                descriptor = output.rsplit(' ', 1)[-1]
                expected = expected_kind(descriptor)
                if expected != kind:
                    bad.append('%s %s %s -> %s [%s]' % (
                        cls.get_name(), method.get_name(), opcode, output, expected))
    if bad:
        raise ValueError('Field opcode/type mismatch in %s:\n%s' % (label, '\n'.join(bad[:20])))
    return True


def verify_coc_wrapper_entry(data, label='classes7.dex'):
    """Final-DEX guard: q7 must unwrap the exact provider before store dispatch."""
    logging.disable(logging.CRITICAL)
    dex = DEX(data)
    seen = set()
    for cls in dex.get_classes():
        if cls.get_name() != 'Lcom/project7/localmanager/LocalGatewayServer;':
            continue
        for method in cls.get_methods():
            if method.get_name() not in ('q7StoryCityCocBegin', 'q7StoryCityCocFinish'):
                continue
            name = method.get_name()
            seen.add(name)
            instructions = list(method.get_code().get_bc().get_instructions()) if method.get_code() else []
            unwrap = any('FailureSafeProfileProvider;->unwrapStore' in ins.get_output()
                         for ins in instructions if ins.get_name().startswith('invoke-'))
            direct_store_test = any(ins.get_name() == 'instance-of' and
                                    'LocalProfileStore;' in ins.get_output() for ins in instructions)
            if not unwrap or direct_store_test:
                raise ValueError('%s %s does not use exact wrapper unwrap' % (label, name))
    required = {'q7StoryCityCocBegin', 'q7StoryCityCocFinish'}
    if seen != required:
        raise ValueError('%s missing COC wrapper entry methods' % label)
    return True


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: verify_manager_field_opcodes.py CLASSES7_DEX')
    path = Path(sys.argv[1])
    verify(path.read_bytes(), str(path))
    print('field-opcode/type scan PASS: ' + str(path))


if __name__ == '__main__':
    main()
