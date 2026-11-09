# -*- coding: ascii -*-
"""P7 source-bound Wish UI views. No profile, global clock/table or currency owner.
Early typed/transport guards install before Member caches; late pages after families.
"""
import sys
import types
import json
import hashlib
_POLICY_RAW_SHA='72762790a130d0710545a9cb95211acfefd084cea4d05d1fe9c84bd9344427bc'
_MARKER='_q7_wish_ui_owner'
_IDS=(5,119,126,143,154,164,397,426,445)
try:
    _TEXT=(basestring,)
except NameError:
    _TEXT=(str,bytes)
def _raw(fn):return getattr(fn,'im_func',getattr(fn,'__func__',fn))
def _globals(fn):return getattr(fn,'func_globals',getattr(fn,'__globals__',{}))
def _cell(value):
    def held():return value
    return getattr(held,'func_closure',getattr(held,'__closure__',None))[0]
def _clone(fn,aliases,gg):
    namespace=dict(_globals(fn));namespace.update(aliases)
    code=getattr(fn,'func_code',getattr(fn,'__code__',None));closure=getattr(fn,'func_closure',getattr(fn,'__closure__',None))
    if closure:
        cells=list(closure)
        for i,name in enumerate(code.co_freevars):
            value=cells[i].cell_contents
            if name in ('func','f') and isinstance(value,types.FunctionType):
                if _globals(value).get('gg',gg)is not gg:raise RuntimeError('Wish decorated gg changed')
                cells[i]=_cell(_clone(value,aliases,gg))
        closure=tuple(cells)
    return types.FunctionType(code,namespace,fn.__name__,getattr(fn,'func_defaults',getattr(fn,'__defaults__',None)),closure)
def _copy(v):
    if isinstance(v,dict):return dict((k,_copy(x))for k,x in v.items())
    if isinstance(v,(tuple,list)):return [_copy(x)for x in v]
    return v
def _pairs(values):
    out={}
    for key,value in values:
        if key in out:raise ValueError('Duplicate Wish policy key')
        out[key]=value
    return out
def _canonical(value):return json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode('ascii')
def _policy(text):
    if not isinstance(text,_TEXT):raise ValueError('Embedded Wish policy required')
    raw=text.encode('ascii') if not isinstance(text,bytes) else text
    if hashlib.sha256(raw).hexdigest()!=_POLICY_RAW_SHA:raise ValueError('Wish policy text changed')
    data=json.loads(text,object_pairs_hook=_pairs)
    if data.get('schema')!='project7-wish-ui-v1'or tuple(data.get('candidate_ids',()))!=_IDS:raise ValueError('Wish scope changed')
    return data
class _View(object):
    def __init__(self,source,**aliases):object.__setattr__(self,'_source',source);object.__setattr__(self,'_aliases',aliases)
    def __getattr__(self,name):return self._aliases[name]if name in self._aliases else getattr(self._source,name)
    def __setattr__(self,name,value):
        if name in ('_source','_aliases'):object.__setattr__(self,name,value)
        elif name in self._aliases:self._aliases[name]=value
        else:setattr(self._source,name,value)
class _Rows(object):
    def __init__(self,source,rows):self.source,self.rows=source,rows
    def get(self,key,default=None):return _copy(self.rows[key])if key in self.rows else self.source.get(key,default)
    def keys(self):return [k for k in self.source.keys()if k not in self.rows]+list(self.rows.keys())
    def __getitem__(self,key):
        marker=object();v=self.get(key,marker)
        if v is marker:raise KeyError(key)
        return v
    def items(self):return [(k,self[k])for k in self.keys()]
    def iteritems(self):return iter(self.items())
    def values(self):return [v for k,v in self.items()]
    def iterkeys(self):return iter(self.keys())
    def itervalues(self):return iter(self.values())
    def __iter__(self):return iter(self.keys())
    def __len__(self):return len(self.keys())
class _Activities(object):
    def __init__(self,scope,source):self.scope,self.source=scope,source
    def get(self,t,default=None):
        value=self.source.get(t,default)
        return _Activity(self.scope,value,t)if t in self.scope.state.pools and value is not default else value
    def __getitem__(self,t):
        marker=object();v=self.get(t,marker)
        if v is marker:raise KeyError(t)
        return v
    def keys(self):return self.source.keys()
    def items(self):return [(t,self[t])for t in self.keys()]
    def iteritems(self):return iter(self.items())
class _Activity(_View):
    def __init__(self,scope,source,t):_View.__init__(self,source);object.__setattr__(self,'scope',scope);object.__setattr__(self,'t',t)
    def __getattr__(self,name):
        self.scope.live()
        if name=='wish_info':return self.scope.groups(self.t)
        if name=='choose_treasure'and self.t==5:return self.scope.choice()[1]
        if name=='get_inc_up_prob':
            def rate(data):
                self.scope.live();row=self.scope.state.pools[self.t]['info'];c=data.inc_up_cnt.get(row.get('inc_up_cnt_type'),0)
                if c>=row.get('up_n',999999):return 1.0-self.get_top_rate()/100.0
                return max(0,c-row.get('up_m',999999))//row.get('up_x',999999)*row.get('up_r',0)/100.0
            return rate
        if name=='get_is_must_up':
            def must(data):
                self.scope.live();return data.inc_up_cnt.get(self.scope.state.pools[self.t]['info'].get('inc_up_cnt_type'),0)>=self.scope.state.pools[self.t]['info'].get('up_n',999999)
            return must
        if name=='get_top_rate':
            def top():self.scope.live();return self.scope.top_rate(self.t)
            return top
        return _View.__getattr__(self,name)
class _Data(_View):
    def __init__(self,scope,source):_View.__init__(self,source);object.__setattr__(self,'scope',scope)
    def __getattr__(self,name):
        s=self.scope;s.live()
        if name=='activity_data':return _Activities(s,s.data.activity_data)
        if name=='inc_up_cnt':return dict(s.data.inc_up_cnt)
        if name=='getTreasureWishIdByDrawType':return lambda t:s.wish_id()if t==5 else getattr(self._source,name)(t)
        if name=='getChooseTreasure':return lambda t:s.choice()if t==5 else getattr(self._source,name)(t)
        if name=='getWishTypeByDrawType':return lambda t:(1 if t==5 else 2 if t in s.state.pools and s.state.pools[t]['family']=='group'else 0)if t in s.state.pools else getattr(self._source,name)(t)
        if name=='getWishGroupInfoListsByDrawType':
            def lists(t,exlude_fixed=False):
                if t not in s.state.pools:return getattr(self._source,name)(t,exlude_fixed)
                out={}
                for key,row in s.state.wish.items():
                    if row['drawType']==t and(not exlude_fixed or not row.get('fix_rate')):out.setdefault(row['gid'],[]).append(key)
                return out
            return lists
        if name=='getWishGroupInfoDict':return lambda t,gid:s.groups(t).get(gid,{})if t in s.state.pools else getattr(self._source,name)(t,gid)
        value=getattr(s.data,name)
        if callable(value)and name.startswith(('getWish','getTreasureWish')):
            def bound(*args,**kwargs):
                s.live();result=_clone(_raw(value),s.aliases(_globals(_raw(value))),s.state.gg)(self,*args,**kwargs)
                if name=='getWishGroupProbDicts'and args and args[0]in s.state.pools:
                    forced=s.forced(args[0])
                    if forced is not None:
                        ids,gids=result;ids=dict((k,1.0 if k==forced else 0.0)for k in ids);gid=s.state.wish[forced]['gid'];gids=dict((k,1.0 if k==gid else 0.0)for k in gids);return ids,gids
                return result
            return bound
        return _View.__getattr__(self,name)
class _Avatar(_View):
    def __init__(self,scope):_View.__init__(self,scope.avatar);object.__setattr__(self,'scope',scope)
    def __getattr__(self,name):
        s=self.scope;s.live()
        if name=='luckyDrawData':return _Data(s,s.state.history_avatar_type(s.avatar,s.state.draw_owner).luckyDrawData)
        if name=='getChoukaInfoDataByType':return lambda t:s.state.draw_owner.panel_row(_copy(s.state.pools[t]['info']))if t in s.state.pools else getattr(s.avatar,name)(t)
        if name=='checkJiaozhiInTime':return lambda key:True if key in s.state.jiaozhi else getattr(s.avatar,name)(key)
        if name=='validSetChooseTreasure':
            raw=_raw(getattr(s.avatar,name))
            return lambda *a,**k:_clone(raw,s.aliases(_globals(raw)),s.state.gg)(self,*a,**k)
        if name=='setChooseTreasure':return lambda *a,**k:s.state.member_owner.choose(s,*a,**k)
        value=getattr(s.avatar,name)
        if callable(value):
            def checked(*args,**kwargs):s.live();return value(*args,**kwargs)
            return checked
        return value
class _Scope(object):
    def __init__(self,state,instance,panel,t):
        gg=state.current();self.state,self.instance,self.panel,self.t=state,instance,panel,t
        self.avatar,self.data,self.ui=gg.avatar,gg.avatar.luckyDrawData,gg.ui
        self.epoch=self.ui._lock;self.node=getattr(instance,'_node',None);self.parent_node=getattr(panel,'_node',None)
        self.init_token=getattr(instance,'_q7_wish_init_token',getattr(instance,'_q7_dynamic_init_token',None));self.parent_token=getattr(panel,'_q7_wish_init_token',getattr(panel,'_q7_dynamic_init_token',None))
        self.events=getattr(panel,'event_handlers',None);self.panels=self.ui.panels;self.tables=[]
        self.transport=state.member_owner.transport(self.avatar)if state.member_owner is not None else None
    def live(self,cleanup=False):
        gg=self.state.current()
        if gg.avatar is not self.avatar or self.avatar.luckyDrawData is not self.data or gg.ui is not self.ui or self.ui._lock is not self.epoch or self.ui.panels is not self.panels:raise RuntimeError('Wish UI owner generation changed')
        if self.state.member_owner is not None and self.state.member_owner.transport(self.avatar)is not self.transport:raise RuntimeError('Wish connection changed')
        if(not cleanup and(not getattr(self.instance,'valid',False)or not getattr(self.panel,'valid',False)))or getattr(self.instance,'_node',None)is not self.node or getattr(self.panel,'_node',None)is not self.parent_node:raise RuntimeError('Wish panel replaced')
        if getattr(self.instance,'_q7_wish_init_token',getattr(self.instance,'_q7_dynamic_init_token',None))is not self.init_token or getattr(self.panel,'_q7_wish_init_token',getattr(self.panel,'_q7_dynamic_init_token',None))is not self.parent_token or getattr(self.panel,'event_handlers',None)is not self.events:raise RuntimeError('Wish panel reinitialized')
        if self.instance.__dict__.get('_q7_wish_scope')is not self or self.state.draw_type(self.instance)!=self.t:raise RuntimeError('Wish show changed')
        for table,source,rot,module,module_data in self.tables:
            if getattr(table,'data',None)is not source or getattr(source,'_rot_id',None)!=rot or getattr(source,'_module',None)is not module or getattr(module,'data',None)is not module_data:raise RuntimeError('Wish source table changed')
        return gg
    def wish_id(self):
        ad=self.data.activity_data.get(5);ctr=list(getattr(ad,'choose_treasure',(0,0,0)))
        if len(ctr)!=3 or any(not isinstance(n,int)or isinstance(n,bool)or n<0 for n in ctr):raise RuntimeError('Wish selection projection changed')
        key=ctr[0]or self.state.policy['default_wish_scope']
        if key not in self.state.wish or self.state.wish[key]['drawType']!=5:raise RuntimeError('Wish archive scope unavailable')
        return key
    def choice(self):
        key=self.wish_id();ad=self.data.activity_data.get(5);ctr=list(getattr(ad,'choose_treasure',(0,0,0)));ctr[0]=key
        if ctr[1]and not self.state.choose.get(ctr[1],{}).get('can_choose'):raise RuntimeError('Wish selected target unavailable')
        return True,ctr
    def callback(self,fn):
        def guarded(*args,**kwargs):
            try:self.live()
            except RuntimeError:return None
            return fn(*args,**kwargs)
        return guarded
    def owned(self,hero):return bool(self.avatar.heroMgrData.getHero(hero))
    def groups(self,t):
        ad=self.data.activity_data.get(t);raw=getattr(ad,'wish_info',{});out=_copy(raw)
        for gid,ids in self.state.group_ids(t).items():
            value=out.setdefault(gid,{});value.setdefault('c',0);value.setdefault('f',[]);value.setdefault('a',[])
            if not isinstance(value['c'],int)or isinstance(value['c'],bool)or value['c']<0 or not set(value['f']).issubset(set(ids))or not set(value['a']).issubset(set(value['f'])):raise RuntimeError('Wish group projection invalid')
            for key in ids:
                if self.owned(self.state.wish[key]['wish_target'])and key not in value['f']:value['f'].append(key);value['a'].append(key)
            if set(ids).issubset(set(value['f'])):value['c']=0
        return out
    def forced(self,t):
        groups=self.groups(t);forced=[]
        for key,row in self.state.wish.items():
            if row['drawType']==t and row.get('fix_rate')and key not in groups[row['gid']]['f']and groups[row['gid']]['c']+1>=row.get('safe_times',999999):forced.append(key)
        if len(forced)>1:raise RuntimeError('Ambiguous Wish safety projection')
        return forced[0]if forced else None
    def top_rate(self,t):
        rows=[r for r in self.state.normals.values()if r.get('type')==t];total=sum(r.get('weight',0)for r in rows);up=sum(r.get('weight',0)for r in rows if r.get('is_up'))
        if not total:raise RuntimeError('Wish UP source mass missing')
        return int(round(100.0*up/total))
    def aliases(self,namespace,cleanup=False):
        self.live(cleanup);avatar=_Avatar(self);aliases={'gg':_GG(self,cleanup,avatar)}
        if namespace.get('cc')is not None:aliases['cc']=_CocosView(namespace['cc'],self)
        rows={'CHOUKA_TREASURE_WISH':self.state.wish,'CHOUKA_NORMAL_DATA':self.state.normals,'CHOUKA_WISH_TREASURE_CHOOSE':self.state.choose,'ITEM_STORE_WISH_CHANGE':self.state.fees,'CHOUKA_INFO_DATA':self.state.infos,'CHOUKA_INFO':self.state.infos,'CHOUKA_JIAOZHI_DATA':self.state.jiaozhi,'UI_COMP_DATA':getattr(self.state,'ui_comp',{}),'CHOUKA_LEIJI_REWARD_DATA':{}}
        for name,fixed in rows.items():
            if name not in namespace:continue
            table=namespace[name];source=table.data;module=getattr(source,'_module',None)
            if not any(old is table for old,_,_,_,_ in self.tables):self.tables.append((table,source,getattr(source,'_rot_id',None),module,getattr(module,'data',None)))
            view_source=dict((k,v)for k,v in source.items()if v.get('drawType')not in self.state.pools)if name=='CHOUKA_LEIJI_REWARD_DATA'else source
            aliases[name]=_View(table,data=_Rows(view_source,fixed))
        return aliases
class _ActionView(_View):
    def __init__(self,source,scope):_View.__init__(self,source);object.__setattr__(self,'scope',scope)
    def __getattr__(self,name):
        source=_View.__getattr__(self,name)
        if name=='start':
            def start(*args,**kwargs):
                self.scope.live()
                args=tuple(self.scope.callback(v)if callable(v)else v for v in args)
                kwargs=dict((k,self.scope.callback(v)if callable(v)else v)for k,v in kwargs.items())
                return source(*args,**kwargs)
            return start
        if name in ('load','stop'):return source
        return _ActionView(source,self.scope)
class _CocosView(_View):
    def __init__(self,source,scope):_View.__init__(self,source);object.__setattr__(self,'scope',scope)
    def __getattr__(self,name):
        value=_View.__getattr__(self,name)
        if name=='cc':return _CocosView(value,self.scope)
        if name=='CallFunc':return _View(value,create=lambda fn:value.create(self.scope.callback(fn)))
        return value
class _ScopedUI(_View):
    def __init__(self,source,scope):_View.__init__(self,source);object.__setattr__(self,'scope',scope)
    def __getattr__(self,name):
        source=_View.__getattr__(self,name)
        return _ActionView(source,self.scope)if name=='actions'else source
class _GG(_View):
    def __init__(self,scope,cleanup,avatar):_View.__init__(self,scope.state.gg,avatar=avatar);object.__setattr__(self,'scope',scope);object.__setattr__(self,'cleanup',cleanup)
    def __getattr__(self,name):
        self.scope.live(self.cleanup)
        if name=='ui':return _ScopedUI(self.scope.ui,self.scope)
        value=_View.__getattr__(self,name)
        if name=='exec_delay':return lambda delay,fn,*a,**k:value(delay,self.scope.callback(fn),*a,**k)
        return value
    def __setattr__(self,name,value):
        if name in('_source','_aliases','scope','cleanup'):object.__setattr__(self,name,value)
        else:self.scope.live(self.cleanup);_View.__setattr__(self,name,value)
_TARGETS=(('cocos.panels.card_yingzhuang','Panel'),('cocos.panels.card_jiaozhi','Panel'),('cocos.panels.card_box','Panel'))
_METHODS=(('on_init','on_load','notify_show','notify_hide','set_info','set_scroll_view','on_touch_treasure','on_btn_close_click','on_btn_go_click','on_btn_change_click','confirm_select_treasure_list','after_choose_treasure'),('on_init','on_load','notify_show','set_info','set_qiyuan','set_jiaozhi','on_left_click','on_right_click','on_close_click','on_target_click','on_change_click'),('getHuodongPanel','canShowWishPanel','canShowWishLeftInfo','update_wish_banner','update_treasure_wish','update_wish_left_info','update_sp_banner'))
class _ClickLease(object):
    def __init__(self,scope,sender):
        self.ui,self.panel,self.sender=scope.ui,scope.instance,sender;self.released=False;self.retained=False
    def release(self):
        if self.released:return
        self.released=True
        if getattr(self.ui,'_q7_wish_click_lease',None)is not self:return
        self.ui._q7_wish_click_lease=None
        if self.retained and getattr(self.ui,'cur_sender',None)is self.sender and getattr(self.ui,'cur_panel',None)is self.panel:
            self.ui.multi_click=0;self.ui.cur_sender=None;self.ui.cur_panel=None;self.sender.release()
class _Installation(object):
    def __init__(self,modules,classes,gg,policy,history_avatar_type,friend_owner,families_owner,member_owner):
        self.modules,self.classes,self.gg,self.policy=modules,classes,gg,policy
        self.policy_sha256=hashlib.sha256(_canonical(policy)).hexdigest();self.history_avatar_type=history_avatar_type;self.friend_owner=friend_owner;self.families_owner=families_owner;self.member_owner=member_owner
        self.draw_owner=families_owner.draw_owner;self.detail_indices=(0,2,6);self.detail_classes=tuple(families_owner.classes[i]for i in self.detail_indices);self.detail_ids=_IDS
        self.pools=dict((p['id'],p)for p in policy['pools']);self.wish=dict((int(k),v)for k,v in policy['wish'].items());self.choose=dict((int(k),v)for k,v in policy['choose'].items());self.fees=dict((int(k),v)for k,v in policy['fees'].items());self.normals=dict((int(k),v)for k,v in policy['normals'].items());self.items=dict((int(k),v)for k,v in policy['items'].items())
        self.ui_comp=dict((int(k),v)for k,v in policy['ui_comp'].items());self.infos=dict((t,_copy(p['info']))for t,p in self.pools.items());self.jiaozhi=dict(((t,r['id']),r)for t,p in self.pools.items()for r in p['jiaozhi'])
        for t,p in self.pools.items():
            if p['family']=='up':self.infos[t]['yijieti']=True;self.infos[t]['up_tips']=u'\u672c\u671fUP\u6982\u7387'
        self.records=[];self.originals={};self.delegates={}
    def current(self):
        if sys.modules.get('gg')is not self.gg or self.friend_owner.current()is not self.gg or self.draw_owner.current()is not self.gg or self.families_owner.current()is not self.gg:raise RuntimeError('Wish companion changed')
        if self.families_owner.friend_owner is not self.friend_owner or self.families_owner.history_avatar_type is not self.history_avatar_type or self.classes[2]is not self.families_owner.classes[0]:raise RuntimeError('Wish exact companion ABI changed')
        if hashlib.sha256(_canonical(self.policy)).hexdigest()!=self.policy_sha256:raise RuntimeError('Wish policy mutation')
        for module,cls,(name,attribute)in zip(self.modules,self.classes,_TARGETS):
            if sys.modules.get(name)is not module or getattr(module,attribute)is not cls or cls.__dict__.get(_MARKER)is not self:raise RuntimeError('Wish module/class generation changed')
        for cls,name,fn in self.records:
            if _raw(getattr(cls,name))is not fn:raise RuntimeError('Wish method replaced')
        if self.member_owner is not None:self.member_owner.check()
        return self.gg
    def group_ids(self,t):
        out={}
        for key,row in self.wish.items():
            if row['drawType']==t:out.setdefault(row['gid'],[]).append(key)
        return out
    def draw_type(self,instance):
        if type(instance)is self.classes[0]:return getattr(instance,'lucky_draw_type',None)
        if type(instance)is self.classes[2]:return instance.get_luckyDraw_type()
        if type(instance)is self.families_owner.classes[6]:return getattr(instance,'cur_drawtype',None)
        return getattr(instance,'_type',None)
    def allowed(self,t):return t in self.policy['detail_ids']and self.draw_owner.allowed(t)
    def resources(self,t,choose=False):
        module=sys.modules.get('C_file')or getattr(sys.modules.get('game3d'),'C_file',None);finder=getattr(module,'find_res_file',None)
        if not callable(finder):raise RuntimeError('Wish resource resolver unavailable')
        for path in self.pools[t]['required_assets']:
            if not finder(path,''):raise RuntimeError('Wish required resource unavailable: '+path)
        if t==5:
            ad=self.gg.avatar.luckyDrawData.activity_data.get(5);ctr=getattr(ad,'choose_treasure',(0,0,0));key=ctr[0]or self.policy['default_wish_scope'];row=self.wish.get(key,{})
            if row.get('drawType')!=5:raise RuntimeError('Wish source scope unavailable')
            ids=[ctr[1]or row['treasure_id']]
            if choose:ids.extend(k for k,r in self.choose.items()if r.get('can_choose'))
            for identity in ids:
                icon=self.items.get(identity,{}).get('icon')
                if not icon or not finder('cocos/image/item/common/%s.png'%icon,''):raise RuntimeError('Wish target icon unavailable')
    def before_request(self,t,avatar):
        gg=self.current()
        if avatar is not gg.avatar:raise RuntimeError('Wish request avatar changed')
        if t not in self.pools:return False
        if not self.allowed(t):raise RuntimeError('Wish entry not admitted')
        self.resources(t);return True
    def pin(self,instance):
        gg=self.current();instance._q7_wish_generation=(getattr(gg,'avatar',None),getattr(getattr(gg,'avatar',None),'luckyDrawData',None),gg.ui);instance._q7_wish_init_token=object();instance.__dict__.pop('_q7_wish_scope',None)
    def scope(self,instance,t=None,renew=False):
        t=self.draw_type(instance)if t is None else t
        if not self.allowed(t):raise RuntimeError('Wish entry not admitted')
        self.resources(t)
        if not renew:
            old=instance.__dict__.get('_q7_wish_scope')
            if old is not None:old.live();return old
        panel=getattr(instance,'_panel',instance);scope=_Scope(self,instance,panel,t);instance._q7_wish_scope=scope;scope.live();return scope
    def invoke_detail(self,index,name,original,instance,args,kwargs):
        self.current()
        if index not in self.detail_indices:raise RuntimeError('Wish delegate target changed')
        expected=self.detail_classes[self.detail_indices.index(index)]
        if type(instance)is not expected:raise RuntimeError('Wish delegate class changed')
        t=(args[0]if args else kwargs.get('_type'))if name=='set_info'else self.draw_type(instance)
        if t not in self.pools:raise RuntimeError('Wish delegate pool changed')
        key=(index,name);prior=self.delegates.get(key)
        if prior is not None and prior is not original:raise RuntimeError('Wish delegate original changed')
        self.delegates[key]=original
        if name=='set_info':instance._type=t
        if name in('on_init','on_load'):
            self.pin(instance)
            if name=='on_init':return original(instance,*args,**kwargs)
        scope=self.scope(instance,t,renew=name in('set_info','notify_show','on_load'));result=_clone(original,scope.aliases(_globals(original)),self.gg)(instance,*args,**kwargs)
        scope.live()
        if name in('set_info','notify_show','on_load'):self.bind_callbacks(instance,scope)
        return result
    def invoke(self,index,name,instance,args,kwargs):
        self.current();original=self.originals[index,name]
        if name in('on_init','on_load'):
            prior=instance.__dict__.get('_q7_wish_scope');self.pin(instance)
            result=original(instance,*args,**kwargs)
            if name=='on_load'and prior is not None and getattr(prior,'constructing',False):
                gg=self.current()
                if gg.avatar is not prior.avatar or gg.ui is not prior.ui or prior.ui._lock is not prior.epoch or gg.avatar.luckyDrawData is not prior.data:raise RuntimeError('Wish owner changed during layer load')
                prior.node=getattr(instance,'_node',None);prior.parent_node=getattr(prior.panel,'_node',None)
                prior.init_token=getattr(instance,'_q7_wish_init_token',None);prior.parent_token=getattr(prior.panel,'_q7_wish_init_token',None);prior.events=getattr(prior.panel,'event_handlers',None)
                instance._q7_wish_scope=prior;prior.live()
            return result
        t=(args[0]if args else kwargs.get('_type'))if name=='notify_show'else self.draw_type(instance)
        if t not in self.pools:return original(instance,*args,**kwargs)
        if name=='notify_show':
            if index==0:instance.lucky_draw_type=t
            else:instance._type=t
        if name in('notify_hide','on_close_click','on_btn_close_click'):
            scope=instance.__dict__.get('_q7_wish_scope')
            if scope is None:return original(instance,*args,**kwargs)
        else:scope=self.scope(instance,t,renew=name=='notify_show')
        scope.constructing=name=='notify_show'and index==0
        try:result=_clone(original,scope.aliases(_globals(original),cleanup=name in('notify_hide','on_close_click','on_btn_close_click')),self.gg)(instance,*args,**kwargs)
        finally:scope.constructing=False
        if name not in('notify_hide','on_close_click','on_btn_close_click'):scope.live()
        if name=='notify_show':self.bind_callbacks(instance,scope)
        if name=='update_sp_banner'and self.pools[t]['family']=='up':
            c=scope.data.inc_up_cnt.get(self.pools[t]['info']['inc_up_cnt_type'],0)
            if not isinstance(c,int)or isinstance(c,bool)or c<0 or c>180:raise RuntimeError('Wish UP projection invalid')
            instance['main.top.sp_jindu.chongneng_num_1'].setString(str(180 if c==0 else max(181-c,1)))
        return result
    def bind_callbacks(self,instance,scope):
        if type(instance)is self.classes[0]:
            index=0;names=(('_node','on_btn_close_click'),('btn_close','on_btn_close_click'),('treasure_item_img','on_touch_treasure'),('btn_change','on_btn_change_click'))
        elif type(instance)is self.classes[1]:
            index=1;names=(('btn_close','on_close_click'),('main.item.touch','on_target_click'),('btn_left','on_left_click'),('btn_right','on_right_click'))
        elif type(instance)is self.detail_classes[0]:
            index=2;names=(('yingzhuang_wish_tips','on_yingzhuang_wish_click'),)
        elif type(instance)is self.detail_classes[1]:
            index=3;names=(('_node','on_tips_click'),)
        elif type(instance)is self.detail_classes[2]:
            index=4;names=(('btn_info','on_info_click'),('chest_click','on_chest_click'),('jiaozhi_tips','on_jiaozhi_click'))
        else:return
        bindings=instance.__dict__.setdefault('_q7_wish_callbacks',{})
        for attr,name in names:
            widget=instance[attr]if '.'in attr else getattr(instance,attr,None)
            if widget is None:continue
            if index<2:source=self.originals[index,name]
            else:source=self.families_owner.detail_original(0 if index==2 else 2 if index==3 else 6,name)
            def make(attr,name,widget,source):
                key=(attr,name);cc=_globals(source).get('cc');enums=getattr(cc,'ccui',None)
                began=getattr(enums,'TOUCH_EVENT_BEGAN',0);ends=(getattr(enums,'TOUCH_EVENT_ENDED',2),getattr(enums,'TOUCH_EVENT_CANCELED',3))
                def bind(fn):bindings[key]=fn;widget.addTouchEventListener(fn)
                def call(args,kwargs):return _clone(source,scope.aliases(_globals(source),cleanup=name in('on_close_click','on_btn_close_click')),self.gg)(instance,*args,**kwargs)
                def live():return scope.live(cleanup=name in('on_close_click','on_btn_close_click'))
                def entry(*args,**kwargs):
                    if bindings.get(key)is not entry:return None
                    event=args[1]if len(args)>1 else kwargs.get('event');sender=args[0]if args else kwargs.get('sender')
                    if event!=began:return None
                    try:live()
                    except RuntimeError:return None
                    old=getattr(scope.ui,'_q7_wish_click_lease',None)
                    if old is not None and not old.released:old.release();return False
                    before=getattr(scope.ui,'cur_sender',None);count=getattr(scope.ui,'multi_click',0);completed=False
                    lease=_ClickLease(scope,sender)
                    try:result=call(args,kwargs);completed=True
                    finally:
                        lease.retained=before is None and count==0 and getattr(scope.ui,'cur_sender',None)is sender and getattr(scope.ui,'cur_panel',None)is instance and getattr(scope.ui,'multi_click',0)>0
                        if lease.retained and not completed:scope.ui._q7_wish_click_lease=lease;lease.release()
                    if index<2 and not lease.retained and not getattr(getattr(scope.ui.panels,'newbee_guidance',None),'is_begin',False):return result
                    scope.ui._q7_wish_click_lease=lease
                    def gesture(*args,**kwargs):
                        event=args[1]if len(args)>1 else kwargs.get('event')
                        if bindings.get(key)is not gesture or lease.released or getattr(scope.ui,'_q7_wish_click_lease',None)is not lease:lease.release();return None
                        if event==began:lease.release();bind(entry);return False
                        completed=False
                        try:live();result=call(args,kwargs);completed=True;return result
                        finally:
                            if event in ends or not completed:
                                lease.release()
                                if bindings.get(key)is gesture:
                                    if getattr(instance,'valid',False)and instance.__dict__.get('_q7_wish_scope')is scope:bind(entry)
                                    else:bindings.pop(key,None)
                    bind(gesture);return result
                return entry
            callback=make(attr,name,widget,source);bindings[(attr,name)]=callback;widget.addTouchEventListener(callback)
        # Event closures are pinned to this exact show generation as well.
        handlers=getattr(instance,'event_handlers',None)
        if isinstance(handlers,dict):
            for key,name in (('treasure_select_list','confirm_select_treasure_list'),('after_choose_treasure','after_choose_treasure')):
                if index==0 and key in handlers:
                    source=self.originals[0,name]
                    def make(source):
                        def event(*args,**kwargs):
                            try:scope.live()
                            except RuntimeError:return None
                            return _clone(source,scope.aliases(_globals(source)),self.gg)(instance,*args,**kwargs)
                        return event
                    handlers[key]=make(source)
    def apply(self):
        state=self
        for index,names in enumerate(_METHODS):
            cls=self.classes[index]
            for name in names:
                original=_raw(getattr(cls,name));self.originals[index,name]=original
                def make(index,name,original):
                    def wrapped(instance,*args,**kwargs):return state.invoke(index,name,instance,args,kwargs)
                    wrapped.__dict__.update(getattr(original,'__dict__',{}));wrapped.__name__=original.__name__;return wrapped
                wrapper=make(index,name,original);setattr(cls,name,wrapper);self.records.append((cls,name,wrapper))
        for cls in self.classes:setattr(cls,_MARKER,self)
        return self

_EARLY=None
class _ChooseLease(_View):
    def __init__(self,pending):
        _View.__init__(self,pending.scope.ui)
        object.__setattr__(self,'pending',pending)
    def lock(self,key,show_panel=True):
        p=self.pending;p.scope.live()
        if key!='setChooseTreasure'or p.acquired:raise RuntimeError('Wish lock ownership changed')
        before=p.epoch.get(key,0)
        try:return self._source.lock(key,show_panel)
        finally:
            p.acquired=p.epoch.get(key,0)>before
            if p.acquired:p.wait=getattr(self._source.panels,'wait',None)
    def unlock(self,key,show_panel=True):
        p=self.pending
        if key!='setChooseTreasure':raise RuntimeError('Wish unlock ownership changed')
        if p.released:return None
        p.released=True
        if p.scope.state.gg.ui is not self._source:
            wait=getattr(p,'wait',None);cancel=getattr(p.scope.state.gg,'exec_cancel',None)
            if wait is not None:
                if callable(cancel):
                    for name in ('show_desc_timer','disconnect_timer'):
                        handle=getattr(wait,name,None)
                        if handle:cancel(handle);setattr(wait,name,None)
                node=getattr(wait,'_node',None)
                if node is not None and getattr(wait,'valid',False):node.setVisible(False)
            return None
        if p.acquired and self._source._lock is p.epoch:return self._source.unlock(key,show_panel)
class _ChoosePending(object):
    def __init__(self,scope,channel):
        self.scope,self.channel=scope,channel;self.epoch=scope.ui._lock
        self.sent=False;self.acquired=False;self.released=False;self.lease=_ChooseLease(self)
class _SendingServer(_View):
    def __init__(self,source,pending):_View.__init__(self,source);object.__setattr__(self,'pending',pending)
    def call_server_method(self,*args,**kwargs):
        p=self.pending
        if p.scope.state.member_owner.transport(p.scope.avatar)is not p.channel:raise RuntimeError('Wish send transport changed')
        # This is the actual ServerProxy wire boundary, not a parameter hash.
        p.sent=True
        return self._source.call_server_method(*args,**kwargs)
class _SendingAvatar(_View):
    def __init__(self,pending):
        _View.__init__(self,pending.scope.avatar,server=_SendingServer(pending.scope.avatar.server,pending))
        object.__setattr__(self,'pending',pending)
    def __getattr__(self,name):
        value=_View.__getattr__(self,name)
        if name in ('callServerMethodReliable','callServerMethod','reSendRpc'):
            raw=_raw(value)
            return lambda *a,**k:raw(self,*a,**k)
        return value
class _MemberOwner(object):
    def __init__(self,gg,module,member,transport_owner):
        self.gg,self.module,self.member,self.transport_owner=gg,module,member,transport_owner
        self.pending=None;self.wrapper=None;self.business_wrapper=None
        self.original=_raw(member.replySetChooseTreasure)
        self.original_choose=_raw(member.setChooseTreasure)
    def _check_avatar_copy(self,avatar_cls):
        if avatar_cls is None or _raw(getattr(avatar_cls,'replySetChooseTreasure',None))is not self.wrapper:raise RuntimeError('Wish Member copy changed')
        expected=self.business_wrapper if self.business_wrapper is not None else self.original_choose
        if _raw(getattr(avatar_cls,'setChooseTreasure',None))is not expected:raise RuntimeError('Wish choose admission copy changed')
        return True
    def check(self):
        self.transport_owner.check()
        if sys.modules.get(self.module.__name__)is not self.module or self.module.Member is not self.member or _raw(self.member.replySetChooseTreasure)is not self.wrapper:raise RuntimeError('Wish Member generation changed')
        if self.business_wrapper is not None and _raw(self.member.setChooseTreasure)is not self.business_wrapper:raise RuntimeError('Wish choose admission changed')
        # Read only an already materialized class: never import ClientAvatar here.
        module=sys.modules.get('entity.ClientAvatar');avatar_cls=getattr(module,'ClientAvatar',None)
        if avatar_cls is not None:self._check_avatar_copy(avatar_cls)
        return self
    def transport(self,avatar):
        self.check();return self.transport_owner.transport(avatar)
    def check_avatar(self,avatar_cls=None):
        self.check()
        if avatar_cls is None:
            module=sys.modules.get('entity.ClientAvatar');avatar_cls=getattr(module,'ClientAvatar',None)
        return self._check_avatar_copy(avatar_cls)
    def choose(self,scope,_type,item_id):
        self.check();scope.live()
        if _type!=5 or scope.t!=5:raise RuntimeError('Wish choose outside admitted scope')
        scope.state.resources(5,choose=True)
        channel=self.transport(scope.avatar)
        if channel is None:raise RuntimeError('Wish transport unavailable')
        old=self.pending
        if old is not None:
            if old.channel is channel:raise RuntimeError('Wish choose result still pending')
            # A different accepted transport has already rejected old packets before
            # entity lookup; no same-connection timeout/reset permits this clear.
            old.lease.unlock('setChooseTreasure');self.pending=None
        p=_ChoosePending(scope,channel);self.pending=p
        aliases=scope.aliases(_globals(self.original_choose));aliases['gg']=_View(self.gg,ui=p.lease,avatar=_Avatar(scope))
        try:return _clone(self.original_choose,aliases,self.gg)(_SendingAvatar(p),_type,item_id)
        finally:
            if not p.sent:
                p.lease.unlock('setChooseTreasure')
                if self.pending is p:self.pending=None
    def reply(self,avatar,ret,_type,info):
        p=self.pending
        if p is None or _type!=5:return None
        if self.transport(avatar)is not p.channel:return None
        # Exactly one logical result after ACK-only duplicate handling. A stale
        # same-connection result drains quarantine but never unlocks current UI.
        self.pending=None
        try:p.scope.live()
        except RuntimeError:
            p.lease.unlock('setChooseTreasure');return None
        aliases={'gg':_View(self.gg,ui=p.lease,avatar=avatar)}
        return _clone(self.original.rpcmethod.func,aliases,self.gg)(avatar,ret,_type,info)

def install_member_guard(transport_owner=None):
    global _EARLY
    if _EARLY is not None:
        if transport_owner is not None and _EARLY.transport_owner is not transport_owner:raise RuntimeError('Wish early reinstall changed')
        return _EARLY.check()
    gg=sys.modules.get('gg')
    if gg is None or getattr(gg,'avatar',None)is not None:raise RuntimeError('Wish early guard precedes Avatar')
    module=__import__('entity.avatar_members.LuckyDrawMember',fromlist=['Member'])
    game_object=__import__('com.base.game_object',fromlist=['members_cache'])
    member=module.Member
    if member in game_object.members_cache:raise RuntimeError('Wish Member already copied')
    if transport_owner is None:
        transport_module=__import__('project7_wish_transport',fromlist=['install']);transport_owner=transport_module.install()
    owner=_MemberOwner(gg,module,member,transport_owner)
    old=owner.original;metadata=getattr(old,'rpcmethod',None)
    if metadata is None or tuple(arg.getname()for arg in metadata.argtypes)!=('r','t','i'):raise RuntimeError('Wish typed schema changed')
    def typed_body(avatar,ret,_type,info):return owner.reply(avatar,ret,_type,info)
    wrapper=module.rpc_method(metadata.rpctype,metadata.argtypes,metadata.pub)(typed_body)
    wrapper.__name__=old.__name__;owner.wrapper=wrapper
    def rejected_unscoped(avatar,*args,**kwargs):
        # All audited paid UI routes call the scoped adapter. A foreign raw
        # producer is refused before the original lock or reliable send.
        if avatar is getattr(gg,'avatar',None):gg.ui.panels.common_message.notify_message(1882)
        return None
    rejected_unscoped.__name__=owner.original_choose.__name__
    owner.business_wrapper=rejected_unscoped
    setattr(member,'setChooseTreasure',rejected_unscoped)
    setattr(member,'replySetChooseTreasure',wrapper);_EARLY=owner
    return owner.check()

def install(policy_text,history_avatar_type=None,friend_owner=None,families_owner=None,member_owner=None):
    policy=_policy(policy_text);gg=sys.modules.get('gg')
    if gg is None or any(x is None for x in(history_avatar_type,friend_owner,families_owner,member_owner)):raise RuntimeError('Wish companions and early guard required')
    modules=[__import__(name,fromlist=[attribute])for name,attribute in _TARGETS];classes=[getattr(m,a)for m,(_,a)in zip(modules,_TARGETS)]
    prior=classes[0].__dict__.get(_MARKER)
    if prior is not None:
        if prior.policy!=policy or prior.history_avatar_type is not history_avatar_type or prior.friend_owner is not friend_owner or prior.families_owner is not families_owner or prior.member_owner is not member_owner:raise RuntimeError('Wish reinstall changed')
        prior.current();return prior
    if any(cls.__dict__.get(_MARKER)is not None for cls in classes):raise RuntimeError('Wish partial class generation')
    state=_Installation(modules,classes,gg,policy,history_avatar_type,friend_owner,families_owner,member_owner)
    if families_owner.friend_owner is not friend_owner or families_owner.history_avatar_type is not history_avatar_type or classes[2]is not families_owner.classes[0]:raise RuntimeError('Wish exact companion required')
    for cls,names in zip(classes,_METHODS):
        for name in names:
            if not isinstance(_raw(getattr(cls,name,None)),types.FunctionType):raise RuntimeError('Wish original method ABI changed: '+name)
    member_owner.check();state.apply();families_owner.register_detail_delegate(state,_IDS,state.invoke_detail)
    verified=sorted(set(policy['verified_ids'])&set(policy['detail_ids']))
    if verified:state.draw_owner.register_request_guard(state,verified,state.before_request)
    return state
