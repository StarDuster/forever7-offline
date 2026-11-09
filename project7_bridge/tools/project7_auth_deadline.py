"""Pinned local authentication deadline; preserve the original success and failure consumers."""
import _bootstrap  # noqa: E402,F401
import ast
import hashlib

SOURCE_SHA256 = '009ac38e8fb42de277128746d3255a23371997fc0476f139b2a147a47f0e94ac'

def patch_source(source):
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError('embedded source SHA mismatch')
    text = source.decode('ascii')
    tree = ast.parse(text)
    outer = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_q7_open']
    submitted = [n for n in outer[0].body if isinstance(n, ast.FunctionDef) and n.name == 'submitted']
    timers = [n for n in submitted[0].body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
              and isinstance(n.value.func, ast.Attribute) and isinstance(n.value.func.value, ast.Name)
              and n.value.func.value.id == 'gg' and n.value.func.attr == 'exec_delay']
    if len(timers) != 1:
        raise ValueError('timer shape mismatch')
    call = timers[0].value
    if len(call.args) != 2 or call.keywords or not isinstance(call.args[0], ast.Constant) or call.args[0].value != 20000 or not isinstance(call.args[1], ast.Name) or call.args[1].id != 'timeout':
        raise ValueError('timer arguments mismatch')
    arg = call.args[0]
    lines = text.splitlines(keepends=True)
    line = lines[arg.lineno - 1]
    if line[arg.col_offset:arg.end_col_offset] != '20000':
        raise ValueError('literal mismatch')
    lines[arg.lineno - 1] = line[:arg.col_offset] + '60000' + line[arg.end_col_offset:]
    return ''.join(lines).encode('ascii')

LOGIN_FID = 3611882431
LOGIN_SHA256 = '8928c1e55d9a035ed0a7cb33587599a3c03bfe338a0a78dde753c1cc2a0259e7'

def patch_login(archive, record):
    import copy, ctypes, io, zlib
    from xdis.unmarshal import load_code
    from marshal27 import dumps
    index = archive.entries.index(record)
    clear = archive.read(index)
    if hashlib.sha256(clear).hexdigest() != LOGIN_SHA256:
        raise ValueError('login module SHA mismatch')
    original = load_code(io.BytesIO(clear), 62211, code_objects={})
    matched = [(i, v) for i, v in enumerate(original.co_consts)
               if isinstance(v, str) and hashlib.sha256(v.encode('ascii')).hexdigest() == SOURCE_SHA256]
    if len(matched) != 1:
        raise ValueError('embedded auth source missing or ambiguous')
    slot, source = matched[0]
    patched = copy.deepcopy(original)
    consts = list(patched.co_consts)
    consts[slot] = patch_source(source.encode('ascii')).decode('ascii')
    patched.co_consts = tuple(consts)
    expected = dumps(patched)
    check = load_code(io.BytesIO(expected), 62211, code_objects={})
    unchanged = copy.deepcopy(check)
    reverted = list(unchanged.co_consts); reverted[slot] = source; unchanged.co_consts = tuple(reverted)
    if dumps(unchanged) != dumps(original):
        raise ValueError('non-auth module data changed')
    reverse = expected[::-1]
    compressed = zlib.compress(bytes(v ^ 154 if i < 128 else v for i,v in enumerate(reverse)))
    buffer = ctypes.create_string_buffer(compressed, len(compressed))
    if archive.lib.f7_rotor(archive.key, buffer, len(compressed), 1):
        raise MemoryError('rotor encode failed')
    return buffer.raw, expected, {
        'policy_ms': 60000, 'old_policy_ms': 20000,
        'original_login_sha256': LOGIN_SHA256,
        'new_login_sha256': hashlib.sha256(expected).hexdigest(),
        'source_sha256': SOURCE_SHA256,
        'patched_source_sha256': hashlib.sha256(consts[slot].encode('ascii')).hexdigest(),
        'embedded_constant_slot': slot, 'other_code_and_constants_unchanged': True,
        'original_auth_success_predicate_unchanged': True,
        'business_wait_unchanged': True, 'automatic_retry': False,
        'native_checksums_verified': False,
    }
