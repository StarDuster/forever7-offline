"""Float-bearing policies bind raw ASCII input; runtime canonical is mutation state."""
from pathlib import Path
import hashlib, sys, unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'offline' / 'current' / 'runtime'))
sys.path.insert(0, str(ROOT / 'project7_bridge' / 'tools'))
import project7_dynamic_ui_families as families
import project7_wish_ui as wish
from project7_feature_assets import dynamic_ui_policy, wish_ui_policy


class RuntimePolicyPinTests(unittest.TestCase):
    def test_float_policy_raw_pins_and_policy_parsing(self):
        dynamic = dynamic_ui_policy(ROOT)
        self.assertEqual(hashlib.sha256(dynamic.encode('ascii')).hexdigest(),
                         'd089f495f0549f24c7069fcb386e5bcabd954ff50a06359d71417f1767604f73')
        self.assertTrue(families._policy(dynamic))
        desire = wish_ui_policy(ROOT)
        self.assertEqual(hashlib.sha256(desire.encode('ascii')).hexdigest(),
                         '72762790a130d0710545a9cb95211acfefd084cea4d05d1fe9c84bd9344427bc')
        self.assertTrue(wish._policy(desire))

    def test_raw_policy_mutation_fails_before_schema(self):
        dynamic = dynamic_ui_policy(ROOT)
        with self.assertRaisesRegex(ValueError, 'text changed'):
            families._policy(dynamic.replace('"publishable_ids"', '"publishable_ids" ', 1))
import _paths  # noqa: E402,F401
