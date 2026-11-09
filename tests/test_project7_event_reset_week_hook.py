"""Shared Week routing and guarded effects prelude, preserving stock branches."""
from pathlib import Path
import unittest
from test_project7_dream_hook import methods, raw, PKG

ROOT = Path(__file__).resolve().parents[1]


class EventResetWeekHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        old = ROOT/'analysis/project7/dream-lifecycle-hook-v1/classes7.dex'
        new = ROOT/'analysis/project7/event-reset-week-hook-v2/classes7.dex'
        if not old.exists() or not new.exists(): raise unittest.SkipTest('Maintainer source/target absent')
        cls.old,cls.new=methods(old),methods(new)

    def key(self,owner,name):
        return next(k for k in self.old if k[0]==PKG+owner+';' and k[1]==name)

    def test_only_two_callers_change_and_no_definitions_added(self):
        self.assertEqual(set(self.old),set(self.new));self.assertEqual(len(self.old),3705)
        changed=[]
        for key,old in self.old.items():
            new=self.new[key];self.assertEqual(old.get_access_flags(),new.get_access_flags())
            if raw(old)!=raw(new):changed.append((key[0],key[1]))
            if old.get_code():
                self.assertEqual(old.get_code().get_ins_size(),new.get_code().get_ins_size())
                expected=32 if key==self.key('LocalGatewayServer','handleWeekRpc') else old.get_code().get_registers_size()
                self.assertEqual(new.get_code().get_registers_size(),expected)
        self.assertCountEqual(changed,[(PKG+'LocalWeekEngine;','<clinit>'),(PKG+'LocalGatewayServer;','handleWeekRpc')])

    def test_family_extension_is_once_before_the_original_store(self):
        key=self.key('LocalWeekEngine','<clinit>');old,new=raw(self.old[key]),raw(self.new[key])
        call=next(i for i,x in enumerate(new) if 'EventResetWeekPolicy;->weekMethods(' in x[1])
        self.assertEqual(new[call][0],'invoke-static')
        self.assertEqual(new[call+1],('move-result-object','v0'))
        self.assertIn('v0, '+PKG+'LocalWeekEngine;->METHODS',new[call+2][1])
        self.assertEqual(old,new[:call]+new[call+2:])
        # Both Gateway and Store reach the same original membership function.
        handle=raw(self.old[self.key('LocalWeekEngine','handles')])
        self.assertIn('METHODS',handle[0][1]);self.assertIn('Arrays;->asList(',handle[1][1])
        self.assertTrue(any('List;->contains(' in x[1] for x in handle))

    def test_week_original_body_and_every_original_branch_preserved(self):
        from androguard.core.dex import Operand
        key=self.key('LocalGatewayServer','handleWeekRpc')
        old,new=list(self.old[key].get_instructions()),list(self.new[key].get_instructions())
        self.assertEqual(raw(self.new[key])[:8],[('move-object/from16','v%d, v%d'%(16+i,24+i)) for i in range(8)])
        records,mapping=[],{i:0 for i in range(8)};i=8;groups=0
        while i<len(new):
            if i+7<len(new) and 'EventResetWeekGateway;->beforeWeek(' in new[i+7].get_output():
                expected=[('move-object/from16','v%d, v%d'%(24+j,r)) for j,r in enumerate([0,1,2,4,5,6,14])]
                self.assertEqual([(op.get_name(),op.get_output()) for op in new[i:i+7]],expected)
                self.assertEqual((new[i+8].get_name(),new[i+8].get_output()),('move-result','v7'))
                self.assertEqual(new[i+9].get_name(),'if-nez')
                self.assertEqual((new[i+10].get_name(),new[i+10].get_output()),('const/4','v7, 1'))
                self.assertEqual((new[i+11].get_name(),new[i+11].get_output()),('return','v7'))
                self.assertEqual(sum(x.get_length() for x in new[i+9:i+12]),2*new[i+9].get_ref_off())
                for j in range(i,i+12):mapping[j]=len(records)
                records.append(('invoke-static','v0, v4, v5, v6, '+PKG+'DreamCoordinator;->recover('+PKG+'LocalGatewayServer; Ljava/lang/String; '+PKG+'LocalTutorialStore$Progress; '+PKG+'LocalEventEngine;)V',None))
                groups+=1;i+=12;continue
            op=new[i];name,text=op.get_name(),op.get_output();mapping[i]=len(records)
            branch=name.startswith(('if-','goto'));records.append((name,None if branch else text,i if branch else None));i+=1
        self.assertEqual(groups,1);self.assertEqual(len(old),len(records))
        def offsets(seq):
            out={};pos=0
            for j,op in enumerate(seq):out[pos]=j;pos+=op.get_length()
            return out
        ao,bo=offsets(old),offsets(new);ap,bp={v:k for k,v in ao.items()},{v:k for k,v in bo.items()}
        for j,(name,text,branch) in enumerate(records):
            self.assertEqual(name.split('/')[0],old[j].get_name().split('/')[0])
            if branch is None:self.assertEqual(text,old[j].get_output())
            else:
                registers=lambda op:tuple(x[1] for x in op.get_operands() if x[0]==Operand.REGISTER)
                self.assertEqual(registers(old[j]),registers(new[branch]))
                self.assertEqual(ao[ap[j]+2*old[j].get_ref_off()],mapping[bo[bp[branch]+2*new[branch].get_ref_off()]])


if __name__=='__main__':unittest.main()
