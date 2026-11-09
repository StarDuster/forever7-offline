"""Shared chapter wrappers preserve complete original bodies and other APIs."""
import _paths  # noqa: E402,F401
from pathlib import Path
import unittest
from test_project7_dream_hook import methods,raw,PKG

ROOT=Path(__file__).resolve().parents[1]
P=PKG+'LocalTutorialStore$Progress;'
CITY=PKG+'LocalCityProgress;'
SIGNATURES={
 ('area','(I)I'):'q7OriginalArea',
 ('mapStages','('+P+'I[B)[B'):'q7OriginalMapStages',
 ('stages','('+P+'I[B)[B'):'q7OriginalStages',
 ('status','('+P+'I[B)I'):'q7OriginalStatus',
 ('consumeVictory','('+P+'[BII)Z'):'q7OriginalConsumeVictory',
}


class StoryMissionHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        old=ROOT/'analysis/project7/reliable-scope-hook-v1/classes7.dex'
        new=ROOT/'analysis/project7/story-mission-hook-v2/classes7.dex'
        if not old.is_file() or not new.is_file():
            raise unittest.SkipTest('Maintainer pinned source/target absent')
        cls.old,cls.new=methods(old),methods(new)
        cls.selected={k:SIGNATURES[(k[1],k[2].replace(' ',''))]
                      for k in cls.old if k[0]==CITY and (k[1],k[2].replace(' ','')) in SIGNATURES}

    def test_only_five_wrappers_and_five_retained_methods_are_added(self):
        self.assertEqual(len(self.old),3705);self.assertEqual(len(self.new),3710)
        self.assertEqual(len(self.selected),5)
        expected={(k[0],name,k[2]) for k,name in self.selected.items()}
        self.assertEqual(set(self.new)-set(self.old),expected)
        self.assertFalse(set(self.old)-set(self.new))
        for key,old in self.old.items():
            new=self.new[key]
            self.assertEqual(old.get_access_flags(),new.get_access_flags())
            if key not in self.selected and key[:2]!=(PKG+'LocalGatewayServer;','handleCombatAdmission'):
                self.assertEqual(raw(old),raw(new),key)
                if old.get_code():
                    self.assertEqual(old.get_code().get_registers_size(),new.get_code().get_registers_size(),key)
        # Unchanged chapterScene and no-profile overloads retain their meaning.
        for name in ('chapterScene','stages','status'):
            self.assertTrue(any(k[0]==CITY and k[1]==name and k not in self.selected for k in self.old))

    def test_original_bodies_registers_and_exception_ranges_are_exactly_retained(self):
        def exceptions(method):
            code=method.get_code()
            if not code.get_tries_size():return []
            handlers=code.get_handlers();by_offset={h.get_off()-handlers.get_off():h for h in handlers.get_list()}
            result=[]
            for tr in code.get_tries():
                h=by_offset[tr.get_handler_off()]
                pairs=[(code.CM.get_type(p.get_type_idx()),p.get_addr()) for p in h.get_handlers()]
                catch_all=h.get_catch_all_addr() if h.get_size()<=0 else None
                result.append((tr.get_start_addr(),tr.get_insn_count(),pairs,catch_all))
            return result
        for key,name in self.selected.items():
            old=self.old[key];retained=self.new[(key[0],name,key[2])]
            self.assertEqual(retained.get_access_flags(),old.get_access_flags()|0x1000)
            self.assertEqual(raw(old),raw(retained),name)
            self.assertEqual(old.get_code().get_registers_size(),retained.get_code().get_registers_size())
            self.assertEqual(old.get_code().get_ins_size(),retained.get_code().get_ins_size())
            self.assertEqual(exceptions(old),exceptions(retained))

    def test_wrapper_forwards_every_incoming_argument_with_same_return_shape(self):
        for key in self.selected:
            method=self.new[key];code=method.get_code();instructions=raw(method)
            count=code.get_ins_size()
            self.assertEqual(count,self.old[key].get_code().get_ins_size())
            self.assertEqual(code.get_registers_size(),count+1)
            self.assertEqual(len(instructions),3)
            prefix=', '.join('v%d'%i for i in range(1,count+1))+', '
            self.assertEqual(instructions[0],('invoke-static',prefix+PKG+'StoryMissionBridge;->'+key[1]+key[2]))
            is_object=key[2].split(')')[-1].startswith(('[','L'))
            self.assertEqual(instructions[1],('move-result-object' if is_object else 'move-result','v0'))
            self.assertEqual(instructions[2],('return-object' if is_object else 'return','v0'))

    def test_trial_party_check_uses_existing_validity_and_preserves_original_control_flow(self):
        from androguard.core.dex import Operand
        from test_project7_reliable_scope_hook import offsets
        key=next(k for k in self.old if k[:2]==(PKG+'LocalGatewayServer;','handleCombatAdmission'))
        old,new=list(self.old[key].get_instructions()),list(self.new[key].get_instructions())
        calls=[i for i,op in enumerate(new) if 'StoryMissionBridge;->partyAllowed(' in op.get_output()]
        self.assertEqual(len(calls),1);call=calls[0]
        self.assertEqual([(op.get_name(),op.get_output()) for op in new[call:call+4]],
                         [('invoke-static','v1, '+PKG+'StoryMissionBridge;->partyAllowed([B)Z'),
                          ('move-result','v0'),('and-int','v17, v17, v0'),
                          ('sget-object','v0, Ljava/lang/Boolean;->FALSE Ljava/lang/Boolean;')])
        self.assertEqual(self.old[key].get_code().get_registers_size(),44)
        self.assertEqual(self.new[key].get_code().get_registers_size(),44)
        self.assertEqual(self.old[key].get_code().get_ins_size(),self.new[key].get_code().get_ins_size())
        kept=[i for i in range(len(new)) if i not in range(call,call+3)]
        mapping={i:(i if i<call else call if i<=call+3 else i-3) for i in range(len(new)+1)}
        ao,bo=offsets(old),offsets(new);ap,bp={v:k for k,v in ao.items()},{v:k for k,v in bo.items()}
        self.assertEqual(len(old),len(kept))
        for oi,ni in enumerate(kept):
            a,b=old[oi],new[ni]
            self.assertEqual(a.get_name().split('/')[0],b.get_name().split('/')[0])
            if a.get_name().startswith(('if-','goto')):
                regs=lambda op:[v[1] for v in op.get_operands() if v[0]==Operand.REGISTER]
                self.assertEqual(regs(a),regs(b))
                self.assertEqual(ao[ap[oi]+2*a.get_ref_off()],mapping[bo[bp[ni]+2*b.get_ref_off()]])
            else:self.assertEqual(a.get_output(),b.get_output())
        # The inserted values use the original request and validity register;
        # the original next sget overwrites the only scratch before its old use.
        old_merge=call
        self.assertTrue(any('supportsHero(' in op.get_output() for op in old[:old_merge]))
        self.assertTrue(any(op.get_name()=='and-int' and op.get_output().startswith('v17, v17,') for op in old[:old_merge]))
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
        self.assertEqual(exceptions(self.old[key],ao,{i:i for i in range(len(old)+1)}),
                         exceptions(self.new[key],bo,mapping))


if __name__=='__main__':unittest.main()
