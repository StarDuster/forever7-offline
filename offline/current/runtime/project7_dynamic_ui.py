# -*- coding: ascii -*-
"""Scoped fixed485 detail UI. No clock/table/Data mutation or RPC/grant owner.
Install after friend+selector, before panels/login. Public admission stays Root's.
"""
import sys
import types
import json
import hashlib
_MARKER='_q7_dynamic_ui_owner'
_CLICK_POLICY='single-retained-gesture-fifo-refuse-overlap-v1'
_POLICY_RAW_SHA='d7f7eac49c94cf9bb6f866ffba0e711efed0dce1813d427789b94797d2011889'
_TARGETS=(('cocos.panels.card_box','Panel'),('cocos.panels.card_jiaozhi_2','Panel'),('cocos.comps.card_common.tips','Comp'),('cocos.comps.card_common.leichong_info_2','Comp'),('cocos.comps.card_common.jiaozhi_info','Comp'))
_METHODS=(('on_yingzhuang_wish_click','check_has_leichong'),('on_init','on_load','notify_show','get_detault_tab_index','refresh','refresh_jiaozhi','refresh_leichou','on_btn_jiaozhi_click','on_btn_leichou_click','do_btn_jiaozhi_click','do_btn_leichou_click','on_close_click','on_target_click'),('on_load','set_info','refresh_show_state','update_leichou_visible','update_leichou_info','set_jiaozhi','on_tips_click','on_jiaozhi_click','check_has_leichong'),('on_load','set_info'),('on_load','set_info','on_memorybless'))
try:
    _TEXT=(basestring,)
except NameError:
    _TEXT=(str,bytes)

def _pairs(values):
    out={}
    for k,v in values:
        if k in out:raise ValueError('Duplicate dynamic UI policy key')
        out[k]=v
    return out

def _policy(text):
    if not isinstance(text,_TEXT):raise ValueError('Embedded dynamic UI policy required')
    raw=text.encode('ascii') if not isinstance(text,bytes) else text
    if hashlib.sha256(raw).hexdigest()!=_POLICY_RAW_SHA:raise ValueError('Dynamic UI policy text changed')
    data=json.loads(text,object_pairs_hook=_pairs)
    return data

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
                if _globals(value).get('gg',gg) is not gg:raise RuntimeError('Dynamic decorated gg changed')
                cells[i]=_cell(_clone(value,aliases,gg))
        closure=tuple(cells)
    return types.FunctionType(code,namespace,fn.__name__,getattr(fn,'func_defaults',getattr(fn,'__defaults__',None)),closure)

class _View(object):
    def __init__(self,source,**aliases):self._source=source;self.__dict__.update(aliases)
    def __getattr__(self,name):return getattr(self._source,name)

class _Rows(object):
    """Copy-on-read fixed rows; unrelated source rows stay delegated."""
    def __init__(self,source,owned,kind):self.source,self.owned,self.kind=source,owned,kind
    def get(self,key,default=None):
        if key in self.owned:return _copy(self.owned[key])
        value=self.source.get(key,default)
        if self.kind=='charge' and isinstance(value,dict) and value.get('drawType')==485:return default
        return value
    def keys(self):
        keys=[k for k in self.source.keys() if k not in self.owned and not(self.kind=='charge' and isinstance(self.source.get(k),dict) and self.source.get(k).get('drawType')==485)]
        return keys+list(self.owned.keys())
    def __getitem__(self,key):
        marker=object();value=self.get(key,marker)
        if value is marker:raise KeyError(key)
        return value
    def __iter__(self):return iter(self.keys())
    def __len__(self):return len(self.keys())
    def items(self):return [(k,self[k]) for k in self.keys()]
    def iteritems(self):return iter(self.items())
    def values(self):return [v for k,v in self.items()]
    def iterkeys(self):return iter(self.keys())
    def itervalues(self):return iter(self.values())

def _copy(value):
    if isinstance(value,dict):return dict((k,_copy(v)) for k,v in value.items())
    if isinstance(value,(list,tuple)):return tuple(_copy(v) for v in value)
    return value

class _ClickLease(object):
    """Original checkMultiClick retain ownership, not a new UI/RPC lock."""
    def __init__(self,scope,sender):self.scope,self.ui,self.sender,self.panel=scope,scope.ui,sender,scope.instance;self.released=False;self.retained=True
    def release_owned(self):
        if getattr(self.ui,'_q7_dynamic_click_lease',None) is None:self.ui._q7_dynamic_click_lease=self;self.release()
    def release(self):
        if self.released:return
        self.released=True
        if getattr(self.ui,'_q7_dynamic_click_lease',None) is not self:return
        self.ui._q7_dynamic_click_lease=None
        if self.retained and getattr(self.ui,'cur_sender',None) is self.sender and getattr(self.ui,'cur_panel',None) is self.panel:
            self.ui.multi_click=0;self.ui.cur_sender=None;self.ui.cur_panel=None
            self.sender.release()

class _Avatar(object):
    def __init__(self,scope):self.scope=scope
    def __getattr__(self,name):
        scope=self.scope;scope.live()
        original=getattr(scope.avatar,name)
        if name=='checkJiaozhiInTime':
            def checked(key):
                scope.live()
                if isinstance(key,tuple) and key in scope.state.jiaozhi:return True
                return original(key)
            return checked
        if name=='getChoukaInfoDataByType':
            def info(t):
                scope.live()
                return _copy(scope.state.policy['info']) if t==485 else original(t)
            return info
        if callable(original):
            def checked(*args,**kwargs):scope.live();return original(*args,**kwargs)
            return checked
        return original

class _GG(object):
    def __init__(self,scope,cleanup=False):self.scope=scope;self.cleanup=cleanup;self.avatar=_Avatar(scope)
    def __getattr__(self,name):self.scope.live(admission=not self.cleanup);return getattr(self.scope.state.gg,name)

class _Scope(object):
    def __init__(self,state,instance,panel):
        gg=state.current();self.state,self.instance,self.panel=state,instance,panel
        self.avatar,self.data,self.ui=gg.avatar,gg.avatar.luckyDrawData,gg.ui
        self.epoch=self.ui._lock;self.node=getattr(instance,'_node',None);self.panels=self.ui.panels
        self.binding=state.binding(panel);self.show=object();self.tables=[]
        self.init_token=getattr(instance,'_q7_dynamic_init_token',None);self.parent_token=getattr(panel,'_q7_dynamic_init_token',None);self.parent_events=getattr(panel,'event_handlers',None);self.parent_node=getattr(panel,'_node',None)
        self.parent_scope=panel.__dict__.get('_q7_dynamic_scope') if type(panel) is state.classes[1] and instance is not panel else None
        self.parent_tab=getattr(panel,'curr_tab_index',None) if type(instance) is state.classes[4] else None
        if not isinstance(self.epoch,dict):raise RuntimeError('Dynamic UI lock ABI changed')
    def live(self,check_type=True,admission=True):
        gg=self.state.current()
        if gg.avatar is not self.avatar or self.avatar.luckyDrawData is not self.data or gg.ui is not self.ui or self.ui._lock is not self.epoch or self.ui.panels is not self.panels:raise RuntimeError('Dynamic UI owner generation changed')
        self.state.generation(self.panel)
        if (getattr(self.instance,'_q7_dynamic_init_token',None) is not self.init_token or getattr(self.panel,'_q7_dynamic_init_token',None) is not self.parent_token or getattr(self.panel,'event_handlers',None) is not self.parent_events or getattr(self.panel,'_node',None) is not self.parent_node):raise RuntimeError('Dynamic panel reinitialized')
        if not getattr(self.instance,'valid',False) or not getattr(self.panel,'valid',False) or getattr(self.instance,'_node',None) is not self.node or self.state.binding(self.panel)!=self.binding:raise RuntimeError('Dynamic panel replaced')
        if self.instance.__dict__.get('_q7_dynamic_scope') is not self:raise RuntimeError('Dynamic show generation changed')
        if check_type and (self.state.draw_type(self.instance)!=485 or self.state.draw_type(self.panel)!=485):raise RuntimeError('Dynamic pool changed')
        if self.instance is not self.panel and type(self.panel) is self.state.classes[1] and self.panel.__dict__.get('_q7_dynamic_scope') is not self.parent_scope:raise RuntimeError('Dynamic parent show changed')
        if self.parent_tab is not None and getattr(self.panel,'curr_tab_index',None)!=self.parent_tab:raise RuntimeError('Dynamic component page changed')
        if type(self.instance) is self.state.classes[2] and getattr(self.panel,'draw_tips',None) is not self.instance:raise RuntimeError('Dynamic tips component replaced')
        if admission and not self.state.draw_owner.allowed(485):raise RuntimeError('Dynamic entry not admitted')
        for table,source,token in self.tables:
            module=getattr(source,'_module',None)
            if (getattr(table,'data',None) is not source or getattr(source,'_rot_id',None)!=token[0] or module is not token[1] or getattr(module,'data',None) is not token[2]):raise RuntimeError('Dynamic table generation changed')
        return gg
    def aliases(self,namespace,cleanup=False):
        self.live(admission=not cleanup);aliases={'gg':_GG(self,cleanup)}
        if cleanup:return aliases
        for key,value in namespace.items():
            if key=='CHOUKA_LEIJI_REWARD_DATA':owned=self.state.charge;kind='charge'
            elif key=='CHOUKA_JIAOZHI_DATA':owned=self.state.jiaozhi;kind='jiaozhi'
            elif key in ('CHOUKA_INFO_DATA','CHOUKA_INFO'):owned={485:self.state.policy['info']};kind='info'
            else:continue
            source=value.data
            if not any(t is value for t,s,token in self.tables):
                if hasattr(source,'_rot_id'):source.get(next(iter(owned)),None) # original lazy read before pinning its rotation identity
                module=getattr(source,'_module',None);self.tables.append((value,source,(getattr(source,'_rot_id',None),module,getattr(module,'data',None))))
            aliases[key]=_View(value,data=_Rows(source,owned,kind))
        return aliases

class _Installation(object):
    def __init__(self,modules,classes,gg,policy,history_avatar_type,friend_owner):
        self.modules,self.classes,self.gg,self.policy=modules,classes,gg,policy
        self.history_avatar_type,self.friend_owner=history_avatar_type,friend_owner
        self.policy_sha256=hashlib.sha256(json.dumps(policy,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode('ascii')).hexdigest()
        self.draw_owner=classes[0].__dict__.get('_q7_draw_ui_owner')
        self.charge=dict((r['id'],r) for r in policy['charge']);self.jiaozhi=dict(((485,r['id']),r) for r in policy['jiaozhi']);self.records=[];self.originals={}
    def current(self):
        if sys.modules.get('gg') is not self.gg or getattr(self.friend_owner,'history_avatar_type',None) is not self.history_avatar_type or self.classes[0].__dict__.get('_q7_friend_ui_owner') is not self.friend_owner or self.classes[0].__dict__.get('_q7_draw_ui_owner') is not self.draw_owner:raise RuntimeError('Dynamic companion owner changed')
        if self.friend_owner.current() is not self.gg or self.draw_owner.current() is not self.gg:raise RuntimeError('Dynamic companion generation changed')
        for module,cls,(name,attr) in zip(self.modules,self.classes,_TARGETS):
            if sys.modules.get(name) is not module or getattr(module,attr) is not cls or cls.__dict__.get(_MARKER) is not self:raise RuntimeError('Dynamic class generation changed')
        canonical=json.dumps(self.policy,ensure_ascii=True,sort_keys=True,separators=(',',':')).encode('ascii')
        if hashlib.sha256(canonical).hexdigest()!=self.policy_sha256:raise RuntimeError('Dynamic policy mutation')
        for cls,name,fn in self.records:
            if _raw(getattr(cls,name)) is not fn:raise RuntimeError('Dynamic method replaced')
        return self.gg
    def generation(self,panel):
        gg=self.current();key='_q7_friend_generation' if type(panel) is self.classes[0] else '_q7_dynamic_generation'
        value=panel.__dict__.get(key)
        if not isinstance(value,tuple) or len(value)!=3 or value[0] is not gg.avatar or value[1] is not gg.avatar.luckyDrawData or value[2] is not gg.ui:raise RuntimeError('Dynamic panel initialization changed')
    def pin(self,instance):
        gg=self.current();generation=(gg.avatar,getattr(gg.avatar,'luckyDrawData',None),gg.ui);prior=instance.__dict__.get('_q7_dynamic_generation')
        if prior is not None and any(a is not b for a,b in zip(prior,generation)):
            if not(prior[0] is None and prior[1] is None) or prior[2] is not gg.ui or instance.__dict__.get('_q7_dynamic_scope') is not None:raise RuntimeError('Dynamic initialization generation changed')
        instance._q7_dynamic_generation=generation
        instance._q7_dynamic_init_token=object()
        instance.__dict__.pop('_q7_dynamic_scope',None)
    def binding(self,panel):
        key='card_box' if type(panel) is self.classes[0] else 'card_jiaozhi_2';manager=self.gg.ui.panels;values=getattr(manager,'__dict__',{});cache=values.get('_panels')
        if isinstance(cache,dict) and cache.get(key) is panel:return ('cache',id(manager),id(cache),id(panel))
        if values.get(key) is panel:return ('attribute',id(manager),id(panel))
        raise RuntimeError('Dynamic panel cache changed')
    def draw_type(self,instance):
        if type(instance) is self.classes[0]:return instance.get_luckyDraw_type()
        if type(instance) is self.classes[1]:return getattr(instance,'draw_type',None)
        return getattr(instance,'_type',None)
    def resources(self):
        module=sys.modules.get('C_file')
        if module is None:module=getattr(sys.modules.get('game3d'),'C_file',None)
        finder=getattr(module,'find_res_file',None)
        if not callable(finder):raise RuntimeError('Dynamic resource lookup unavailable')
        for path in self.policy['required_assets']:
            if not finder(path,''):raise RuntimeError('Dynamic required resource unavailable: '+path)
    def scope(self,instance):
        old=instance.__dict__.get('_q7_dynamic_scope')
        if old is not None:
            if type(instance) is self.classes[0] and getattr(instance,'event_handlers',None) is not old.parent_events:
                self.generation(instance);instance.__dict__.pop('_q7_dynamic_scope',None)
            else:old.live();return old
        panel=instance if type(instance) in self.classes[:2] else instance._panel
        self.generation(panel)
        if type(instance) not in self.classes[:2]:self.generation(instance)
        scope=_Scope(self,instance,panel);instance._q7_dynamic_scope=scope;scope.live();return scope
    def callbacks(self,instance,scope):
        if type(instance) is self.classes[1]:names=(('btn_jiaozhi','on_btn_jiaozhi_click'),('btn_leichou','on_btn_leichou_click'),('btn_close','on_close_click'),('jiaozhi_item_touch','on_target_click'),('leichou_page1_item_touch','on_target_click'))
        elif type(instance) is self.classes[2]:names=(('_node','on_tips_click'),)
        elif type(instance) is self.classes[4]:names=tuple(('brd%d.memorybless'%i,'on_memorybless') for i in range(1,4))
        else:return
        bindings=instance.__dict__.setdefault('_q7_dynamic_callbacks',{})
        for attr,name in names:
            widget=instance[attr] if type(instance) is self.classes[4] else getattr(instance,attr,None)
            if widget is None:continue
            original=getattr(instance,name)
            def make(widget,attr,name,original,scope):
                key=(attr,name);source=self.originals[self.classes.index(type(instance)),name];namespace=_globals(source);cc=namespace.get('cc')
                began=getattr(getattr(cc,'ccui',None),'TOUCH_EVENT_BEGAN',0);ended=(getattr(getattr(cc,'ccui',None),'TOUCH_EVENT_ENDED',2),getattr(getattr(cc,'ccui',None),'TOUCH_EVENT_CANCELED',3))
                decorated=type(instance) is self.classes[1]
                def bind(fn):bindings[key]=fn;widget.addTouchEventListener(fn)
                def alive(fn):return bindings.get(key) is fn
                def entry(*args,**kwargs):
                    if not alive(entry):return None
                    event=args[1] if len(args)>1 else kwargs.get('event');sender=args[0] if args else kwargs.get('sender')
                    if scope is None:
                        old=getattr(self.gg.ui,'_q7_dynamic_click_lease',None)
                        if isinstance(old,_ClickLease) and event in ended:old.release();return None
                        return original(*args,**kwargs)
                    # No BEGIN-owned token exists in an entry callback. Late END
                    # must never be reassigned to a newer same-sender gesture.
                    if event!=began:return None
                    scope.live(admission=name!='on_close_click')
                    # Event enum has no unique touch ID: only a BEGIN-owned,
                    # freshly bound gesture callback may execute END business.
                    old=getattr(scope.ui,'_q7_dynamic_click_lease',None)
                    if isinstance(old,_ClickLease) and not old.released:
                        old.release();return False # ambiguous overlap: cancel, require fresh BEGIN
                    before_sender=getattr(scope.ui,'cur_sender',None);before_count=getattr(scope.ui,'multi_click',0);completed=False
                    try:result=original(*args,**kwargs);completed=True
                    finally:
                        retained=(before_sender is None and before_count==0 and getattr(scope.ui,'cur_sender',None) is sender and getattr(scope.ui,'cur_panel',None) is instance and getattr(scope.ui,'multi_click',0)>0)
                        if retained and not completed:_ClickLease(scope,sender).release_owned()
                    guidance=getattr(getattr(scope.ui.panels,'newbee_guidance',None),'is_begin',False)
                    if decorated and not retained and not guidance:return result
                    lease=_ClickLease(scope,sender);lease.retained=retained;scope.ui._q7_dynamic_click_lease=lease
                    def gesture(*args,**kwargs):
                        event=args[1] if len(args)>1 else kwargs.get('event')
                        if not alive(gesture) or lease.released or getattr(scope.ui,'_q7_dynamic_click_lease',None) is not lease:
                            lease.release();return None
                        if event==began:
                            lease.release();bind(entry);return False # FIFO/refuse overlapping BEGIN
                        completed=False
                        try:scope.live(admission=name!='on_close_click');result=original(*args,**kwargs);completed=True;return result
                        finally:
                            if event in ended or not completed:
                                lease.release()
                                if alive(gesture):
                                    if getattr(instance,'valid',False) and instance.__dict__.get('_q7_dynamic_scope') is scope:bind(entry)
                                    else:bindings.pop(key,None)
                    bind(gesture);return result
                return entry
            callback=make(widget,attr,name,original,scope);bindings[(attr,name)]=callback;widget.addTouchEventListener(callback)
    def invoke(self,index,name,instance,args,kwargs):
        original=self.originals[index,name]
        if name in ('on_init','on_load'):
            self.pin(instance);return original(instance,*args,**kwargs)
        incoming=args[0] if args and name in ('notify_show','set_info') else self.draw_type(instance)
        if name=='set_info' and index in (3,4):incoming=args[1] if len(args)>1 else kwargs.get('_type')
        if incoming!=485:
            if name in ('notify_show','set_info'):instance.__dict__.pop('_q7_dynamic_scope',None)
            result=original(instance,*args,**kwargs)
            if name in ('notify_show','set_info') and index in (1,2,4):self.callbacks(instance,None)
            return result
        if name in ('notify_show','set_info'):
            self.resources();
            if not self.draw_owner.allowed(485):raise RuntimeError('Dynamic entry not admitted')
            panel=instance if index==1 else instance._panel;self.generation(panel)
            if index>1:self.generation(instance)
            scope=_Scope(self,instance,panel);instance._q7_dynamic_scope=scope
            # Original setter's first action assigns the incoming type.
            if index==1:instance.draw_type=485
            else:instance._type=485
            scope.live()
        else:
            if name=='on_close_click':
                scope=instance.__dict__.get('_q7_dynamic_scope')
                if scope is None:raise RuntimeError('Dynamic close scope missing')
                scope.live(admission=False);result=_clone(original,scope.aliases(_globals(original),cleanup=True),self.gg)(instance,*args,**kwargs)
                event=args[1] if len(args)>1 else kwargs.get('event');ended=getattr(getattr(_globals(original).get('cc'),'ccui',None),'TOUCH_EVENT_ENDED',2)
                if event==ended and instance.__dict__.get('_q7_dynamic_scope') is scope:instance.__dict__.pop('_q7_dynamic_scope',None)
                return result
            scope=self.scope(instance)
        if index==0 and name=='check_has_leichong':return bool(self.charge)
        if index==2 and name=='on_jiaozhi_click':
            # Exact original marshal branch (decompiler ternary is malformed):
            # source has charge -> original card_jiaozhi_2, no custom panel.
            scope.live();layer=instance._panel.add_layer(self.gg.ui.panels.card_jiaozhi_2);return instance._panel.proc_event('show',485,_children=True,_layer=layer)
        result=_clone(original,scope.aliases(_globals(original)),self.gg)(instance,*args,**kwargs)
        scope.live()
        if name in ('notify_show','set_info') and index in (1,2,4):self.callbacks(instance,scope)
        return result
    def apply(self):
        state=self
        for index,names in enumerate(_METHODS):
            cls=self.classes[index]
            for name in names:
                original=_raw(getattr(cls,name));self.originals[index,name]=original
                def make(index,name,original):
                    def wrapped(instance,*args,**kwargs):return state.invoke(index,name,instance,args,kwargs)
                    wrapped.__dict__.update(getattr(original,'__dict__',{}));wrapped.__name__=original.__name__;return wrapped
                wrapped=make(index,name,original);setattr(cls,name,wrapped);self.records.append((cls,name,wrapped))
        for cls in self.classes:setattr(cls,_MARKER,self)
        return self

def install(policy_text,history_avatar_type=None,friend_owner=None):
    policy=_policy(policy_text);gg=sys.modules.get('gg')
    if gg is None or history_avatar_type is None or friend_owner is None:raise RuntimeError('Dynamic companion installation required')
    modules=[__import__(name,fromlist=[attr]) for name,attr in _TARGETS];classes=[getattr(m,attr) for m,(name,attr) in zip(modules,_TARGETS)]
    prior=classes[0].__dict__.get(_MARKER)
    if prior is not None:
        if prior.history_avatar_type is not history_avatar_type or prior.friend_owner is not friend_owner or prior.policy!=policy:raise RuntimeError('Dynamic reinstall changed')
        prior.current();return prior
    if classes[0].__dict__.get('_q7_friend_ui_owner') is not friend_owner or classes[0].__dict__.get('_q7_draw_ui_owner') is None:raise RuntimeError('Dynamic exact companion marker required')
    state=_Installation(modules,classes,gg,policy,history_avatar_type,friend_owner)
    # All targets/schema/owners checked before mutating any class.
    for cls,names in zip(classes,_METHODS):
        if cls.__dict__.get(_MARKER) is not None:raise RuntimeError('Partial dynamic installation')
        for name in names:
            if not isinstance(_raw(getattr(cls,name,None)),types.FunctionType):raise RuntimeError('Dynamic method ABI changed: '+name)
    if friend_owner.current() is not gg or state.draw_owner.current() is not gg:raise RuntimeError('Dynamic companion gg changed')
    if _globals(_raw(state.draw_owner.history_aliases)).get('_HistoryAvatar') is not history_avatar_type:raise RuntimeError('Dynamic exact HistoryAvatar class required')
    if state.draw_owner.policy['asset_sha256']!=policy['base_sha256'] or not set(policy['pools']).issubset(state.draw_owner.history):raise RuntimeError('Dynamic history binding changed')
    return state.apply()
