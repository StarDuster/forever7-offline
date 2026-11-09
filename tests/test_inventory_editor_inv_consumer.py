"""Finite original InvData consumer for replay delete/upsert semantics.

Uses the original InvData.updateItems/deleteItems bodies. ItemData, catalog and
Cocos events are host seams; no fake server dispatcher.

MAINTAINER DEPENDENCY: reads original-py-640 InvData source and lib2to3; not part of source export.
"""
import ast
import sys
import types
import unittest
from pathlib import Path
from lib2to3.refactor import RefactoringTool, get_fixers_from_package

ROOT = Path(__file__).resolve().parents[1]
FIX = RefactoringTool(get_fixers_from_package('lib2to3.fixes'))
NS = types.SimpleNamespace


class FakeItem(object):
    def __init__(self, inv_id=0):
        self.invId = inv_id

    def initFromDict(self, info):
        self.uuid = info['u']
        self.itemid = info['i']
        self.type = info.get('type', 1)
        self.wrap = info.get('w', 0)
        self.prior = info.get('prior', 0)
        self.treasureExclusive = False
        self.treasureCost = 0
        self.treasureExpDict = {}

    def getPersistentDict(self):
        return {'u': self.uuid, 'i': self.itemid, 'type': self.type, 'w': self.wrap}


class FakeItemModule(object):
    ItemData = FakeItem


def load_inv_data():
    class ItemType(object):
        CATEGORY_COMMON = 'common'
        CATEGORY_TREASURE = 'treasure'
        CATEGORY_TASK = 'task'
        CATEGORY_GIFT = 'gift'
        CATEGORY_FURNITURE = 'furniture'
        CATEGORY_XINWU = 'xinwu'
    env = {'time': __import__('time'), 'ItemData': FakeItemModule,
           'ITEM_DATA': NS(data={}), 'const': NS(ItemType=ItemType)}
    text = (ROOT / 'analysis/original-py-640/entity/avatar_attrs/InvData.py').read_text()
    tree = ast.parse(str(FIX.refactor_string(text, 'InvData.py')))
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'InvData')
    exec(compile(ast.Module(body=[node], type_ignores=[]), 'InvData.py:host', 'exec'), env)
    return env['InvData']


class InvDataReplayTest(unittest.TestCase):
    def test_upsert_cannot_delete_and_ordered_replay_removes(self):
        InvData = load_inv_data()
        inv = InvData()
        inv.updateItems([{'u': 'uuid-a', 'i': 1, 'type': 1, 'w': 2}])
        self.assertEqual(inv.invByUUID['uuid-a'].wrap, 2)
        # Absolute upsert alone leaves the old stack; it cannot represent a
        # committed replacement to zero.
        inv.updateItems([{'u': 'uuid-a', 'i': 1, 'type': 1, 'w': 0}])
        self.assertIn('uuid-a', inv.invByUUID)
        # Replay order from the backend: delete tombstone before current upsert.
        inv.deleteItems(['uuid-a'])
        self.assertNotIn('uuid-a', inv.invByUUID)
        inv.updateItems([])
        self.assertNotIn('uuid-a', inv.invByUUID)
        print('PASS original InvData: absolute upsert cannot delete; ordered deleteItems replay removes')


if __name__ == '__main__':
    unittest.main(verbosity=2)
