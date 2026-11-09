"""Fixed core city seams plus the query-only Gateway area resolver."""
import _paths  # noqa: E402,F401
from pathlib import Path
import gzip,hashlib,json,re,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tests'));sys.path.insert(0,str(ROOT/'offline'/'current'/'tools'))
from test_project7_dream_hook import methods,raw,PKG
from test_project7_reliable_scope_hook import offsets
from project7_component import restore
P=PKG+'LocalTutorialStore$Progress;';H=PKG+'StoryCityPolicy;'
C=PKG+'LocalCityProgress;';CH=PKG+'LocalChapterCityEngine;';W=PKG+'LocalWeekEngine;';E=PKG+'LocalStoryEntryPolicy;';B=PKG+'BsonLite;';G=PKG+'LocalGatewayServer;';L=PKG+'LocalStoryRuleRegistry$$ExternalSyntheticLambda4;'
QUERY='(Ljava/lang/Integer; Z [B)I';RESOLVE='(Ljava/lang/Integer; Z)I'
class StoryCityHookTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from loguru import logger
  logger.disable('androguard')
  from androguard.core.dex import DEX
  cls.source=ROOT/'analysis/project7/trial-retry-hook-v1/classes7.dex';cls.target=ROOT/'analysis/project7/story-city-coc-gateway-v1/classes7.dex'
  if not cls.source.is_file() or not cls.target.is_file():raise unittest.SkipTest('Pinned maintainer source/candidate absent')
  cls.old,cls.new=methods(cls.source),methods(cls.target)
  cls.od,cls.nd=DEX(cls.source.read_bytes()),DEX(cls.target.read_bytes())
 def key(self,owner,name,desc=None,new=False):return next(k for k in (self.new if new else self.old) if k[:2]==(owner,name)and(desc is None or k[2].replace(' ','')==desc.replace(' ','')))
 def branch_target(self,ins,pos,index):
  addr={v:k for k,v in pos.items()};return pos[addr[index]+2*ins[index].get_ref_off()]
 def test_source_target_and_bounded_delta_roundtrip_pins(self):
  self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(),'7f13c24a613676ee520bf6ed2590a6bf33788cb6955c92f3e9f446dee89c0d82')
  self.assertEqual(hashlib.sha256(self.target.read_bytes()).hexdigest(),'fee369231e8924923f774cdbda4961f91b6ab87cee237b249cff8229b535f1c6')
  folder=ROOT/'project7_bridge/runtime/project7_story_city_patch';contract=json.loads((folder/'contract.json').read_text());patch=(folder/'seams.xor-zlib').read_bytes()
  self.assertEqual(hashlib.sha256(patch).hexdigest(),contract['patch']['sha256']);self.assertEqual(restore(self.source.read_bytes(),patch,contract['target']['bytes']),self.target.read_bytes())
  self.assertIn('LocalGatewayServer.q7QueryAreaId(Ljava/lang/Integer;Z[B)I',contract['query_seam']['resolver']);self.assertIn('LocalGatewayServer.q7QueryAreaAllowed',contract['query_seam']['gate'])
 def test_four_added_definitions_and_fourteen_bodies_changed_no_class_or_field_change(self):
  self.assertEqual(len(self.old),3711);self.assertEqual(len(self.new),3717)
  supports=self.key(E,'supports');area=self.key(B,'allAreaInfoReplyDocument','(Z'+P+'[B)[B');query=self.key(G,'q7QueryAreaId',QUERY,new=True);allow=self.key(G,'q7QueryAreaAllowed','(Ljava/lang/Integer;[B)Z',new=True)
  begin=self.key(G,'q7StoryCityCocBegin',None,new=True);finish=self.key(G,'q7StoryCityCocFinish',None,new=True)
  self.assertEqual(set(self.new)-set(self.old),{(E,'q7OriginalSupports',supports[2]),(B,'q7OriginalAllAreaInfoReplyDocument',area[2]),(G,'q7QueryAreaId',query[2]),(G,'q7QueryAreaAllowed',allow[2]),(G,'q7StoryCityCocBegin',begin[2]),(G,'q7StoryCityCocFinish',finish[2])});self.assertFalse(set(self.old)-set(self.new))
  expected={(C,n)for n in('area','mapStages','stages','status','consumeVictory')}|{(CH,'state'),(CH,'locked'),(E,'supports'),(B,'allAreaInfoReplyDocument'),(W,'resetProfile'),(G,'handleCombatAdmission'),(G,'handleCombatOfflineFinish'),(G,'handleClient'),(G,'handleReliableRpc'),(L,'apply')}
  changed=[]
  for k,v in self.old.items():
   n=self.new[k];self.assertEqual(v.get_access_flags(),n.get_access_flags(),k)
   if raw(v)!=raw(n):changed.append(k[:2])
   if v.get_code()and k not in(supports,area):
    self.assertEqual(v.get_code().get_registers_size(),n.get_code().get_registers_size(),k);self.assertEqual(v.get_code().get_ins_size(),n.get_code().get_ins_size(),k)
  self.assertEqual(len(changed),17);self.assertEqual(set(changed),expected|{(PKG+'LocalPuzzleEngine$Room;','<init>'),(PKG+'LocalPuzzleEngine$Clue;','<init>')})
  def classes(dex):
   def init(f):
    v=f.get_init_value();return None if v is None else v.get_value()
   return {c.get_name():(c.get_access_flags(),c.get_superclassname(),tuple(c.get_interfaces()),c.CM.get_string(c.get_source_file_idx())if c.get_source_file_idx()!=0xffffffff else None,tuple(c.get_annotations()),[(f.get_name(),f.get_descriptor(),f.get_access_flags(),init(f))for f in c.get_fields()])for c in dex.get_classes()}
  self.assertEqual(len(self.od.get_classes()),649);self.assertEqual(classes(self.od),classes(self.nd))
 def test_two_bridges_preserve_every_original_instruction_and_exact_access(self):
  for owner,name,bridge,desc in((E,'supports','q7OriginalSupports','(I)Z'),(B,'allAreaInfoReplyDocument','q7OriginalAllAreaInfoReplyDocument','(Z'+P+'[B)[B')):
   k=self.key(owner,name,desc);old=self.old[k];retained=self.new[(owner,bridge,k[2])]
   self.assertEqual(raw(old),raw(retained));self.assertEqual(retained.get_access_flags(),old.get_access_flags()|0x1000)
   self.assertEqual(old.get_code().get_registers_size(),retained.get_code().get_registers_size());self.assertEqual(old.get_code().get_ins_size(),retained.get_code().get_ins_size())
   count=old.get_code().get_ins_size();obj=desc.endswith('[B');self.assertEqual(self.new[k].get_code().get_registers_size(),count+1)
   self.assertEqual(raw(self.new[k]),[('invoke-static',', '.join('v%d'%i for i in range(1,count+1))+', '+H+'->'+name+k[2]),('move-result-object'if obj else'move-result','v0'),('return-object'if obj else'return','v0')])
   self.assertEqual(self.exceptions(old),self.exceptions(retained))
 def test_seven_same_shape_redirects_are_single_instruction_changes(self):
  for owner,name,oldowner in[(C,n,PKG+'StoryMissionBridge;')for n in('area','mapStages','stages','status','consumeVictory')]+[(L,'apply',CH)]:
   k=next(k for k,v in self.old.items()if k[:2]==(owner,name)and any(oldowner+"->"in text for _,text in raw(v)));a,b=raw(self.old[k]),raw(self.new[k]);self.assertEqual(len(a),len(b));diff=[(x,y)for x,y in zip(a,b)if x!=y]
   if name=='handleCombatAdmission':
    self.assertEqual(len(diff),2,k)
    party=[d for d in diff if 'partyAllowed' in d[1][1]][0];self.assertEqual(party[1],(party[0][0],party[0][1].replace(oldowner,H)))
    coc=[d for d in diff if 'q7StoryCityCocBegin' in d[1][1]][0];self.assertIn('updateEconomy',coc[0][1]);self.assertEqual(coc[1][0],'invoke-static')
   else:
    self.assertEqual(len(diff),1,k);x,y=diff[0];self.assertEqual(x[0],'invoke-static');self.assertEqual(y,(x[0],x[1].replace(oldowner,H)))
   self.assertEqual(self.exceptions(self.old[k]),self.exceptions(self.new[k]))
 def test_coc_admission_inserts_tutorial_store_save(self):
  k=self.key(G,'handleCombatAdmission');a,b=raw(self.old[k]),raw(self.new[k]);self.assertEqual(len(b),len(a)+1)
  self.assertTrue(any('StoryCityPolicy;->partyAllowed' in text for _,text in b))
  i=next(i for i,x in enumerate(b)if 'q7StoryCityCocBegin' in x[1]);self.assertEqual(b[i-1][0],'iget-object');self.assertIn('LocalGatewayServer;->tutorialStore',b[i-1][1]);self.assertEqual(b[i+1][0],'move-result-object')
 def test_state_prefix_forwards_original_registers_and_fallthrough_keeps_full_cfg(self):
  for name,rs,obj in(('state','v1, v2',True),('locked','v2, v3',False)):
   k=self.key(CH,name);a,b=list(self.old[k].get_instructions()),list(self.new[k].get_instructions());prefix=raw(self.new[k])[:6]
   self.assertEqual(prefix[:2],[('invoke-static',rs+', '+H+'->handlesState([B I)Z'),('move-result','v0')]);self.assertEqual(prefix[2][0],'if-eqz')
   self.assertEqual(prefix[3:], [('invoke-static',rs+', '+H+'->'+name+k[2]),('move-result-object'if obj else'move-result','v0'),('return-object'if obj else'return','v0')])
   bo=offsets(b);bp={v:k for k,v in bo.items()};self.assertEqual(bo[bp[2]+2*b[2].get_ref_off()],6)
   self.preserved(k,[(i,i+6)for i in range(len(a))],{i:0 if i<6 else i-6 for i in range(len(b)+1)})
 def test_week_reset_only_wraps_sole_original_return_and_keeps_every_branch(self):
  k=self.key(W,'resetProfile');a,b=list(self.old[k].get_instructions()),list(self.new[k].get_instructions());returns=[i for i,op in enumerate(a)if op.get_name().startswith('return')];self.assertEqual(returns,[len(a)-1]);ret=returns[0]
  self.assertEqual(raw(self.old[k])[-1],('return-object','v0'));self.assertEqual(raw(self.new[k])[ret:ret+3],[('invoke-static','v0, '+H+'->resetProfile([B)[B'),('move-result-object','v0'),('return-object','v0')])
  self.preserved(k,[(i,i if i<ret else i+2)for i in range(len(a))],{i:i if i<ret else ret if i<=ret+2 else i-2 for i in range(len(b)+1)})
 def test_unselected_overloads_and_policy_gates_are_exactly_unchanged(self):
  for owner,name in((E,'blocksOrdinaryOpening'),(CH,'refresh'),(C,'chapterScene')):
   for k in self.old:
    if k[:2]==(owner,name):self.assertEqual(raw(self.old[k]),raw(self.new[k]),k)
  for k in self.old:
   if k[0]==B and k[1]=='allAreaInfoReplyDocument'and k[2].replace(' ','')!='(Z'+P+'[B)[B':self.assertEqual(raw(self.old[k]),raw(self.new[k]))
  self.assertFalse(any(k[1].startswith('resolveArea')and raw(v)!=raw(self.new[k])for k,v in self.old.items()))
 def test_query_resolver_and_allowed_gate_are_exact(self):
  q=self.new[self.key(G,'q7QueryAreaId',QUERY,new=True)];al=self.new[self.key(G,'q7QueryAreaAllowed','(Ljava/lang/Integer;[B)Z',new=True)]
  self.assertEqual((q.get_access_flags(),q.get_code().get_registers_size(),q.get_code().get_ins_size()),(0x0a,5,3));self.assertEqual(len(list(q.get_instructions())),27)
  ins=list(q.get_instructions());pos=offsets(ins)
  self.assertEqual([x.get_name()for x in ins],['invoke-static','move-result','if-nez','goto/32','if-eqz','if-eqz','invoke-virtual','move-result','const/4','if-lt','const/16','if-gt','return','invoke-static','move-result','return','if-eqz','invoke-virtual','move-result','return','const/4','return','const/4','return','invoke-static','move-result','return'])
  self.assertEqual(ins[0].get_output(),'v4, '+H+'->owns([B)Z');self.assertEqual(ins[24].get_output(),'v2, v3, '+G+'->resolveAreaId(Ljava/lang/Integer; Z)I')
  self.assertEqual(self.branch_target(ins,pos,2),4);self.assertEqual(self.branch_target(ins,pos,3),24);self.assertEqual(self.branch_target(ins,pos,4),16);self.assertEqual(self.branch_target(ins,pos,5),22)
  self.assertEqual((al.get_access_flags(),al.get_code().get_registers_size(),al.get_code().get_ins_size()),(0x0a,4,2));self.assertEqual(len(list(al.get_instructions())),18)
  ai=list(al.get_instructions());apos=offsets(ai);self.assertEqual(ai[0].get_output(),'v3, '+H+'->owns([B)Z');self.assertEqual(self.branch_target(ai,apos,2),14);self.assertEqual(self.branch_target(ai,apos,3),14);self.assertEqual(self.branch_target(ai,apos,7),16);self.assertEqual(self.branch_target(ai,apos,9),11);self.assertEqual(self.branch_target(ai,apos,10),14);self.assertEqual(self.branch_target(ai,apos,13),16)
  self.assertEqual(sum(1 for v in self.new.values()for _,text in raw(v)if G+'->resolveAreaId('in text),1)
  self.assertEqual(sum(1 for v in self.new.values()for _,text in raw(v)if G+'->q7QueryAreaId('in text),2)
  self.assertEqual(sum(1 for v in self.new.values()for _,text in raw(v)if G+'->q7QueryAreaAllowed('in text),2)
  legacy=self.old[self.key(G,'resolveAreaId',RESOLVE)];self.assertEqual(raw(legacy),raw(self.new[self.key(G,'resolveAreaId',RESOLVE)]))
 def test_query_callsites_load_once_before_allowed_and_reuse_the_profile(self):
  cases=(('handleClient',1362,1368,1371,1390,1364,1406,1782,'load',4,19),('handleReliableRpc',2494,2500,2503,2523,2496,2537,2655,'snapshot',3,20))
  for name,resolve,load,replyOld,reply,normal,logAt,count,provider,flag,shift in cases:
   k=self.key(G,name);a,b=list(self.old[k].get_instructions()),list(self.new[k].get_instructions());self.assertEqual(len(a),count-shift);self.assertEqual(len(b),count)
   for i in range(3):self.assertEqual(raw(self.old[k])[load+i],raw(self.new[k])[resolve+i])
   aidx=resolve+3;qidx=aidx+3;self.assertIn('q7QueryAreaAllowed',b[aidx].get_output());self.assertIn('q7QueryAreaId',b[qidx].get_output())
   self.assertEqual(b[aidx+1].get_output(),('v4' if name=='handleClient' else 'v3'));self.assertEqual(b[aidx].get_output().split(', ')[1],b[resolve+2].get_output())
   self.assertEqual(b[qidx].get_output().split(', ')[2],b[resolve+2].get_output())
   self.assertIn(provider,raw(self.new[k])[resolve+1][1]);self.assertEqual(b[resolve+2].get_output(),self.profile_reg(b[reply]))
   between=[x.get_output()for x in b[aidx+1:reply]if 'ProfileProvider;->' in x.get_output()];self.assertEqual(between,[],'no second profile load between allowed and reply')
   self.assertEqual(raw(self.old[k])[replyOld],raw(self.new[k])[reply])
   for i in range(replyOld+1,len(a)):
    j=self.map_index(name,i);self.assertTrue(j is not None)
    if a[i].get_name().startswith(('if-','goto')):continue
    self.assertEqual(raw(self.old[k])[i],raw(self.new[k])[j])
   for i in range(0,resolve):
    if a[i].get_name().startswith(('if-','goto')):continue
    self.assertEqual(raw(self.old[k])[i],raw(self.new[k])[i])
   for i in range(load+3,replyOld):self.assertIsNone(self.map_index(name,i))
   ao,bo=offsets(a),offsets(b)
   for i,x in enumerate(a):
    if x.get_name().startswith(('if-','goto')):
     ta=self.branch_target(a,ao,i);j=self.map_index(name,i);self.assertIsNotNone(j);tb=self.branch_target(b,bo,j);tj=self.map_index(name,ta);self.assertEqual(tb,tj,(name,i,ta))
   inv={j:i for i in range(len(a))if(j:=self.map_index(name,i))is not None}
   self.assertEqual(self.exceptions(self.old[k]),self.exceptions(self.new[k],inv))
 def map_index(self,name,i):
  if name=='handleClient':
   if i<1362:return i
   if i<1364:return i+3
   if i<1368:return i+22
   if i<1371:return None
   return i+19
  if i<2494:return i
  if i<2496:return i+3
  if i<2500:return i+23
  if i<2503:return None
  return i+20
 def profile_reg(self,ins):return [p for p in ins.get_output().split(', ')if p.startswith('v')][-1]
 def test_owned_unknown_sends_show_message_and_no_area_reply(self):
  k=self.key(G,'handleClient');a,b=list(self.old[k].get_instructions()),list(self.new[k].get_instructions());bo=offsets(b)
  self.assertEqual([x.get_name()for x in b[1365:1386]],['invoke-static','move-result','if-eqz','invoke-static','move-result','goto/32','invoke-virtual','move-result','const-string','invoke-static','move-result-object','const-string','const-string','filled-new-array','move-result-object','invoke-static','move-result-object','invoke-static','move-result-object','invoke-direct','goto/32'])
  self.assertEqual((b[1367].get_output(),self.branch_target(b,bo,1367)),('v4, +009h',1371));self.assertEqual(self.branch_target(b,bo,1370),1386);self.assertEqual(self.branch_target(b,bo,1385),1406)
  reject=[x.get_output()for x in b[1371:1386]];self.assertTrue(any('showMessageStr' in x for x in reject));self.assertTrue(any('BsonLite;->document(' in x for x in reject));self.assertTrue(any('ProtoLite;->entityMessage(' in x for x in reject));self.assertTrue(any('writeFrame(' in x for x in reject));self.assertFalse(any('areaInfoReplyDocument' in x or 'areaStagesReplyDocument' in x for x in reject));self.assertFalse(any('completeEmptyCallback' in x for x in reject))
  k=self.key(G,'handleReliableRpc');a,b=list(self.old[k].get_instructions()),list(self.new[k].get_instructions());bo=offsets(b)
  self.assertEqual((b[2499].get_output(),self.branch_target(b,bo,2499)),('v3, +009h',2503));self.assertEqual(self.branch_target(b,bo,2502),2519);self.assertEqual(self.branch_target(b,bo,2518),2537)
  reject=[x.get_output()for x in b[2503:2519]];self.assertTrue(any('showMessageStr' in x for x in reject));self.assertTrue(any('writeFrame(' in x for x in reject));self.assertFalse(any('areaStagesReplyDocument' in x or 'areaInfoReplyDocument' in x for x in reject));self.assertFalse(any('completeEmptyCallback' in x for x in reject))
 def test_query_behavior_allowed_gate_and_nonowned_delegation(self):
  catalog=json.loads(gzip.decompress((ROOT/'analysis/project7/story-city-catalog-v1/catalog-v1.json.gz').read_bytes()));known={a['id']for a in catalog['areas']}
  qe=self.emulator(self.new[self.key(G,'q7QueryAreaId',QUERY,new=True)]);ae=self.emulator(self.new[self.key(G,'q7QueryAreaAllowed','(Ljava/lang/Integer;[B)Z',new=True)])
  def legacy(idv,strict):
   if not strict:return 0 if idv is None else idv
   if idv is None:return 1
   return idv if 1<=idv<=8 else 1
  for owned in(False,True):
   for strict in(False,True):
    for idv in(1,9,10000,42,None,9999,10004,-1):
     allow=not owned or idv is None or idv in known or 1<=idv<=8
     self.assertEqual(ae(idv,strict,owned,known),1 if allow else 0,('allow',owned,strict,idv))
     if allow:
      want=(1 if strict else 0)if(owned and idv is None)else(idv if owned else legacy(idv,strict))
      self.assertEqual(qe(idv,strict,owned,known),want,('q',owned,strict,idv))
  for idv in(9,10000,10003,42):
   self.assertEqual(ae(idv,True,False,set()),1,'pre-prepare non-owned allowed');self.assertEqual(qe(idv,True,False,set()),legacy(idv,True))
 def emulator(self,method):
  ins=list(method.get_instructions());pos=offsets(ins)
  def legacy(idv,strict):
   if not strict:return 0 if idv is None else idv
   if idv is None:return 1
   return idv if 1<=idv<=8 else 1
  def run(requested,strict,owned,known):
   reg={0:None,1:None,2:requested,3:1 if strict else 0,4:object()};pc=0
   while True:
    op=ins[pc];name=op.get_name();out=op.get_output()
    if name=='if-eqz':
     regno=int(re.search(r'v(\d+)',out).group(1));zero=reg[regno] is None if regno==2 else reg[regno]==0
     if zero:pc=self.branch_target(ins,pos,pc);continue
    elif name=='if-nez':
     regno=int(re.search(r'v(\d+)',out).group(1))
     if reg[regno] is not None and reg[regno]!=0:pc=self.branch_target(ins,pos,pc);continue
    elif name in('if-lt','if-gt'):
     r1,r2=[int(x)for x in re.findall(r'v(\d+)',out)[:2]]
     if(reg[r1]<reg[r2])if name=='if-lt'else(reg[r1]>reg[r2]):pc=self.branch_target(ins,pos,pc);continue
    elif name in('const','const/4','const/16'):
     m=re.match(r'v(\d+), (-?\d+)$',out);reg[int(m.group(1))]=int(m.group(2))
    elif name in('goto','goto/16','goto/32'):pc=self.branch_target(ins,pos,pc);continue
    elif name=='invoke-virtual':
     self.assertIn('Integer;->intValue()I',out);reg[0]=reg[2]
    elif name=='invoke-static':
     if H+'->owns([B)Z' in out:reg[0]=1 if owned else 0
     elif H+'->knownArea(I)Z' in out:reg[1]=1 if reg[0]in known else 0
     elif G+'->resolveAreaId(' in out:reg[0]=legacy(reg[2],reg[3]==1)
     else:raise AssertionError(('unexpected static',out))
    elif name=='move-result':pass
    elif name=='return':
     regno=int(re.search(r'v(\d+)',out).group(1));return reg[regno]
    else:raise AssertionError(('unexpected',name,out))
    pc+=1
  return run
 def test_puzzle_room_and_clue_only_raise_upper_bound(self):
  room=self.key(PKG+'LocalPuzzleEngine$Room;','<init>','([Ljava/lang/String;)V');clue=self.key(PKG+'LocalPuzzleEngine$Clue;','<init>','([Ljava/lang/String;)V')
  ra,rb=list(self.old[room].get_instructions()),list(self.new[room].get_instructions())
  ca,cb=list(self.old[clue].get_instructions()),list(self.new[clue].get_instructions())
  self.assertEqual((len(ra),len(rb),len(ca),len(cb)),(69,70,25,26))
  self.assertEqual(self.old[room].get_code().get_registers_size(),self.new[room].get_code().get_registers_size());self.assertEqual(self.old[clue].get_code().get_registers_size(),self.new[clue].get_code().get_registers_size())
  self.assertEqual([x.get_name()for x in ra[:54]],[x.get_name()for x in rb[:54]]);self.assertEqual((rb[53].get_name(),rb[53].get_output()),('if-lt','v7, v0, +018h'))
  self.assertEqual((rb[54].get_name(),rb[54].get_output()),('const/4','v4, 4'));self.assertEqual((rb[55].get_name(),rb[55].get_output()),('if-gt','v7, v4, +015h'))
  self.assertEqual(raw(self.old[room])[54],('if-gt','v7, v1, +015h'))
  ro=offsets(ra);rn=offsets(rb)
  for i in range(54,len(ra)):
   if ra[i].get_name().startswith(('if-','goto')):continue
   self.assertEqual(raw(self.old[room])[i],raw(self.new[room])[i+1])
  self.assertEqual(self.branch_target(rb,rn,55),self.branch_target(ra,ro,54)+1)
  self.assertEqual([x.get_name()for x in ca[:16]],[x.get_name()for x in cb[:16]])
  self.assertEqual((cb[16].get_name(),cb[16].get_output()),('const/4','v3, 4'))
  self.assertEqual((cb[19].get_name(),cb[19].get_output()),('if-gt','v2, v3, +005h'))
  self.assertEqual((cb[20].get_name(),cb[20].get_output()),('if-ltz','v5, +003h'))
  for i in range(16,len(ca)):
   if ca[i].get_name().startswith(('if-','goto')):continue
   self.assertEqual(raw(self.old[clue])[i],raw(self.new[clue])[i+1])
  co,cn=offsets(ca),offsets(cb)
  for oi,ni in ((16,17),(17,18),(18,19),(19,20)):
   ta=self.branch_target(ca,co,oi);tb=self.branch_target(cb,cn,ni);self.assertEqual(tb,ta if ta<16 else ta+1)
 def preserved(self,key,pairs,mapping):
  from androguard.core.dex import Operand
  a,b=list(self.old[key].get_instructions()),list(self.new[key].get_instructions());ao,bo=offsets(a),offsets(b);ap,bp={v:k for k,v in ao.items()},{v:k for k,v in bo.items()}
  self.assertEqual(len(pairs),len(a))
  for oi,ni in pairs:
   x,y=a[oi],b[ni];self.assertEqual(x.get_name().split('/')[0],y.get_name().split('/')[0])
   if x.get_name().startswith(('if-','goto')):
    regs=lambda op:[r[1]for r in op.get_operands()if r[0]==Operand.REGISTER];self.assertEqual(regs(x),regs(y));self.assertEqual(ao[ap[oi]+2*x.get_ref_off()],mapping[bo[bp[ni]+2*y.get_ref_off()]])
   else:self.assertEqual(x.get_output(),y.get_output())
  self.assertEqual(self.exceptions(self.old[key]),self.exceptions(self.new[key],mapping))
 def exceptions(self,method,mapping=None):
  code=method.get_code();ops=list(method.get_instructions());positions=offsets(ops);mapping=mapping or {i:i for i in range(len(ops)+1)}
  if not code.get_tries_size():return []
  hs=code.get_handlers();handlers={h.get_off()-hs.get_off():h for h in hs.get_list()};rows=[]
  for tr in code.get_tries():
   h=handlers[tr.get_handler_off()];pairs=[(code.CM.get_type(p.get_type_idx()),mapping[positions[2*p.get_addr()]])for p in h.get_handlers()];catch=mapping[positions[2*h.get_catch_all_addr()]]if h.get_size()<=0 else None;rows.append((mapping[positions[2*tr.get_start_addr()]],mapping[positions[2*(tr.get_start_addr()+tr.get_insn_count())]],pairs,catch))
  return rows
if __name__=='__main__':unittest.main()
