"""Regression: historical production-contract source paths resolve after the split."""
import _paths  # noqa: E402,F401
import unittest
from forever7_paths import RECORDED_SOURCE_PATHS, resolve_recorded_path

PATHS = (
    'runtime/android_history_draw/src/com/project7/localmanager/HistoryDrawPolicy.java',
    'runtime/offline_battle.py',
    'runtime/offline_conditions.py',
    'runtime/offline_stage.py',
    'runtime/project7_action_ledger_code20_patch/seams.xor-zlib',
    'runtime/project7_action_ledger_integration_candidate/trigger-extra-code20-v1.tsv',
    'runtime/project7_bson_fast/BsonLite-fast.dex',
    'runtime/project7_bson_fast/BsonLite.smali',
    'runtime/project7_event_auto_trigger_candidate/trigger-extra-v1.tsv',
    'runtime/project7_event_auto_trigger_condition_candidate/trigger-extra-conditions-v1.tsv',
    'runtime/project7_mainline32_data_candidate/catalog-v1.json.gz',
    'runtime/project7_mainline32_data_candidate/contract-v1.json',
    'runtime/project7_manager_rpc_projection_patch/LocalGatewayServer.smali',
)


class RecordedPathTests(unittest.TestCase):
    def test_thirteen_historical_production_paths_resolve(self):
        self.assertEqual(len(PATHS), 13)
        self.assertEqual(set(PATHS), set(RECORDED_SOURCE_PATHS))
        for recorded in PATHS:
            with self.subTest(recorded=recorded):
                target = resolve_recorded_path(recorded)
                self.assertEqual(target, _paths.ROOT / RECORDED_SOURCE_PATHS[recorded])
                # Three pinned artifacts are intentionally private/ignored in a
                # tracked-only worktree; their structural target is still verified.
                if recorded not in {
                        'runtime/project7_bson_fast/BsonLite-fast.dex',
                        'runtime/project7_mainline32_data_candidate/catalog-v1.json.gz',
                        'runtime/project7_mainline32_data_candidate/contract-v1.json'}:
                    self.assertTrue(target.is_file(), recorded)


if __name__ == '__main__':
    unittest.main()
