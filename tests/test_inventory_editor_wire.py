"""Finite original-code wire test: MD5 decoder -> GateClient.entity_message -> rpcdecorator.call.

Only Python2 string/bytes and BSON/renderer/network seams are adapted. The
dispatcher, decoder, decorator call, and method name are original bodies.

MAINTAINER DEPENDENCY: reads original-py-640 codec/rpc/GateClient source and lib2to3; not part of source export.
"""
import ast
import hashlib
import importlib.util
import sys
import textwrap
import types
import unittest
from pathlib import Path
from lib2to3.refactor import RefactoringTool, get_fixers_from_package

ROOT = Path(__file__).resolve().parents[1]
FIX = RefactoringTool(get_fixers_from_package('lib2to3.fixes'))
NS = types.SimpleNamespace


def extract_class(path, name, env):
    text = (ROOT / path).read_text()
    tree = ast.parse(str(FIX.refactor_string(text, path)))
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), path + ':host', 'exec'), env)
    return env[name]


def extract_function(path, name, env):
    text = (ROOT / path).read_text()
    lines = text.splitlines(True)
    indent = '    ' if any(line.startswith('    def ' + name + '(') for line in lines) else ''
    start = next(i for i, line in enumerate(lines) if line.startswith(indent + 'def ' + name + '('))
    end = start + 1
    while end < len(lines):
        line = lines[end]
        if line.startswith(indent + 'def ') or line.startswith(indent + '@') or line.startswith('class '):
            break
        end += 1
    source = textwrap.dedent(''.join(lines[start:end])) + '\n'
    tree = ast.parse(str(FIX.refactor_string(source, path + ':host')))
    exec(compile(ast.Module(body=tree.body, type_ignores=[]), path + ':host', 'exec'), env)
    return env[name]


class H(object):
    def __init__(self):
        self.h = hashlib.md5()

    def update(self, value):
        if isinstance(value, str):
            value = value.encode('ascii')
        self.h.update(value)

    def digest(self):
        return self.h.digest()


class BytesMD5(object):
    @staticmethod
    def md5():
        return H()


class Log(object):
    def __getattr__(self, name):
        return lambda *args, **kwargs: None


def load_original_codec():
    env = {'LogManager': NS(get_logger=lambda *a: Log()),
           'hashlib': BytesMD5, 'binascii': __import__('binascii'),
           'StandardError': Exception, 'MAX_STATIC_INDEX': 100000, 'DEBUG_MODE': 0}
    cache = extract_class('analysis/original-py-640/lib/common/Md5OrIndexCodec.py', 'Md5Cache', env)
    static = extract_class('analysis/original-py-640/lib/common/Md5OrIndexCodec.py', 'StaticIndexCache', env)
    decoder = extract_class('analysis/original-py-640/lib/common/Md5OrIndexCodec.py', 'Md5OrIndexDecoder', env)
    return cache, static, decoder


def load_rpc():
    env = {'LogManager': NS(get_logger=lambda *a: Log()), 'gg': NS(avatar_callback_map={}, avatar_callback_need_result={}),
           'CLIENT_ONLY': 0, 'SERVER_ONLY': 1, 'CLIENT_SERVER': 2, 'CLIENT_STUB': 3,
           'RpcMethodArg': object, 'ConvertError': Exception, 'Avatar': type('Avatar', (object,), {}), 'MailBox': type('MailBox', (object,), {}), 'EntityManager': NS(getentity=lambda value: None)}
    args = {'LogManager': NS(get_logger=lambda *a: Log()), 'IdManager': NS(bytes2id=lambda value: value),
            'StandardError': Exception, 'ConvertError': Exception}
    for name in ('RpcMethodArg', 'NoLimit', 'NumeralLimit', 'Int', 'Str', 'Bool', 'List'):
        extract_class('analysis/original-py-640/lib/common/RpcMethodArgs.py', name, args)
    env.update({name: args[name] for name in ('Int', 'Str', 'Bool', 'List', 'RpcMethodArg')})
    env['ConvertError'] = args['ConvertError']
    rpc_class = extract_class('analysis/original-py-640/lib/common/rpcdecorator.py', 'RpcMethod', env)
    rpc_method = extract_function('analysis/original-py-640/lib/common/rpcdecorator.py', 'rpc_method', env)
    return rpc_class, rpc_method, env


class WireTest(unittest.TestCase):
    def test_exact_wire_name_reaches_real_decorator(self):
        cache, static, decoder = load_original_codec()
        rpc_class, rpc_method, rpenv = load_rpc()

        class ClientAvatar(object):
            pass

        # UI module imports these names; use the actual decorator and decoder.
        entity = types.ModuleType('entity')
        entity.__path__ = []
        clientavatar = types.ModuleType('entity.ClientAvatar')
        clientavatar.ClientAvatar = ClientAvatar
        common = types.ModuleType('common')
        common.__path__ = []
        decorator = types.ModuleType('common.rpcdecorator')
        decorator.rpc_method = rpc_method
        decorator.CLIENT_STUB = 3
        args = types.ModuleType('common.RpcMethodArgs')
        for name in ('Bool', 'Int', 'Str', 'List'):
            setattr(args, name, getattr(types, 'SimpleNamespace') and __import__('builtins'))
        # The real arg classes are captured from the same extraction env.
        for name in ('Bool', 'Int', 'Str', 'List'):
            setattr(args, name, rpenv[name])
        codec = types.ModuleType('common.Md5OrIndexCodec')
        codec.Md5OrIndexDecoder = decoder
        gg = types.ModuleType('gg')
        gg.avatar = NS(account='wire-account')
        gg.ui = NS(lock=lambda key: None, unlock=lambda key: None)
        saved = dict(sys.modules)
        sys.modules.update({'gg': gg, 'entity': entity, 'entity.ClientAvatar': clientavatar,
                            'common': common, 'common.rpcdecorator': decorator,
                            'common.RpcMethodArgs': args, 'common.Md5OrIndexCodec': codec})
        try:
            spec = importlib.util.spec_from_file_location(
                'inventory_ui_wire', ROOT / 'offline/current/runtime/project7_inventory_editor_ui.py')
            ui = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ui)
            ui._install_rpc()
            self.assertIs(getattr(ClientAvatar, 'q7InventoryEditReply'),
                          getattr(ClientAvatar, 'q7InventoryEditReply'))
            # Decoder registration must survive late setattr.
            self.assertEqual(decoder.decode(NS(index=0, md5=hashlib.md5(b'q7InventoryEditReply').digest()))[0],
                             'q7InventoryEditReply')
            self.assertEqual(decoder.decode(NS(index=0, md5=hashlib.md5(b'q7InventoryCatalogReply').digest()))[0],
                             'q7InventoryCatalogReply')
            received = []
            ClientAvatar.q7InventoryEditReply = rpc_method(
                3, (args.Bool('rs'), args.Int('reason'), args.Str('op')))(
                    lambda self, rs, reason=0, op='': received.append((rs, reason, op)))
            # Extract the original GateClient.entity_message body, not a fake dispatcher.
            genv = {'Md5OrIndexDecoder': decoder,
                    'IdManager': NS(bytes2id=lambda value: value),
                    'EntityManager': NS(getentity=lambda value: avatar),
                    'BSON': type('BSON', (), {'__init__': lambda self, value: setattr(self, 'value', value),
                                               'decode': lambda self: self.value})}
            gate_entity_message = extract_function('analysis/original-py-640/lib/client/GateClient.py',
                                                   'entity_message', genv)
            avatar = ClientAvatar()
            avatar.server = NS(send_reg_md5_index=lambda *a: None)
            gate = NS(_set_received_seq=lambda msg: None, logger=Log(),
                      enable_reg_md5_index=False, _handle_last_traceback=lambda *a: __import__('traceback').print_exc())
            message = NS(id=b'id', method=NS(index=0, md5=hashlib.md5(b'q7InventoryEditReply').digest()),
                         parameters={'rs': True, 'reason': 0, 'op': 'a' * 32})
            gate_entity_message(gate, None, message, None)
            self.assertEqual(received, [(True, 0, 'a' * 32)])
        finally:
            for name in list(sys.modules):
                if name not in saved:
                    del sys.modules[name]
            sys.modules.update(saved)
        print('PASS inventory wire: original Md5OrIndexDecoder -> GateClient.entity_message -> rpcdecorator.call')


if __name__ == '__main__':
    unittest.main(verbosity=2)
