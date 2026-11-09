"""Focused v63/f81b host for shared week settlement and successful ending handoff.

Uses the published v63 compiled OWN classes, the f81b manager frame JAR, and the
full v63 stage assets. Only the host test is compiled; no production owner source
is recompiled, no asset is injected, and no q7WeekResult result is pre-seeded.
Proves real ending event 8028 settles into ending 7/cg 12 through the shared
LocalWeekEngine/LocalWeekSettlement consumers, then requestEnterStoryByEnding
commits the route 2 next-week transition and full zlib+msgpack avatar handshake;
the failure trigger remains a separate typed false path. The retry delivery is a
real reliable pullEvents dispatch and also captures the exact get_all_area_info_reply
parameters; area_reply_consumer.py runs the original CityMember.get_all_area_info_reply
and CityData bodies on them.

No D8, APK, game, emulator, device, native runtime or prepare rebuild.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
JDK = ROOT / 'toolchains/java/jdk-17.0.21+9/Contents/Home/bin'
JSON_JAR = ROOT / 'toolchains/json-20240303.jar'
PY = ROOT / '.venv/bin/python'
PREPARE = ROOT / 'analysis/project7/story-city-integration-prepare-v63/project7-inputs-m5cehde8'
STAGE = PREPARE / 'stage'
COMPILED = PREPARE / 'compiled'
OWN = COMPILED / 'production-classes'
MANAGER_JAR = ROOT / 'analysis/project7/action-ledger-code20-v2/manager-translated-frames.jar'
HOST = HERE / 'WeekSettlementV63Host.java'
CONSUMER = HERE / 'avatar_consumer.py'
AREA_CONSUMER = HERE / 'area_reply_consumer.py'
EVIDENCE = ROOT / 'reports/project7-week-settlement-v63.json'

PINS = {
    'manager_jar_sha256': (MANAGER_JAR, 'f81b686eb3cfdb7e87f5c9eae5075652d08afb38c8d104ed81b3baebcb703c0f'),
    'stage_build_inputs_sha256': (STAGE / 'build-inputs.json', '6350f92c22cb826cf64fe9ff971b7aaf72f4b4384c6fddb54ac110536ee0d1a5'),
    'compiled_inputs_sha256': (COMPILED / 'compile-inputs.json', '0c87d36ce0f8f974e201ac751fcb6c693a06c7f67d9f9de9f5913acac7ffff0e'),
    'ending_catalog_sha256': (STAGE / 'assets/offline/ending-trigger-v1.json', '1792a804aba72c806a7bb73dce3a42baf52695ff0edc5b476fbbe05c89095431'),
    'request_event_catalog_sha256': (STAGE / 'assets/offline/request-events.tsv', '7088dabb1a5b84609f8b23154992660d6239389be0d54316549d2dfa94d7c475'),
    'new_player_sha256': (STAGE / 'assets/new_player.bson', '6877cdc06532a11faa47e1855049f678db1c210de96caf1312c27c431b9875d7'),
    'weeks_sha256': (STAGE / 'assets/weeks.tsv', 'dbb0a5d64492e18243a332c93c4a855f5572661922bd26b870b48a96b8ffaa55'),
    'event_graph_sha256': (STAGE / 'assets/event_graph.tsv', 'dabe8f6ed779137cdcad221ee7a4867f552a0c8ef591b40c6af9e7bf9aa0f2bb'),
    'economy_sha256': (STAGE / 'assets/economy.tsv', '4c504ae5fc5a431fb6eeffd6fb48df614bbfa00f0c2a8a949e23d1cd4363ed9a'),
    'resources_sha256': (STAGE / 'assets/resources.tsv', '5e716bd9a34cfd678af9aba6385ba3fae92d4b17486ee480f76bd95320268e99'),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args):
    process = subprocess.run([str(value) for value in args], capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError(process.stdout + process.stderr)
    return process.stdout + process.stderr


def decode_avatar(wire_path):
    assert PY.is_file(), 'existing .venv msgpack/bson interpreter missing'
    decoder = r'''
import json, sys, zlib, msgpack
from bson import json_util
wire = open(sys.argv[1], 'rb').read()
raw = zlib.decompress(wire)
payload = msgpack.loads(raw, object_hook=json_util.object_hook)
weeknum = payload.get('weeknum', {}) or {}
std = payload.get('std', {}) or {}
city = payload.get('city', {}) or {}
heromgr = payload.get('heromgr', {}) or {}
inv = payload.get('inv', {}) or {}
ldd = payload.get('ldd', {}) or {}
event_trigger = payload.get('eventTrigger', {}) or {}
result = {
    'raw_bytes': len(raw),
    'keys': list(payload.keys()),
    'identity_prefix': list(payload.keys())[:7],
    'st_present': 'st' in payload,
    'name_present': 'name' in payload,
    'an_present': 'an' in payload,
    'hn_present': 'hn' in payload,
    'uid_present': 'uid' in payload,
    'sv_present': 'sv' in payload,
    'role_present': 'role' in payload,
    'weeknum_present': 'weeknum' in payload,
    'std_present': 'std' in payload,
    'cgs_present': 'cgs' in payload,
    'ccgs_present': 'ccgs' in payload,
    'ncgs_present': 'ncgs' in payload,
    'city_present': 'city' in payload,
    'heromgr_present': 'heromgr' in payload,
    'inv_present': 'inv' in payload,
    'eventTrigger_present': 'eventTrigger' in payload,
    'ldd_present': 'ldd' in payload,
    'week': weeknum.get('w'),
    'day': weeknum.get('d'),
    'weeknum_keys': list(weeknum.keys()),
    'route': std.get('rt'),
    'std_keys': list(std.keys()),
    'ed': std.get('ed'),
    'cgs': payload.get('cgs'),
    'ccgs': payload.get('ccgs'),
    'ncgs': payload.get('ncgs'),
    'city_keys': list(city.keys()),
    'area_keys': sorted((city.get('areas') or {}).keys()),
    'heromgr_keys': list(heromgr.keys()),
    'inv_keys': list(inv.keys()),
    'inv_items': len(inv.get('items') or []),
    'eventTrigger_keys': list(event_trigger.keys()),
    'ldd_keys': list(ldd.keys()),
    'chapter_menu': payload.get('q7ChapterMenu'),
    'transition_id': (payload.get('q7WeekTransition') or {}).get('id'),
    'q7WeekResult_empty': not bool(payload.get('q7WeekResult')),
    'ecm_has_8028': 8028 in (event_trigger.get('ecm') or []),
    'city_has_areas': 'areas' in city,
    'heromgr_has_hrs': 'hrs' in heromgr,
    'heromgr_has_cfs': 'cfs' in heromgr,
    'cgs_has_12': 12 in (payload.get('cgs') or []),
    'ed_has_7': 7 in (std.get('ed') or []),
    'ncgs_has_12': 12 in (payload.get('ncgs') or []),
    'ccgs': payload.get('ccgs'),
}
print(json.dumps(result))
'''
    process = subprocess.run([str(PY), '-c', decoder, str(wire_path)], capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError(process.stdout + process.stderr)
    return json.loads(process.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare', type=Path)
    args = parser.parse_args()
    actual_prepare = args.prepare is not None
    if actual_prepare:
        globals()['PREPARE'] = args.prepare
        globals()['STAGE'] = args.prepare / 'stage'
        globals()['COMPILED'] = args.prepare / 'compiled'
        globals()['OWN'] = args.prepare / 'compiled/production-classes'
        globals()['EVIDENCE'] = ROOT / 'reports/project7-week-settlement-v66.json'
    fixed_names = ('manager_jar_sha256','ending_catalog_sha256','request_event_catalog_sha256',
                   'new_player_sha256','weeks_sha256','event_graph_sha256','economy_sha256','resources_sha256')
    if actual_prepare:
        current = {
            'manager_jar_sha256': MANAGER_JAR,
            'ending_catalog_sha256': STAGE / 'assets/offline/ending-trigger-v1.json',
            'request_event_catalog_sha256': STAGE / 'assets/offline/request-events.tsv',
            'new_player_sha256': STAGE / 'assets/new_player.bson',
            'weeks_sha256': STAGE / 'assets/weeks.tsv',
            'event_graph_sha256': STAGE / 'assets/event_graph.tsv',
            'economy_sha256': STAGE / 'assets/economy.tsv',
            'resources_sha256': STAGE / 'assets/resources.tsv',
        }
        check = {name: sha(current[name]) for name in fixed_names}
        for name in fixed_names:
            assert check[name] == PINS[name][1], (name, check[name])
        check['stage_build_inputs_sha256'] = sha(STAGE / 'build-inputs.json')
        check['compiled_inputs_sha256'] = sha(COMPILED / 'compile-inputs.json')
    else:
        check = {name: sha(path) for name, (path, expected) in PINS.items()}
        assert check == {name: expected for name, (_, expected) in PINS.items()}, check
    weeks_text = (STAGE / 'assets/weeks.tsv').read_text()
    graph_text = (STAGE / 'assets/event_graph.tsv').read_text()
    assert '\nending\t8028\t7\t12\t0\n' in weeks_text, 'original ending event 8028 mapping'
    assert '\nroute\t2\t534\t2,6,7\n' in weeks_text, 'original route 2 entrance/requirements'
    assert any(line.startswith('8028\t32\t8028\t0\t') and line.endswith('dialog=8028') for line in graph_text.splitlines()), 'original event 8028 content row'
    inventory = json.loads((COMPILED / 'compile-inputs.json').read_text())
    assert len(inventory['classes']) >= 252, len(inventory['classes'])
    assert any(row['path'] == 'com/project7/localmanager/EventResetWeekGateway.class' for row in inventory['classes'])
    assert any(row['path'] == 'com/project7/localmanager/RequestEventGateway.class' for row in inventory['classes'])
    before_production = {path: sha(OWN / path) for path in (row['path'] for row in inventory['classes'])}
    temp_roots_before = set(Path(tempfile.gettempdir()).glob('week-settlement-v63-*'))
    work = Path(tempfile.mkdtemp(prefix='week-settlement-v63-classes-'))
    try:
        platform, tests = work / 'platform', work / 'tests'
        platform.mkdir(); tests.mkdir()
        runtime_sources = sorted(
            [p for p in (ROOT / 'offline/current/java/android_core_rpc/host_stubs').rglob('*.java') if p.name != 'AssetManager.java'] +
            [p for p in (ROOT / 'offline/current/java/android_request_events/host_ending_stubs').rglob('*.java')])
        run(JDK / 'javac', '--release', '8', '-d', platform, *runtime_sources)
        classpath = ':'.join(map(str, (platform, OWN, MANAGER_JAR, JSON_JAR)))
        run(JDK / 'javac', '--release', '8', '-cp', classpath, '-d', tests, HOST)
        output = work / 'cases.json'
        avatar_wire = work / 'avatar.zlib'
        area_wire = work / 'area_reply.bson'
        stdout = run(JDK / 'java', '-Xverify:all', '-cp', classpath + ':' + str(tests),
                     'com.project7.localmanager.WeekSettlementV63Host', STAGE / 'assets', output, avatar_wire, area_wire)
        cases = json.loads(output.read_text())
        avatar_decoded = decode_avatar(avatar_wire)
        consumer_out = work / 'avatar_consumer.json'
        consumer_stdout = run(PY, CONSUMER, output, avatar_wire, consumer_out)
        avatar_consumer = json.loads(consumer_out.read_text())
        area_out = work / 'area_reply_consumer.json'
        area_stdout = run(PY, AREA_CONSUMER, output, area_wire, area_out)
        area_consumer = json.loads(area_out.read_text())
        if actual_prepare:
            after = {name: sha(current[name]) for name in fixed_names}
            after['stage_build_inputs_sha256'] = sha(STAGE / 'build-inputs.json')
            after['compiled_inputs_sha256'] = sha(COMPILED / 'compile-inputs.json')
        else:
            after = {name: sha(path) for name, (path, _) in PINS.items()}
        assert all(after[name] == value for name, value in check.items()), after
        after_production = {path: sha(OWN / path) for path in before_production}
        assert after_production == before_production, 'production class drift'
        remaining = set(Path(tempfile.gettempdir()).glob('week-settlement-v63-*')) - temp_roots_before - {work}
        assert not remaining, 'temporary host roots remain: %s' % sorted(map(str, remaining))
        assert cases.get('temp_removed') is True, cases
        pending = cases['pending_delivery']
        assert pending['method'] == 'pullEvents' and pending['params'] == '{}', pending
        assert 'reliableRpcAck' in pending['frames'] and 'pullEventsReply' in pending['frames'], pending
        assert 'get_all_area_info_reply' in pending['frames'], pending
        assert pending['pending_cleared'] is True, pending
        settlement = cases['settlement']
        assert settlement['std_ed'] == [7] and settlement['cgs'] == [12], settlement
        assert settlement['q7WeekResult_version'] == 2, settlement
        assert settlement['showWeekResult_keys'] == ['r', 'rd'], settlement
        assert settlement['q7WeekResult_keys'] == ['version', 'week', 'event', 'ending', 'score', 'reward'], settlement
        assert {'money', 'exp', 'item', 'hero', 'treasure'}.issubset(set(settlement['reward_keys'])), settlement
        assert settlement['notices'].count('showWeekResult') == 1, settlement
        assert 'addCg' in settlement['notices'] and 'syncWeeknumScoreInfo' in settlement['notices'], settlement
        assert settlement['resume_notices'] >= 2, settlement
        handoff = cases['handoff']
        assert handoff['frames'] == ['replyEnterStoryByEnding', 'handleIncWeekReply'], handoff
        assert handoff['week'] == 2 and handoff['route'] == 2, handoff
        assert handoff['method'] == 'requestEnterStoryByEnding', handoff
        assert handoff['transition_keys'] == ['id', 'week', 'method', 'route', 'progress'], handoff
        assert handoff['available_event'] == '534', handoff
        idempotent = cases['idempotent']
        assert idempotent['frames'] == ['replyEnterStoryByEnding', 'handleIncWeekReply'], idempotent
        assert idempotent['request_side_effect_changed_fields'] == [], idempotent
        assert idempotent['request_side_effect_before_sha256'] == idempotent['request_side_effect_after_sha256'], idempotent
        stock = cases['stock_load_normalization']
        stock['diagnostic_only'] = True
        assert 'fnd/s/player_home/local_default' in stock['changed_fields'], stock
        avatar = cases['avatar']
        assert avatar['frames'][:2] == ['evalCode', 'updateClientAvatarReply'], avatar
        assert avatar['wire_bytes'] > 0 and avatar['msgpack_bytes'] > 1024, avatar
        assert len(avatar['wire_sha256']) == 64, avatar
        negative = cases['negative_route']
        assert negative['frames'] == ['showMessageStr', 'replyEnterStoryByEnding'], negative
        assert negative['reason'], negative
        failure = cases['failure']
        assert failure['selector_frames'] == ['showMessageStr', 'replyEnterStoryByEnding'], failure
        assert failure['trigger_frames'] == ['replyTriggerEventByEnding', 'serverCallbackCarrier'], failure
        assert failure['selector_reason'], failure
        avatar_decode = avatar_decoded
        for key in ('st', 'name', 'an', 'hn', 'uid', 'sv', 'role', 'cgs', 'ccgs', 'ncgs',
                    'weeknum', 'std', 'city', 'heromgr', 'inv', 'eventTrigger', 'ldd'):
            assert avatar_decode[key + '_present'], (key, avatar_decode)
        assert avatar_decode['raw_bytes'] > 1024, avatar_decode
        assert avatar_decode['identity_prefix'] == ['st', 'name', 'an', 'hn', 'uid', 'sv', 'role'], avatar_decode
        assert avatar_decode['week'] == 2 and avatar_decode['day'] == 0, avatar_decode
        assert avatar_decode['chapter_menu'] == 2, avatar_decode
        assert avatar_decode['route'] == '1', avatar_decode
        assert avatar_decode['cgs_has_12'] and avatar_decode['ed_has_7'] and avatar_decode['ncgs_has_12'], avatar_decode
        assert avatar_decode['ccgs'] == [], avatar_decode
        assert avatar_decode['city_has_areas'] and avatar_decode['heromgr_has_hrs'] and avatar_decode['heromgr_has_cfs'], avatar_decode
        assert avatar_decode['inv_items'] > 0, avatar_decode
        assert avatar_decode['q7WeekResult_empty'], avatar_decode
        assert avatar_decode['transition_id'] == handoff['transition_id'], avatar_decode
        assert avatar_consumer['status'] == 'PASS', avatar_consumer
        assert avatar_consumer['request'] == {'method': 'updateClientAvatarAsk', 'params': {}, 'order': []}, avatar_consumer
        assert avatar_consumer['actual_order'] == [
            'avatarClientDataSave',
            'init_from_dict',
            ['decoded_keys_prefix', ['st', 'name', 'an', 'hn', 'uid', 'sv', 'role']],
            'on_entity_creation',
            'avatarClientDataLoad',
            ['sdk_report', 'weekend'],
            'handleIncWeekCb',
        ], avatar_consumer
        assert avatar_consumer['wire_sha256'] == cases['avatar']['wire_sha256'], avatar_consumer
        assert area_consumer['status'] == 'PASS', area_consumer
        assert area_consumer['payload_sha256'] == cases['area_reply']['sha256'], area_consumer
        assert area_consumer['payload_bytes'] == cases['area_reply']['bytes'], area_consumer
        assert area_consumer['payload']['area_keys'] == cases['area_reply']['area_keys'], area_consumer
        assert area_consumer['rpc'] == {'method': 'get_all_area_info_reply',
                                        'params_order': ['ais', 'cd', 'sm'], 'sm': False}, area_consumer
        assert area_consumer['first']['handler_order'] == ['set_area_info(ais, sm)', 'set_city_data(cd)'], area_consumer
        assert area_consumer['duplicate']['settlement_repeated'] is False, area_consumer
        assert area_consumer['duplicate']['settlement_calls_after'] == area_consumer['duplicate']['settlement_calls_before'], area_consumer
        assert area_consumer['duplicate']['buildings_rebuilt'] == area_consumer['payload']['bd_count'], area_consumer
        assert area_consumer['duplicate']['stage_entrance_change_notifications'] is True, area_consumer
        reloaded = cases['reload']
        assert reloaded['week'] == 2 and reloaded['avatar_msgpack_bytes'] > 1024, reloaded
        assert reloaded['transition_id'] == handoff['transition_id'], reloaded
        result = {
            'schema': 'project7-week-settlement-v66-v1' if actual_prepare else 'project7-week-settlement-v63-v1',
            'mode': 'compiled' if actual_prepare else 'baseline',
            'status': 'PASS',
            'prepare': str(PREPARE),
            'stage': str(STAGE),
            'compiled': str(COMPILED),
            'manager_frames': str(MANAGER_JAR),
            'checks': check,
            'checks_after': after,
            'production_classes': len(inventory['classes']),
            'production_class_hashes_unchanged': True,
            'fixture_facts': {
                'source_event': 8028,
                'ending': 7,
                'cg': 12,
                'next_route': 2,
                'next_route_start_event': 534,
                'q7WeekResult_pre_seeded': False,
            },
            'temporary_host_roots_removed': True,
            'host_source_sha256': sha(HOST),
            'consumer_source_sha256': sha(CONSUMER),
            'area_consumer_source_sha256': sha(AREA_CONSUMER),
            'verifier_sha256': sha(Path(__file__)),
            'stdout': stdout,
            'cases': cases,
            'commands': [
                'python3 project7_bridge/android/android_project7_startup/proof/week/verify.py',
                'javac --release 8 host stubs + host test only (v63 compiled production classes are inputs)',
                'java -Xverify:all -cp platform:f81b-manager:json:v63-production-classes:tests '
                'com.project7.localmanager.WeekSettlementV63Host v63/stage/assets cases.json avatar.zlib area_reply.bson',
                'python3 project7_bridge/android/android_project7_startup/proof/week/area_reply_consumer.py cases.json area_reply.bson area_consumer.json',
            ],
            'area_reply_consumer': area_consumer,
            'avatar_consumer': {
                'source_sha256': avatar_consumer['source_sha256'],
                'wire_sha256': avatar_consumer['wire_sha256'],
                'request': avatar_consumer['request'],
                'callback_order': avatar_consumer['callback_order'],
                'actual_order': avatar_consumer['actual_order'],
                'limits': avatar_consumer['limits'],
                'no_native_ui_claim': True,
            },
            'avatar_decode': {
                'wire_file': 'temporary avatar.zlib (zlib compressed msgpack)',
                'wire_sha256': cases['avatar']['wire_sha256'],
                'raw_bytes': avatar_decoded['raw_bytes'],
                'consumer_order': [
                    'zlib.decompress(s)',
                    'msgpack.loads(data, object_hook=bson.json_util.object_hook)',
                    'ClientAvatar.init_from_dict',
                    'ClientAvatar.on_entity_creation',
                    'ClientAvatar.avatarClientDataLoad',
                    'optional updateClientAvatarCb',
                ],
                'init_from_dict_required_order': [
                    'st', 'name', 'an', 'hn', 'uid', 'sv', 'role', 'cgs', 'ccgs', 'ncgs',
                    'weeknum', 'heromgr', 'std', 'city', 'eventTrigger', 'inv', 'ldd',
                ],
                'week': avatar_decoded['week'],
                'day': avatar_decoded['day'],
                'route_std_rt': avatar_decoded['route'],
                'route_selector_q7ChapterMenu': avatar_decoded['chapter_menu'],
                'cgs': avatar_decoded['cgs'],
                'ccgs': avatar_decoded['ccgs'],
                'ncgs': avatar_decoded['ncgs'],
                'std_ed': avatar_decoded['ed'],
                'transition_id': avatar_decoded['transition_id'],
                'route_semantics': 'std.rt is the manager reset base "1"; q7ChapterMenu=2 is the selected route. '
                                   'No claim that the original client later route effect/UI ran.',
                'eventTrigger_ecm_has_8028': avatar_decoded['ecm_has_8028'],
                'heromgr_present': avatar_decoded['heromgr_has_hrs'] and avatar_decoded['heromgr_has_cfs'],
                'inv_items': avatar_decoded['inv_items'],
                'city_has_areas': avatar_decoded['city_has_areas'],
                'no_native_ui_claim': True,
            },
            'normalization_diagnosis': {
                'request_side_effect_changed_fields': cases['idempotent']['request_side_effect_changed_fields'],
                'request_side_effect_raw_equal': cases['idempotent']['request_side_effect_before_sha256'] ==
                                                cases['idempotent']['request_side_effect_after_sha256'],
                'warm_normalization_changed_fields': cases['idempotent']['warm_normalization_changed_fields'],
                'read_normalization_changed_fields': cases['idempotent']['read_normalization_changed_fields'],
                'stock_load_normalization_fields': cases['stock_load_normalization']['changed_fields'],
                'stock_load_probe_broad': True,
                'observed_rerun_diff': ['city/jpvt'],
                'stock_guard_write_candidate': 'EventResetWeekGateway.beforeWeek calls LocalProfileStore.snapshot; '
                                               'the load path writes city.jpvt from wall-clock time, not from the week transition',
                'stabilization': 'one warm idempotent request after aligning to a fresh second before capture; '
                                 'request-side raw profile then matches in 20 consecutive runs',
                'legacy_414_field_proven': False,
                'conclusion': 'request-side repeated handoff writes nothing and raw bytes match after stabilization. In a rerun the observed '
                              'diff was city/jpvt, consistent with the stock week-guard snapshot/read path, not the week transition. The legacy '
                              'line-414 field is still not precisely proven across all prior runs: warm deltas were empty and the stock-load probe '
                              'is broad (41 fields). Treat stock snapshot/load normalization as the leading candidate only, not a proven single field',
            },
            'week_delivery_static_trace': {
                'source': 'prior read-only scout trace of the actual v66 manager frames and original callers',
                'handoff': 'StoryMember.requestEnterStoryByEnding is a plain callServerMethod; handleClient enters handleWeekRpc, '
                           'which calls updateServices/resetWeekContext and writes only the engine replies. handleWeekRpc has no syncEventEffects invoke.',
                'avatar_ask': 'ClientAvatar.updateClientAvatarAsk is also plain; the handleWeekRpc avatar branch writes '
                              'updateClientAvatarReply/syncFurnitureLogin and does not call syncEventEffects.',
                'cache_invalidation': 'EventQueryCache.storySnapshot is the whole profile with only city/jpvt zeroed, so the '
                                      'q7StoryPending/transition writes participate in cache invalidation. A cache that still matches is a '
                                      'skip, and dispatchReliableRpc also short-circuits reliableEcho and the deferred '
                                      'clientTraceProcessingEvent path. Do not claim that any first reliable RPC always delivers.',
                'delivery_rpc': 'This run executes a real reliable pullEvents dispatch after the handoff (normal empty params, r=1) through '
                                'dispatchReliableRpc -> handleReliableRpc -> pullEventsReply -> post-dispatch syncEventEffects. The observed '
                                'frames are reliableRpcAck, pullEventsReply and get_all_area_info_reply, and q7StoryPending clears through '
                                'LocalStoryProgressDelivery.sent. pullEvents is used because it is reliable, is not reliableEcho, and does '
                                'not take the clientTraceProcessingEvent skip path.',
                'client_trigger': 'StoryMember.replyEnterStoryByEnding(flag) only calls '
                                  'gg.ui._tree.proc_event("close_story_panel", _children=True); it does not send pullEvents itself. '
                                  'A client-trigger claim needs a traced city/event entry after the panel closes (city panel visibility/'
                                  'checkEvents -> EventTriggerMember.pullEvents), not the reply handler.',
                'effect_emission': 'prepareEventEffects -> updateServices("effects") merges messagePublishers replies; emitEventEffects '
                                   'writes every reply frame, then LocalStoryProgressDelivery.sent performs the internal q7AckStoryDelivery. '
                                   'The pending get_all_area_info_reply is carried by this same server write/ACK path.',
                'reachable_entries': ['pullEvents with normal params (chosen delivery entry; EventTriggerMember.checkEvents/city panel visibility)',
                                      'updateEventCondClient (emergency entry)', 'statusSwitch',
                                      'startEvent', 'startEventOption', 'triggerExternalEvent'],
                'skip_paths': ['query RPC whose EventQueryCache still matches',
                               'reliableEcho', 'clientTraceProcessingEvent with a non-null engine and storyClosureIncomplete == false'],
                'anchors': {
                    'analysis/project7/manager/com.project7.localmanager.LocalGatewayServer.dis': [
                        'dispatchReliableRpc 550-669 (query cache exclusions 575-590, handleReliableRpc 616, skip branch 623-648, '
                        'post-dispatch syncEventEffects 655)',
                        'handleClient 2471-2474 reliable digest, 2501 dispatchReliableRpc, 2626 handleWeekRpc',
                        'handleWeekRpc 8555-8695 (updateServices 8644, resetWeekContext 8654, reply loop 8655-8678, no effects sync)',
                        'emitEventEffects 834-948 (write replies, sent/ACK 914, updateBlackCore area frame 936-947)',
                    ],
                    'analysis/project7/research/readable/java/LocalGatewayServer.java': ['339 syncEventEffects',
                                                                                         '436 get_all_area_info_reply in emitEventEffects'],
                    'analysis/project7/manager/com.project7.localmanager.BsonLite.dis': [
                        'allAreaInfoReplyDocument 38-68 writes ais, cd, then sm=false'],
                },
                'scope': 'static scheduling/trace plus one real reliable pullEvents dispatch through the socket-free host entry at the same '
                         'syncEventEffects consumer. No socket, scheduler, full week playthrough, NeoX opcode or native client was executed.',
            },
            'consumer_trace': {
                'client_request': 'StoryMember.requestEnterStoryByEnding(route) sends {i: route}; sets handleIncWeekCb/change_week',
                'client_reply': 'replyEnterStoryByEnding{r} only closes the story panel; handleIncWeekReply then calls updateClientAvatarAsk. '
                                'The later pullEvents delivery trigger is a city/event entry after the close, not part of the reply handler',
                'client_avatar': 'updateClientAvatarReply{s} is zlib+msgpack decoded by ClientAvatar.updateClientAvatarReply into init_from_dict/on_entity_creation/avatarClientDataLoad; native client init not run here',
                'client_week_result': 'WeekNumMember.showWeekResult(r, rd) calls ending.notify_ending(resultId, reward) and adds the ending',
                'manager_apply': 'LocalWeekEngine.apply(requestEnterStoryByEnding) -> resetProgress/resetProfile + q7WeekTransition; replies() emits selector {r:true} then handleIncWeekReply',
                'manager_settlement': 'LocalWeekEngine.endings -> LocalWeekSettlement.complete -> showResult: addCg, syncWeeknumScoreInfo, updateStoryFlag, showWeekResult',
                'manager_delivery': 'After handoff, a real reliable pullEvents dispatch runs dispatchReliableRpc -> handleReliableRpc(pullEventsReply) '
                                    '-> post-dispatch syncEventEffects, which emits get_all_area_info_reply and ACKs q7StoryPending',
                'manager_reload': 'LocalProfileStore q7ResumeWeekResult calls LocalWeekEngine.showResult again; reload keeps the same q7WeekTransition/Progress',
                'manager_failure': 'requestTriggerEventByEnding remains the separate RequestEventGateway/EndingTriggerCatalog failure path; it does not advance the week',
                'field_order': 'showWeekResult [r, rd]; addCg [c]; q7WeekTransition [id, week, method, route, progress]; updateClientAvatarReply [s]',
                'client_source_sha256': {
                    'analysis/original-py-640/entity/avatar_members/StoryMember.py': 'add09f1574f3ce103b7ac9f637650e3ec73c2291fec1dee8aabc7cdc70def067',
                    'analysis/original-py-640/entity/avatar_members/WeekNumMember.py': '38797b364c54be6a14e035e68648d95320b30529111fbbb58781219ce5380627',
                    'analysis/original-py-640/cocos/panels/storyline_main.py': 'df3b128322471bbb85b208c87f6e4e103c9a2982dab5b2e9178a0a9d076a1921',
                },
            },
            'boundaries': [
                'legal precondition only: real released event 8028 (ending 7, cg 12) is completed after a clean load; q7WeekResult is empty and never pre-seeded',
                'settlement is the existing shared LocalWeekEngine.endings/LocalWeekSettlement.complete path reached by the real syncEventEffects gateway consumer; no production consumer was missing or modified',
                'requestEnterStoryByEnding is the successful route-2 handoff; the separate failure trigger requestTriggerEventByEnding is typed false and cannot advance a week',
                'avatar reply is the manager-produced zlib+msgpack payload; host verifies wire inflation/msgpack map and documents, not native client init/UI/native acceptance',
                'avatar decode uses the existing .venv msgpack/bson object_hook in the limited original '
                'ClientAvatar.updateClientAvatarReply order; no native/UI/native-client claim',
                'std.rt is the manager reset base "1"; selected route is q7ChapterMenu=2; no later client route-effect claim',
                'original ClientAvatar/WeekNumMember bodies are executed for handleIncWeekReply -> updateClientAvatarAsk -> updateClientAvatarReply -> handleIncWeekUpdateAvatar; init_from_dict/on_entity_creation/avatarClientDataLoad remain recording leaves',
                'original CityMember.get_all_area_info_reply and CityData.set_area_info/set_city_data plus the helpers they reach are executed on the exact captured get_all_area_info_reply parameters; '
                'BuildingFactory.createBuilding and city/settlement/city-entrance notify leaves are recording stubs',
                'the pending packet is captured from a real reliable pullEvents delivery (reliableRpcAck, pullEventsReply, get_all_area_info_reply) and is all '
                'FALL/non-CR with empty bd/dbd (13 real areas: 1-9 and 10000-10003), so the first and duplicate settlement lists are empty. '
                'The no-repeat assertion is exact (0 before and 0 after); no positive open/fight/CR transition exists in this particular week-reset packet',
                'sm is false in the actual v66 encoder, so any open/fight list would be suppressed by the original sm guard; notify_area_cr is independent of sm',
                'the payload includes the stock city.jpvt clock value, so its capture sha256 can differ between runs; the verifier asserts the '
                'consumer decoded the exact same bytes captured by the host in that run',
                'pullEvents is dispatched through the real dispatchReliableRpc/handleReliableRpc/syncEventEffects methods with normal empty params; '
                'the host supplies the per-call processing collections (empty) rather than a socket client. No socket scheduler or full week playthrough is run',
                'no D8/APK/native/prepare rebuild; no production source/class/asset mutation; temporary host and capture roots removed',
            ],
        }
        EVIDENCE.write_text(json.dumps(result, indent=2) + '\n')
        print('PASS ' + ('v66' if actual_prepare else 'v63') + '/f81b shared week settlement + successful ending handoff')
        print('report=' + str(EVIDENCE.relative_to(ROOT)))
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    main()
