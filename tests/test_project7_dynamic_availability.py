"""Only the reviewed dynamic UI is admitted; data/backend sets are not UI sets."""
import _paths  # noqa: E402,F401
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'offline'/'current'/'tools'))
import project7_feature_assets as assets


class DynamicAvailabilityTests(unittest.TestCase):
    def test_public_delta_is_verified_family_scope_and_preserves_original_static_set(self):
        rows=[line.split('\t') for line in (ROOT/'offline/current/data/project7_history_catalog/catalog-v3.tsv').read_text().splitlines() if line.startswith('P\t')]
        static={int(row[1]) for row in rows if row[4]=='1'}
        policy=json.loads(assets.history_ui_policy())
        public=set(policy['ready_ids'])
        self.assertEqual(len(static),385)
        self.assertEqual(public-static,set(assets.DYNAMIC_PUBLIC_READY_IDS)|set(assets.WISH_PUBLIC_READY_IDS))
        self.assertEqual(len(public-static),55)
        self.assertTrue(static<=public)
        self.assertFalse(public.intersection((1,354,484)))
        self.assertEqual(public,set(policy['all_history_ids']))
        self.assertEqual(policy['asset_sha256'],assets.HISTORY_CATALOG_SHA)

    def test_exact_detail_policy_matches_scope_without_making_its_own_ready_claim(self):
        detail=json.loads(assets.dynamic_ui_policy())
        self.assertEqual(detail['detail_ids'],list(assets.DYNAMIC_PUBLIC_READY_IDS))
        self.assertEqual(detail['verified_ids'],detail['detail_ids'])
        self.assertEqual(detail['publishable_ids'],detail['detail_ids'])
        self.assertEqual(detail['public_ready_ids'],[])
        self.assertEqual(detail['base_sha256'],assets.HISTORY_CATALOG_SHA)
        self.assertEqual(detail['backend_sha256'],assets.DYNAMIC_CATALOG_SHA)
        for pool in detail['pools']:
            for name in ('cocos/common_icon.csb','cocos/hero_herolist_common.csb','cocos/res/hkytw5.ttf'):
                self.assertIn(name,pool['required_assets'])

    def test_other_backend_candidate_cannot_be_accidentally_published(self):
        with patch.object(assets,'DYNAMIC_PUBLIC_READY_IDS',assets.DYNAMIC_PUBLIC_READY_IDS+(5,)):
            with self.assertRaises(ValueError):assets.history_ui_policy()
            with self.assertRaises(ValueError):assets.dynamic_ui_policy()
        with patch.object(assets,'WISH_PUBLIC_READY_IDS',assets.WISH_PUBLIC_READY_IDS+(485,)):
            with self.assertRaises(ValueError):assets.history_ui_policy()
            with self.assertRaises(ValueError):assets.wish_ui_policy()

    def test_wish_scope_is_exact_and_disjoint_from_family_owner(self):
        wish=json.loads(assets.wish_ui_policy())
        self.assertEqual(wish['detail_ids'],list(assets.WISH_PUBLIC_READY_IDS))
        self.assertEqual(wish['verified_ids'],wish['detail_ids'])
        self.assertEqual(wish['public_ready_ids'],[])
        self.assertFalse(set(wish['detail_ids'])&set(assets.DYNAMIC_PUBLIC_READY_IDS))
        self.assertEqual(wish['backend_sha256'],assets.WISH_CATALOG_SHA)

    def test_draw_policy_accepts_generated_manifest_and_rejects_old_or_widened(self):
        spec=importlib.util.spec_from_file_location('availability_draw_ui',ROOT/'offline/current/runtime/project7_draw_ui.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        current=json.loads(assets.history_ui_policy())
        self.assertEqual(module._history_policy(json.dumps(current)),current)
        for ready in ([t for t in current['ready_ids'] if t!=485],current['ready_ids']+[1]):
            changed=dict(current,ready_ids=sorted(ready))
            with self.assertRaises(ValueError):module._history_policy(json.dumps(changed))


if __name__=='__main__':unittest.main()
