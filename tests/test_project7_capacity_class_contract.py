"""Regression for startup passing a ClientAvatar class to capacity projection."""
import _paths  # noqa: E402,F401
import importlib.util
import unittest

from tests.test_project7_shadow_capacity import Harness, ROOT


class CapacityClassContractTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()

    def tearDown(self):
        self.h.close()

    def test_startup_class_assembly_without_avatar_instance(self):
        spec = importlib.util.spec_from_file_location(
            "capacity_startup_contract", ROOT / "runtime/project7_startup_hook.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        startup = module.StartupPolicy.__new__(module.StartupPolicy)
        startup.tutorials = {"avatar_methods": {}}
        startup.tutorial_completion = None
        startup.trial_retry = None
        startup.wish_member = None
        startup.capacity = self.h.state
        self.assertIsNone(self.h.gg.avatar)
        startup.check_avatar()
        self.assertIsNone(self.h.gg.avatar)

    def test_class_check_preserves_generation_and_instance_guards(self):
        self.assertIs(self.h.state.check_avatar_class(self.h.ClientAvatar), self.h.state)
        with self.assertRaises(RuntimeError):
            self.h.state.check_avatar_class(type("OtherAvatar", (), {}))
        with self.assertRaises(RuntimeError):
            self.h.state.check_avatar(self.h.ClientAvatar)
        self.h.ClientAvatar.init_from_dict = lambda *args: None
        with self.assertRaises(RuntimeError):
            self.h.state.check_avatar_class(self.h.ClientAvatar)


if __name__ == "__main__":
    unittest.main()
