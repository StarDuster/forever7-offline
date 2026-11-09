"""The auto-trigger projection must never drop a divergent emergency condition."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from project7_event_auto_trigger_candidate import require_emergency_match


class EmergencyGuardTests(unittest.TestCase):
    def test_absent_condition_equals_false(self):
        require_emergency_match(1, {"conds": {}}, {"isEmergencyEvent": False})

    def test_explicit_zero_equals_false(self):
        require_emergency_match(1, {"conds": {101: "0"}}, {"isEmergencyEvent": False})

    def test_explicit_one_equals_true(self):
        require_emergency_match(1, {"conds": {101: "1"}}, {"isEmergencyEvent": True})

    def test_nonbinary_condition_fails_closed(self):
        for value in ("2", "-1", "true", "01"):
            with self.assertRaises(ValueError):
                require_emergency_match(1, {"conds": {101: value}}, {"isEmergencyEvent": True})
            with self.assertRaises(ValueError):
                require_emergency_match(1, {"conds": {101: value}}, {"isEmergencyEvent": False})

    def test_divergence_fails_closed(self):
        for value, content in (("0", True), ("1", False), ("x", False)):
            with self.assertRaises(ValueError):
                require_emergency_match(1, {"conds": {101: value}},
                                        {"isEmergencyEvent": content})

    def test_absent_condition_cannot_hide_true_emergency(self):
        with self.assertRaises(ValueError):
            require_emergency_match(1, {"conds": {}}, {"isEmergencyEvent": True})


if __name__ == "__main__":
    unittest.main()
