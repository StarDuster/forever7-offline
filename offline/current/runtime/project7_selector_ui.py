# -*- coding: ascii -*-
"""Scoped fixed640 history selector UI; original choice RPC and data owner.
No disk/network/game clock/probability changes. Install before login/panels.
"""
import sys
import types
import json
import hashlib
import calendar
_TARGET='entity.ClientAvatar'
_TAB='cocos.panels.card_tab'
_CHOOSER='cocos.panels.card_hero_choose'
_DATA='entity.avatar_attrs.LuckyDrawData'
_MARKER='_q7_selector_ui_owner'
_POLICY_SHA='56fa68017308f2114bda9d63eb769428cba0eefd4290bd515dd801d1810b84dc'
try:
    _TEXT=(basestring,)
except NameError:
    _TEXT=(str,bytes)

def _pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out:raise ValueError('Duplicate selector policy key')
        out[k]=v
    return out

def _policy(text):
    if not isinstance(text,_TEXT):raise ValueError('Embedded selector policy required')
    data=json.loads(text,object_pairs_hook=_pairs)
    canonical=json.dumps(data,sort_keys=True,separators=(',',':')).encode('ascii')
    if hashlib.sha256(canonical).hexdigest()!=_POLICY_SHA:raise ValueError('Selector policy changed')
    return data

def _raw(fn):
    return getattr(fn, 'im_func', getattr(fn, '__func__', fn))


def _globals(fn):
    return getattr(fn, 'func_globals', getattr(fn, '__globals__', {}))


def _cell(value):
    def captured():
        return value
    return getattr(captured, 'func_closure', getattr(captured, '__closure__', None))[0]


def _clone(original, aliases, gg):
    namespace = dict(_globals(original))
    namespace.update(aliases)
    code = getattr(original, 'func_code', getattr(original, '__code__', None))
    closure = getattr(original, 'func_closure', getattr(original, '__closure__', None))
    if closure:
        cells = list(closure)
        for index, name in enumerate(code.co_freevars):
            value = cells[index].cell_contents
            if name in ('func', 'f') and isinstance(value, types.FunctionType):
                if _globals(value).get('gg') is not gg:
                    raise RuntimeError('Selector decorated body has stale gg')
                cells[index] = _cell(_clone(value, aliases, gg))
        closure = tuple(cells)
    defaults = getattr(original, 'func_defaults', getattr(original, '__defaults__', None))
    return types.FunctionType(code, namespace, original.__name__, defaults, closure)


class _CleanupGG(object):
    def __init__(self, source, ui):
        self._source, self.ui = source, ui

    def __getattr__(self, name):
        return getattr(self._source, name)


class _RequestLease(object):
    """One original UI lock count, bound to its UI and reset generation."""
    def __init__(self, state, key):
        self.state, self.ui, self.key = state, state.gg.ui, key
        self.epoch = self.ui._lock
        self.mapping, self.claimed, self.released = None, False, False
        self.show_panel = True
        self.wait = None
        self.exec_cancel = getattr(state.gg, 'exec_cancel', None)
        self.unlock_body = _raw(self.ui.unlock)
        if not isinstance(getattr(self.ui, '_lock', None), dict):
            raise RuntimeError('Selector original UI lock ABI changed')
        if not isinstance(self.unlock_body, types.FunctionType):
            raise RuntimeError('Selector original UI unlock ABI changed')

    def claim(self, key, show_panel=True):
        if key != self.key or self.claimed or self.released or self.ui._lock is not self.epoch:
            raise RuntimeError('Selector request lock scope changed')
        self.mapping = self.ui._lock
        self.show_panel = show_panel
        before = self.mapping.get(key, 0)
        self.wait = self.ui.panels.wait
        try:
            return self.ui.lock(key, show_panel)
        finally:
            self.claimed = self.mapping.get(key, 0) > before

    def retire_wait(self):
        # UIPanel.destroy uses current gg.ui even for an old wait instance.
        # Cancel only the captured old scheduler handles; never call destroy.
        wait = self.wait
        if wait is None:
            return None
        for name in ('show_desc_timer', 'disconnect_timer'):
            handle = getattr(wait, name, None)
            if handle:
                if not callable(self.exec_cancel):
                    raise RuntimeError('Selector original wait scheduler changed')
                self.exec_cancel(handle)
                setattr(wait, name, None)
        node = getattr(wait, '_node', None)
        if node is not None and getattr(wait, 'valid', False):
            node.setVisible(False)
        return None

    def release(self, key=None):
        if key is not None and key != self.key:
            raise RuntimeError('Selector cleanup lock scope changed')
        if self.released:
            return None
        self.released = True
        if not self.claimed:
            return None
        if sys.modules.get('gg') is not self.state.gg or self.state.gg.ui is not self.ui:
            return self.retire_wait()
        if self.ui._lock is not self.mapping or self.mapping.get(self.key, 0) <= 0:
            return None
        # Original unlock's gg.ui.panels.wait must also stay on the old UI.
        return _clone(self.unlock_body, {'gg': _CleanupGG(self.state.gg, self.ui)}, self.state.gg)(
            self.ui, self.key, self.show_panel)


class _RequestUI(object):
    def __init__(self, gg, lease):
        self.gg, self.lease = gg, lease

    def live(self):
        current = self.gg.live()
        if current.ui is not self.lease.ui:
            raise RuntimeError('Selector request UI generation changed')
        return current

    def lock(self, key='default', show_panel=True):
        self.live()
        return self.lease.claim(key, show_panel)

    def unlock(self, key='default', show_panel=True):
        return self.lease.release(key)

    def __getattr__(self, name):
        self.live()
        return getattr(self.lease.ui, name)




class _EpochTime(object):
    """Canonicalize one fixed source end_time; never replace the game clock."""
    timezone=0
    def __init__(self,source,end,stamp):self.source,self.end,self.stamp=source,end,stamp
    def mktime(self,value):
        if tuple(value)!=self.end:raise RuntimeError('Selector source epoch changed')
        return self.stamp
    def __getattr__(self,name):return getattr(self.source,name)


class _Scope(object):
    def __init__(self,state,t,avatar,origin=None,lease=None):
        self.state,self.t,self._avatar,self._data=state,t,avatar,avatar.luckyDrawData
        self._ui,self._epoch=state.gg.ui,state.gg.ui._lock
        self.origin,self.lease=origin,lease
        self.panel,self.chooser=None,None

    def live(self):
        gg=self.state.current()
        if (gg.avatar is not self._avatar or self._avatar.luckyDrawData is not self._data or
                gg.ui is not self._ui or self._ui._lock is not self._epoch):
            raise RuntimeError('Selector owner/UI generation changed')
        if self.origin is not None:self.origin.live()
        if self.panel is not None:
            if gg.ui.panels is not self._panels:raise RuntimeError('Selector panel manager changed')
            cache=getattr(self._panels,'__dict__',{}).get('_panels')
            if self._cache is not None and cache is not self._cache:raise RuntimeError('Selector panel cache changed')
            for key,mode,target in self._panel_bindings:
                current=cache.get(key) if mode=='cache' else getattr(self._panels,'__dict__',{}).get(key)
                if current is not target:raise RuntimeError('Selector target panel replaced')
            if (not self.panel.valid or not self.chooser.valid or self.panel.draw_type!=self.t or
                    self.state.popups.get(self.chooser) is not self):
                raise RuntimeError('Selector popup/pool generation changed')
        return gg

    def __getattr__(self,name):
        if name=='ui' and self.lease is not None:return _RequestUI(self,self.lease)
        gg=self.live()
        return _Avatar(self) if name=='avatar' else getattr(gg,name)


class _Helpers(object):
    def __init__(self,source,scope):self.source,self.scope=source,scope
    def get_active_uaid(self,rotation):
        self.scope.live()
        raw=_raw(getattr(self.scope._avatar,'validSetChooseHeroes'))
        expected=_globals(raw)['const'].RotationType.SELF_CHOOSE_HERO
        return (None,None) if rotation==expected else self.source.get_active_uaid(rotation)
    def __getattr__(self,name):self.scope.live();return getattr(self.source,name)


class _Transport(object):
    def __init__(self,scope,source):self.scope,self.source=scope,source
    def __getattr__(self,name):
        self.scope.live();original=getattr(self.source,name)
        if name!='call_server_method':return original
        def called(*args,**kwargs):
            self.scope.live()
            try:return original(*args,**kwargs)
            except Exception:
                if self.scope.lease is not None:self.scope.lease.release()
                raise
        return called


class _Avatar(object):
    def __init__(self,scope):object.__setattr__(self,'_scope',scope)
    def __setattr__(self,name,value):self._scope.live();setattr(self._scope._avatar,name,value)
    def __getattr__(self,name):
        scope=self._scope;scope.live()
        if name=='setChooseHeroes':
            def choose(t,heroes):
                scope.live()
                if t!=scope.t:raise RuntimeError('Selector popup pool changed')
                return scope.state.request(scope._avatar,t,heroes,scope)
            return choose
        original=getattr(scope._avatar,name)
        if name=='server':return _Transport(scope,original)
        raw=_raw(original)
        if not isinstance(raw,types.FunctionType) or not (hasattr(original,'im_self') or hasattr(original,'__self__')):return original
        def called(*args,**kwargs):
            scope.live()
            if name=='checkDrawInTime' and args and args[0]==scope.t:return True
            aliases={'gg':scope}
            if name=='validSetChooseHeroes':aliases['helpers']=_Helpers(_globals(raw)['helpers'],scope)
            return _clone(raw,aliases,scope.state.gg)(self,*args,**kwargs)
        return called


class _Logic(object):
    def __init__(self,source,scope):self.source,self.scope=source,scope
    def get_select_heroes(self,panel):
        self.scope.live()
        if panel is not self.scope.chooser:raise RuntimeError('Selector chooser changed')
        rank=panel.choose_order[panel.curr_idx]
        if rank not in (3,4):raise RuntimeError('Selector rank changed')
        return list(self.scope.state.policy['s' if rank==4 else 'a'])
    def __getattr__(self,name):
        self.scope.live();original=getattr(self.source,name);raw=_raw(original)
        if not isinstance(raw,types.FunctionType):return original
        def called(*args,**kwargs):
            self.scope.live()
            return _clone(raw,{'gg':self.scope},self.scope.state.gg)(self,*args,**kwargs)
        return called


class _Config(object):
    def __init__(self,source,scope):self.source,self.scope=source,scope
    def get_main_config(self,panel):self.scope.live();return self.source.get_main_config(panel)
    def get_choose_config(self,panel):
        self.scope.live();result=dict(self.source.get_choose_config(panel))
        result['text']=tuple((path,text+u'\n\u79bb\u7ebf\u56fa\u5b9a640\u5019\u9009' if path=='popup.text' else text) for path,text in result.get('text',()))
        return result
    def __getattr__(self,name):return getattr(self.source,name)


class _Panel(object):
    def __init__(self,source,scope):self.source,self.scope=source,scope
    def __getattr__(self,name):
        self.scope.live()
        if name=='draw_type':return self.scope.t
        original=getattr(self.source,name)
        if name!='proc_event':return original
        def event(*args,**kwargs):
            self.scope.live()
            if args and args[0]=='show':
                kwargs=dict(kwargs);chooser=self.scope.chooser
                logic=self.scope.state.chooser_module.UILogic
                config=self.scope.state.chooser_module.UIConfig
                kwargs['ui_logic']=_Logic(logic,self.scope)
                kwargs['ui_config']=_Config(config,self.scope)
            return original(*args,**kwargs)
        return event


class _Installation(object):
    def __init__(self,gg,modules,classes,policy,history_avatar_type,originals):
        self.gg,self.modules,self.classes,self.policy=gg,modules,classes,policy
        self.history_avatar_type,self.originals=history_avatar_type,originals
        self.chooser_module=modules[2]
        self.records=[];self.popups={};self.pending=[]

    def current(self):
        if sys.modules.get('gg') is not self.gg:raise RuntimeError('Selector gg generation changed')
        for name,module,attribute,cls in zip((_TARGET,_TAB,_CHOOSER,_DATA),self.modules,('ClientAvatar','Panel','Panel','LuckyDrawData'),self.classes):
            if sys.modules.get(name) is not module or getattr(module,attribute) is not cls or cls.__dict__.get(_MARKER) is not self:raise RuntimeError('Selector class generation changed')
        for cls,name,fn in self.records:
            if cls.__dict__.get(name) is not fn:raise RuntimeError('Selector installed method changed')
        return self.gg

    def normalize(self,avatar):
        gg=self.current()
        if avatar is gg.avatar:return avatar
        owner=self.classes[1].__dict__.get('_q7_draw_ui_owner');values=getattr(avatar,'__dict__',{})
        if (self.history_avatar_type is None or type(avatar) is not self.history_avatar_type or owner is None or
                values.get('_state') is not owner or values.get('_source') is not gg.avatar or owner.current() is not gg):raise RuntimeError('Selector avatar changed')
        return gg.avatar

    def request(self,avatar,t,heroes,origin=None):
        avatar=self.normalize(avatar)
        if t not in self.policy['ready_ids']:return self.originals['setChooseHeroes'](avatar,t,heroes)
        lease=_RequestLease(self,'setChooseHero');scope=_Scope(self,t,avatar,origin,lease)
        self.pending.append(scope)
        try:return _clone(self.originals['setChooseHeroes'],{'gg':scope},self.gg)(_Avatar(scope),t,heroes)
        except Exception:
            lease.release()
            raise
        finally:
            if not lease.claimed and scope in self.pending:self.pending.remove(scope)

    def reply(self,avatar,parameters):
        t=parameters.get('t') if isinstance(parameters,dict) else None
        if type(t) not in (int,) or t not in self.policy['ready_ids']:
            if any(s._avatar is avatar for s in self.pending) and type(t) not in (int,):return None
            return self.originals['replySetChooseHeroes'](avatar,parameters)
        scope=next((s for s in self.pending if s._avatar is avatar and s.t==t),None)
        if scope is None:return None
        meta=self.originals['replySetChooseHeroes'].rpcmethod
        def deliver(actor,ret,pool,heroes):
            if scope in self.pending:self.pending.remove(scope)
            scope.lease.release()
            try:scope.live()
            except RuntimeError:return None
            return _clone(meta.func,{'gg':scope},self.gg)(actor,ret,pool,heroes)
        # Same original argument schema/conversion. No callback is invented;
        # this family is completed by the typed reply's own unlock contract.
        rpc=type(meta)(deliver,meta.rpctype,meta.argtypes,meta.pub)
        return rpc.call(avatar,None,parameters)

    def open(self,panel,args,kwargs):
        gg=self.current();t=panel.draw_type
        if t not in self.policy['ready_ids']:return self.originals['on_open_choose_click'](panel,*args,**kwargs)
        prior=panel.__dict__.get('_q7_selector_generation')
        if (prior is None or not panel.valid or prior[0] is not gg.avatar or prior[1] is not gg.avatar.luckyDrawData or prior[2] is not gg.ui):raise RuntimeError('Selector origin panel changed')
        scope=_Scope(self,t,gg.avatar);scope.panel=panel;scope.chooser=gg.ui.panels.card_hero_choose
        scope._panels=gg.ui.panels;scope._cache=getattr(scope._panels,'__dict__',{}).get('_panels')
        scope._panel_bindings=[]
        for key,target in (('card_tab',panel),('card_hero_choose',scope.chooser)):
            if isinstance(scope._cache,dict) and scope._cache.get(key) is target:mode='cache'
            elif getattr(scope._panels,'__dict__',{}).get(key) is target:mode='attribute'
            else:raise RuntimeError('Selector stable panel binding missing')
            scope._panel_bindings.append((key,mode,target))
        self.popups[scope.chooser]=scope
        return _clone(self.originals['on_open_choose_click'],{'gg':scope},gg)(_Panel(panel,scope),*args,**kwargs)

    def restore_callbacks(self,panel):
        for name,wrapped,original in panel.__dict__.pop('_q7_selector_callbacks',[]):
            if panel.__dict__.get(name) is not wrapped:raise RuntimeError('Selector popup callback changed')
            setattr(panel,name,original)

    def popup_callbacks(self,panel,scope):
        self.restore_callbacks(panel);records=[]
        for name in ('on_close_click','on_btn_click'):
            original=getattr(panel,name);raw=_raw(original)
            if not isinstance(raw,types.FunctionType):raise RuntimeError('Selector popup callback ABI changed')
            def make(raw):
                def called(*args,**kwargs):
                    scope.live()
                    return _clone(raw,{'gg':scope},self.gg)(panel,*args,**kwargs)
                return called
            wrapped=make(raw);setattr(panel,name,wrapped);records.append((name,wrapped,original))
        panel._q7_selector_callbacks=records

    def show(self,panel,args,kwargs):
        logic=kwargs.get('ui_logic')
        if isinstance(logic,_Logic):
            logic.scope.live()
            if logic.scope.state is not self or logic.scope.chooser is not panel:raise RuntimeError('Selector popup owner changed')
            self.popup_callbacks(panel,logic.scope)
        else:
            self.popups.pop(panel,None)
            self.restore_callbacks(panel)
            if isinstance(getattr(panel,'ui_logic',None),_Logic):panel.ui_logic=panel.ui_logic.source
            if isinstance(getattr(panel,'ui_config',None),_Config):panel.ui_config=panel.ui_config.source
        return self.originals['notify_show'](panel,*args,**kwargs)

    def close(self,panel,args,kwargs):
        scope=self.popups.get(panel)
        if scope is None:return self.originals['notify_close'](panel,*args,**kwargs)
        try:scope.live()
        except RuntimeError:
            self.popups.pop(panel,None)
            node=getattr(panel,'_node',None)
            if node is not None and getattr(panel,'valid',False):node.setVisible(False)
            return None
        self.popups.pop(panel,None)
        self.restore_callbacks(panel)
        if isinstance(getattr(panel,'ui_logic',None),_Logic):panel.ui_logic=panel.ui_logic.source
        if isinstance(getattr(panel,'ui_config',None),_Config):panel.ui_config=panel.ui_config.source
        return self.originals['notify_close'](panel,*args,**kwargs)

    def bind(self,cls,name,fn):
        original=getattr(cls,name);fn.__dict__.update(getattr(original,'__dict__',{}));fn.__name__=original.__name__
        setattr(cls,name,fn);self.records.append((cls,name,fn))

    def apply(self):
        state=self;avatar,tab,chooser,data_cls=self.classes
        def setter(actor,t,heroes):return state.request(actor,t,heroes)
        def reply(actor,parameters):return state.reply(actor,parameters)
        def init(panel,*args,**kwargs):
            gg=state.current();prior=panel.__dict__.get('_q7_selector_generation');generation=(gg.avatar,gg.avatar.luckyDrawData,gg.ui)
            if prior is not None and any(a is not b for a,b in zip(prior,generation)):raise RuntimeError('Selector origin initialization changed')
            panel._q7_selector_generation=generation
            return state.originals['on_init'](panel,*args,**kwargs)
        def opened(panel,*args,**kwargs):return state.open(panel,args,kwargs)
        def shown(panel,*args,**kwargs):return state.show(panel,args,kwargs)
        def closed(panel,*args,**kwargs):return state.close(panel,args,kwargs)
        def getter(data,t,check=False):
            original=state.originals['getChooseHeroes']
            if not check or t not in state.policy['ready_ids']:return original(data,t,check)
            state.current()
            namespace=_globals(original)
            clock=_EpochTime(namespace['time'],state.ends[t],state.policy['epochs'][str(t)])
            return _clone(original,{'time':clock},state.gg)(data,t,check)
        for cls,name,fn in ((data_cls,'getChooseHeroes',getter),(avatar,'setChooseHeroes',setter),(avatar,'replySetChooseHeroes',reply),(tab,'on_init',init),(tab,'on_open_choose_click',opened),(chooser,'notify_show',shown),(chooser,'notify_close',closed)):self.bind(cls,name,fn)
        # Native dispatch may invoke rpcmethod.call directly instead of the
        # Python outer wrapper. Preserve its schema, but bind a fresh typed
        # body to the same owner/lease dispatch (never the old raw body).
        meta=self.originals['replySetChooseHeroes'].rpcmethod
        def typed_reply(actor,ret,pool,heroes):
            return state.reply(actor,{'r':ret,'t':pool,'h':heroes})
        reply.rpcmethod=type(meta)(typed_reply,meta.rpctype,meta.argtypes,meta.pub)
        for cls in self.classes:setattr(cls,_MARKER,self)
        return self


def install(policy_text,history_avatar_type=None):
    policy=_policy(policy_text);gg=__import__('gg')
    modules=[__import__(name,fromlist=[attribute]) for name,attribute in ((_TARGET,'ClientAvatar'),(_TAB,'Panel'),(_CHOOSER,'Panel'),(_DATA,'LuckyDrawData'))]
    classes=[getattr(m,a) for m,a in zip(modules,('ClientAvatar','Panel','Panel','LuckyDrawData'))]
    owners=[cls.__dict__.get(_MARKER) for cls in classes]
    if any(owner is not None for owner in owners):
        if owners[0] is None or any(o is not owners[0] for o in owners) or owners[0].policy!=policy or owners[0].history_avatar_type is not history_avatar_type:raise RuntimeError('Selector mixed installation')
        return owners[0].current() and owners[0]
    if getattr(gg,'avatar',None) is not None:raise RuntimeError('Selector requires pre-login install')
    panels=getattr(getattr(gg,'ui',None),'panels',None)
    if any(n in getattr(panels,'__dict__',{}).get('_panels',{}) for n in ('card_tab','card_hero_choose')):raise RuntimeError('Selector panels already bound')
    originals={}
    for cls,names in ((classes[0],('setChooseHeroes','replySetChooseHeroes')),(classes[1],('on_init','on_open_choose_click')),(classes[2],('notify_show','notify_close')),(classes[3],('getChooseHeroes',))):
        for name in names:
            raw=_raw(getattr(cls,name,None))
            if not isinstance(raw,types.FunctionType) or _globals(raw).get('gg') is not gg:raise RuntimeError('Selector original ABI/globals changed')
            originals[name]=raw
    valid=_raw(getattr(classes[0],'validSetChooseHeroes',None))
    if not isinstance(valid,types.FunctionType) or _globals(valid).get('gg') is not gg:raise RuntimeError('Selector original validation missing')
    namespace=_globals(valid);roster=namespace['HERO_SELF_CHOOSE_INFO'].data;heroes=namespace['HERO_DATA'].data
    for rank,key in ((4,'s'),(3,'a')):
        actual=sorted(h for h,row in roster.items() if row.get('avaliable')==1 and heroes.get(h,{}).get('hero_composite_init_rank')==rank)
        if actual!=policy[key]:raise RuntimeError('Selector client fallback metadata changed')
    meta=getattr(originals['replySetChooseHeroes'],'rpcmethod',None)
    if meta is None or _globals(meta.func).get('gg') is not gg:raise RuntimeError('Selector original typed reply missing')
    namespace=_globals(originals['getChooseHeroes']);table=namespace['CHOUKA_INFO_DATA'].data;ends={}
    for t in policy['ready_ids']:
        end=tuple(table[t]['end_time'])
        if calendar.timegm(end)!=policy['epochs'][str(t)]:raise RuntimeError('Selector source epoch mismatch')
        ends[t]=end
    state=_Installation(gg,modules,classes,policy,history_avatar_type,originals);state.ends=ends
    return state.apply()
