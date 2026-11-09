"""Original poster guard and chooser callbacks, not an invented selector."""
from pathlib import Path
import textwrap
from types import SimpleNamespace as NS
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Widget:
    def setVisible(self, value): self.visible = value


class OriginalSelfChooseRouteTests(unittest.TestCase):
    def setUp(self):
        self.requests, self.events, self.entries, self.timers = [], [], [], []
        self.chooser = object()
        self.engine = NS(avatar=NS(luckyDrawData=NS(getChooseHeroes=lambda *args: (False, [0, 0])),
            setChooseHeroes=lambda wire, heroes: self.requests.append((wire, heroes)),
            checkGamePlaySwitch=lambda kind, yes, no: yes()),
            ui=NS(panels=NS(card_hero_choose=self.chooser),
                  actions=NS(card_tab=NS(tab_out=NS(start=lambda: None)))),
            exec_delay=lambda delay, callback: self.timers.append(callback))
        namespace = {'gg': self.engine, 'cc': NS(ccui=NS(TOUCH_EVENT_ENDED=2)),
            'CHOUKA_INFO_DATA': NS(data={wire: {'self_choose': True} for wire in (265,369,427,454,455,484)}),
            'const': NS(LuckyDrawIdx=NS(S=0, A=1), GamePlayName=NS(FRIENDSUMMON=1),
                        LuckyDrawType=NS(NORMAL=1, FRIEND=99, NEWFRIEND=131))}
        source = (ROOT/'analysis/native-mainline-delivery/card_tab.py').read_text()
        self.functions = {}
        for name in ('refresh_open_cost_coin_and_btn', '_on_open_go_click', 'on_open_choose_click'):
            start = source.index('    def ' + name + '(')
            end = source.index('\n    def ', start + 10)
            body = source[start:end].split('\n    @')[0]
            exec(textwrap.dedent(body), namespace)
            self.functions[name] = namespace[name]
        self.panel = NS(valid=True, cover=False, draw_type=265, _node=Widget(),
            add_layer=lambda target: 'original-chooser-layer',
            proc_event=lambda *args, **kwargs: self.events.append((args, kwargs)),
            _on_activity_click=self.entries.append)
        for name in ('once_cost_1','all_cost_2','all_cost_1','panel_open2',
                     'btn_open_go','panel_open','btn_open_choose'):
            setattr(self.panel, name, Widget())

    def test_stock_missing_choice_guard_is_bypassed_by_private_go_for_every_selfchoose_pool(self):
        for wire in (265,369,427,454,455,484):
            self.panel.draw_type = wire
            self.functions['refresh_open_cost_coin_and_btn'](self.panel)
            self.assertTrue(self.panel.btn_open_choose.visible)
            self.assertFalse(self.panel.btn_open_go.visible)
            self.assertFalse(self.panel.panel_open.visible)
            self.functions['_on_open_go_click'](self.panel)
            self.assertEqual(self.entries[-1], wire)
        self.assertEqual(self.requests, [])

    def test_original_choose_button_waits_for_actual_selection_and_cancel_sends_nothing(self):
        choose = self.functions['on_open_choose_click']
        choose(self.panel, None, 0)
        self.assertEqual(self.events, [])
        choose(self.panel, None, 2)
        args, kwargs = self.events[-1]
        self.assertEqual(args, ('show',))
        self.assertEqual(kwargs['choose_heroes'], [0, 0])
        self.assertEqual(kwargs['choose_order'], [3, 4])
        self.assertEqual(kwargs['_layer'], 'original-chooser-layer')
        self.assertEqual(self.requests, [])  # Cancel simply never calls callback.
        kwargs['callback']([135, 117])
        self.assertEqual(self.requests, [(265, [135, 117])])
        self.assertEqual(self.entries, [])


if __name__ == '__main__':
    unittest.main()
