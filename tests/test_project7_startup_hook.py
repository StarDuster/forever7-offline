"""Finite source/body host models; no original NeoX/Python2 opcode execution."""
import ast
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import textwrap
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'project7_bridge' / 'tools'))
from xdis.unmarshal import load_code
from project7_script_hook import embedded_loader, build_startup_overlay
spec = importlib.util.spec_from_file_location('p7_policy', ROOT/'runtime/project7_startup_hook.py')
hook = importlib.util.module_from_spec(spec); spec.loader.exec_module(hook)
NS = types.SimpleNamespace
TUTORIAL = (ROOT/'offline/runtime/offline_tutorials.py').read_text('ascii')


def appended(name):
    code = load_code(io.BytesIO((ROOT/('analysis/project7/scripts/'+name+'.marshal')).read_bytes()), 62211, code_objects={})
    values = [v.decode('ascii') if isinstance(v,bytes) else v for v in code.co_consts if isinstance(v,(str,bytes))]
    return next(v for v in values if len(v)>300 and '_q7_' in v)


def source_function(source, name, namespace):
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node],type_ignores=[]), '<extracted-ascii-function>', 'exec'), namespace)
    return namespace[name]


def decompiled_function(path, name, namespace, indent=0):
    lines = (ROOT/path).read_text().splitlines(True)
    prefix = ' '*indent
    start = next(i for i,l in enumerate(lines) if l.startswith(prefix+'def '+name+'('))
    end = next((i for i in range(start+1,len(lines)) if lines[i].strip() and not lines[i].startswith(prefix+' ') and not lines[i].startswith('\n')),len(lines))
    source = textwrap.dedent(''.join(lines[start:end]))
    # Explicit finite Py3 adaptation: Py2 sys.modules.items() is a snapshot.
    source = source.replace('sys.modules.items()', 'list(sys.modules.items())')
    return source_function(source,name,namespace)


class ResourceHarness:
    directories=[]
    def __init__(self, clean=None):
        self.directory=tempfile.TemporaryDirectory(); self.directories.append(self.directory); self.path=Path(self.directory.name)/'synthetic.json'
        self.events=[]; self.bad=False
        self.pconst=NS(VERSION=455, PLATFORM_NAME='android', PART_RAW='raw', ERROR_NONE=0,
            ERROR_PART_CHECK_NOTREADY=7, ERROR_PART_DOWNLOAD_NOTREADY=8,
            ERROR_PART_DOWNLOAD_FAIL=9,DOWNLOAD_LIST='unused',Q7_OFFLINE_MODE=False)
        self.state={'schema':1,'version':455,'platform':'android','parts':[['pack',[[640,[[1,'synthetic']]]]]],
            'packs':[[640,[['pack',[]]]]],'manifest':{'pack':[1,['synthetic']]}}
        self.path.write_text(json.dumps(self.state))
        def check(*args):
            self.events.append('native_check')
            return (1,None) if self.bad else (0,[])
        self.files=NS(check_npk=check,check_raw=check)
        self.task=type('PartTask',(),{'PACKS':[],'PARTS':{},'CHECKS':{}})
        no=lambda *a,**k:None
        self.download=NS(download_cleanlocal=no,download_start=no)
        self.globals={'pconst':self.pconst,'patch_file':self.files,'PartTask':self.task,
            'pdownload':self.download,'putils':NS(error_record=lambda c:self.events.append(('error',c))),
            'logger':NS(info=no,warning=no),'_q7_start_json':json,'_Q7_RESOURCE_SNAPSHOT_LIMIT':1024*1024,
            '_q7_snapshot_path':lambda:str(self.path)}
        for name in ('clean_info','query_complete','download_complete','download'):
            func=decompiled_function('analysis/original-py-640/patch/patch_part.py',name,self.globals,4)
            setattr(self.task,name,func)
        self.globals['_q7_original_query_complete']=self.task.query_complete
        self.task.query_complete=source_function(appended('patch/patch_part'),'_q7_query_complete',self.globals)
        source_function(appended('patch/patch_part'),'_q7_local_part_query',self.globals)
        self.task.query=self.globals['_q7_local_part_query']
        patch_globals=dict(self.globals,patch_part=NS(PartTask=self.task))
        verify=source_function(appended('patch/patch'),'_q7_verify_offline_resources',patch_globals)
        activate=source_function(appended('patch/patch'),'_q7_activate_game_mode',patch_globals)
        self.patch=NS(pconst=self.pconst,patch_part=patch_globals['patch_part'],patch_file=self.files,
            _q7_verify_offline_resources=verify,_q7_activate_game_mode=activate,
            clean=clean or (lambda state:self.events.append('original_clean')))
        self.policy=hook.install(self.patch,TUTORIAL,lambda code:self.events.append(code))
        # Finite harness has no cocos package; the lifecycle guard is unit-tested separately.
        self.policy.install_wardrobe_lifecycle=lambda:None
        self.policy.install_settlement_lifecycle=lambda:None
    def activate(self):
        state=self.patch._q7_verify_offline_resources();self.patch._q7_activate_game_mode(state);return state
    def request(self,parts=()):
        task=self.task();task.parts=parts;task.query_files=[];task.query_cb=None
        return task


class HotfixGuardTests(unittest.TestCase):
    def test_offline_hotfix_guard_skips_remote_pipeline(self):
        calls=[]
        hotfix=NS(
            download_hotfix=lambda *a, **k: calls.append('download'),
            before_hotfix=lambda *a, **k: calls.append('before') or False,
            after_hotfix=lambda: calls.append('after') or False)
        patch=NS(patch_hotfix=hotfix)
        self.assertTrue(hook.install_offline_hotfix_guard(patch))
        received=[]
        self.assertIsNone(hotfix.download_hotfix(received.append))
        self.assertEqual(received,[''])
        self.assertEqual(calls,[])
        # The original before/after methods are retained, not replaced by fake success.
        self.assertIs(hotfix.before_hotfix('content'),False)
        self.assertIs(hotfix.after_hotfix(),False)

    def test_offline_hotfix_guard_completes_original_step_generator(self):
        calls=[]
        hotfix=NS(
            download_hotfix=lambda cb: calls.append('download') or cb(None),
            before_hotfix=lambda content: calls.append(('before',content)) or True,
            after_hotfix=lambda: calls.append('after') or True)
        pconst=NS(PLATFORM='android', ERROR_NONE=0, ERROR_PATCH_HOTFIX_DOWNLOAD=5,
                  ERROR_PATCH_HOTFIX_BEFORE=6, DOWNLOAD_LIST='list')
        game3d=NS(PLATFORM_WIN32='win32')
        def retry(proc):
            yield from proc()
        def noop(*args, **kwargs):
            return None
        namespace={
            'retry':retry,'patch_hotfix':hotfix,'pconst':pconst,'game3d':game3d,
            'pdctool':NS(dctool_patchlist_request=noop,dctool_patchlist_fail=lambda *a: calls.append(('fail',)+a)),
            'putils':NS(is_neox2=lambda:False,error_record=noop),
            'pdownload':NS(download_cleanlocal=noop),
            'logger':NS(info=noop,error=noop),
            'msgbox_error':noop,'msgbox_wait':lambda:False,
        }
        function=decompiled_function('analysis/original-py-640/patch/patch.py','step_hotfix',namespace)
        self.assertTrue(hook.install_offline_hotfix_guard(NS(patch_hotfix=hotfix)))
        generator=function()
        list(generator)
        self.assertNotIn('download',calls)
        self.assertEqual([c for c in calls if c[0]=='fail'], [])
        self.assertFalse([c for c in calls if c[0]=='before'])

    def test_offline_hotfix_guard_absent_is_noop(self):
        self.assertFalse(hook.install_offline_hotfix_guard(NS()))

class WardrobeLifecycleTests(unittest.TestCase):
    def test_refresh_pendant_delayed_callback_is_cancelled_after_destroy(self):
        calls=[]
        original_delay_calls=[]
        gg=types.ModuleType('gg')
        def delay(ticks, callback):
            original_delay_calls.append((ticks,callback))
        gg.exec_delay=delay
        with patch.dict(sys.modules, {'gg':gg}):
            namespace={'gg':gg,'calls':calls}
            exec("class Scroll:\n    _node=object()\nclass Panel:\n    valid=True\n    _node=object()\n    pendant_list=Scroll()\n    def refresh_pendant(self):\n        gg.exec_delay(1, lambda: calls.append('jump'))",namespace)
            Panel=namespace['Panel']
            module=types.SimpleNamespace(Member=Panel)
            self.assertTrue(hook.install_wardrobe_lifecycle_guard(module))
            self.assertTrue(hook.install_wardrobe_lifecycle_guard(module))
            panel=Panel()
            panel.refresh_pendant()
            self.assertEqual(gg.exec_delay, delay)
            self.assertEqual(len(original_delay_calls),1)
            ticks, guarded=original_delay_calls[0]
            panel.valid=False
            guarded()
            self.assertEqual(calls,[])
            panel.valid=True
            panel._node=None
            guarded()
            self.assertEqual(calls,[])
            panel._node=object(); panel.pendant_list._node=None
            guarded()
            self.assertEqual(calls,[])
            panel.pendant_list._node=object()
            guarded()
            self.assertEqual(calls,[])
            fresh=Panel();fresh.refresh_pendant();_,fresh_guard=original_delay_calls[-1]
            fresh_guard();self.assertEqual(calls,['jump'])

class PanelGuardContractTests(unittest.TestCase):
    def test_private_method_is_name_mangled_and_all_required_methods_must_wrap(self):
        namespace={'gg':types.SimpleNamespace(exec_delay=lambda d,c:c)}
        exec("class Panel:\n    def refresh_skin_comps(self): pass\n    def __refresh_pendant_comps(self): pass",namespace)
        module=types.SimpleNamespace(Panel=namespace['Panel'])
        self.assertTrue(hook.install_panel_delay_guard(module,('refresh_skin_comps','__refresh_pendant_comps')))
        self.assertTrue(hasattr(namespace['Panel'],'_Panel__refresh_pendant_comps'))
        self.assertTrue(hasattr(namespace['Panel'],'_q7_wrapped__Panel__refresh_pendant_comps'))
        self.assertTrue(hook.install_panel_delay_guard(module,('refresh_skin_comps','__refresh_pendant_comps')))
        self.assertFalse(hook.install_panel_delay_guard(module,('refresh_skin_comps','__missing_private')))

    def test_python2_descriptor_reads_compare_underlying_functions(self):
        class Panel:
            def refresh_pendant(self): pass
        class Descriptor:
            def __init__(self, function): self.function=function
            def __get__(self, instance, owner):
                return types.MethodType(self.function, instance if instance is not None else owner)
        module=types.SimpleNamespace(Panel=Panel)
        self.assertTrue(hook.install_panel_delay_guard(module,('refresh_pendant',)))
        wrapper=getattr(Panel,'_q7_wrapped_refresh_pendant')
        Panel.refresh_pendant=Descriptor(wrapper)
        self.assertTrue(hook.install_panel_delay_guard(module,('refresh_pendant',)))

    def test_foreign_replacement_after_install_is_rejected(self):
        namespace={'gg':types.SimpleNamespace(exec_delay=lambda d,c:c)}
        exec("class Panel:\n    def refresh_pendant(self): pass",namespace)
        module=types.SimpleNamespace(Panel=namespace['Panel'])
        self.assertTrue(hook.install_panel_delay_guard(module,('refresh_pendant',)))
        namespace['Panel'].refresh_pendant=lambda self: None
        self.assertFalse(hook.install_panel_delay_guard(module,('refresh_pendant',)))

class StartupTests(unittest.TestCase):
    def test_render_mode_default_inert_and_png_explicit(self):
        h=ResourceHarness()
        self.assertEqual(h.policy.render_mode,'astc')
        with patch.dict(sys.modules):
            sys.modules.pop('C_file',None)
            h.policy.install_render_compat()
            self.assertNotIn('C_file',sys.modules)
            calls=[]
            module=types.ModuleType('C_file');module.set_path_patch=lambda a,b:calls.append((a,b))
            sys.modules['C_file']=module
            cocos=types.ModuleType('cocos');ui=types.ModuleType('cocos.ui_manager')
            class UIManager:
                @staticmethod
                def init_astc_modifer(self):
                    calls.append(('cocos','cocos2'))
            ui.UIManager=UIManager;cocos.ui_manager=ui
            sys.modules['cocos']=cocos;sys.modules['cocos.ui_manager']=ui
            h.policy.render_mode='png'
            h.policy.install_render_compat()
            self.assertEqual(calls,[('cocos','cocos')])
            UIManager.init_astc_modifer(None)
            self.assertEqual(calls[-1],('cocos','cocos'))
            h.policy.render_mode='astc'
            h.policy.install_render_compat()
            self.assertEqual(len(calls),2)
        with self.assertRaises(ValueError):
            hook.StartupPolicy(h.patch,TUTORIAL,render_mode='invalid')

    def test_wish_embedded_modules_keep_exact_early_and_late_owners(self):
        h=ResourceHarness();p=h.policy
        p.wish_transport_source='OWNER=object()\ndef install():\n    return OWNER\n'
        p.wish_ui_source=('MEMBER=object()\nCALLS=[]\n'
                          'def install_member_guard(transport):\n    CALLS.append(transport)\n    return MEMBER\n'
                          'def install(policy,**companions):\n    CALLS.append((policy,companions))\n    return companions\n')
        p.wish_ui_policy='fixed-host-policy'
        p.draw_ui_namespace={'_HistoryAvatar':object()};p.friend_ui=object();p.dynamic_ui=object()
        with patch.dict(sys.modules):
            for name in ('project7_wish_ui','project7_wish_transport'):sys.modules.pop(name,None)
            sys.modules['gg']=types.ModuleType('gg')
            p.install_wish_early();member=p.wish_member;transport=p.wish_transport
            p.install_wish_early()
            self.assertIs(p.wish_member,member);self.assertIs(p.wish_transport,transport)
            self.assertEqual(p.wish_ui_module.CALLS,[transport,transport])
            p.install_wish_ui()
            policy,companions=p.wish_ui_module.CALLS[-1]
            self.assertEqual(policy,p.wish_ui_policy)
            self.assertIs(companions['families_owner'],p.dynamic_ui)
            self.assertIs(companions['friend_owner'],p.friend_ui)
            self.assertIs(companions['member_owner'],member)
            self.assertIs(companions['history_avatar_type'],p.draw_ui_namespace['_HistoryAvatar'])
            sys.modules['project7_wish_transport']=types.ModuleType('foreign')
            with self.assertRaises(RuntimeError):p.install_wish_ui()

    def test_wish_partial_module_load_is_removed_and_foreign_owner_preserved(self):
        h=ResourceHarness();name='project7_wish_ui'
        with patch.dict(sys.modules):
            sys.modules.pop(name,None)
            with self.assertRaises(ValueError):h.policy._wish_module(name,'raise ValueError("host")',None)
            self.assertNotIn(name,sys.modules)
            foreign=types.ModuleType(name);sys.modules[name]=foreign
            with self.assertRaises(RuntimeError):h.policy._wish_module(name,'pass',None)
            self.assertIs(sys.modules[name],foreign)

    def test_pinned_archive_extension_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            report=build_startup_overlay(
                ROOT/'analysis/project7/official-build-inputs-v3/assets/script.npk',
                ROOT/'analysis/project7/official-build-inputs-v3/assets/project7_local.npk',
                Path(directory)/'startup.npk')
        self.assertEqual(report['entries'],21)
        self.assertEqual(len(report['original_p7_entries_unchanged']),19)
        self.assertEqual(report['auth_deadline']['policy_ms'],60000)
        self.assertTrue(report['auth_deadline']['decoded_roundtrip_verified'])
        self.assertTrue(report['other_init_constants_unchanged'])
        self.assertFalse(report['native_reader_verified'])
        self.assertTrue(report['collection_visibility_embedded'])
        self.assertTrue(report['draw_ui_embedded'])
        self.assertEqual(report['render_mode'],'astc')
        self.assertTrue(report['render_loader_option'])
        self.assertFalse(report['frida_required'])

    def test_resource_native_failure_and_binding(self):
        h=ResourceHarness(); h.bad=True
        with self.assertRaises(ValueError):h.patch._q7_verify_offline_resources()
        self.assertIsNone(h.policy.activation);self.assertFalse(hasattr(h.pconst,'INDEX'))
        with self.assertRaises(RuntimeError):h.patch._q7_activate_game_mode(h.state)
        h.bad=False;state=h.activate();self.assertEqual(h.pconst.INDEX,640);self.assertEqual(h.pconst.VERSION,455)
        with self.assertRaises(RuntimeError):h.patch._q7_activate_game_mode(state)
        self.assertFalse(h.policy.live())

    def test_index_hydration_and_original_failure(self):
        h=ResourceHarness();state=h.activate();task=h.request();task.clean_info()
        self.assertIn(640,h.task.CHECKS['pack']);self.assertNotIn('640',h.task.CHECKS['pack'])
        # Mutating source or hydrated structures cannot mutate retained frozen basis.
        state['packs'][:]=[];h.task.PACKS[:]=[];task.clean_info();self.assertTrue(h.task.PACKS)
        result=[];task.query(result.append);self.assertEqual(result,[0]);self.assertEqual(h.events.count('native_check'),2)
        # query_complete clears dictionaries without clean_info; query entry restores, native rechecks.
        h.task.PACKS=[];h.task.PARTS={};h.task.CHECKS={};result=[];task.query(result.append)
        self.assertEqual(result,[0]);self.assertTrue(h.task.CHECKS)
        bad=h.request(('unknown',));result=[];bad.query(result.append)
        self.assertEqual(result,[None]);self.assertFalse(h.policy.live());self.assertEqual(h.task.CHECKS,{})
        with self.assertRaises(RuntimeError):h.patch.clean(True)
        result=[];bad.query(result.append);self.assertEqual(result,[None])

    def test_requested_part_native_failure(self):
        h=ResourceHarness();h.activate();h.bad=True;result=[]
        h.request().query(result.append)
        self.assertEqual(result,[None]);self.assertFalse(h.policy.live())
        self.assertEqual(h.task.CHECKS,{})

    def test_original_optional_download_not_fake_success(self):
        h=ResourceHarness();h.activate();task=h.request();sizes=[];task.query(sizes.append)
        self.assertEqual(sizes,[0]);self.assertEqual(task.query_files,[])
        done=[];task.download(done.append);self.assertEqual(done,[False]);self.assertFalse(h.policy.live())

    def test_original_clean_done_order_and_failure(self):
        h=ResourceHarness();h.activate();events=[]
        fake_modules={'logic.old':object(),'com.old':object(),'gg':object(),'entity.stays':object()}
        no=lambda *a,**kw:None
        render=NS(set_logic=lambda value:events.append('render_cleared'))
        ns={'logger':NS(info=no,error=no),'pconst':NS(DOWNLOAD_LIST='',DOWNLOAD_PATCH='',DOWNLOAD_MINFULL='',CMD_ARG=''),
            'render':render,'_task_part':NS(clean_task=lambda:events.append('task_clean')),'_task_mf':None,
            'pdownload':NS(download_cleantask=no,download_cleanlocal=no),'putils':NS(job_clean=no,error_clean=no),
            'sys':NS(modules=fake_modules),'pdrpf':NS(drpf_update_success=lambda:events.append('done_success'),drpf_update_fail=no),
            'patch_hotfix':NS(after_hotfix=lambda:True),'_panel':None}
        original_clean=decompiled_function('analysis/original-py-640/patch/patch.py','clean',ns)
        h=ResourceHarness(clean=original_clean);h.activate()
        h.policy.install_wish_early=lambda:events.append('wish_early_install')
        h.policy.install_trial_retry=lambda:events.append('trial_retry_install')
        h.policy.install_tutorials=lambda:events.append('tutorial_install')
        h.policy.install_collection=lambda:events.append('collection_install')
        h.policy.install_draw_ui=lambda:events.append('draw_ui_install')
        h.policy.install_dynamic_ui=lambda:events.append('family_install')
        h.policy.install_wish_ui=lambda:events.append('wish_ui_install')
        h.policy.install_login=lambda:events.append('login_guard_install')
        ns['clean']=h.patch.clean
        modules={}
        def module(name):
            value=types.ModuleType(name);modules[name]=value;return value
        com=module('com');const=module('com.const');com.const=const;const.DEBUG_MPH=False;const.DEBUG_DBX=False
        gg=module('gg');logic=module('logic');game=module('logic.game_logic');logic.game_logic=game
        game.start=lambda:events.append('game_start')
        saved={k:sys.modules.get(k) for k in modules};sys.modules.update(modules)
        try:
            done=decompiled_function('analysis/original-py-640/patch/patch.py','done',ns)
            done(True)
            self.assertLess(events.index('wish_early_install'),events.index('trial_retry_install'))
            self.assertLess(events.index('trial_retry_install'),events.index('tutorial_install'))
            self.assertLess(events.index('task_clean'),events.index('tutorial_install'))
            self.assertLess(events.index('tutorial_install'),events.index('collection_install'))
            self.assertLess(events.index('collection_install'),events.index('draw_ui_install'))
            self.assertLess(events.index('draw_ui_install'),events.index('login_guard_install'))
            self.assertLess(events.index('family_install'),events.index('wish_ui_install'))
            self.assertLess(events.index('wish_ui_install'),events.index('login_guard_install'))
            self.assertLess(events.index('login_guard_install'),events.index('game_start'))
            self.assertEqual(set(fake_modules),{'entity.stays'})
            ns['_task_part']=None;ns['_task_mf']=None;events[:]=[]
            def fail():raise RuntimeError('synthetic tutorial import failure')
            h.policy.install_tutorials=fail
            with self.assertRaises(RuntimeError):done(True)
            self.assertNotIn('game_start',events);self.assertFalse(h.policy.live())
        finally:
            for k,v in saved.items():
                if v is None:sys.modules.pop(k,None)
                else:sys.modules[k]=v

    def test_collection_install_failure_uses_startup_repair(self):
        h=ResourceHarness();h.activate()
        h.policy.install_tutorials=lambda:None
        h.policy.install_login=lambda:None
        h.policy.collection_source='def install(policy):\n    raise ValueError("synthetic collection failure")\n'
        h.policy.collection_policy='synthetic-policy'
        with self.assertRaisesRegex(ValueError, 'synthetic collection failure'):
            h.patch.clean(True)
        self.assertFalse(h.policy.live())
        self.assertEqual(h.pconst.Q7_STARTUP_REPAIR_REQUIRED, 'startup_policy_install_failed')

    def test_collection_source_and_policy_are_bound_together(self):
        h=ResourceHarness()
        with self.assertRaises(ValueError):
            hook.StartupPolicy(h.patch,TUTORIAL,collection_source='unused')

    def test_draw_ui_failure_prevents_start_and_uses_repair(self):
        h=ResourceHarness();h.activate()
        h.policy.install_tutorials=lambda:None
        h.policy.install_collection=lambda:None
        issued=[]
        h.policy.install_login=lambda:issued.append('login')
        h.policy.draw_ui_source='def install():\n    raise RuntimeError("synthetic draw UI failure")\n'
        with self.assertRaisesRegex(RuntimeError, 'synthetic draw UI failure'):
            h.patch.clean(True)
        self.assertFalse(h.policy.live())
        self.assertEqual(h.pconst.Q7_STARTUP_REPAIR_REQUIRED,'startup_policy_install_failed')
        self.assertEqual(issued,[])


    def test_furniture_failure_stops_login_after_draw_install(self):
        h=ResourceHarness();h.activate();events=[]
        h.policy.install_tutorials=lambda:events.append('tutorial')
        h.policy.install_collection=lambda:events.append('collection')
        h.policy.install_draw_ui=lambda:events.append('draw')
        h.policy.install_login=lambda:events.append('login')
        h.policy.furniture_ui_source='def install(policy):\n    raise RuntimeError("synthetic furniture failure")\n'
        h.policy.furniture_ui_policy='fixed-test-policy'
        with self.assertRaisesRegex(RuntimeError,'synthetic furniture failure'):
            h.patch.clean(True)
        self.assertEqual(events,['tutorial','collection','draw'])
        self.assertFalse(h.policy.live())
        self.assertEqual(h.pconst.Q7_STARTUP_REPAIR_REQUIRED,'startup_policy_install_failed')

    def test_furniture_install_bound_policy_and_order(self):
        h=ResourceHarness();h.activate();events=[]
        with self.assertRaises(ValueError):
            hook.StartupPolicy(h.patch,TUTORIAL,furniture_ui_source='unused')
        h.policy.install_tutorials=lambda:events.append('tutorial')
        h.policy.install_collection=lambda:events.append('collection')
        h.policy.install_draw_ui=lambda:events.append('draw')
        h.policy.install_login=lambda:events.append(('login',h.policy.furniture_ui))
        h.policy.furniture_ui_source='def install(policy):\n    return ("furniture",policy)\n'
        h.policy.furniture_ui_policy='fixed-test-policy'
        h.patch.clean(True)
        self.assertEqual(events,['tutorial','collection','draw',('login',('furniture','fixed-test-policy'))])


    def test_friend_install_receives_exact_draw_view_type_after_furniture(self):
        h=ResourceHarness();h.activate();events=[];view_type=type('KnownHistoryView',(),{})
        h.policy.install_tutorials=lambda:events.append('tutorial')
        h.policy.install_collection=lambda:events.append('collection')
        def draw():
            events.append('draw');h.policy.draw_ui_namespace={'_HistoryAvatar':view_type}
        h.policy.install_draw_ui=draw
        h.policy.install_furniture_ui=lambda:events.append('furniture')
        h.policy.friend_ui_source='def install(history_avatar_type=None):\n    return history_avatar_type\n'
        h.policy.install_login=lambda:events.append(('login',h.policy.friend_ui))
        h.patch.clean(True)
        self.assertEqual(events,['tutorial','collection','draw','furniture',('login',view_type)])

    def test_selector_receives_exact_draw_type_and_runs_after_friend(self):
        h=ResourceHarness();h.activate();events=[];view=type('KnownHistoryView',(),{})
        h.policy.install_tutorials=lambda:None;h.policy.install_collection=lambda:None
        def draw():h.policy.draw_ui_namespace={'_HistoryAvatar':view}
        h.policy.install_draw_ui=draw;h.policy.install_furniture_ui=lambda:None
        h.policy.install_friend_ui=lambda:events.append('friend')
        h.policy.selector_ui_source='def install(policy,history_avatar_type=None):\n    return (policy,history_avatar_type)\n'
        h.policy.selector_ui_policy='fixed-selector'
        h.policy.install_login=lambda:events.append(h.policy.selector_ui)
        h.patch.clean(True)
        self.assertEqual(events,['friend',('fixed-selector',view)])

    def test_tutorial_completion_members_precede_avatar_and_panels_follow_ui(self):
        h=ResourceHarness();h.activate();events=[]
        h.policy.install_tutorials=lambda:events.append('bypass')
        h.policy.tutorial_completion_source='phase=[]\nclass Owner:\n    def check_avatar(self, cls):\n        pass\ndef install():\n    phase.append("members")\n    return Owner()\ndef install_panels():\n    phase.append("panels")\n'
        def checked(name,phase):
            self.assertEqual(h.policy.tutorial_completion_namespace['phase'],phase)
            events.append(name)
        h.policy.install_collection=lambda:checked('collection',['members'])
        h.policy.install_draw_ui=lambda:checked('draw',['members'])
        h.policy.install_furniture_ui=lambda:checked('furniture',['members'])
        h.policy.install_friend_ui=lambda:checked('friend',['members'])
        h.policy.install_selector_ui=lambda:checked('selector',['members'])
        h.policy.install_dynamic_ui=lambda:checked('dynamic',['members'])
        h.policy.install_login=lambda:checked('login',['members','panels'])
        h.patch.clean(True)
        self.assertEqual(events,['bypass','collection','draw','furniture','friend','selector','dynamic','login'])

    def test_dynamic_receives_exact_companion_owners_after_selector_before_panels(self):
        h=ResourceHarness();h.activate();events=[];view=type('HistoryView',(),{});friend=object()
        h.policy.install_tutorials=lambda:None;h.policy.install_collection=lambda:None
        def draw():h.policy.draw_ui_namespace={'_HistoryAvatar':view}
        def friends():h.policy.friend_ui=friend
        h.policy.install_draw_ui=draw;h.policy.install_friend_ui=friends
        h.policy.install_furniture_ui=lambda:None
        h.policy.install_selector_ui=lambda:events.append('selector')
        h.policy.dynamic_ui_source='def install(policy,history_avatar_type=None,friend_owner=None):\n    return (policy,history_avatar_type,friend_owner)\n'
        h.policy.dynamic_ui_policy='fixed-dynamic'
        def panels():events.append(('panels',h.policy.dynamic_ui))
        h.policy.install_tutorial_completion_panels=panels
        h.policy.install_login=lambda:events.append('login')
        h.patch.clean(True)
        self.assertEqual(events,['selector',('panels',('fixed-dynamic',view,friend)),'login'])

    def test_dynamic_partial_configuration_and_missing_owners_rejected(self):
        h=ResourceHarness()
        for arguments in ({'dynamic_ui_source':'unused'},{'dynamic_ui_policy':'unused'},
                          {'dynamic_ui_source':'unused','dynamic_ui_policy':'fixed'}):
            with self.assertRaises(ValueError):hook.StartupPolicy(h.patch,TUTORIAL,**arguments)
        h.policy.dynamic_ui_source='def install(*args,**kwargs):\n    return object()\n'
        h.policy.dynamic_ui_policy='fixed'
        with self.assertRaisesRegex(RuntimeError,'installed draw and friend'):
            h.policy.install_dynamic_ui()

    def test_dynamic_failure_prevents_panels_and_login_and_requires_repair(self):
        h=ResourceHarness();h.activate();events=[]
        h.policy.install_tutorials=lambda:None;h.policy.install_collection=lambda:None
        h.policy.install_draw_ui=lambda:None;h.policy.draw_ui_namespace={'_HistoryAvatar':object}
        h.policy.install_furniture_ui=lambda:None;h.policy.install_friend_ui=lambda:None
        h.policy.friend_ui=object();h.policy.install_selector_ui=lambda:None
        h.policy.dynamic_ui_source='def install(*args,**kwargs):\n    raise RuntimeError("dynamic failure")\n'
        h.policy.dynamic_ui_policy='fixed'
        h.policy.install_tutorial_completion_panels=lambda:events.append('panels')
        h.policy.install_login=lambda:events.append('login')
        with self.assertRaisesRegex(RuntimeError,'dynamic failure'):h.patch.clean(True)
        self.assertEqual(events,[]);self.assertFalse(h.policy.live())
        self.assertEqual(h.pconst.Q7_STARTUP_REPAIR_REQUIRED,'startup_policy_install_failed')

    def test_tutorial_panel_failure_prevents_login_and_uses_repair(self):
        h=ResourceHarness();h.activate();issued=[]
        h.policy.install_tutorials=lambda:None;h.policy.install_collection=lambda:None
        h.policy.install_draw_ui=lambda:None;h.policy.install_furniture_ui=lambda:None
        h.policy.install_friend_ui=lambda:None;h.policy.install_selector_ui=lambda:None
        h.policy.tutorial_completion_source='def install():\n    return object()\ndef install_panels():\n    raise RuntimeError("tutorial panel failure")\n'
        h.policy.install_login=lambda:issued.append('login')
        with self.assertRaisesRegex(RuntimeError,'tutorial panel failure'):h.patch.clean(True)
        self.assertEqual(issued,[]);self.assertFalse(h.policy.live())
        self.assertEqual(h.pconst.Q7_STARTUP_REPAIR_REQUIRED,'startup_policy_install_failed')

    def test_selector_failure_prevents_login_and_uses_repair(self):
        h=ResourceHarness();h.activate();issued=[]
        h.policy.install_tutorials=lambda:None;h.policy.install_collection=lambda:None
        h.policy.install_draw_ui=lambda:None;h.policy.install_furniture_ui=lambda:None
        h.policy.install_friend_ui=lambda:None;h.policy.draw_ui_namespace={'_HistoryAvatar':object}
        h.policy.selector_ui_source='def install(policy,history_avatar_type=None):\n    raise RuntimeError("selector failure")\n'
        h.policy.selector_ui_policy='fixed-selector'
        h.policy.install_login=lambda:issued.append('login')
        with self.assertRaisesRegex(RuntimeError,'selector failure'):h.patch.clean(True)
        self.assertEqual(issued,[]);self.assertFalse(h.policy.live())
        self.assertEqual(h.pconst.Q7_STARTUP_REPAIR_REQUIRED,'startup_policy_install_failed')

    def test_friend_install_failure_prevents_login_and_routes_repair(self):
        h=ResourceHarness();h.activate();issued=[]
        h.policy.install_tutorials=lambda:None;h.policy.install_collection=lambda:None
        h.policy.install_draw_ui=lambda:None;h.policy.install_furniture_ui=lambda:None
        h.policy.draw_ui_namespace={'_HistoryAvatar':object}
        h.policy.friend_ui_source='def install(history_avatar_type=None):\n    raise RuntimeError("synthetic friend failure")\n'
        h.policy.install_login=lambda:issued.append('login')
        with self.assertRaisesRegex(RuntimeError,'synthetic friend failure'):h.patch.clean(True)
        self.assertFalse(h.policy.live());self.assertEqual(issued,[])
        self.assertEqual(h.pconst.Q7_STARTUP_REPAIR_REQUIRED,'startup_policy_install_failed')


class FakeModules(unittest.TestCase):
    def setUp(self):self.saved={}
    def tearDown(self):
        for name,value in self.saved.items():
            if value is None:sys.modules.pop(name,None)
            else:sys.modules[name]=value
    def module(self,name):
        if name not in self.saved:self.saved[name]=sys.modules.get(name)
        module=types.ModuleType(name);sys.modules[name]=module
        if '.' in name:
            parent,leaf=name.rsplit('.',1)
            if parent not in sys.modules:self.module(parent)
            setattr(sys.modules[parent],leaf,module)
        return module
    def tutorial_modules(self):
        targets={'entity.avatar_attrs.NewbeeData':'NewbeeData','entity.avatar_members.NewbeeMember':'Member',
            'entity.avatar_members.EventTriggerMember':'Member'}
        for name in ('newbee_guidance','newbee_mask','combat_guide_hero','combat_guide_restrain',
            'city_yanhua_guide','combat_monster','city','common_confirm'):
            targets['cocos.panels.'+name]='Panel'
        for name,cls in targets.items():setattr(self.module(name),cls,type(cls,(),{}))
        self.module('com.base.game_object').members_cache={}
        self.module('gg').exec_delay=lambda ms,callback:callback()
    def test_tutorial_copy_cache_and_continuations(self):
        self.tutorial_modules();h=ResourceHarness();h.policy.install_tutorials()
        member=sys.modules['entity.avatar_members.NewbeeMember'].Member
        event=sys.modules['entity.avatar_members.EventTriggerMember'].Member
        # Execute the exact member-copy half of decompiled GameObjectMeta.__init__.
        # Explicit host adaptation supplies Python2 inspect/unbound-method .im_func semantics;
        # updater registration half is excluded, not claimed as a complete metaclass runtime.
        lines=(ROOT/'analysis/original-py-640/com/base/game_object.py').read_text().splitlines(True)
        start=next(i for i,l in enumerate(lines) if l.startswith('    def __init__(cls, name, bases, dct):'))
        end=next(i for i in range(start,len(lines)) if lines[i].startswith('        super(GameObjectMeta'))
        source=textwrap.dedent(''.join(lines[start:end]))
        class Py2Method:
            def __init__(self,function):self.im_func=function
        def members(cls):
            return [(name,Py2Method(value) if isinstance(value,types.FunctionType) else value)
                    for name,value in cls.__dict__.items()]
        base=type('GameObjectMember',(),{})
        # Real member classes inherit this marker; synthetic classes reproduce that relation.
        member_copy=type('MemberCopy',(base,),dict(member.__dict__))
        event_copy=type('EventCopy',(base,),dict(event.__dict__))
        cache={};namespace={'members_cache':cache,'method_cache':{},'GameObjectMember':base,
            'inspect':NS(getmembers=members,ismethod=lambda obj:isinstance(obj,Py2Method))}
        copy_body=source_function(source,'__init__',namespace)
        avatar=type('ClientAvatar',(),{})
        copy_body(avatar,'ClientAvatar',(member_copy,event_copy),{})
        self.assertIn(member_copy,cache)
        # im_func extraction copied raw function into actual avatar; late Member changes cannot update it.
        previous=avatar.startEventNewbee
        event_copy.startEventNewbee=lambda *a:None
        self.assertIs(avatar.startEventNewbee,previous)
        self.module('entity.ClientAvatar').ClientAvatar=avatar
        h.policy.check_avatar();h.policy.install_tutorials()
        self.assertIs(hook._raw(avatar.startEventNewbee),h.policy.tutorials['namespace']['continue_story_without_teaching'])
        obj=avatar();seen=[];obj.startEventUI=seen.append;obj.startEventNewbee('synthetic-event')
        self.assertEqual(seen,['synthetic-event'])
        callback=[];h.policy.tutorials['namespace']['skip_guidance'](obj,1,lambda:callback.append(True))
        self.assertEqual(callback,[True]);self.assertFalse(hasattr(obj,'completedEvents'))
        avatar.startEventNewbee=lambda *a:None
        with self.assertRaises(RuntimeError):h.policy.check_avatar()
    def test_tutorial_rejects_prebuilt_cache_and_avatar(self):
        self.tutorial_modules();h=ResourceHarness()
        member=sys.modules['entity.avatar_members.NewbeeMember'].Member
        sys.modules['com.base.game_object'].members_cache[member]=[]
        with self.assertRaises(RuntimeError):h.policy.install_tutorials()
        sys.modules['com.base.game_object'].members_cache={}
        self.module('entity.ClientAvatar').ClientAvatar=type('ClientAvatar',(),{})
        with self.assertRaises(RuntimeError):h.policy.install_tutorials()
    def login(self):
        h=ResourceHarness();h.activate();module=self.module('cocos.panels.login');gg=self.module('gg')
        queue=[];gg.exec_delay=lambda ms,callback:queue.append((ms,callback));gg._q7_login_attempt=None
        gg.logic=NS(game_state=NS(current=2),online_state=NS(current=0));gg.ui=NS(panels=NS(_panels={}))
        module.gg=gg;module.const=NS(GameState=NS(LOGIN=2),OnlineState=NS(OFFLINE=0));module.cc=NS(ccui=NS(TOUCH_EVENT_ENDED=2))
        clicks=[]
        def _q7_click(instance,sender,event):clicks.append((instance,sender,event))
        module._q7_click=_q7_click
        module.Panel=type('Panel',(),{'on_user_click':_q7_click})
        panel=module.Panel();panel.valid=True;panel.visible=True;panel.mask=NS(isVisible=lambda:False)
        gg.ui.panels._panels['login']=panel;h.policy.install_login()
        return h,module,gg,panel,queue,clicks
    def test_login_one_existing_delay_and_once(self):
        h,module,gg,panel,queue,clicks=self.login()
        panel.notify_setting();panel.notify_setting();self.assertEqual(len(queue),1);self.assertEqual(queue[0][0],700)
        self.assertEqual(clicks,[]);queue.pop()[1]();self.assertEqual(clicks,[(panel,0,2)])
        panel.notify_setting();self.assertEqual(queue,[])
        # A rebuilt panel after failure is not automatically resubmitted.
        other=module.Panel();gg.ui.panels._panels['login']=other;other.notify_setting();self.assertEqual(queue,[])
    def test_own_loader_python2_grammar_alias_and_original_once(self):
        # Parse our new source/loader with Python2 grammar, then convert only our
        # exec statement for host execution; no original game code object runs.
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore',DeprecationWarning)
            from lib2to3.refactor import RefactoringTool
        convert=RefactoringTool(['lib2to3.fixes.fix_exec'])
        own=(ROOT/'runtime/project7_startup_hook.py').read_text('ascii')
        convert.refactor_string(own,'project7_startup_hook.py')
        loader=str(convert.refactor_string(embedded_loader(),'own_loader.py'))
        h=ResourceHarness()
        # Fresh original methods: the loader itself must own their one installation.
        patch=self.module('patch.patch');package=sys.modules['patch'];package.__path__=[]
        fresh=ResourceHarness()
        # Unwrap existing harness by reconstructing original startup seam from the
        # preserved source functions in its globals, not the installed wrappers.
        ns=fresh.globals
        for name in ('clean_info','query_complete','download_complete'):
            setattr(fresh.task,name,decompiled_function('analysis/original-py-640/patch/patch_part.py',name,ns,4))
        ns['_q7_original_query_complete']=fresh.task.query_complete
        fresh.task.query=source_function(appended('patch/patch_part'),'_q7_local_part_query',ns)
        pg=dict(ns,patch_part=NS(PartTask=fresh.task))
        patch.pconst=fresh.pconst;patch.patch_part=pg['patch_part'];patch.patch_file=fresh.files
        patch.clean=lambda state:None
        patch._q7_verify_offline_resources=source_function(appended('patch/patch'),'_q7_verify_offline_resources',pg)
        patch._q7_activate_game_mode=source_function(appended('patch/patch'),'_q7_activate_game_mode',pg)
        called=[];env={'_f7_original_start':lambda:called.append(True)}
        exec(compile(loader,'<own-loader>','exec'),env,env)
        self.assertEqual(called,[True]);self.assertTrue(patch._p7_startup_policy.installed)
        self.assertEqual(patch._p7_startup_policy.dynamic_ui_source,
                         (ROOT/'offline/current/runtime/project7_dynamic_ui_families.py').read_text('ascii'))
        from project7_feature_assets import dynamic_ui_policy
        self.assertEqual(patch._p7_startup_policy.dynamic_ui_policy,dynamic_ui_policy())
        self.assertEqual(patch._p7_startup_policy.trial_retry_source,
                         (ROOT/'offline/current/runtime/project7_trial_retry_compat.py').read_text('ascii'))
        self.assertEqual(patch._p7_startup_policy.trial_retry_policy,
                         (ROOT/'offline/current/java/android_trial_retry/trial-ui-policy-v1.json').read_text('ascii'))
        self.assertEqual(patch._p7_startup_policy.wish_ui_source,
                         (ROOT/'offline/current/runtime/project7_wish_ui.py').read_text('ascii'))
        self.assertEqual(patch._p7_startup_policy.wish_transport_source,
                         (ROOT/'offline/current/runtime/project7_wish_transport.py').read_text('ascii'))
        from project7_feature_assets import wish_ui_policy
        self.assertEqual(patch._p7_startup_policy.wish_ui_policy,wish_ui_policy())
        with self.assertRaises(RuntimeError):exec(compile(loader,'<own-loader>','exec'),env,env)
        self.assertEqual(called,[True])

    def test_login_stale_guards(self):
        for change in ('panel','logic','gg','attempt','mask','hidden','invalid','game','online','activation','repair','click'):
            h,module,gg,panel,queue,clicks=self.login();panel.notify_setting()
            if change=='panel':gg.ui.panels._panels['login']=object()
            elif change=='logic':gg.logic=object()
            elif change=='gg':self.module('gg')
            elif change=='attempt':gg._q7_login_attempt={'stage':'form'}
            elif change=='mask':panel.mask.isVisible=lambda:True
            elif change=='hidden':panel.visible=False
            elif change=='invalid':panel.valid=False
            elif change=='game':gg.logic.game_state.current=4
            elif change=='online':gg.logic.online_state.current=3
            elif change=='activation':h.activate()
            elif change=='repair':h.policy.repair('synthetic_failure')
            elif change=='click':module.Panel.on_user_click=lambda *a:None
            queue.pop()[1]();self.assertEqual(clicks,[],change)
            panel.notify_setting()
            if change!='activation':self.assertEqual(queue,[],change)


def tearDownModule():
    for directory in ResourceHarness.directories:directory.cleanup()

if __name__=='__main__':unittest.main()
import _paths  # noqa: E402,F401
