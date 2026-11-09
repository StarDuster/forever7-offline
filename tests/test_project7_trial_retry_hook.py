"""Trial lifecycle prefixes retain original fallthrough, caches and exception paths."""
import _paths  # noqa: E402,F401
from pathlib import Path
import unittest
from test_project7_dream_hook import methods,raw,PKG
from test_project7_reliable_scope_hook import offsets

ROOT=Path(__file__).resolve().parents[1]
G=PKG+'LocalGatewayServer;';B=PKG+'LocalEventBattleEngine;';T=PKG+'TrialRetryGateway;'


class TrialRetryHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=ROOT/'analysis/project7/story-mission-hook-v2/classes7.dex'
        target=ROOT/'analysis/project7/trial-retry-hook-v1/classes7.dex'
        if not source.is_file() or not target.is_file():raise unittest.SkipTest('Maintainer fixed source/target absent')
        cls.old,cls.new=methods(source),methods(target)

    def key(self,owner,name):return next(k for k in self.old if k[:2]==(owner,name))

    def test_exact_definition_and_changed_body_scope(self):
        self.assertEqual(len(self.old),3710);self.assertEqual(len(self.new),3711)
        sync=self.key(B,'sync');self.assertEqual(set(self.new)-set(self.old),{(B,'q7OriginalSync',sync[2])})
        self.assertFalse(set(self.old)-set(self.new));changes=[]
        for key,old in self.old.items():
            new=self.new[key];self.assertEqual(old.get_access_flags(),new.get_access_flags())
            if raw(old)!=raw(new):changes.append(key[:2])
            if old.get_code() and key!=sync:
                self.assertEqual(old.get_code().get_registers_size(),new.get_code().get_registers_size())
                self.assertEqual(old.get_code().get_ins_size(),new.get_code().get_ins_size())
        self.assertCountEqual(changes,[(B,'sync')]+[(G,n) for n in ('handleCombatAdmission','handleCombatOfflineFinish','finishAbandonedStory','prepareEventEffects')])

    def test_begin_only_redirects_original_authorized_call(self):
        key=self.key(G,'handleCombatAdmission');old,new=raw(self.old[key]),raw(self.new[key])
        self.assertEqual(len(old),len(new));changes=[(a,b) for a,b in zip(old,new) if a!=b]
        self.assertEqual(len(changes),1)
        self.assertEqual(changes[0],(('invoke-virtual','v11, v15, '+PKG+'LocalEventEngine;->beginStoryBattle(I)Z'),
                                    ('invoke-static','v7, v6, v10, v11, v15, '+T+'->begin('+G+' Ljava/lang/String; '+PKG+'LocalTutorialStore$Progress; '+PKG+'LocalEventEngine; I)Z')))

    def test_sync_original_body_retained_and_same_argument_wrapper(self):
        key=self.key(B,'sync');retained=self.new[(B,'q7OriginalSync',key[2])]
        self.assertEqual(raw(self.old[key]),raw(retained))
        self.assertEqual(retained.get_access_flags(),self.old[key].get_access_flags()|0x1000)
        self.assertEqual(retained.get_code().get_registers_size(),self.old[key].get_code().get_registers_size())
        self.assertEqual(raw(self.new[key]),[('invoke-static','v0, v1, v2, '+T+'->sync'+key[2]),('return-void','')])

    def test_prefixes_forward_real_parameters_and_preserve_all_original_branches_and_tries(self):
        from androguard.core.dex import Operand
        for name,helper,parameter_range,skip in (
            ('handleCombatOfflineFinish','handleFinish',(23,31),4),
            ('finishAbandonedStory','handleGiveup',(13,20),4),
            ('prepareEventEffects','recover',(16,19),1)):
            key=self.key(G,name);old,new=list(self.old[key].get_instructions()),list(self.new[key].get_instructions())
            prefix=raw(self.new[key])[:skip]
            self.assertEqual(prefix[0][0],'invoke-static/range')
            self.assertTrue(prefix[0][1].startswith('v%d ... v%d, %s->%s('%(*parameter_range,T,helper)))
            if skip==4:
                self.assertEqual(prefix[1],('move-result','v0'));self.assertEqual(prefix[2][0],'if-eqz')
                self.assertEqual(prefix[3],('return-void',''))
                self.assertEqual(2*new[2].get_ref_off(),sum(op.get_length() for op in new[2:4]))
            self.assertEqual(len(new)-skip,len(old))
            ao,bo=offsets(old),offsets(new);ap,bp={v:k for k,v in ao.items()},{v:k for k,v in bo.items()}
            mapping={i:0 if i<skip else i-skip for i in range(len(new)+1)}
            for i,a in enumerate(old):
                ni=i+skip;b=new[ni]
                self.assertEqual(a.get_name().split('/')[0],b.get_name().split('/')[0])
                if a.get_name().startswith(('if-','goto')):
                    regs=lambda op:[x[1] for x in op.get_operands() if x[0]==Operand.REGISTER]
                    self.assertEqual(regs(a),regs(b))
                    self.assertEqual(ao[ap[i]+2*a.get_ref_off()],mapping[bo[bp[ni]+2*b.get_ref_off()]])
                else:self.assertEqual(a.get_output(),b.get_output())
            def exceptions(method,positions,index_map):
                code=method.get_code()
                if not code.get_tries_size():return []
                hs=code.get_handlers();handlers={h.get_off()-hs.get_off():h for h in hs.get_list()};rows=[]
                for tr in code.get_tries():
                    h=handlers[tr.get_handler_off()]
                    pairs=[(code.CM.get_type(p.get_type_idx()),index_map[positions[2*p.get_addr()]]) for p in h.get_handlers()]
                    catch_all=index_map[positions[2*h.get_catch_all_addr()]] if h.get_size()<=0 else None
                    rows.append((index_map[positions[2*tr.get_start_addr()]],index_map[positions[2*(tr.get_start_addr()+tr.get_insn_count())]],pairs,catch_all))
                return rows
            self.assertEqual(exceptions(self.old[key],ao,{i:i for i in range(len(old)+1)}),exceptions(self.new[key],bo,mapping))


if __name__=='__main__':unittest.main()


class TrialRetryPolicyPinTests(unittest.TestCase):
    def test_canonical_policy_pin_matches_runtime_and_raw_binding(self):
        import hashlib, json, re
        policy_path = ROOT / 'offline/current/java/android_trial_retry/trial-ui-policy-v1.json'
        raw = policy_path.read_bytes()
        canonical = json.dumps(json.loads(raw), sort_keys=True, ensure_ascii=True,
                               separators=(',', ':')).encode('ascii')
        self.assertEqual(hashlib.sha256(canonical).hexdigest(),
                         'f198e19879e2b819dad3e6a545476e64fbf7ef6664df629264e1ec781cda766c')
        compat = (ROOT / 'offline/current/runtime/project7_trial_retry_compat.py').read_text()
        self.assertIn("_SHA='f198e19879e2b819dad3e6a545476e64fbf7ef6664df629264e1ec781cda766c'", compat)
        hook = (ROOT / 'tools/project7_script_hook.py').read_text()
        self.assertIn("TRIAL_UI_POLICY_SHA = '" + hashlib.sha256(raw).hexdigest() + "'", hook)
