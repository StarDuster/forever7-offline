"""Explicit complete original hero-wish periods; no clock or row rewrite."""
import copy
import sys
import unittest
from test_gacha_archive import ROOT,archive
sys.path.insert(0,str(ROOT/'analysis/research-agent'))
from read_literal_marshal import read


class HeroWishArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base=ROOT/'analysis/android640-scripts/com/data/cdata'
        cls.table=read(base/'chouka_treasure_wish.marshal')
        cls.heroes=read(base/'hero.marshal')
    def setUp(self):archive.offline_archive_clear()
    def tearDown(self):archive.offline_archive_clear()

    def test_all14_rows_group_by_complete_epoch_for_six_explicit_wires(self):
        before=copy.deepcopy(self.table)
        ids=[]
        for wire in (1,119,126,143,154,164):
            row=dict(wire_t=wire,category='hero_treasure')
            with self.assertRaises(ValueError):archive.archive_make_session(row,self.table)
            periods=archive.archive_hero_wish_periods(self.table,wire,self.heroes)
            self.assertEqual(len(periods),1)
            period=periods[0];ids.extend(period['hero_wish_ids'])
            context=archive.archive_make_session(row,self.table,hero_wish_id=period['hero_wish_id'])
            self.assertEqual(context['hero_wish_ids'],period['hero_wish_ids'])
            self.assertEqual(context['hero_wish_policy'],'offline-original-hero-wish-period-v1')
            archive._f7_archive_session=context
            self.assertEqual(archive.archive_scoped_hero_wish_ids(self.table,wire),period['hero_wish_ids'])
            for wish in period['hero_wish_ids']:
                original=self.table[wish]
                self.assertEqual(tuple(original['begin_time']),period['begin'])
                self.assertEqual(tuple(original['end_time']),period['end'])
                self.assertIn(self.heroes[original['wish_target']]['name'],period['name'])
            self.assertIn(period,archive.archive_filter(periods,archive.archive_date(period['begin'])))
        self.assertEqual(len(ids),14)
        self.assertEqual(len(set(ids)),14)
        self.assertEqual(before,self.table)
        self.assertEqual(archive.archive_hero_wish_periods(self.table,5),[])
        self.assertEqual(archive.archive_hero_wish_periods(self.table,354),[])

    def test_scope_rejects_partial_cross_wire_unknown_or_changed_policy(self):
        context=archive.archive_make_session(dict(wire_t=1,category='hero_treasure'),self.table,hero_wish_id=11)
        for bad in (None,dict(context,wire_t=119),dict(context,hero_wish_ids=[11]),
                    dict(context,hero_wish_ids=[11,12,999]),dict(context,hero_wish_ids=[13,12,11]),
                    dict(context,hero_wish_policy='unapproved')):
            archive._f7_archive_session=bad
            self.assertIsNone(archive.archive_scoped_hero_wish_ids(self.table,1))
        with self.assertRaises(ValueError):
            archive.archive_make_session(dict(wire_t=119,category='hero_treasure'),self.table,hero_wish_id=11)

    def test_original_group_getter_filters_exact_epoch_and_keeps_fixed_exclusion(self):
        fallback=[]
        getter=archive.make_archive_wish_group_getter(lambda self,wire,fixed=False:fallback.append(wire)or {'original':[]},self.table)
        self.assertEqual(getter(None,1),{'original':[]})
        archive._f7_archive_session=archive.archive_make_session(dict(wire_t=1,category='hero_treasure'),self.table,hero_wish_id=11)
        self.assertEqual(getter(None,1),{1:[11,12],2:[13]})
        self.assertEqual(getter(None,1,True),{1:[11,12]})
        self.assertEqual(getter(None,119),{'original':[]})
        archive._f7_archive_session['hero_wish_ids']=[11]
        self.assertEqual(getter(None,1),{'original':[]})
        self.assertEqual(fallback,[1,119,1])


if __name__=='__main__':unittest.main()
