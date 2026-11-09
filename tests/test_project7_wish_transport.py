"""Bounded original Gate/Channel/Controller/EntityManager bodies, no sockets/game.
Protobuf deserialization, timer scheduling and TCP are explicit inert host seams.
"""
import _paths  # noqa: E402,F401
import ast,importlib.util,struct,sys,types,unittest
from pathlib import Path
from unittest.mock import patch
from tests.test_project7_wish_ui import FIX,ROOT,NS
spec=importlib.util.spec_from_file_location('wish_transport',ROOT/'offline/current/runtime/project7_wish_transport.py');transport=importlib.util.module_from_spec(spec);spec.loader.exec_module(transport)
def original_class(path,name,env):
 text=(ROOT/'analysis/original-py-640'/path).read_text();tree=ast.parse(str(FIX.refactor_string(text,path)))
 cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name==name)
 exec(compile(ast.Module(body=[cls],type_ignores=[]),path+':finite-original','exec'),env)
 return env[name]
def p7_disconnect_original(env):
 # P7 differs from640 only in these two callback constants' class owner.
 # Verify decoded instructions, then make the same bounded source substitution;
 # never execute any original NeoX/Python2 opcode.
 from bytecode27 import read
 from xdis.bytecode import Bytecode
 from xdis.opcodes import opcode_27
 def find(code):
  for value in code.co_consts:
   if hasattr(value,'co_code'):
    if value.co_name=='gate_disconnect':return value
    hit=find(value)
    if hit is not None:return hit
 a=find(read(ROOT/'analysis/project7/scripts/logic/logic_state.marshal'));b=find(read(ROOT/'analysis/android640-scripts/logic/logic_state.marshal'))
 left=[(i.offset,i.opname,i.argval)for i in Bytecode(a,opcode_27)];right=[(i.offset,i.opname,i.argval)for i in Bytecode(b,opcode_27)]
 changes=[(x,y)for x,y in zip(left,right)if x!=y]
 assert len(left)==len(right)and changes==[((82,'LOAD_FAST','gate'),(82,'LOAD_GLOBAL','GateClient')),((85,'LOAD_ATTR','__class__'),(85,'LOAD_ATTR','GateClient')),((107,'LOAD_FAST','gate'),(107,'LOAD_GLOBAL','GateClient')),((110,'LOAD_ATTR','__class__'),(110,'LOAD_ATTR','GateClient'))]
 text=(ROOT/'analysis/original-py-640/logic/logic_state.py').read_text();start=text.index('    def gate_disconnect(');end=text.index('    def ',start+5);text=__import__('textwrap').dedent(text[start:end])
 for name in ('CB_ON_CONNECT_FAILED','CB_ON_CREATE_ENTITY'):text=text.replace('GateClient.GateClient.'+name,'gate.__class__.'+name)
 exec(compile(str(FIX.refactor_string(text+'\n','p7-disconnect-selected-source')),'p7-disconnect-selected-source','exec'),env)
 return env['gate_disconnect']
class Log:
 def __getattr__(self,name):return lambda *args:None
class Tcp:
 def __init__(self,ip,port,owner):self.owner=owner;self.closed=False
 def async_connect(self):pass
 def close(self):self.closed=True
 def getpeername(self):return ('synthetic',1)
 def set_channel_interface_obj(self,channel):self.channel=channel
class Timer:
 def __init__(self):self.events=[]
 def addTimer(self,timeout,cb):
  t=NS(callback=cb,cancelled=False);t.cancel=lambda:setattr(t,'cancelled',True);self.events.append(t);return t
class TransportTests(unittest.TestCase):
 def setUp(self):
  self.timers=Timer();self.log=NS(get_logger=lambda *a:Log());self.gg=types.ModuleType('gg');self.gg.logic=NS(gate_client=None);self.gg.avatar=None
  self.env={'LogManager':self.log}
  self.manager=original_class('lib/common/EntityManager.py','EntityManager',self.env)
  self.rpcenv={'service':NS(RpcController=object,RpcChannel=object),'LogManager':self.log,'unpack':struct.unpack,'MobileRequest':NS(request=lambda:NS(data=b''),request_parser=lambda:None)}
  self.Controller=original_class('lib/mobilerpc/RpcChannel.py','MobileRpcController',self.rpcenv)
  self.RpcChannel=original_class('lib/mobilerpc/RpcChannel.py','MobileRpcChannel',self.rpcenv)
  self.chenv={'LogManager':self.log,'TcpClient':Tcp,'Timer':self.timers,'MobileRpcChannel':self.RpcChannel}
  self.Channel=original_class('lib/mobilerpc/ChannelClient.py','ChannelClient',self.chenv)
  self.decoded=[];self.created=[];self.effects=[]
  class Decoder:
   def decode(inner,value):self.decoded.append(value);return value,False
  class BSON:
   def __init__(inner,value):inner.value=value
   def decode(inner):return inner.value
  class Encoder:
   def addindex(inner,*v):self.effects.append(('index',v))
  self.genv={'client_gate_pb2':NS(IGateClient=object,SessionSeed=lambda:NS()),'LogManager':self.log,'ChannelClient':self.Channel,'Md5OrIndexEncoder':Encoder,'IdManager':NS(bytes2id=lambda i:i),'EntityManager':self.manager,'Md5OrIndexDecoder':Decoder(),'BSON':BSON,'EntityFactory':NS(instance=lambda:NS(create_entity=lambda kind,eid:self.created.append((kind,eid)))),'common_pb2':NS(ConnectServerReply=NS(RECONNECT_SUCCEEDED=2,RECONNECT_FAILED=3))}
  self.Gate=original_class('lib/client/GateClient.py','GateClient',self.genv)
  self.penv={'LogManager':self.log}
  self.Proxy=original_class('lib/client/ServerProxy.py','ServerProxy',self.penv)
  self.penv['MessageCache']=original_class('lib/client/ServerProxy.py','MessageCache',self.penv)
  self.Cached=original_class('lib/client/ServerProxy.py','CachedServerProxy',self.penv)
  self.gm=types.ModuleType('finite.GateClient');self.gm.GateClient=self.Gate
  self.cm=types.ModuleType('finite.ChannelClient');self.cm.ChannelClient=self.Channel
  self.pm=types.ModuleType('finite.ServerProxy');self.pm.ServerProxy=self.Proxy;self.pm.CachedServerProxy=self.Cached;self.gm.ChannelClient=self.Channel;self.gm.ServerProxy=self.Proxy;self.gm.CachedServerProxy=self.Cached
  self.modules=patch.dict(sys.modules,{'gg':self.gg,self.gm.__name__:self.gm,self.cm.__name__:self.cm,self.pm.__name__:self.pm});self.modules.start();self.addCleanup(self.modules.stop)
  self.guard=transport.install(self.gm,self.cm,self.pm)
 def gate(self):
  g=self.Gate('synthetic',1,dict(enforce_encryption=False,loginkeypath='',loginkeycontent='',use_keyczar=False));self.gg.logic.gate_client=g
  # Avoid handshake protobuf transport; success calls original channel_cb body up to this explicit seam.
  self.genv['client_gate_pb2'].IGateService_Stub=lambda channel:NS(rpc_channel=channel)
  g._connect_server=lambda channel:self.effects.append(('connect',channel))
  g.start_game(5);g.client.handle_new_connection(g.client.client)
  return g,g._q7_wish_channel
 def packet(self,gate,channel,name,request):
  # Actual MobileRpcChannel.on_request -> actual MobileRpcController -> Gate method.
  class Request:
   def ParseFromString(self,payload):self.__dict__.update(request.__dict__)
  service=NS(GetDescriptor=lambda:NS(methods=[name]),GetRequestClass=lambda method:Request,CallMethod=lambda method,controller,req,done:getattr(gate,method)(controller,req,done))
  channel.rpc_service=service;channel.rpc_request.data=struct.pack('<H',0)+b'host-seam'
  self.assertTrue(channel.on_request())
 def msg(self,**values):return NS(HasField=lambda n:n=='seq',seq=8,**values)
 def test_old_channel_late_lookup_fixed_eid_has_no_new_entity_effect(self):
  old,oc=self.gate();new,nc=self.gate();entity=NS(reply=lambda value:self.effects.append(('reply',value)))
  self.manager.addentity(7,entity);request=self.msg(id=7,method='reply',parameters={'r':1})
  self.packet(old,oc,'entity_message',request);self.assertEqual(self.decoded,[]);self.assertIsNone(new.received_seq)
  self.packet(new,nc,'entity_message',request);self.assertIn(('reply',{'r':1}),self.effects);self.assertEqual(new.received_seq,8)
 def test_old_create_destroy_before_seq_factory_and_new_destroy_original(self):
  old,oc=self.gate();new,nc=self.gate();destroyed=[];self.manager.addentity(7,NS(destroy=lambda:destroyed.append(7)))
  self.packet(old,oc,'create_entity',self.msg(id=7,type='Other',info={}));self.packet(old,oc,'destroy_entity',self.msg(id=7))
  self.assertEqual(self.decoded,[]);self.assertEqual(self.created,[]);self.assertEqual(destroyed,[])
  self.packet(new,nc,'destroy_entity',self.msg(id=7));self.assertEqual(destroyed,[7]);self.assertEqual(new.received_seq,8)
 def test_all_eight_rpc_old_controller_rejected_before_original(self):
  old,oc=self.gate();new,nc=self.gate()
  for name in transport._RPC:self.packet(old,oc,name,self.msg())
  self.assertEqual(old.received_seq,None);self.assertEqual(self.decoded,[])
  new._send_session_key=lambda c:self.effects.append(('seed',c));self.packet(new,nc,'seed_reply',self.msg(seed=123));self.assertIn(('seed',nc),self.effects)
  self.packet(new,nc,'session_key_ok',self.msg());self.assertEqual(self.effects[-1],('connect',nc))
  self.packet(new,nc,'chat_to_client',self.msg(message='synthetic'));self.assertEqual(new.received_seq,8)
  self.packet(new,nc,'reg_md5_index',self.msg(md5='synthetic',index=1));self.assertEqual(self.effects[-1],('index',('synthetic',1)))
 def test_current_create_connect_reply_keep_original_bodies(self):
  gate,channel=self.gate();hits=[];gate.register_on_event_callback(gate.CB_ON_CONNECT_REPLY,lambda value:hits.append(value))
  self.packet(gate,channel,'connect_reply',self.msg(type=1));self.assertEqual(hits,[1])
  self.packet(gate,channel,'create_entity',self.msg(id=9,type='Other',info={}));self.assertEqual(self.created,[('Other',9)]);self.assertEqual(gate.received_seq,8)
 def test_failure_consumes_attempt_and_late_success_cannot_revive_it(self):
  gate,channel=self.gate();gate.disconnect();gate.start_game(5);tcp=gate.client.client
  gate.client.handle_connection_failed(tcp);self.assertIsNone(gate.client._q7_wish_attempt)
  gate.client.handle_new_connection(tcp);self.assertIsNone(gate._q7_wish_channel);self.assertEqual(gate.status,gate.ST_CONNECT_FAILED)
 def test_old_tcp_success_failure_and_timeout_do_not_use_new_callback(self):
  g,channel=self.gate();oldtcp=g.client.client;oldtimer=self.timers.events[-1]
  g.disconnect();g.start_game(5);newtimer=self.timers.events[-1];status=g.status
  g.client.handle_new_connection(oldtcp);g.client.handle_connection_failed(oldtcp);oldtimer.callback()
  self.assertEqual(g.status,status);self.assertFalse(newtimer.cancelled);self.assertIsNone(g._q7_wish_channel)
  g.client.handle_new_connection(g.client.client);self.assertIsNotNone(g._q7_wish_channel)
 def test_actual_disconnect_new_gate_flow_and_stale_listener(self):
  g,oldchannel=self.gate();self.gg.logic.gate_client=None;g.disconnect();new,newchannel=self.gate()
  oldchannel.rpc_service=g;g.on_channel_disconnected(oldchannel);self.assertIs(self.guard.channel(new),newchannel)
  self.assertTrue(oldchannel.conn.closed)
 def test_original_logic_disconnect_then_new_gate_connect_authority(self):
  from tests.test_project7_wish_ui import original
  class Stub:
   def __init__(stub,channel):stub.rpc_channel=channel
   def seed_request(stub,*args):pass
  self.genv['client_gate_pb2'].IGateService_Stub=Stub;self.genv['common_pb2'].Void=lambda:NS()
  self.gg.server_current=NS(region=NS(gate_next=lambda:('synthetic',1)),region_name='synthetic');self.gg.ui=NS(panels=NS(login=NS(notify_connect=lambda retry:None)));self.gg.account=None
  logic=self.gg.logic;logic.online_state=NS(current=0);logic.gate_timer=None;logic.gate_retry=0;logic.logger=Log();logic.except_hook=lambda *a:None;logic.on_gate_timeout=lambda:None;logic.on_gate_entity=lambda *a:None;logic.on_gate_invalid=lambda:None
  env={'gg':self.gg,'const':NS(CLIENT_PUBKEY='synthetic-public-key',GATE_RETRY=3),'GateClient':self.gm}
  connect=original('analysis/original-py-640/logic/logic_state.py','gate_connect',env);disconnect=p7_disconnect_original(env)
  encrypter=NS(LoginKeyEncrypterNokeyczar=lambda *args:NS())
  with patch.dict(sys.modules,{'common.SessionEncrypter':encrypter}):
   connect(logic);old=logic.gate_client;old.client.handle_new_connection(old.client.client);old_channel=old._q7_wish_channel
   self.assertIs(self.guard.channel(old),old_channel);disconnect(logic);self.assertIsNone(logic.gate_client)
   connect(logic);new=logic.gate_client;new.client.handle_new_connection(new.client.client);self.assertIsNot(new,old)
   self.assertIsNone(self.guard.channel(old));self.assertIsNotNone(self.guard.channel(new))
   self.packet(old,old_channel,'entity_message',self.msg(id=7,method='reply',parameters={}))
   self.assertEqual(self.decoded,[])
 def test_same_gate_replaced_channel_old_listener_and_proxy_do_not_clear_new(self):
  g,old=self.gate();g.disconnect();g.start_game(5);g.client.handle_new_connection(g.client.client);new=g._q7_wish_channel
  actor=NS(server=None,on_lose_server=lambda:self.effects.append('lost'),set_server=lambda s:self.effects.append('clear'))
  proxy=self.Proxy(NS(rpc_channel=new),None);proxy.setowner(actor);actor.server=proxy
  proxy.on_channel_disconnected(old);g.on_channel_disconnected(old);self.assertIs(proxy.stub.rpc_channel,new);self.assertNotIn('lost',self.effects)
  g.on_channel_disconnected(new);proxy.on_channel_disconnected(new);self.assertIn('lost',self.effects);self.assertIsNone(proxy.stub)
 def test_non_gate_channel_original_and_repeat_install_identity(self):
  c=self.Channel('synthetic',1,object());hits=[];c.connect(lambda channel:hits.append(channel),5);c.handle_connection_failed(c.client);self.assertEqual(hits,[None]);self.assertIs(transport.install(self.gm,self.cm,self.pm),self.guard)
 def test_dead_reset_signature_remains_original_type_error_not_reconnect_proof(self):
  g,c=self.gate()
  with self.assertRaises(TypeError):g.reset()
  self.assertIsNone(g._q7_wish_channel)
if __name__=='__main__':unittest.main()
