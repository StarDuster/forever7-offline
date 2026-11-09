# -*- coding: ascii -*-
"""Standalone opt-in original-UI audit. Python 2.7; no runtime patch/install.

Loaded only by an actor through the existing development-probe transport.
No original callable is replaced. Only the allowed original navigation/preview
handlers and gg.exec_delay are invoked. Status writes are separate audit files.
"""
import copy
import hashlib
import json
import os
import re
import time


AUDIT_TASKS = ('_task_model','_task_attaches','_task_sfx','_decorate_task','_artifact_task','_awake_task')
AUDIT_ANIMS = ('_anims','_animidle','_touch_anim','_begin_touch_anim','_animcb')
AUDIT_HERO_FIELDS = ('curSkin','lastNorCurSkin','awakeStage','awakeSkinStyle','wearPendantInfo')
AUDIT_SKIN_FIELDS = ('id','uuid','curDye','pendingDye','curWenluItemid','curWenluDye','pendingWenluDye','pendingWenluBlinkData','wenluBlinkData','heroTreasure','createTime','isInvisibleAwakeSkin','forbid','dyeSetTime','texture','textureDye')


def audit_value(value):
    if value is None or type(value) in (bool,int,float,str):return value
    try:
        if isinstance(value,unicode):return value
        if isinstance(value,long):return value
    except NameError:pass
    if isinstance(value,(list,tuple)):return [audit_value(v) for v in value]
    if isinstance(value,dict):return dict((str(k),audit_value(v))for k,v in value.items())
    return {'type':type(value).__module__+'.'+type(value).__name__,'value':str(value)}


def audit_digest(value):
    return hashlib.sha256(json.dumps(audit_value(value),sort_keys=True,separators=(',',':')).encode('ascii')).hexdigest()


def audit_disk_profile(raw):
    """Read actual OfflineSaveStore envelope; never rewrite/checksum-normalize it."""
    envelope=json.loads(raw)
    if not isinstance(envelope,dict)or envelope.get('format')!=1 or 'payload'not in envelope:
        raise ValueError('Missing/unsupported OfflineSaveStore envelope')
    try:integer_types=(int,long);string_types=(basestring,)
    except NameError:integer_types=(int,);string_types=(str,)
    revision=envelope.get('revision');checksum=envelope.get('sha256')
    if isinstance(revision,bool)or not isinstance(revision,integer_types)or revision<1 or not isinstance(checksum,string_types)or not re.match(r'^[a-f0-9]{64}$',checksum):
        raise ValueError('Malformed OfflineSaveStore envelope metadata')
    payload=envelope['payload']
    try:string_types=(basestring,)
    except NameError:string_types=(str,)
    if isinstance(payload,string_types):payload=json.loads(payload)
    if not isinstance(payload,dict)or not isinstance(payload.get('profile'),dict):
        raise ValueError('OfflineSaveStore payload.profile must be a dictionary')
    return payload['profile'],dict((key,envelope.get(key))for key in ('format','revision','sha256'))


def audit_raw_hero(hero):
    fields = dict((key,audit_value(getattr(hero,key)))for key in AUDIT_HERO_FIELDS if hasattr(hero,key))
    missing = [key for key in AUDIT_HERO_FIELDS if not hasattr(hero,key)]
    fields['artifact_context']={'openArtifact':audit_value(getattr(hero,'openArtifact',None)),
        'raw_fields':audit_value(getattr(getattr(hero,'artifact',None),'__dict__',{})),
        'missing':not hasattr(hero,'artifact')}
    skins = {}
    for uid,skin in hero.skins.items():
        values = dict((key,audit_value(getattr(skin,key)))for key in AUDIT_SKIN_FIELDS if hasattr(skin,key))
        # Preserve any additional raw texture fields; never call persistence getters.
        values.update(dict((key,audit_value(value))for key,value in getattr(skin,'__dict__',{}).items()if 'texture' in key.lower()))
        skins[str(uid)] = values
    return {'fields':fields,'missing':missing,'skins':skins}


def audit_route(panel, hero, template):
    """No fabricated UUID, catalog alias, release override, or dye pairing."""
    owned = sorted(((str(uid),uid,skin)for uid,skin in hero.skins.items()if skin.id==template),key=lambda row:row[0])
    if owned:
        label,uid,skin = owned[0]
        if bool(getattr(skin,'isInvisibleAwakeSkin',False)):
            return {'kind':'owned_ias','uid':uid,'uid_text':label,'instances':len(owned)}
        comps = [c for c in panel.skin_comps if getattr(c,'skin_uuid',None)==uid and getattr(c,'skin_id',None)==template and c._node.isVisible()]
        if len(comps)==1 and not getattr(skin,'forbid',False):
            return {'kind':'owned','uid':uid,'uid_text':label,'instances':len(owned)}
    return {'kind':'catalog','instances':len(owned)}


def audit_readiness(scene, panel, expected):
    wrapper = getattr(scene,'scene_model',None)
    model = getattr(wrapper,'model',None) if wrapper is not None else None
    missing = []
    scene_values = {}
    for key in ('real_model_id','model_visible','all_thing_loaded','model_can_touch'):
        if not hasattr(scene,key):missing.append('scene.'+key)
        else:scene_values[key]=audit_value(getattr(scene,key))
    tasks,anims = {},{}
    for key in AUDIT_TASKS:
        if wrapper is None or not hasattr(wrapper,key):missing.append('scene_model.'+key)
        else:tasks[key]=audit_value(getattr(wrapper,key))
    for key in AUDIT_ANIMS:
        if wrapper is None or not hasattr(wrapper,key):missing.append('scene_model.'+key)
        else:anims[key]=audit_value(getattr(wrapper,key))
    if model is None or not hasattr(model,'valid'):missing.append('model.valid')
    if model is None or not hasattr(model,'filename'):missing.append('model.filename')
    if not hasattr(panel,'skin_model_id'):missing.append('hero_model.skin_model_id')
    filename = getattr(model,'filename',None)
    reasons = list(missing)
    if scene_values.get('real_model_id')!=expected or getattr(panel,'skin_model_id',None)!=expected:reasons.append('model_identity')
    for key in ('model_visible','all_thing_loaded','model_can_touch'):
        if scene_values.get(key) is not True:reasons.append(key)
    if not bool(getattr(model,'valid',False)):reasons.append('model_invalid')
    if filename is None or str(expected) not in re.findall(r'\d+',str(filename).replace('\\','/').split('/')[-1]):reasons.append('model_filename')
    if any(value not in (None,[],{})for value in tasks.values()):reasons.append('pending_tasks')
    if anims.get('_anims') or anims.get('_touch_anim') or anims.get('_begin_touch_anim') or anims.get('_animcb'):reasons.append('transient_animation')
    if not anims.get('_animidle'):reasons.append('idle_unknown')
    return {'ready':not reasons,'reasons':reasons,'missing':missing,'scene':scene_values,'tasks':tasks,'animations':anims,
        'epoch':[id(scene),id(wrapper),id(model)],'filename':audit_value(filename),'expected_model':expected}


def audit_stable(samples):
    return (len(samples)==3 and all(row['ready']and row['fingerprint']==samples[-1]['fingerprint']for row in samples)
        and all(samples[index+1]['time']-samples[index]['time']>=.5 for index in range(2)))


class ReadonlyWardrobeAudit(object):
    def __init__(self, gg, status_path, run_id, provenance, scene_key=None):
        self.gg=gg;self.status_path=status_path;self.run_id=run_id;self.provenance=provenance;self.scene_key=scene_key
        self.phase='idle';self.generation=0;self.job=None;self.records=[];self.last=None
        self.batch_digest=None
    def emit(self, phase, **fields):
        self.phase=phase
        payload={'protocol':1,'run_id':self.run_id,'job_id':(self.job or {}).get('job_id'),
            'generation':self.generation,'request_nonce':getattr(self,'request_nonce',None),'phase':phase,'time':time.time(),'provenance':self.provenance}
        if phase=='paused':
            payload.update(integrity_baseline=audit_value(getattr(self,'baseline',None)),integrity_current=audit_value(getattr(self,'latest_permanent',None)),disk_evidence=audit_value(getattr(self,'last_disk_evidence',None)))
        payload.update(audit_value(fields));self.last=payload
        folder=os.path.dirname(self.status_path)
        if not os.path.isdir(folder):raise ValueError('Actor must provide an existing audit directory')
        temporary=self.status_path+'.part'
        with open(temporary,'w')as handle:handle.write(json.dumps(payload,sort_keys=True))
        os.rename(temporary,self.status_path)
    def recover(self):
        """Actor has already returned through original Back; never navigate/reset."""
        if self.phase=='idle':return
        if self.phase!='paused'or not self.base_fence():raise ValueError('Recovery requires same owner/proxy and paused audit')
        self.check_permanent()
        panel=self.gg.ui.panels.hero_herolist
        if not getattr(panel,'valid',False)or not getattr(panel,'visible',False)or self.gg.city_container.get_current_scene()is self.scene:
            raise ValueError('Actor must return to original visible hero list first')
        if self.scene is not None:
            wrapper=getattr(self.scene,'scene_model',None)
            if wrapper is None or any(not hasattr(wrapper,key)or getattr(wrapper,key)not in(None,[],{})for key in AUDIT_TASKS):
                raise ValueError('Old original task queues not proven drained')
        self.generation+=1
        self.emit('idle',recovery='Actor original return verified; no save/collection restoration')
    def run_fence(self):
        owner=self.gg.avatar;proxy=getattr(self.gg,'_f7_avatar_proxy',None)
        if hasattr(self,'run_owner')and(owner is not self.run_owner or proxy is not self.run_proxy):raise ValueError('Audit run owner/proxy changed; explicit replan/resume required')
        self.run_owner=owner;self.run_proxy=proxy
    def inventory(self):
        self.run_fence()
        self.owner=self.gg.avatar;self.proxy=getattr(self.gg,'_f7_avatar_proxy',None)
        if self.proxy is None or self.proxy.owner is not self.owner:raise ValueError('Canonical owner/proxy mismatch')
        self.batch_digest=audit_digest(self.proxy.profile)
        heroes=self.proxy.profile.get('heroes',{})
        self.emit('idle',inventory={'digest':self.batch_digest,'heroes':len(heroes),
            'skin_instances':sum(len(h.get('sk',{}))for h in heroes.values()),'owner_key':audit_value(getattr(self.owner,'id',None)),'hero_ids':sorted(int(h)for h in heroes)})
    def profile(self):
        return self.proxy.profile
    def permanent(self):
        hero=self.gg.avatar.heroMgrData.getHero(self.job['hero_id'])
        out={'profile':audit_digest(self.profile()),'raw_hero':audit_raw_hero(hero)if hero is not None else {'native_hero_missing':True}}
        if self.save_path:
            with open(self.save_path,'rb')as handle:raw=handle.read()
            self.last_disk_evidence={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
            saved_profile,envelope=audit_disk_profile(raw)
            out['stored_profile']=audit_digest(saved_profile)
            out['stored_envelope']=envelope
            out['save_sha256']=hashlib.sha256(raw).hexdigest()
        return out
    def check_permanent(self):
        current=self.permanent()
        self.latest_permanent=current
        # Whole-save hash is evidence only: original seen flags are separate.
        for key in ('profile','raw_hero','stored_profile'):
            if current.get(key)!=self.baseline.get(key):raise RuntimeError('Readonly mutation detected: '+key)
        return current
    def base_fence(self):
        return (getattr(self.gg,'_f7_readonly_wardrobe_audit',None)is self and self.gg.avatar is self.owner
            and getattr(self.gg,'_f7_avatar_proxy',None)is self.proxy)
    def scene_fence(self, selection=True):
        if not self.base_fence()or self.gg.city_container.get_current_scene()is not self.scene:return False
        panels=self.gg.ui.panels
        # Original wardrobe tab deliberately hides hero_common itself.
        if not getattr(panels.hero_common,'valid',False)or getattr(panels.hero_common,'tab_now',None)!='wardrobe':return False
        if not all(getattr(p,'valid',False)and getattr(p,'visible',False)for p in (panels.hero_wardrobe,panels.hero_model)):return False
        if getattr(panels.hero_common,'hero_id',None)!=self.job['hero_id']or getattr(panels.hero_wardrobe,'hero_id',None)!=self.job['hero_id']or getattr(panels.hero_model,'hero_id',None)!=self.job['hero_id']:return False
        if selection and self.route:
            p=panels.hero_wardrobe
            if self.route['kind'].startswith('owned')or self.route['kind']=='hero_current':
                if getattr(p,'skin_uuid',None)!=self.route['uid']:return False
                hero=self.owner.heroMgrData.getHero(self.job['hero_id'])
                if self.route['uid']not in hero.skins or hero.skins[self.route['uid']].id!=self.template:return False
            if self.route['kind']=='catalog'and(getattr(p,'cur_page',None)!=2 or getattr(p,'skin_id',None)!=self.template):return False
        return True
    def schedule(self, callback):
        generation=self.generation
        def delayed():
            if self.generation!=generation or getattr(self.gg,'_f7_readonly_wardrobe_audit',None)is not self:return
            if not self.base_fence():self.emit('paused',reason='owner_proxy_or_job_fence');return
            try:callback()
            except Exception as error:self.fail(str(error))
        self.gg.exec_delay(500,delayed)
    def start(self, job):
        if self.phase!='idle':raise RuntimeError('One outstanding job; cleanup or actor recovery required')
        self.run_fence()
        self.generation+=1;self.job=copy.deepcopy(job);self.owner=self.gg.avatar
        self.proxy=getattr(self.gg,'_f7_avatar_proxy',None)
        if self.proxy is None or self.proxy.owner is not self.owner:raise ValueError('Canonical proxy/owner mismatch')
        self.save_path=job.get('save_path');self.route=None;self.scene=None;self.samples=[];self.capture_epoch=None;self.selection_committed=False
        self.started=time.time();self.timeout=float(job.get('timeout',40));self.result=None
        self.baseline=self.permanent()
        inventory=audit_digest(self.profile())
        if self.batch_digest is None:self.batch_digest=inventory
        if self.batch_digest!=inventory:raise ValueError('Batch inventory changed; pause and replan')
        self.emit('opening',baseline=self.baseline,inventory_digest=inventory)
        if self.job['hero_id']in(46,125):self.result={'load_status':'original_hidden_no_model'};self.finish_without_navigation();return
        if self.owner.heroMgrData.getHero(self.job['hero_id'])is None:
            self.result={'load_status':'original_UI_unreachable','reason':'Native hero not owned; no collection injection'};self.finish_without_navigation();return
        p=self.gg.ui.panels.hero_herolist
        if not getattr(p,'valid',False)or not getattr(p,'visible',False):self.emit('paused',reason='Original visible hero list required');return
        if self.job['hero_id']not in p.curr_show_hero_list:
            self.result={'load_status':'original_UI_unreachable','reason':'hero_not_visible_in_original_list'};self.finish_without_navigation();return
        self.origin_scene=self.gg.city_container.get_current_scene()
        if self.scene_key is None:self.scene_key=__import__('com.const',fromlist=['SCENE_HERO']).SCENE_HERO
        p.on_hero_click(self.job['hero_id'])
        self.scene=self.gg.city_container.get_scene_by_key(self.scene_key)
        if self.scene is None:raise ValueError('Original hero scene not registered after original entry')
        self.schedule(self.wait_hero)
    def wait_hero(self):
        if time.time()-self.started>self.timeout:self.fail('hero_navigation_timeout');return
        current=self.gg.city_container.get_current_scene()
        if current is not self.scene:
            if current is not self.origin_scene:self.emit('paused',reason='Unexpected scene navigation during original hero entry');return
            self.schedule(self.wait_hero);return
        p=self.gg.ui.panels.hero_common
        visible=getattr(p,'visible',False)or (getattr(p,'tab_now',None)=='wardrobe'and getattr(self.gg.ui.panels.hero_wardrobe,'visible',False))
        if not getattr(p,'valid',False)or not visible or getattr(p,'hero_id',None)!=self.job['hero_id']:
            self.schedule(self.wait_hero);return
        p.on_tab_click('wardrobe',instant=True);self.schedule(self.select)
    def select(self):
        if not self.scene_fence(False):self.emit('paused',reason='Navigation/visibility fence before selection');return
        p=self.gg.ui.panels.hero_wardrobe
        if getattr(p,'preview_show',None)is not False:raise ValueError('Non-preview wardrobe required')
        hero=self.owner.heroMgrData.getHero(self.job['hero_id'])
        self.template=self.job.get('template_id')
        if self.template is None:
            uid=hero.lastNorCurSkin if hero.awakeSkinStyle else hero.curSkin
            if uid not in hero.skins:raise ValueError('Canonical current skin UUID missing')
            self.template=hero.skins[uid].id;self.route={'kind':'hero_current','uid':uid,'uid_text':str(uid)}
        else:
            self.route=audit_route(p,hero,self.template)
            if self.route['kind'].startswith('owned'):
                p.select_skin(self.route['uid'],notify=True)
            else:
                p.enter_buy()
                comp=p.comp_wardrobe
                offered=[c for c in comp.sub_comps if c._node.isVisible() and getattr(c,'skin_id',None)in comp.skins
                    and (getattr(c,'skin_id',None)==self.template or getattr(c,'dye_skin',None)==self.template)]
                if len(offered)!=1:
                    self.result={'load_status':'original_UI_unreachable','reason':'No exact original catalog preview component/dye pair','route':audit_value(self.route)}
                    self.cleanup();return
                displayed=offered[0]
                base=displayed.skin_id
                dye=self.template if getattr(displayed,'dye_skin',None)==self.template else None
                self.route.update(catalog_base=base,displayed_dye=dye)
                p.ue_explor_skin(base,notify=True,dye_skin=dye)
        self.selection_committed=True
        self.expected=p.get_model_by_skin(self.template)
        self.selected_at=time.time();self.emit('loading',route=self.route,template_id=self.template)
        self.schedule(self.poll)
    def sample(self):
        if not self.scene_fence():raise ValueError('Scene/panel/selection fence')
        permanent=self.check_permanent()
        p=self.gg.ui.panels.hero_wardrobe;hero=self.owner.heroMgrData.getHero(self.job['hero_id'])
        data=audit_readiness(self.scene,self.gg.ui.panels.hero_model,self.expected)
        if self.capture_epoch is not None and data['epoch']!=self.capture_epoch:raise ValueError('Model epoch changed after stable capture request')
        actual=[skin for uid,skin in hero.skins.items()if str(uid)==self.route.get('uid_text')]
        data.update(time=time.time(),owner=id(self.owner),proxy=id(self.proxy),hero_id=self.job['hero_id'],template_id=self.template,
            uuid=self.route.get('uid_text'),route=self.route,common_visible=getattr(self.gg.ui.panels.hero_common,'visible',None),common_tab=getattr(self.gg.ui.panels.hero_common,'tab_now',None),permanent=permanent,wardrobe_dye=audit_value(getattr(p,'dye_skin_color',None)),wardrobe_current_dye=audit_value(getattr(p,'cur_dye_color',None)))
        data['dye_schemes']=[audit_value(skin.getCurDyeScheme())for skin in actual]
        data['fingerprint']=audit_digest([data['epoch'],self.expected,data['filename'],data['uuid'],data['hero_id'],data['template_id'],data['animations'],permanent.get('raw_hero'),data['wardrobe_dye'],data['wardrobe_current_dye'],data['dye_schemes']])
        return data
    def poll(self):
        data=self.sample();self.samples.append(data);self.samples=self.samples[-3:]
        stable=audit_stable(self.samples)
        if stable:
            self.capture_epoch=data['epoch'];self.capture_token=audit_digest([self.run_id,self.job['job_id'],self.generation,data['fingerprint'],time.time()])
            self.capture_started=time.time()
            self.emit('ready_capture',token=self.capture_token,samples=self.samples,visual_status='unreviewed')
            self.schedule(self.watch_capture);return
        if time.time()-self.started>self.timeout:self.fail('load_or_settle_timeout');return
        self.emit('loading',samples=self.samples);self.schedule(self.poll)
    def watch_capture(self):
        if self.phase not in ('ready_capture','capture_before'):return
        self.sample()
        if time.time()-self.capture_started>float(self.job.get('capture_timeout',20)):
            self.fail('screenshot_handshake_timeout');return
        self.schedule(self.watch_capture)
    def checkpoint(self, token, stage, frame=None):
        if token!=getattr(self,'capture_token',None)or self.phase not in ('ready_capture','capture_before'):raise ValueError('Stale screenshot handshake')
        try:
            data=self.sample()
            if not data['ready']or data['fingerprint']!=self.samples[-1]['fingerprint']:raise ValueError('Screenshot stability mismatch')
            if stage=='before'and self.phase=='ready_capture':
                self.capture_before=data;self.emit('capture_before',token=token,sample=data);return
            if stage!='after'or self.phase!='capture_before'or not frame:raise ValueError('Screenshot handshake order')
            self.result={'load_status':'loaded_unreviewed','visual_status':'unreviewed','before':self.capture_before,'after':data,'frame':frame,'token':token,'samples':self.samples}
            self.cleanup()
        except Exception as error:self.fail(str(error))
    def fail(self, reason):
        self.result={'load_status':'timeout'if 'timeout'in reason else'failed','reason':reason,'samples':self.samples}
        epoch_changed=False
        if self.capture_epoch is not None and self.scene is not None:
            wrapper=getattr(self.scene,'scene_model',None)
            epoch_changed=[id(self.scene),id(wrapper),id(getattr(wrapper,'model',None))]!=self.capture_epoch
        if not self.base_fence()or epoch_changed or self.scene is not None and not self.scene_fence(self.selection_committed):self.emit('paused',result=self.result,reason='User/scene fence; no automatic navigation');return
        try:self.check_permanent()
        except Exception as error:self.emit('paused',result=self.result,reason=str(error));return
        self.cleanup()
    def finish_without_navigation(self):
        self.check_permanent();self.records.append(self.result);self.emit('idle',result=self.result,inventory_digest=audit_digest(self.profile()))
    def cleanup(self):
        if not self.scene_fence(False):self.emit('paused',result=self.result,reason='Cleanup scene fence');return
        self.emit('cleanup',result=self.result)
        p=self.gg.ui.panels.hero_wardrobe
        if getattr(p,'cur_page',None)==2:p.exit_buy()
        self.cleanup_samples=[]
        self.cleanup_started=time.time();self.schedule(self.drain)
    def drain(self):
        if not self.scene_fence(False):self.emit('paused',result=self.result,reason='Cleanup selection/navigation changed');return
        self.check_permanent()
        panel=self.gg.ui.panels.hero_model
        expected=getattr(panel,'skin_model_id',None)
        data=audit_readiness(self.scene,panel,expected)
        data['time']=time.time()
        if data['ready']:
            self.cleanup_samples.append(data);self.cleanup_samples=self.cleanup_samples[-3:]
        else:self.cleanup_samples=[]
        stable=(len(self.cleanup_samples)==3 and all(v['epoch']==data['epoch']and v['filename']==data['filename']for v in self.cleanup_samples)
            and all(self.cleanup_samples[index+1]['time']-self.cleanup_samples[index]['time']>=.5 for index in range(2)))
        if not stable:
            if time.time()-self.cleanup_started>10:self.emit('paused',result=self.result,reason='Late original load/idle tasks remain; do not overlap next hero');return
            self.schedule(self.drain);return
        self.gg.ui.panels.hero_common.on_navigation_canvas_back()
        self.schedule(self.wait_list)
    def wait_list(self):
        self.check_permanent()
        p=self.gg.ui.panels.hero_herolist
        if getattr(p,'valid',False)and getattr(p,'visible',False)and self.gg.city_container.get_current_scene()is not self.scene:
            self.records.append(self.result);self.emit('idle',result=self.result,inventory_digest=audit_digest(self.profile()));return
        if time.time()-self.cleanup_started>10:self.emit('paused',result=self.result,reason='Original return navigation did not settle');return
        self.schedule(self.wait_list)
