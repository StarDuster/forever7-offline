"""Focused v65/f81b host for the legal week-2 route2 handoff and event 539.

The host drives the published v65 OWN classes with the existing f81b manager
frame jar and full v65 stage assets. It settles the real released ending event
8028, performs the real requestEnterStoryByEnding(2) transition, then completes
534..539 through the real Gateway startEvent/clientTraceProcessingEvent path.
No 539 receipt, route4-1 value or area1 state is seeded. Only the host test is
compiled; no production source is recompiled, no prepare/D8/APK/native.

The verifier only asserts observable results from that run.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
JDK = ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
JSON_JAR = ROOT / 'toolchains/json-20240303.jar'
PREPARE = ROOT / 'analysis/project7/story-city-integration-prepare-v65/project7-inputs-83akv7as'
STAGE = PREPARE / 'stage'
COMPILED = PREPARE / 'compiled'
OWN = COMPILED / 'production-classes'
MANAGER_JAR = ROOT / 'analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar'
DEX_JARS = ROOT / 'toolchains/dex2jar-v2.4/dex-tools-v2.4/lib'
IFACE_FIX = ROOT / 'analysis/project7/cg-v61-dispatch-host/InterfaceCallFix.java'
HOST = HERE / 'Route539EffectHost.java'
CANDIDATE_SOURCE = ROOT / 'offline/current/java/android_story_city/src/com/project7/localmanager/StoryCityPolicy.java'
CANDIDATE_STUBS = ROOT / 'offline/current/java/android_story_city/compile_stubs'
EVIDENCE = ROOT / 'reports/project7-route539-effect-host.json'
CANDIDATE_EVIDENCE = ROOT / 'reports/project7-route539-effect-host-candidate.json'

PINS = {
    'manager_jar_sha256': (MANAGER_JAR, 'f81b686eb3cfdb7e87f5c9eae5075652d08afb38c8d104ed81b3baebcb703c0f'),
    'stage_build_inputs_sha256': (STAGE / 'build-inputs.json', '6350f92c22cb826cf64fe9ff971b7aaf72f4b4384c6fddb54ac110536ee0d1a5'),
    'compiled_inputs_sha256': (COMPILED / 'compile-inputs.json', 'f90bf001b199ca73fd759110975d668d358e40e1476eb491057e46321a1ed698'),
    'event_graph_sha256': (STAGE / 'assets/event_graph.tsv', 'dabe8f6ed779137cdcad221ee7a4867f552a0c8ef591b40c6af9e7bf9aa0f2bb'),
    'weeks_sha256': (STAGE / 'assets/weeks.tsv', 'dbb0a5d64492e18243a332c93c4a855f5572661922bd26b870b48a96b8ffaa55'),
    'new_player_sha256': (STAGE / 'assets/new_player.bson', '6877cdc06532a11faa47e1855049f678db1c210de96caf1312c27c431b9875d7'),
    'story_city_catalog_sha256': (STAGE / 'assets/project7_story_city/catalog-v1.json.gz', 'af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args):
    process = subprocess.run([str(value) for value in args], capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError(process.stdout + process.stderr)
    return process.stdout + process.stderr


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def validate_area_reply(name, case, before_status, after_status):
    reply = case['area_reply']
    for side, expected in (('before', before_status), ('after', after_status)):
        row = reply[side]
        check(row['keys'] == ['ais', 'cd', 'sm'], name + ': area reply ' + side + ' keys')
        check(row['sm'] is False, name + ': area reply ' + side + ' sm false')
        check(len(base64.b64decode(row['parameters_b64'])) == row['parameters_bytes'],
              name + ': area reply ' + side + ' parameters length')
        check(hashlib.sha256(base64.b64decode(row['parameters_b64'])).hexdigest() == row['parameters_sha256'],
              name + ': area reply ' + side + ' parameters sha256')
        check(hashlib.sha256(base64.b64decode(row['ais_b64'])).hexdigest() == row['ais_sha256'],
              name + ': area reply ' + side + ' ais sha256')
        check(hashlib.sha256(base64.b64decode(row['cd_b64'])).hexdigest() == row['cd_sha256'],
              name + ': area reply ' + side + ' cd sha256')
        check(row['area_1_st'] == expected, name + ': area reply ' + side + ' area_1 ' +
              str(row['area_1_st']) + ' != ' + str(expected))
        check(row['profile_changed_by_login'] is True,
              name + ': ordinary login bootstrap visible in profile ' + side)
    check(reply['before']['area_1_st'] == case['before_chain']['all_area_info_status'],
          name + ': ordinary before matches host projection')
    check(reply['after']['area_1_st'] == case['after_chain']['all_area_info_status'],
          name + ': ordinary after matches host projection')


def validate_case(name, case, expected_observable):
    before, after = case['before_chain'], case['after_chain']
    expected_area = {'foundation_1043': (0, 0), 'foundation_none': (-1, -1),
                     'control_1004_only': (1, 1)}[name]
    validate_area_reply(name, case, *expected_area)
    check(before['std_rt'] == '1', name + ': legal route base 1')
    check(before['chapter_menu'] == 2, name + ': menu selector 2')
    check(before['chapter_receipt_539'] is False, name + ': no 539 receipt before')
    check(before['chapter_state_1'] is None, name + ': no area1 state before')
    check(after['std_rt'] == '4-1', name + ': 539 writes route 4-1')
    check(after['route_event_539'] is True, name + ': 539 route ledger')
    check(after['chapter_receipt_539'] is False, name + ': 539 city receipt false')
    check(after['chapter_receipt_key_539'] is False, name + ': 539 city receipt key absent')
    check(after['chapter_state_1'] is None, name + ': 539 areaFree state dropped')
    check(after['chapter_effect_keys'] == [] and after['chapter_state_keys'] == [],
          name + ': baseline writes no city receipt/state')
    check(after['story_city_owns'] is False, name + ': menu2/rt4-1 outside shared city scope')
    check(after['chapter_city_active'] is False, name + ': chapter city inactive')
    check(case['seam_profile_unchanged'] is True, name + ': ownership seam no-op')
    check(case['sync_route_parameters']['rt'] == '4-1', name + ': syncRoute rt 4-1')
    chain = case['chain']
    check(len(chain) == 6, name + ': six chain steps')
    check([row['event'] for row in chain] == [534, 535, 536, 537, 538, 539], name + ': exact chain order')
    check(chain[-1]['sync_route'] == 1, name + ': one syncRoute on 539')
    check(all(row['sync_route'] == 0 for row in chain[:-1]), name + ': no route sync before 539')

    reload = case['reload']
    check(reload['state']['completed_539'] is True, name + ': reload keeps 539')
    check(reload['state']['std_rt'] == '4-1', name + ': reload keeps 4-1')
    check(reload['state']['chapter_receipt_539'] is False and reload['state']['chapter_receipt_key_539'] is False,
          name + ': reload keeps dropped receipt')
    check(reload['state']['chapter_state_1'] is None, name + ': reload keeps dropped state')
    check(reload['state']['city_status'] == after['city_status'], name + ': reload status stable')
    check(reload['replay_sync_route'] == 0, name + ': replay emits no second syncRoute')
    check(reload['replay_state']['std_rt'] == '4-1', name + ': replay keeps 4-1')
    check(reload['replay_state']['chapter_receipt_539'] is False and reload['replay_state']['chapter_receipt_key_539'] is False,
          name + ': replay keeps receipt absent')

    reset = case['reset_progress']
    check(reset['completed_539'] is False, name + ': resetProgress never retains 539')
    check(reset['week_index'] == 3 and reset['available_534'] is True, name + ': next week 3 entrance')
    check(case['tutorial_foundation'].count(1043) == 1, name + ': 1043 in original foundation')
    check(case['tutorial_foundation'].count(539) == 0, name + ': 539 not in foundation')

    if name == 'foundation_1043':
        check(before['city_status'] == 0 and after['city_status'] == 0, name + ': area1 status stays free')
        check(before['all_area_info_status'] == 0 and after['all_area_info_status'] == 0,
              name + ': area info status stays free')
        check(before['city_data_sha256'] == after['city_data_sha256'], name + ': get_city_data unchanged')
        check(reset['completed_1043'] is True, name + ': resetProgress retains 1043')
        check(reset['status_area1'] == 0, name + ': next week area1 free without 539 replay')
        check(case['effect_observable'] is False, name + ': no observable effect loss')
    elif name == 'foundation_none':
        check(before['city_status'] == after['city_status'] == 2, name + ': bare handoff leaves area1 status 2')
        check(case['effect_observable'] is True and case['bare_handoff'] is True,
              name + ': bare handoff state exposes the dropped areaFree[1]')
    elif name == 'control_1004_only':
        check(before['city_status'] == 1 and after['city_status'] == 1, name + ': control area1 remains FIGHT')
        check(case['effect_observable'] is True, name + ': control shows where the effect would matter')
        check(case['control_only'] is True, name + ': control explicitly non-handoff evidence')
        reset_status = case['reset_progress'].get('status_area1')
        check(reset_status == 1, name + ': 1004-only next week remains FIGHT without 539')
    else:
        raise AssertionError(name)


def validate_candidate_case(name, case):
    before, after = case['before_chain'], case['after_chain']
    expected_area = {'foundation_1043': (0, 0), 'foundation_none': (-1, -1),
                     'control_1004_only': (1, 0)}[name]
    validate_area_reply(name, case, *expected_area)
    check(before['chapter_menu'] == 2 and before['std_rt'] == '1', name + ': legal menu2 handoff')
    check(after['std_rt'] == '4-1', name + ': real 539 route')
    check(case['candidate_effect_applied_by_gateway'] is True, name + ': effect came from the gateway pass')
    check(after['chapter_receipt_539'] is True and after['chapter_receipt_key_539'] is True,
          name + ': gateway writes exactly the 539 receipt')
    check(after['chapter_state_1'] == 0, name + ': gateway writes area1 state 0')
    check(after['chapter_effect_keys'] == ['539'], name + ': exactly one 539 receipt')
    check(after['chapter_state_keys'] == ['1'], name + ': exactly one area1 state')
    check(after['city_status'] == 0, name + ': gateway area1 status 0')
    check(after['story_city_status'] == 0, name + ': gateway story-city status 0')
    check(after['story_city_owns'] is True, name + ': candidate owns the menu2 handoff')
    check('get_all_area_info_reply' in case['chain'][-1]['trace_frames'],
          name + ': gateway 539 trace emits area info projection')
    check(case['candidate_duplicate_unchanged'] is True, name + ': duplicate gateway pass unchanged')
    check(case['seam_profile_unchanged'] is True, name + ': candidate seam receipt-idempotent')

    reload = case['reload']
    check(reload['state']['chapter_receipt_539'] is True and reload['state']['chapter_receipt_key_539'] is True,
          name + ': reload keeps candidate receipt')
    check(reload['state']['chapter_state_1'] == 0 and reload['state']['city_status'] == 0,
          name + ': reload keeps candidate area1 state/status')
    check(reload['state']['chapter_effect_keys'] == ['539'] and reload['state']['chapter_state_keys'] == ['1'],
          name + ': reload keeps exactly one receipt/state')
    check(reload['candidate_reload_unchanged'] is True, name + ': reload gateway pass unchanged')
    check(reload['replay_sync_route'] == 0, name + ': replay emits no second syncRoute')
    check(reload['replay_state']['chapter_receipt_539'] is True and reload['replay_state']['chapter_state_1'] == 0,
          name + ': replay keeps one candidate receipt/state')
    check('candidate_replay_replies' in reload, name + ': replay gateway effect pass ran')
    check(case['reset_progress']['completed_539'] is False, name + ': resetProgress never retains 539')

    regressions = case['candidate_regressions']
    expected = {
        'menu2_transition_owns': True,
        'menu2_no_transition_owns': False,
        'menu3_transition_owns': False,
        'legacy_transition_owns': False,
        'menu25_transition_owns': True,
        'menu4_dedicated_owns': True,
        'menu4_no_transition_owns': False,
        'menu4_an_active': True,
        'menu4_an_locked': True,
        'menu4_shared_locked': True,
        'menu2_7044_an_locked': True,
        'menu2_7044_shared_locked': True,
        'menu2_7044_an_lock_preserved': True,
        'menu2_7044_chapter_lock_written': False,
        'menu2_7044_chapter_lock_keys': [],
        'menu2_7044_receipt_keys': [],
        'menu2_7044_receipt_written': False,
    }
    for key, value in expected.items():
        check(regressions[key] == value, name + ': regression ' + key + '=' + str(value))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', action='store_true')
    parser.add_argument('--prepare', type=Path)
    args = parser.parse_args()
    actual_prepare = args.prepare is not None
    if actual_prepare:
        globals()['PREPARE'] = args.prepare
        globals()['STAGE'] = args.prepare / 'stage'
        globals()['COMPILED'] = args.prepare / 'compiled'
        globals()['OWN'] = args.prepare / 'compiled/production-classes'
        globals()['EVIDENCE'] = ROOT / 'reports/project7-route539-v66-compiled.json'
    candidate_mode = args.candidate or actual_prepare
    evidence_path = CANDIDATE_EVIDENCE if candidate_mode and not actual_prepare else globals()['EVIDENCE']
    fixed_names = ('manager_jar_sha256','event_graph_sha256','weeks_sha256','new_player_sha256','story_city_catalog_sha256')
    fixed_paths = {
        'manager_jar_sha256': MANAGER_JAR,
        'event_graph_sha256': STAGE / 'assets/event_graph.tsv',
        'weeks_sha256': STAGE / 'assets/weeks.tsv',
        'new_player_sha256': STAGE / 'assets/new_player.bson',
        'story_city_catalog_sha256': STAGE / 'assets/project7_story_city/catalog-v1.json.gz',
    }
    if actual_prepare:
        initial = {name: sha(fixed_paths[name]) for name in fixed_names}
        initial['stage_build_inputs_sha256'] = sha(STAGE / 'build-inputs.json')
        initial['compiled_inputs_sha256'] = sha(COMPILED / 'compile-inputs.json')
        for name in fixed_names:
            check(initial[name] == PINS[name][1], name + ' fixed hash changed')
    else:
        initial = {name: sha(path) for name, (path, _) in PINS.items()}
        check(initial == {name: expected for name, (_, expected) in PINS.items()}, initial)
    inventory = json.loads((COMPILED / 'compile-inputs.json').read_text())
    check(len(inventory['classes']) == 253, len(inventory['classes']))
    check(inventory['apk_built'] is False and inventory['dex_built'] is False and inventory['native_verified'] is False,
          'compiled inputs boundary')
    inventory_hashes = {row['path']: row['sha256'] for row in inventory['classes']}
    check({row['path']: sha(OWN / row['path']) for row in inventory['classes']} == inventory_hashes,
          'OWN classes match compile-inputs sha256')
    before_production = dict(inventory_hashes)
    source_hashes = inventory.get('source_hashes') or {}
    for path, digest in source_hashes.items():
        check(Path(path).is_file() and sha(Path(path)) == digest, 'source hash changed: ' + path)
    temp_before = set(Path(tempfile.gettempdir()).glob('route539-effect-*'))
    work = Path(tempfile.mkdtemp(prefix='route539-host-classes-'))
    try:
        platform, tests = work / 'platform', work / 'tests'
        platform.mkdir()
        tests.mkdir()
        sources = sorted(
            [p for p in (ROOT / 'offline/current/java/android_core_rpc/host_stubs').rglob('*.java') if p.name != 'AssetManager.java'] +
            [p for p in (ROOT / 'offline/current/java/android_request_events/host_ending_stubs').rglob('*.java')])
        run(JDK / 'javac', '--release', '8', '-d', platform, *sources)
        dex_classpath = ':'.join(sorted(str(p) for p in DEX_JARS.glob('*.jar')))
        ifacefix = work / 'ifacefix'
        ifacefix.mkdir()
        run(JDK / 'javac', '-nowarn', '-cp', dex_classpath, '-d', ifacefix, IFACE_FIX)
        hostfix = work / 'manager-translated-frames-hostfix.jar'
        fixout = run(JDK / 'java', '-cp', str(ifacefix) + ':' + dex_classpath,
                     'InterfaceCallFix', MANAGER_JAR, hostfix)
        check('interface_call_fixes=2' in fixout, 'manager interface-call repair: ' + fixout)
        manager_jar = hostfix
        base_cp = ':'.join(map(str, (platform, OWN, manager_jar, JSON_JAR)))
        if candidate_mode and not actual_prepare:
            stubs, candidate = work / 'stubs', work / 'candidate'
            stubs.mkdir(); candidate.mkdir()
            run(JDK / 'javac', '--release', '8', '-cp', platform, '-d', stubs,
                *sorted(CANDIDATE_STUBS.rglob('*.java')))
            candidate_cp = ':'.join(map(str, (platform, stubs, OWN, manager_jar, JSON_JAR)))
            run(JDK / 'javac', '--release', '8', '-cp', candidate_cp, '-d', candidate, CANDIDATE_SOURCE)
            classpath = ':'.join(map(str, (platform, candidate, OWN, manager_jar, JSON_JAR)))
        else:
            classpath = base_cp
        run(JDK / 'javac', '--release', '8', '-cp', classpath, '-d', tests, HOST)
        cases_path = work / 'cases.json'
        java_args = [JDK / 'java', '-Xverify:all', '-cp', classpath + ':' + str(tests),
                     'com.project7.localmanager.Route539EffectHost', STAGE / 'assets', cases_path]
        if candidate_mode:
            java_args.append('candidate')
        stdout = run(*java_args)
        cases = json.loads(cases_path.read_text())
        if candidate_mode:
            for key in ('foundation_1043', 'foundation_none', 'control_1004_only'):
                validate_candidate_case(key, cases[key])
            check(cases['facts']['mode'] == 'candidate', 'candidate host mode')
        else:
            for key, expected in (('foundation_1043', False), ('foundation_none', True), ('control_1004_only', True)):
                validate_case(key, cases[key], expected)
            check(cases['facts']['mode'] == 'baseline', 'baseline host mode')
        payload = json.loads((work / 'area_reply_payload.json').read_text())
        check(payload['schema'] == 'project7-route539-area-reply-payload-v1', 'area payload schema')
        check(payload['fixture'] == 'control_1004_only', 'area payload fixture')
        control = cases['control_1004_only']['area_reply']
        for side in ('before', 'after'):
            check(payload[side]['parameters_sha256'] == control[side]['parameters_sha256'],
                  'area payload ' + side + ' parameters sha256')
            check(payload[side]['ais_sha256'] == control[side]['ais_sha256'],
                  'area payload ' + side + ' ais sha256')
            check(payload[side]['cd_sha256'] == control[side]['cd_sha256'],
                  'area payload ' + side + ' cd sha256')
            check(payload[side]['area_1_st'] == control[side]['area_1_st'],
                  'area payload ' + side + ' area_1')
            check((work / ('area_reply_' + side + '.bson')).read_bytes() ==
                  base64.b64decode(payload[side]['parameters_b64']),
                  'area payload ' + side + ' bson bytes')
        check(control['before']['area_1_st'] == 1, 'control ordinary before area_1 FIGHT')
        check(control['after']['area_1_st'] == (0 if candidate_mode else 1),
              'control ordinary after area_1 ' + ('FREE' if candidate_mode else 'FIGHT'))
        check(control['before']['parameters_sha256'] != control['after']['parameters_sha256'],
              'control ordinary payload changes across 539')
        label = 'v66' if actual_prepare else ('candidate' if candidate_mode else 'v65')
        area_json = ROOT / 'reports' / ('project7-route539-area-reply-' + label + '.json')
        area_before = ROOT / 'reports' / ('project7-route539-area-reply-before-' + label + '.bson')
        area_after = ROOT / 'reports' / ('project7-route539-area-reply-after-' + label + '.bson')
        published = dict(payload)
        published['mode'] = 'compiled' if actual_prepare else ('candidate' if candidate_mode else 'baseline')
        published['host_source_sha256'] = sha(HOST)
        published['verifier_sha256'] = sha(Path(__file__))
        area_json.write_text(json.dumps(published, indent=2) + '\n')
        area_before.write_bytes(base64.b64decode(payload['before']['parameters_b64']))
        area_after.write_bytes(base64.b64decode(payload['after']['parameters_b64']))
        check(cases['facts']['q7WeekResult_pre_seeded'] is False, 'no pre-seeded week result')
        check(cases['facts']['route_4_1_pre_seeded'] is False, 'no pre-seeded route')
        check(cases['facts']['area1_result_pre_seeded'] is False, 'no pre-seeded area1 result')
        check(cases['facts']['checks'] > 100, 'host check count')
        if actual_prepare:
            after = {name: sha(fixed_paths[name]) for name in fixed_names}
            after['stage_build_inputs_sha256'] = sha(STAGE / 'build-inputs.json')
            after['compiled_inputs_sha256'] = sha(COMPILED / 'compile-inputs.json')
        else:
            after = {name: sha(path) for name, (path, _) in PINS.items()}
        check(all(after[name] == value for name, value in initial.items()), 'pinned input drift')
        after_production = {row['path']: sha(OWN / row['path']) for row in inventory['classes']}
        check(after_production == before_production, 'production class drift from compile-inputs sha256')
        remaining = set(Path(tempfile.gettempdir()).glob('route539-effect-*')) - temp_before - {work}
        check(not remaining, 'temporary roots remain: %s' % sorted(map(str, remaining)))
        report = {
            'schema': ('project7-route539-effect-host-compiled-v1' if actual_prepare else
                       'project7-route539-effect-host-candidate-v1' if candidate_mode else 'project7-route539-effect-host-v1'),
            'status': 'PASS',
            'mode': 'compiled' if actual_prepare else ('candidate' if candidate_mode else 'baseline'),
            'candidate_label': ('menu2-unclaimed-city-effect-compiled' if actual_prepare else
                                'menu2-unclaimed-city-effect' if candidate_mode else None),
            'frozen_integration': False,
            'prepare': str(PREPARE),
            'stage': str(STAGE),
            'compiled': str(COMPILED),
            'manager_frames': str(MANAGER_JAR),
            'manager_frames_sha256': sha(MANAGER_JAR),
            'manager_hostfix_sha256': sha(manager_jar),
            'manager_interface_call_fixes': 2,
            'area_reply_payload': {
                'schema': payload['schema'],
                'source': 'ordinary loopback handleClient method 5 get_all_area_info_reply',
                'file': str(area_json),
                'before_bson': str(area_before),
                'after_bson': str(area_after),
                'before_sha256': payload['before']['parameters_sha256'],
                'after_sha256': payload['after']['parameters_sha256'],
                'before_area_1_st': payload['before']['area_1_st'],
                'after_area_1_st': payload['after']['area_1_st'],
                'sm': payload['before']['sm'],
                'before_bytes': payload['before']['parameters_bytes'],
                'after_bytes': payload['after']['parameters_bytes'],
            },
            'pins': initial,
            'production_classes': len(inventory['classes']),
            'production_classes_unchanged': True,
            'temporary_roots_removed': True,
            'host_source_sha256': sha(HOST),
            'verifier_sha256': sha(Path(__file__)),
            'candidate_source_sha256': sha(CANDIDATE_SOURCE) if candidate_mode else None,
            'candidate_class_sha256': sha(OWN / 'com/project7/localmanager/StoryCityPolicy.class') if actual_prepare else None,
            'candidate_stub_sha256': (sha(CANDIDATE_STUBS / 'com/project7/localmanager/StoryCityApiStubs.java') if actual_prepare or candidate_mode else None),
            'source_hashes_matched': True,
            'stdout': stdout,
            'cases': cases,
            'commands': [
                'python3 project7_bridge/android/android_project7_startup/proof/week/verify_route539.py' + (' --candidate' if candidate_mode and not actual_prepare else '') + (' --prepare ' + str(PREPARE) if actual_prepare else ''),
                'javac --release 8 (host stubs + host only; ' + ('v66 compiled production classes' if actual_prepare else 'v65 production classes') + ' are inputs)',
                'java InterfaceCallFix f81b-manager.jar <temp>/manager-translated-frames-hostfix.jar',
                'java -Xverify:all -cp platform:' + ('v66' if actual_prepare else 'v65') + '-OWN:f81b-manager-hostfix:json:tests '
                'com.project7.localmanager.Route539EffectHost ' + ('v66' if actual_prepare else 'v65') + '/stage/assets cases.json',
            ],
            'conclusion': {
                'route': 'event 539 writes std.rt 4-1 and emits one real syncRoute',
                'effect': ('event 539 areaFree[1] is applied once for menu2/rt4-1 via the compiled candidate'
                           if actual_prepare else
                           'event 539 areaFree[1] is dropped at the menu2/rt4-1 city ownership boundary '
                           '(no q7ChapterEffects receipt, no q7ChapterStates[1])'),
                'observable_1043': 'with a completed source 1043, resetProgress retains it; area1 status and '
                                    'get_city_data are identical before/after 539 and after reload/replay, so the '
                                    'dropped areaFree[1] is not observable',
                'observable_bare': 'the bare handoff state matching WeekSettlementV63Host (cleared completedEvents, '
                                   'no 1004/1043, high school locked) leaves area1 status 2 before and after 539; '
                                   'areaFree[1] would have made it 0, so the drop is observable there but not '
                                   'for a tutorial-complete source',
                'reset_progress': 'original resetProgress retains 1043 and never retains 539; the next week still '
                                  'projects area1 free without replaying the 539 effect',
                'control': 'the bare handoff state (no 1004/1043) and a synthetic 1004-only source leave area1 '
                           'status 2/1, showing the condition under which the dropped areaFree[1] would be '
                           'observable; only the tutorial-complete 1043/1004 source is equivalent',
                'fix': 'baseline uses frozen v65 OWN classes and still drops the effect. The production source '
                       'candidate adds only the policy opt-in/menu2 ownership; the existing f81b chapter-city rule '
                       'already calls StoryCityPolicy.refresh. Candidate mode compiles that source overlay; no '
                       'prepare/D8/APK/native and no route patch.',
            },
            'candidate_fix': {
                'adopted': False,
                'minimal_shape': 'Decide city-effect ownership from the newly completed event and its declared '
                                 'city effect, not from menu/route constants: at the Gateway effect seam, when no '
                                 'legacy city owner is active, call StoryCityPolicy.refresh and let it accept a '
                                 'known-area effect. No 4-1 or menu2 literal.',
                'why_not_applied': 'StoryCityPolicy.refresh has no production Gateway caller in v65, and the v65 '
                                  'city catalog does not declare menu2 effects. A same-host candidate needs both a '
                                  'production hook and catalog/ownership data, which exceeds a generic ownership '
                                  'change; it is also unnecessary for a tutorial-complete handoff because 1043 is '
                                  'retained.',
                'verification': 'not implemented or run',
            },
            'boundaries': [
                'no prepare/D8/APK/native/emulator',
                'candidate mode compiles the edited StoryCityPolicy.java into a temporary overlay; v65 OWN classes remain untouched',
                'baseline mode does not use or edit the candidate source',
                'status is the actual LocalCityProgress/StoryCityPolicy seam; area info and city data are the '
                'actual BsonLite allAreaInfoReplyDocument/cityDataReplyDocument projections used by the Gateway',
                'client UI/dialogue rendering is not executed',
            ],
        }
        if candidate_mode:
            report['conclusion'] = {
                'route': 'event 539 still writes std.rt 4-1 and one real syncRoute',
                'candidate': 'StoryCityPolicy opt-in unclaimed menu2 ownership accepts the committed handoff and '
                             'adopts only a completed event whose @route equals the active route; 539 areaFree[1] '
                             'writes q7ChapterEffects[539] and q7ChapterStates[1]=0 exactly once.',
                'status': 'after the gateway effect pass, area1 status is 0 for the 1043, none and 1004 foundations; '
                          'the bare/1004 loss seen in baseline is closed.',
                'idempotency': 'duplicate gateway effect pass, Store reload and 539 replay add no second receipt or state.',
                'dedicated': 'menu4/AN 7044 locks remain owned by LocalAnCityEngine; menu3 and legacy menu11/rt12 '
                             'stay unowned; menu25/dedicated owners are unchanged.',
                'integration': 'the existing f81b chapter-city rule '
                               '(LocalStoryRuleRegistry$$ExternalSyntheticLambda4) calls StoryCityPolicy.refresh; '
                               'this candidate uses that seam. It is a source overlay, not prepared/frozen '
                               'integration or a full mainline PASS.',
                'fix': 'candidate source implemented; no prepare/D8/APK/native.',
            }
            report['candidate_fix'] = {
                'adopted': True,
                'frozen_integration': False,
                'source': 'offline/current/java/android_story_city/src/com/project7/localmanager/StoryCityPolicy.java',
                'gateway_caller': 'present: LocalStoryRuleRegistry$$ExternalSyntheticLambda4 -> '
                                  'StoryCityPolicy.refresh (AFTER_ROUTE)',
                'verification': 'reports/project7-route539-effect-host-candidate.json',
            }
        else:
            report['candidate_fix'] = {
                'adopted': True,
                'shown_in_baseline': False,
                'frozen_integration': False,
                'source': 'offline/current/java/android_story_city/src/com/project7/localmanager/StoryCityPolicy.java',
                'verification': 'reports/project7-route539-effect-host-candidate.json',
                'note': 'baseline uses the frozen v65 OWN classes; candidate mode compiles the source overlay',
                'gateway_caller': 'present: LocalStoryRuleRegistry$$ExternalSyntheticLambda4 -> StoryCityPolicy.refresh',
            }
        evidence_path.write_text(json.dumps(report, indent=2) + '\n')
        print('report=' + str(evidence_path.relative_to(ROOT)))
        print('PASS route539 effect host cases=3 checks=' + str(cases['facts']['checks']))
    finally:
        for path in (work,):
            if path.exists():
                for each in sorted(path.rglob('*'), reverse=True):
                    if each.is_file():
                        each.unlink()
                    elif each.is_dir():
                        each.rmdir()
                path.rmdir()
        for path in set(Path(tempfile.gettempdir()).glob('route539-effect-*')) - temp_before:
            if path.is_dir():
                for each in sorted(path.rglob('*'), reverse=True):
                    if each.is_file():
                        each.unlink()
                    elif each.is_dir():
                        each.rmdir()
                path.rmdir()


if __name__ == '__main__':
    main()
