# -*- coding: ascii -*-
"""P7 Gate-owned transport generation guard; no wire or entity-id changes.
Install before constructing a Gate. Non-Gate ChannelClients remain original.
"""
import sys
import types
_MARKER='_q7_wish_transport_owner'
_RPC=('seed_reply','session_key_ok','connect_reply','chat_to_client',
      'create_entity','entity_message','destroy_entity','reg_md5_index')
def _raw(fn):return getattr(fn,'im_func',getattr(fn,'__func__',fn))
class _ConnectView(object):
    def __init__(self,source,check):
        object.__setattr__(self,'source',source);object.__setattr__(self,'check',check)
    def __getattr__(self,name):
        return self.check if name=='_check_connection' else getattr(self.source,name)
    def __setattr__(self,name,value):setattr(self.source,name,value)
class _Owner(object):
    def __init__(self,gg,modules):
        self.gg,self.modules=gg,modules
        self.classes=(modules[0].GateClient,modules[1].ChannelClient,
                      modules[2].ServerProxy,modules[2].CachedServerProxy)
        self.records=[]
    def check(self):
        if sys.modules.get('gg') is not self.gg:raise RuntimeError('Wish transport gg changed')
        for module,cls,name in ((self.modules[0],self.classes[0],'GateClient'),
                               (self.modules[1],self.classes[1],'ChannelClient'),
                               (self.modules[2],self.classes[2],'ServerProxy'),
                               (self.modules[2],self.classes[3],'CachedServerProxy')):
            if sys.modules.get(module.__name__) is not module or getattr(module,name,None)is not cls:raise RuntimeError('Wish transport module changed')
        if self.modules[0].ChannelClient is not self.classes[1]or self.modules[0].ServerProxy is not self.classes[2]or self.modules[0].CachedServerProxy is not self.classes[3]:raise RuntimeError('Wish transport import aliases changed')
        for cls,name,wrapper in self.records:
            if _raw(getattr(cls,name,None))is not wrapper:raise RuntimeError('Wish transport wrapper changed')
        return self
    def current_gate(self,gate):
        return getattr(getattr(self.gg,'logic',None),'gate_client',None)is gate
    def channel(self,gate):
        return getattr(gate,'_q7_wish_channel',None)if self.current_gate(gate)else None
    def transport(self,avatar):
        self.check();gate=getattr(getattr(self.gg,'logic',None),'gate_client',None)
        channel=self.channel(gate)if gate is not None else None
        if avatar is not getattr(self.gg,'avatar',None)or channel is None:return None
        server=getattr(avatar,'server',None)
        return channel if getattr(getattr(server,'stub',None),'rpc_channel',None)is channel else None
    def invalidate(self,gate):
        gate._q7_wish_channel=None
        gate._q7_wish_retiring=None
        client=getattr(gate,'client',None)
        if client is not None:client._q7_wish_attempt=None
    def owned(self,client):
        gate=getattr(client,'rpc_service',None)
        return gate if type(gate)is self.classes[0]and getattr(gate,'client',None)is client else None
    def wrap(self,cls,name,body):
        original=_raw(getattr(cls,name))
        if not isinstance(original,types.FunctionType):raise RuntimeError('Wish transport original ABI changed')
        def wrapper(instance,*args,**kwargs):return body(original,instance,args,kwargs)
        wrapper.__name__=original.__name__;wrapper.__dict__.update(getattr(original,'__dict__',{}))
        setattr(cls,name,wrapper);self.records.append((cls,name,wrapper))
    def apply(self):
        gate,client,proxy,cached=self.classes;state=self
        def invalidate(original,instance,args,kwargs):
            state.invalidate(instance);return original(instance,*args,**kwargs)
        for name in ('start_game','resume_game','disconnect','reset'):self.wrap(gate,name,invalidate)
        def reset(original,instance,args,kwargs):
            owner=state.owned(instance)
            if owner is not None:state.invalidate(owner)
            return original(instance,*args,**kwargs)
        self.wrap(client,'reset',reset)
        def connect(original,instance,args,kwargs):
            owner=state.owned(instance)
            if owner is None:return original(instance,*args,**kwargs)
            if not state.current_gate(owner):return None
            state.invalidate(owner)
            token=object();instance._q7_wish_attempt=token;tcp=instance.client
            callback=args[0]if args else kwargs['callback']
            def live():return state.current_gate(owner)and instance._q7_wish_attempt is token and instance.client is tcp
            def delivered(channel):
                if not live():return None
                try:return callback(channel)
                finally:
                    if channel is None and instance._q7_wish_attempt is token:state.invalidate(owner)
            def check():
                if live():return state.original_check(instance)
            values=list(args);options=dict(kwargs)
            if values:values[0]=delivered
            else:options['callback']=delivered
            return original(_ConnectView(instance,check),*values,**options)
        self.original_check=_raw(getattr(client,'_check_connection'));self.wrap(client,'connect',connect)
        def tcp_callback(original,instance,args,kwargs):
            owner=state.owned(instance)
            if owner is None:return original(instance,*args,**kwargs)
            con=args[0]if args else kwargs['con']
            if not state.current_gate(owner)or con is not instance.client or getattr(instance,'_q7_wish_attempt',None)is None:return None
            return original(instance,*args,**kwargs)
        for name in ('handle_new_connection','handle_connection_failed'):self.wrap(client,name,tcp_callback)
        def channel_cb(original,instance,args,kwargs):
            channel=args[0]if args else kwargs.get('rpc_channel')
            if not state.current_gate(instance)or getattr(instance.client,'_q7_wish_attempt',None)is None:return None
            if channel is not None and getattr(channel,'conn',None)is not instance.client.client:return None
            instance._q7_wish_channel=channel
            return original(instance,*args,**kwargs)
        self.wrap(gate,'channel_cb',channel_cb)
        def rpc(original,instance,args,kwargs):
            controller=args[0]if args else kwargs.get('_controller')
            channel=state.channel(instance)
            if channel is None or getattr(controller,'rpc_channel',None)is not channel:return None
            return original(instance,*args,**kwargs)
        for name in _RPC:self.wrap(gate,name,rpc)
        def disconnected(original,instance,args,kwargs):
            channel=args[0]if args else kwargs.get('rpc_channel')
            if channel is not state.channel(instance)or channel is None:return None
            state.invalidate(instance);instance._q7_wish_retiring=channel
            return original(instance,*args,**kwargs)
        self.wrap(gate,'on_channel_disconnected',disconnected)
        def proxy_disconnect(original,instance,args,kwargs):
            channel=args[0]if args else kwargs.get('_rpc_channel')
            stub=getattr(instance,'stub',None);owner=getattr(instance,'owner',None)
            # An old channel listener must never clear a replacement stub/owner.
            if channel is not getattr(stub,'rpc_channel',None):return None
            if owner is None or getattr(owner,'server',None)is not instance:return None
            gate=getattr(getattr(state.gg,'logic',None),'gate_client',None)
            if not state.current_gate(gate)or (state.channel(gate)is not channel and getattr(gate,'_q7_wish_retiring',None)is not channel):return None
            return original(instance,*args,**kwargs)
        for cls in (proxy,cached):self.wrap(cls,'on_channel_disconnected',proxy_disconnect)
        for cls in self.classes:setattr(cls,_MARKER,self)
        return self

def install(gate_module=None,channel_module=None,proxy_module=None):
    gg=sys.modules.get('gg')
    if gg is None:raise RuntimeError('Wish transport gg required')
    modules=(gate_module or __import__('client.GateClient',fromlist=['GateClient']),
             channel_module or __import__('mobilerpc.ChannelClient',fromlist=['ChannelClient']),
             proxy_module or __import__('client.ServerProxy',fromlist=['ServerProxy']))
    cls=modules[0].GateClient;prior=cls.__dict__.get(_MARKER)
    if prior is not None:
        if prior.modules!=modules:raise RuntimeError('Wish transport reinstall changed')
        return prior.check()
    if getattr(gg,'avatar',None)is not None or getattr(getattr(gg,'logic',None),'gate_client',None)is not None:raise RuntimeError('Wish transport must precede Gate creation')
    classes=(cls,modules[1].ChannelClient,modules[2].ServerProxy,modules[2].CachedServerProxy)
    if modules[0].ChannelClient is not classes[1]or modules[0].ServerProxy is not classes[2]or modules[0].CachedServerProxy is not classes[3]:raise RuntimeError('Wish transport exact imported classes required')
    if any(c.__dict__.get(_MARKER)is not None for c in classes):raise RuntimeError('Wish transport partial generation')
    required=(('start_game','resume_game','disconnect','reset','channel_cb','on_channel_disconnected')+_RPC,('reset','connect','_check_connection','handle_new_connection','handle_connection_failed'),('on_channel_disconnected',),('on_channel_disconnected',))
    for target,names in zip(classes,required):
        for name in names:
            if not isinstance(_raw(getattr(target,name,None)),types.FunctionType):raise RuntimeError('Wish transport complete original ABI required')
    return _Owner(gg,modules).apply()
