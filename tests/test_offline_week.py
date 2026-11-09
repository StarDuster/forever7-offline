"""Original-table host contracts; modern codec test is not native runtime QA."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
import zlib
import msgpack
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'tools'))
from export_game_catalogs import decode
from offline_week import (prepare_week_result,prepare_week_route_handoff,
    prepare_week_transition,prepare_week_avatar_reply,can_enter_week_route,read_week_history)


class ModelObjectId:
    """Host type models exactly the statically verified original $oid hook."""
    def __init__(self,value): self.value=value
    def __str__(self): return self.value
    def __eq__(self,other): return isinstance(other,ModelObjectId) and self.value==other.value
    def __deepcopy__(self,memo): return ModelObjectId(self.value)


class WeekCycleTests(unittest.TestCase):
    def setUp(self):
        self.fixture=json.loads((ROOT/'tests/fixtures/offline_week_cdata.json').read_text())
        self.tables=decode(self.fixture['tables'])
        skin='a'*24; treasure='b'*24; gacha_item='c'*24
        self.state={'story':{'version':1,'week':0,'date':7,'route':'1','sub_routes':[1],
                             'emergency':False,'cg':[11],'endings':[2],
                             'notes':{'p':{},'n':{},'pn':[123],'ppn':False},
                             'battle_wins':[101,1101],'blackcores':{'2':1},'pending_effects':{},
                             'city_values':{'av':0,'bf':300,'rv':20,'dv':10,'fv':30},
                             'city_areas':{'1':{'id':1,'lv':3,'st':[0,False,False],'bd':{}}}},
                    'profile':{'heroes':{'24':{'sl':3,'so':2,'cf':10,'ef':75,
                        'cs':skin,'sk':{skin:{'u':skin,'i':24}},'ti':{'items':[{'u':treasure}]},'as':2}},
                        'economy':{'version':1,'money':12345,'exp':300,'level':7},
                        'treasures':{'version':1,'items':[{'u':treasure,'i':1002}]}},
                    'gacha':{'opened_total':99,'items':[{'u':gacha_item,'i':1003}],'group':{'cards':[1,2]}},
                    'completed_events':[8029],'processing_events':[],'available_events':[],
                    'conditions':[[102,4]],'event_traces':[[8029,[['dialog',[8029]]]]],
                    'battle':{'version':1,'active':None,'receipts':[]},
                    'day':{'version':1,'stock_day':7,'intent':None,'receipt':None,'review':None},
                    'status':'city','player_name':'host-name'}
        self.handoff={'kind':'week_result','event':8029,'result':1,'token':'ending:8029','in_advance':False}

    def earned(self):
        return prepare_week_result(self.state,self.handoff,self.tables['events'],self.tables['endings'])[0]

    def snapshot(self,state):
        heroes=[]
        for key,saved in state['profile']['heroes'].items():
            native=copy.deepcopy(saved)
            native['cs']=ModelObjectId(native['cs'])
            for skin in native['sk'].values():skin['u']=ModelObjectId(skin['u'])
            for item in native['ti']['items']: item['u']=ModelObjectId(item['u'])
            heroes.append((int(key),native))
        items=copy.deepcopy(state['profile']['treasures']['items']+state['gacha']['items'])
        for item in items:item['u']=ModelObjectId(item['u'])
        story=state['story'];economy=state['profile']['economy']
        return {'st':1790000000,'name':state['player_name'],'an':'offline','uid':1,'sv':1,'role':1,
                'level':economy['level'],'money':economy['money'],'exp':economy['exp'],
                'weeknum':{'w':story['week'],'d':state['day']['stock_day'],'c':{},'l':{}},
                'city':dict(copy.deepcopy(story['city_values']),areas={'area_'+k:copy.deepcopy(v) for k,v in story['city_areas'].items()}),
                'heromgr':{'hrs':heroes,'cfs':None},'inv':{'items':items},
                'std':{'rt':story['route'],'srt':story['sub_routes'],'ed':story.get('endings',[])},
                'eventTrigger':{'ae':state['available_events'],'pe':state['processing_events'],'ecm':state['completed_events'],'gle':[],'ecd':{}},
                'ldd':{'ct':state['gacha']['opened_total'],'iof':state['gacha']['group'] is not None},
                'np':story['notes'],'cgs':story.get('cgs',story.get('cg',[])),'ccgs':[]}

    def pack(self,snapshot):
        def original_default_model(obj):
            if isinstance(obj,ModelObjectId): return {'$oid':str(obj)}
            raise TypeError('unsupported host snapshot object')
        # Raw-string subset and default callback are present in ORIGINAL0.4.7
        # fallback.Packer signature. No modern-only options go into live codec.
        return msgpack.packb(snapshot,default=original_default_model,use_bin_type=False)

    def test_original_source_hashes_and_047_wire_contract(self):
        for name,digest in self.fixture['sha256'].items():
            path=ROOT/('analysis/android640-scripts/com/data/cdata/'+name+'.marshal')
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),digest)
        for path,digest in self.fixture['wire_sources'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
        self.assertEqual(self.fixture['wire_contract']['version'],[0,4,7])

    def test_real_completed_event_awards_only_original_ending_and_cg(self):
        before=copy.deepcopy(self.state)
        earned,notices,changed=prepare_week_result(self.state,self.handoff,self.tables['events'],self.tables['endings'])
        self.assertTrue(changed)
        self.assertEqual(earned['story']['endings'],[1,2])
        self.assertIn(self.tables['endings'][1]['cg'],earned['story']['cg'])
        self.assertEqual(notices[-1][0],'showWeekResult')
        self.assertEqual(notices[-1][1]['r'],1)
        self.assertEqual(notices[0],('addCg',{'c':[21]}))
        self.assertEqual(earned['story']['cgs'],earned['story']['cg'])
        self.assertEqual(earned['profile'],before['profile'])
        self.assertEqual(earned['completed_events'],before['completed_events'])
        replay=prepare_week_result(earned,self.handoff,self.tables['events'],self.tables['endings'])
        self.assertFalse(replay[2])
        self.assertEqual(replay[1],notices)
        self.assertEqual(self.state,before)

    def test_unfinished_wrong_or_early_normal_ending_cannot_be_earned(self):
        for kind in ('unfinished','wrong','early'):
            state=copy.deepcopy(self.state);handoff=copy.deepcopy(self.handoff)
            if kind=='unfinished':state['completed_events']=[]
            if kind=='wrong':handoff['result']=3
            if kind=='early':state['day']['stock_day']=2
            with self.assertRaises(ValueError):prepare_week_result(state,handoff,self.tables['events'],self.tables['endings'])
        early=copy.deepcopy(self.state);early['day']['stock_day']=2;early['completed_events']=[1431]
        result=prepare_week_result(early,{'kind':'week_result','event':1431,'result':104,'token':'ending:1431'},self.tables['events'],self.tables['endings'])
        self.assertEqual(result[0]['week_protocol']['result']['ending'],104)

    def test_original_stay_inc_week_retains_only_actually_completed_original_events(self):
        from test_offline_event_effects import read_source
        content = read_source(ROOT/'analysis/decompiled/event_content.py')
        stay = sorted(event for event, row in content.items() if row.get('stay_inc_week'))
        self.assertEqual(stay, [9, 32, 417, 423, 424])
        tables = dict(self.tables, events=content)
        source = self.earned()
        source['completed_events'] = [9, 32, 417, 8029]
        planned, notices, changed = prepare_week_transition(source, 'handleIncWeekAsk', 'stay:one', tables)
        self.assertTrue(changed)
        self.assertEqual(planned['completed_events'], [9, 32, 417])
        self.assertNotIn(423, planned['completed_events'])
        self.assertNotIn(424, planned['completed_events'])
        self.assertEqual(source['completed_events'], [9, 32, 417, 8029])
        self.assertEqual(planned['processing_events'], [])

    def test_next_week_resets_only_weekly_state_and_retains_all_owned_assets(self):
        source=self.earned();before=copy.deepcopy(source)
        candidate,notices,changed=prepare_week_transition(source,'handleIncWeekAsk','week:one',self.tables)
        self.assertTrue(changed)
        self.assertEqual(notices,[('handleIncWeekReply',{})])
        self.assertEqual(candidate['story']['week'],1)
        self.assertEqual(candidate['day']['stock_day'],0)
        self.assertEqual(candidate['story']['date'],0)
        self.assertEqual(candidate['story']['city_values']['av'],24)
        self.assertEqual(candidate['story']['city_areas']['1']['mbn'],4)
        self.assertEqual(candidate['available_events'],[[1030,1]])
        self.assertEqual(candidate['completed_events'],[])
        self.assertEqual(candidate['conditions'],[])
        self.assertEqual(candidate['story']['endings'],source['story']['endings'])
        self.assertEqual(candidate['story']['cg'],source['story']['cg'])
        self.assertEqual(candidate['gacha'],source['gacha'])
        expected_profile=copy.deepcopy(source['profile']);expected_profile['heroes']['24']['cf']=100
        self.assertEqual(candidate['profile'],expected_profile)
        self.assertEqual(candidate['week_protocol']['history'][0]['completed_events'],[8029])
        self.assertFalse(candidate['week_protocol']['history'][0]['abandoned'])
        self.assertEqual(source,before)

    def test_restart_abandons_without_granting_an_ending_and_requires_player_action(self):
        with self.assertRaises(ValueError):prepare_week_transition(self.state,'handleIncWeekAsk','no-ending',self.tables)
        with self.assertRaises(ValueError):prepare_week_transition(self.state,'handleResetWeekAsk','no-auth',self.tables)
        candidate,notices,changed=prepare_week_transition(self.state,'handleResetWeekAsk','authorized',self.tables,authorized_reset=True)
        self.assertEqual(notices,[('handleResetWeekReply',{})])
        self.assertEqual(candidate['story']['endings'],[2])
        self.assertEqual(candidate['story']['cg'],[11])
        self.assertTrue(candidate['week_protocol']['history'][0]['abandoned'])
        self.assertEqual(candidate['profile']['economy'],self.state['profile']['economy'])

    def test_route_handoff_requires_completed_original_event_and_table_route(self):
        state=copy.deepcopy(self.state);state['completed_events'].append(510)
        handoff={'kind':'route','event':510,'route':'8-1','token':'route:510'}
        candidate,notices,changed=prepare_week_route_handoff(state,handoff,self.tables['events'],self.tables['routes'])
        self.assertTrue(changed)
        self.assertEqual(candidate['story']['route'],'8-1')
        self.assertEqual(notices,[('syncRoute',{'rt':'8-1','srt':[],'i':False,'hsd':{'hs':[],'hsf':False,'hst':0},'fbd':{}})])
        self.assertFalse(prepare_week_route_handoff(candidate,handoff,self.tables['events'],self.tables['routes'])[2])
        with self.assertRaises(ValueError):prepare_week_route_handoff(self.state,handoff,self.tables['events'],self.tables['routes'])

    def test_original_selector_and_of_or_ending_unlocks_and_special_entry5(self):
        self.assertTrue(can_enter_week_route(self.state,2,self.tables['scores'])) # actualending2
        state=copy.deepcopy(self.state);state['story']['endings']=[]
        self.assertFalse(can_enter_week_route(state,2,self.tables['scores']))
        state['story']['week']=2
        self.assertFalse(can_enter_week_route(state,5,self.tables['scores']))
        state['story']['client_event_finish']=False
        self.assertTrue(can_enter_week_route(state,5,self.tables['scores']))
        state['story']['week']=3
        self.assertTrue(can_enter_week_route(state,5,self.tables['scores']))

    def test_selector_reply_closes_original_panel_then_updates_full_avatar(self):
        source=self.earned();source['story']['week']=1
        candidate,notices,changed=prepare_week_transition(source,'requestEnterStoryByEnding','select:2',self.tables,route_entry=2)
        self.assertEqual(notices,[('replyEnterStoryByEnding',{'r':True}),('handleIncWeekReply',{})])
        self.assertEqual(candidate['available_events'],[[self.tables['scores'][2]['init_event'],1]])
        self.assertEqual(candidate['story']['week'],2)

    def test_original_wire_adapter_restores_object_id_fields_and_complete_snapshot(self):
        transitioned=prepare_week_transition(self.earned(),'handleIncWeekAsk','wire:one',self.tables)[0]
        candidate,notices,changed=prepare_week_avatar_reply(transitioned,self.snapshot,self.pack)
        self.assertTrue(changed)
        self.assertFalse(candidate['week_protocol']['awaiting_avatar'])
        self.assertEqual(notices[0][0],'updateClientAvatarReply')
        def original_hook_model(document):
            return ModelObjectId(str(document['$oid'])) if '$oid'in document else document
        # Modern host decode options are confined to the TEST. Live client uses
        # its original0.4.7 loads/object_hook; no native runtime claim is made.
        decoded=msgpack.unpackb(zlib.decompress(notices[0][1]['s']),raw=False,strict_map_key=False,object_hook=original_hook_model)
        hero=decoded['heromgr']['hrs'][0][1]
        self.assertIsInstance(hero['cs'],ModelObjectId)
        self.assertIsInstance(next(iter(hero['sk'].values()))['u'],ModelObjectId)
        self.assertIsInstance(hero['ti']['items'][0]['u'],ModelObjectId)
        self.assertIsInstance(decoded['inv']['items'][0]['u'],ModelObjectId)
        self.assertEqual(decoded['weeknum']['w'],1)
        self.assertEqual(decoded['eventTrigger']['ecm'],[])
        self.assertIn(1,decoded['std']['ed'])
        self.assertEqual(len(decoded['inv']['items']),2)
        self.assertTrue(transitioned['week_protocol']['awaiting_avatar'])

    def test_partial_or_stale_avatar_and_asset_loss_cannot_acknowledge_reset(self):
        transitioned=prepare_week_transition(self.earned(),'handleIncWeekAsk','wire:bad',self.tables)[0]
        for kind in ('partial','oldweek','hero','skin','treasure','cg','ending','gacha'):
            def bad_builder(state,kind=kind):
                snapshot=self.snapshot(state)
                if kind=='partial':return {}
                if kind=='oldweek':snapshot['weeknum']['w']=0
                if kind=='hero':snapshot['heromgr']['hrs']=[]
                if kind=='skin':snapshot['heromgr']['hrs'][0][1]['sk']={}
                if kind=='treasure':snapshot['inv']['items']=[]
                if kind=='cg':snapshot['cgs']=[]
                if kind=='ending':snapshot['std']['ed']=[]
                if kind=='gacha':snapshot['ldd']['ct']=0
                return snapshot
            with self.assertRaises(ValueError,msg=kind):prepare_week_avatar_reply(transitioned,bad_builder,self.pack)
        self.assertTrue(transitioned['week_protocol']['awaiting_avatar'])

    def test_week_replay_and_handshake_serialize_transitions_without_second_reset(self):
        source=self.earned()
        first,notices,_=prepare_week_transition(source,'handleIncWeekAsk','serial:one',self.tables)
        replay,again,changed=prepare_week_transition(first,'handleIncWeekAsk','serial:one',self.tables)
        self.assertFalse(changed)
        self.assertEqual(replay,first)
        self.assertEqual(again,notices)
        with self.assertRaises(ValueError):prepare_week_transition(first,'handleResetWeekAsk','serial:two',self.tables,authorized_reset=True)
        ready=prepare_week_avatar_reply(first,self.snapshot,self.pack)[0]
        second=prepare_week_transition(ready,'handleResetWeekAsk','serial:two',self.tables,authorized_reset=True)[0]
        self.assertEqual(second['story']['week'],2)
        self.assertEqual(second['available_events'],[[1066,1]])
        self.assertEqual(len(second['week_protocol']['history']),2)


    def test_lossless_week_history_retains_real_story_trace_without_duplicating_assets(self):
        source=self.earned()
        next_state=prepare_week_transition(source,'handleIncWeekAsk','archive:one',self.tables)[0]
        entry=next_state['week_protocol']['history'][0]
        self.assertNotIn('story',entry)
        decoded=read_week_history(entry)
        self.assertEqual(decoded['story'],source['story'])
        self.assertEqual(decoded['event_traces'],source['event_traces'])
        self.assertEqual(decoded['conditions'],source['conditions'])
        self.assertNotIn('profile',decoded)
        corrupt=copy.deepcopy(entry);corrupt['archive_sha256']='0'*64
        with self.assertRaises(ValueError):read_week_history(corrupt)

    def test_canonical_effects_cgs_survive_reset_even_without_legacy_cg_key(self):
        state=copy.deepcopy(self.state)
        state['story'].pop('cg')
        state['story']['cgs']=[11,13]
        state['story']['new_cgs']=[13]
        restarted=prepare_week_transition(state,'handleResetWeekAsk','cgs:reset',self.tables,authorized_reset=True)[0]
        self.assertEqual(restarted['story']['cgs'],[11,13])
        self.assertEqual(restarted['story']['new_cgs'],[])
        self.assertEqual(restarted['story']['endings'],[2])


    def test_every_original_fixture_ending_mapping_uses_completed_event_not_timer(self):
        count=0
        for event,row in self.tables['events'].items():
            if not row.get('release') or 'weekResult' not in row:continue
            source=copy.deepcopy(self.state)
            source['completed_events']=[event]
            handoff={'kind':'week_result','event':event,'result':row['weekResult'],'token':'ending:%s'%event}
            candidate,notices,changed=prepare_week_result(source,handoff,self.tables['events'],self.tables['endings'])
            self.assertTrue(changed)
            self.assertEqual(notices[-1][1]['r'],row['weekResult'])
            self.assertEqual(candidate['completed_events'],[event])
            self.assertEqual(candidate['profile'],source['profile'])
            count+=1
        self.assertGreater(count,250)

    def test_failed_full_snapshot_encoding_never_clears_the_committed_handshake(self):
        source=prepare_week_transition(self.earned(),'handleIncWeekAsk','encoder-fail',self.tables)[0]
        before=copy.deepcopy(source)
        def fail(snapshot):raise TypeError('unsupported native ObjectId without ExtendedJSON')
        with self.assertRaises(TypeError):prepare_week_avatar_reply(source,self.snapshot,fail)
        self.assertEqual(source,before)
        self.assertTrue(source['week_protocol']['awaiting_avatar'])


    def test_original_week_items_clear_but_paid_draw_and_treasure_assets_remain(self):
        source=self.earned()
        source['gacha']['items'].append({'i':12,'u':'d'*24,'w':1})
        source['gacha']['items'].append({'i':12,'u':'e'*24,'w':1,'tr':{'cl':1}})
        next_state=prepare_week_transition(source,'handleIncWeekAsk','clear-week-items',self.tables)[0]
        ids={item['u'] for item in next_state['gacha']['items']}
        self.assertNotIn('d'*24,ids)
        self.assertIn('c'*24,ids)
        self.assertIn('e'*24,ids)
        self.assertEqual(next_state['gacha']['opened_total'],99)
        self.assertEqual(next_state['gacha']['group'],source['gacha']['group'])
        self.assertEqual(next_state['profile']['treasures'],source['profile']['treasures'])
        self.assertEqual(next_state['week_protocol']['history'][0]['cleared_week_items'],[{'i':12,'u':'d'*24,'w':1}])


    def test_native_building_object_id_is_accepted_but_city_flags_stay_strict(self):
        transitioned=prepare_week_transition(self.earned(),'handleIncWeekAsk','building-oid',self.tables)[0]
        def builder(state):
            snapshot=self.snapshot(state)
            building=snapshot['city']['areas']['area_1']['bd']['1']
            building['uuid']=ModelObjectId(building['uuid'])
            return snapshot
        candidate,notices,changed=prepare_week_avatar_reply(transitioned,builder,self.pack)
        self.assertTrue(changed)
        def wrong_city(state):
            snapshot=builder(state);snapshot['city']['areas']['area_1']['st'][0]=1
            return snapshot
        with self.assertRaises(ValueError):prepare_week_avatar_reply(transitioned,wrong_city,self.pack)

    def test_banned_group_preserves_owned_hero_and_cannot_duplicate_groups(self):
        transitioned=prepare_week_transition(self.earned(),'handleIncWeekAsk','banned-group',self.tables)[0]
        transitioned['story']['banned_heroes']={'24':True}
        def banned_builder(state):
            snapshot=self.snapshot(state)
            snapshot['heromgr']['bhrs']=snapshot['heromgr']['hrs']
            snapshot['heromgr']['hrs']=[]
            return snapshot
        self.assertTrue(prepare_week_avatar_reply(transitioned,banned_builder,self.pack)[2])
        def duplicated_builder(state):
            snapshot=banned_builder(state)
            snapshot['heromgr']['hrs']=copy.deepcopy(snapshot['heromgr']['bhrs'])
            return snapshot
        with self.assertRaises(ValueError):prepare_week_avatar_reply(transitioned,duplicated_builder,self.pack)


    def test_new_week_explicit_original_loader_defaults_replace_stale_route_template(self):
        from offline_event_effects import apply_event_effects_snapshot
        source=self.earned()
        source['story'].update(clues=[7],failed_clues=[8],clues_read=True,
            clue_details_read={7:True},rely_value=9,support_value=10,yisake_value=80,
            cityMusic='old-music',cityTheme='old-theme')
        source['profile']['heroes']['24']['cfd']=True
        transitioned=prepare_week_transition(source,'handleIncWeekAsk','clear-route-defaults',self.tables)[0]
        self.assertFalse(transitioned['profile']['heroes']['24']['cfd'])
        template=self.snapshot(transitioned)
        template['std'].update(cl=[7],fc=[8],cr=True,dr={7:True},srv=9,ssv=10,yiv=80,
                               cm='old-music',ct='old-theme')
        projected=apply_event_effects_snapshot(transitioned,template)
        expected={'cl':[],'fc':[],'cr':False,'dr':{},'srv':0,'ssv':0,'yiv':0,'cm':None,'ct':None}
        for key,value in expected.items():self.assertEqual(projected['std'][key],value)


if __name__=='__main__':unittest.main()
