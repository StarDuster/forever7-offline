"""Exactly one same-descriptor choose caller; original chooser/grants untouched."""
from pathlib import Path
import unittest
from test_project7_dream_hook import methods, raw, PKG

ROOT=Path(__file__).resolve().parents[1]


class SelectorHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        old=ROOT/'analysis/project7/event-reset-week-hook-v2/classes7.dex'
        new=ROOT/'analysis/project7/selector-hook-v1/classes7.dex'
        if not old.exists() or not new.exists():raise unittest.SkipTest('Maintainer source/target absent')
        cls.old,cls.new=methods(old),methods(new)

    def test_only_apply_current_changes_without_new_definitions_or_registers(self):
        self.assertEqual(set(self.old),set(self.new));self.assertEqual(len(self.old),3705)
        changed=[]
        for key,old in self.old.items():
            new=self.new[key];self.assertEqual(old.get_access_flags(),new.get_access_flags())
            if old.get_code():
                self.assertEqual(old.get_code().get_registers_size(),new.get_code().get_registers_size())
                self.assertEqual(old.get_code().get_ins_size(),new.get_code().get_ins_size())
            if raw(old)!=raw(new):changed.append(key)
        self.assertEqual(len(changed),1);self.assertEqual(changed[0][:2],(PKG+'LocalDrawEngine;','applyCurrent'))

    def test_original_choose_and_all_original_caller_instructions_are_retained(self):
        key=next(k for k in self.old if k[0]==PKG+'LocalDrawEngine;' and k[1]=='applyCurrent')
        old,new=raw(self.old[key]),raw(self.new[key]);self.assertEqual(len(old),len(new))
        different=[(a,b) for a,b in zip(old,new) if a!=b];self.assertEqual(len(different),1)
        a,b=different[0];self.assertEqual(a[0],'invoke-static');self.assertEqual(b[0],'invoke-static')
        self.assertTrue(b[1].startswith('v1, v8, v2, v4, '+PKG+'SelectorPolicy;->choose('))
        self.assertEqual(a,(b[0],b[1].replace('SelectorPolicy;->choose','LocalDrawEngine;->choose')))
        chooser=next(k for k in self.old if k[0]==PKG+'LocalDrawEngine;' and k[1]=='choose')
        self.assertTrue(self.old[chooser].get_access_flags()&2)
        self.assertEqual(raw(self.old[chooser]),raw(self.new[chooser]))


if __name__=='__main__':unittest.main()
