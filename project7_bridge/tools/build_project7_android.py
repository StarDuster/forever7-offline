"""Assemble the fixed Project7 original-APK build after static/javac preparation.

Import and preflight are read-only. Calling build is an explicit future assembly
operation: D8, ZIP, development signing, verification, then atomic publication.
No emulator, device, install or game execution exists in this module.
"""
from __future__ import annotations
import _bootstrap  # noqa: E402,F401
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import tempfile
import zipfile
import re
from extract_scripts import ScriptArchive

from project7_compile import verify_stage
from project7_component import PINS, COMPONENT_SHA256, DEXES, npk
from project7_build_inputs import validate_loader, patch_manifest
from project7_dex_filter import definitions, REMOVE
from verify_manager_field_opcodes import verify as verify_manager_field_opcodes, verify_coc_wrapper_entry
from project7_feature_hooks import PINS as FEATURE_HOOK_PINS
from project7_feature_assets import (HISTORY_CATALOG, HISTORY_CATALOG_SHA,
                                    REQUEST_EVENT_CATALOG, REQUEST_EVENT_CATALOG_SHA, history_ui_policy,
                                    ENDING_TRIGGER_CATALOG, ENDING_TRIGGER_CATALOG_SHA,
                                    FURNITURE_CATALOG, FURNITURE_CATALOG_SHA, furniture_ui_policy,
                                    DREAM_CATALOG, DREAM_CATALOG_SHA, EVENT_RESET_CATALOG, EVENT_RESET_CATALOG_SHA,
                                    SELECTOR_CATALOG, SELECTOR_CATALOG_SHA, selector_ui_policy,
                                    BAIYE_CATALOG, BAIYE_CATALOG_SHA, BAIYE_FRAGMENTS, BAIYE_FRAGMENTS_SHA,
                                    DYNAMIC_CATALOG, DYNAMIC_CATALOG_SHA, BAIYE_SHOP_CATALOG, BAIYE_SHOP_CATALOG_SHA,
                                    dynamic_ui_policy, DYNAMIC_PUBLIC_READY_IDS,
                                    WISH_CATALOG, WISH_CATALOG_SHA, WISH_PUBLIC_READY_IDS, wish_ui_policy,
                                    STORY_MISSION_CATALOG, STORY_MISSION_CATALOG_SHA,
                                    STORY_MENU_SHARED_CATALOG, STORY_MENU_SHARED_CATALOG_SHA,
                                    MENU10_ENTRY_CATALOG, MENU10_ENTRY_CATALOG_SHA,
                                    STORY_EXTENDED_ASSETS, STORY_CITY_EXTENDED_ASSETS)
MANAGER_SHA = '0b4c41a5461840fb7bdb02529732a2c6849d604893b6a9390b9a9404618d0eb4'
FINAL_STORY_EXTENDED_ASSETS = dict(STORY_EXTENDED_ASSETS, **STORY_CITY_EXTENDED_ASSETS)

from _bootstrap import ROOT
from forever7_paths import java_module_root
RESOURCE_MANIFEST = 'assets/offline_resource_manifest.json'
RESOURCE_MANIFEST_SHA = 'c2e926909541ea2070f58a3b5c702c8989c10db081d299abb6f1fc193ec8ae4f'
PLAN_SHA = '647a1ec62aa56d87a291ce1b9121cbd3a97cf5c00fa71e97d1f6e1d283080675'
DRAW_CATALOG = 'assets/project7_draw_policy/catalog-v2.tsv'
DRAW_CATALOG_SHA = 'e250ace8d74eaf87769a709532e5a4e1ae69eb2d1acfedf520b79e0323136319'
DEV_PASSWORD = 'forever7-local-dev'
REQUIRED = frozenset({
    'Lcom/forever7/offline/Project7ResourceInitActivity;',
    'Lcom/forever7/offline/Project7BundledResources;',
    'Lcom/forever7/offline/Project7RepairHost;',
    'Lcom/forever7/offline/Project7RepairProtocol;',
    'Lcom/netease/qrzd/Project7LoginDialog;',
    'Lcom/project7/localmanager/CoreGapBridge;',
    'Lcom/project7/localmanager/CoreDrawPolicy;',
    'Lcom/project7/localmanager/DrawPolicyCatalog;',
    'Lcom/project7/localmanager/DrawPolicyBson;',
    'Lcom/project7/localmanager/HistoryDrawPolicy;',
    'Lcom/project7/localmanager/HistoryCatalog;',
    'Lcom/project7/localmanager/HistoryBson;',
    'Lcom/project7/localmanager/HistoryFurniturePolicy;',
    'Lcom/project7/localmanager/SelectorPolicy;',
    'Lcom/project7/localmanager/DynamicDrawPolicy;',
    'Lcom/project7/localmanager/BaiyeGateway;',
    'Lcom/project7/localmanager/BaiyeShopGateway;',
    'Lcom/project7/localmanager/BaiyeTransactions;',
    'Lcom/project7/localmanager/InventoryEditorGateway;',
    'Lcom/project7/localmanager/StoryBasicsGateway;',
    'Lcom/project7/localmanager/WishGateway;',
    'Lcom/project7/localmanager/TrialRetryGateway;',
    'Lcom/project7/localmanager/WishDrawPolicy;',
    'Lcom/project7/localmanager/StoryMissionBridge;',
    'Lcom/project7/localmanager/DreamCoordinator;',
    'Lcom/project7/localmanager/DreamRequestGateway;',
    'Lcom/project7/localmanager/DreamPatrolGatewayHooks;',
    'Lcom/project7/localmanager/DreamEconomyPolicy;',
    'Lcom/project7/localmanager/DreamWeekPolicy;',
    'Lcom/project7/localmanager/EventResetWeekPolicy;',
    'Lcom/project7/localmanager/EventResetWeekGateway;',
    'Lcom/project7/localmanager/DreamPatrolReply;',
    'Lcom/project7/localmanager/OfflineMechanismGateway;',
    'Lcom/project7/localmanager/RequestEventGateway;',
    'Lcom/project7/localmanager/RequestEventCatalog;',
    'Lcom/project7/localmanager/RequestEventAdmission;',
    'Lcom/project7/localmanager/CgRewardPlan;',
    'Lcom/project7/localmanager/FullCollectionInitializer;',
    'Lcom/project7/localmanager/StableIdentityBootstrap;',
    'Lcom/project7/localmanager/SinglePackageGateway;',
    'Lcom/project7/localmanager/Project7StartupCoordinator;'})
GAME_SHA256 = {
    'classes.dex': '9bc9bc424cb76936ad6b1893c135849b2bfaf7349462a5d41eb92b858bd23c1c',
    'classes2.dex': 'ddbb61e1946a900f0bd9cf408ee654f73589cdbecbda7b96df59c4f3a1e5aac0',
    'classes3.dex': 'bc89db68cf8df44f04621ec7387e222fafefcbe6a951a777007cb8b020943a4c',
    'classes4.dex': '55ba79bb0fbf261822c594b8a7c4f616cec615dd364ff1205d9e2f51dac95f4b',
    'classes5.dex': 'ea827ddfd9f219bd5f7dcfa321e6960790c6993bbfc4827188a2095efffa3b12'}
SOURCE_DIRS = ('android_resource_init', 'android_single_package', 'android_autologin',
               'android_collection', 'android_project7_startup', 'android_project7_repair', 'android_core_rpc',
               'android_draw_policy', 'android_history_draw', 'android_selector_draw', 'android_dynamic_draw', 'android_request_events',
               'android_dream_mode', 'android_week_reset', 'android_story_missions', 'android_trial_retry', 'android_baiye_transactions', 'android_baiye_shop', 'android_story_basics', 'android_story_city', 'android_story_shared', 'android_wish_draw', 'android_mechanism_gateway')
STUBS = ('offline/current/java/android_single_package/compile_stubs/com/project7/localmanager/ManagerApiStubs.java',
         'offline/current/java/android_autologin/compile_stubs/com/netease/neox/NativeInterface.java')
def _startup_source(root, name):
    from forever7_paths import runtime_source
    return runtime_source(name)


STARTUP_SOURCE_HASHES = (
    ('project7_startup_hook.py', 'hook_source_sha256'),
    ('offline_tutorials.py', 'tutorial_source_sha256'),
    ('project7_tutorial_completion.py', 'tutorial_completion_source_sha256'),
    ('project7_trial_retry_compat.py', 'trial_retry_compat_source_sha256'),
    ('android_trial_retry/trial-ui-policy-v1.json', 'trial_retry_ui_policy_sha256'),
    ('project7_collection_visibility.py', 'collection_source_sha256'),
    ('project7_collection_visibility/policy.json', 'collection_policy_sha256'),
    ('project7_shadow_capacity.py', 'capacity_source_sha256'),
    ('project7_shadow_capacity/policy.json', 'capacity_policy_sha256'),
    ('project7_draw_ui.py', 'draw_ui_source_sha256'),
    ('project7_furniture_ui.py', 'furniture_ui_source_sha256'),
    ('project7_friend_ui.py', 'friend_ui_source_sha256'),
    ('project7_selector_ui.py', 'selector_ui_source_sha256'),
    ('project7_dynamic_ui_families.py', 'dynamic_ui_source_sha256'),
    ('project7_wish_ui.py', 'wish_ui_source_sha256'),
    ('project7_wish_transport.py', 'wish_transport_source_sha256'),
    ('project7_inventory_editor_ui.py', 'inventory_ui_source_sha256'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def file_sha(path):
    with Path(path).open('rb') as stream:
        return stream_sha(stream)


def stream_sha(stream):
    value = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        value.update(block)
    return value.hexdigest()


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'Duplicate JSON member')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)


def safe_name(name):
    require(isinstance(name, str) and name and '\\' not in name and '\0' not in name,
            'Unsafe member path')
    path = PurePosixPath(name)
    require(not path.is_absolute() and all(part not in ('', '.', '..') for part in name.split('/')),
            'Unsafe member path')
    return name


def stage_path(root, name):
    safe_name(name)
    path = root / name
    require(not root.is_symlink() and path.resolve().is_relative_to(root.resolve()),
            'Symlink/outside inventory member')
    current = root
    for part in PurePosixPath(name).parts:
        current = current / part
        require(not current.is_symlink(), 'Symlink inventory member')
    return path


def is_signature(name):
    upper = name.upper()
    if not upper.startswith('META-INF/'):
        return False
    leaf = upper[len('META-INF/'):]
    return '/' not in leaf and (leaf == 'MANIFEST.MF' or leaf.startswith('SIG-') or
                               leaf.endswith(('.SF', '.RSA', '.DSA', '.EC')))


def zip_inventory(archive, ignore_signatures=False):
    result = {}
    for info in archive.infolist():
        name = info.filename
        require(name not in result, 'Duplicate ZIP path')
        safe_name(name[:-1] if name.endswith('/') else name)
        require(not info.flag_bits & 1 and info.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED),
                'Encrypted/unsupported ZIP payload')
        require(((info.external_attr >> 16) & 0o170000) in (0, 0o100000, 0o040000),
                'ZIP symlink/special payload')
        with archive.open(info) as stream:
            digest = stream_sha(stream)
        result[name] = {'bytes': info.file_size, 'sha256': digest}
    if ignore_signatures:
        return {name: row for name, row in result.items() if not is_signature(name)}
    return result


def class_name(data):
    """Read only class-file constant pool/internal name, never load bytecode."""
    require(len(data) >= 10 and data[:4] == b'\xca\xfe\xba\xbe', 'Invalid Java class header')
    count = struct.unpack_from('>H', data, 8)[0]
    offset, index, pool, tags = 10, 1, {}, {}
    while index < count:
        require(offset < len(data), 'Truncated class constant pool')
        tag = data[offset]
        tags[index] = tag
        offset += 1
        if tag == 1:
            require(offset + 2 <= len(data), 'Truncated class UTF8 size')
            size = struct.unpack_from('>H', data, offset)[0]
            offset += 2
            require(offset + size <= len(data), 'Truncated class UTF8')
            pool[index] = data[offset:offset + size]
            offset += size
        elif tag in (7, 8, 16, 19, 20):
            require(offset + 2 <= len(data), 'Truncated class reference')
            pool[index] = struct.unpack_from('>H', data, offset)[0]
            offset += 2
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            offset += 4
        elif tag in (5, 6):
            offset += 8
            index += 1
        elif tag == 15:
            offset += 3
        else:
            raise ValueError('Unsupported class constant tag')
        require(offset <= len(data), 'Truncated class constants')
        index += 1
    require(offset + 6 <= len(data), 'Truncated class identity')
    this_class = struct.unpack_from('>H', data, offset + 2)[0]
    require(tags.get(this_class) == 7 and tags.get(pool.get(this_class)) == 1, 'Invalid class identity constant type')
    value = pool.get(pool.get(this_class))
    require(isinstance(value, bytes), 'Invalid class identity reference')
    name = value.decode('ascii')
    safe_name(name)
    require(re.fullmatch(r'[A-Za-z_$][A-Za-z0-9_$/]*', name) is not None, 'Invalid internal class name')
    return name


def family(descriptor):
    return descriptor.rstrip(';').split('$', 1)[0] + ';'


def source_family(path):
    source = path.read_text(encoding='utf-8')
    match = re.search(r'^\s*package\s+([A-Za-z_][A-Za-z0-9_.]*)\s*;', source, re.MULTILINE)
    require(match is not None, 'Production source package missing')
    return 'L' + match.group(1).replace('.', '/') + '/' + path.stem + ';'


SYNTHETIC_D8_ALLOWED = {'Lcom/android/tools/r8/annotations/LambdaMethod;'}


def check_collisions(own, game, manager, expected, allowed):
    require(REQUIRED <= own and expected <= own, 'Required compiled definition missing from own DEX')
    # D8 emits this synthetic annotation interface for lambda metadata; it has
    # only abstract getters and no code/data. It is not an API stub or source
    # feature and cannot collide with game/manager classes.
    allowed = set(allowed) | SYNTHETIC_D8_ALLOWED
    unexpected = sorted(name for name in own if family(name) not in allowed)
    require(not unexpected, 'Unexpected own DEX/API-stub definition: ' + ', '.join(unexpected[:16]))
    require(not own.intersection(manager.union(*game)), 'Own DEX collides with original game/manager')
    require(not manager.intersection(set().union(*game)), 'Manager collides with game definitions')
    # Existing duplicate definitions among the five pinned game DEX are not new
    # own-class collisions (original APK has fourteen such duplicates).
    return {'own_definitions': len(own), 'manager_definitions': len(manager),
            'game_existing_duplicate_definitions': sum(map(len, game)) - len(set().union(*game)),
            'own_collision_count': 0}


def reject_output_alias(output, inputs, roots=()):
    require(not output.is_symlink() and (not output.exists() or output.is_file()), 'Output must be a regular file or absent')
    require(output.suffix.lower() == '.apk', 'Output must have .apk suffix')
    for root in roots:
        require(not output.resolve().is_relative_to(root.resolve()), 'Output inside immutable input directory')
    for path in inputs:
        require(output.resolve() != path.resolve(), 'Output aliases build input')
        if output.exists() and path.exists():
            require(not os.path.samefile(output, path), 'Output hardlinks build input')


def verify_compiled(stage, compiled, generated, root=ROOT):
    report = read_json(compiled / 'compile-inputs.json')
    require(report.get('format') == 'project7-compiled-inputs-v1' and report.get('backend') == 'project7' and
            report.get('minimum_android_api') == 26 and report.get('stub_classes_packaged') is False,
            'Current Project7 compilation required')
    expected_sources = [p for name in SOURCE_DIRS for p in (java_module_root(root, name) / 'src').rglob('*.java')]
    expected_sources += [root / name for name in STUBS]
    expected_sources += list((root / 'offline/current/java/android_core_rpc/compile_stubs').rglob('*.java')) + generated
    expected_sources += list((root / 'offline/current/java/android_draw_policy/compile_stubs').rglob('*.java'))
    expected_sources += list((root / 'offline/current/java/android_dynamic_draw/compile_stubs').rglob('*.java'))
    expected_sources += list((root / 'offline/current/java/android_request_events/compile_stubs').rglob('*.java'))
    expected_sources += list((root / 'offline/current/java/android_dream_mode/compile_stubs').rglob('*.java'))
    expected_sources += list((root / 'offline/current/java/android_week_reset/compile_stubs').rglob('*.java'))
    expected_sources += list((root / 'offline/current/java/android_story_missions/compile_stubs').rglob('*.java'))
    expected_sources += [root / 'offline/current/java/android_trial_retry/compile_stubs/com/project7/localmanager/TrialApiStubs.java']
    expected_sources += list((root / 'offline/current/java/android_baiye_shop/compile_stubs').rglob('*.java'))
    expected_sources += list((root / 'offline/current/java/android_wish_draw/compile_stubs').rglob('*.java'))
    expected_sources += list((root / 'offline/current/java/android_mechanism_gateway/compile_stubs').rglob('*.java'))
    expected_sources += list((root / 'offline/current/java/android_story_city/compile_stubs').rglob('*.java'))
    expected_paths = {p.resolve(): p for p in expected_sources}
    actual_paths = {}
    for name, digest in report['source_hashes'].items():
        path = Path(name)
        if not path.is_absolute():
            path = root / path
        require(path.resolve() not in actual_paths and path.resolve() in expected_paths and
                path.is_file() and not path.is_symlink() and file_sha(path) == digest,
                'Compilation source inventory/hash mismatch')
        actual_paths[path.resolve()] = path
    require(set(actual_paths) == set(expected_paths), 'Incomplete compilation source inventory')
    groups = report.get('groups')
    require(isinstance(groups, list) and {group['group'] for group in groups} == {'startup', 'core-rpc', 'draw-policy', 'history-draw', 'request-events', 'dream-mode', 'week-reset', 'story-missions', 'trial-retry', 'baiye-transactions', 'wish-draw', 'mechanism-gateway', 'story-city'} and
            len(groups) == 13 and all(type(group['production_classes']) is int and
                                   0 < group['production_classes'] <= 4096 for group in groups),
            'Compilation group inventory mismatch')
    grouped = [Path(name) if Path(name).is_absolute() else root / name for group in groups for name in group['sources']]
    production_sources = {path.resolve() for path in expected_sources if '/compile_stubs/' not in path.as_posix()}
    require(len(grouped) == len({path.resolve() for path in grouped}) and
            {path.resolve() for path in grouped} == production_sources, 'Compilation group source list mismatch')
    allowed = {source_family(p) for p in expected_sources if '/compile_stubs/' not in p.as_posix()}
    require(len(allowed) == len(production_sources), 'Duplicate source class families')
    production = compiled / 'production-classes'
    descriptors, names = set(), set()
    for row in report['classes']:
        name = safe_name(row['path'])
        require(name.endswith('.class') and name not in names, 'Unsafe/duplicate compiled class')
        path = stage_path(production, name)
        require(path.is_file() and path.stat().st_size == row['bytes'] and file_sha(path) == row['sha256'],
                'Compiled class inventory/hash mismatch')
        internal = class_name(path.read_bytes())
        require(internal + '.class' == name, 'Class internal name/path mismatch')
        descriptor = 'L' + internal + ';'
        require(descriptor not in descriptors and family(descriptor) in allowed,
                'Duplicate or compile-only production class')
        names.add(name)
        descriptors.add(descriptor)
    require(len(names) == sum(group['production_classes'] for group in groups) and
            REQUIRED <= descriptors, 'Incomplete source-bound Project7 compilation inventory')
    require({p.relative_to(production).as_posix() for p in production.rglob('*') if p.is_file()} == names,
            'Uninventoried compiled class payload')
    api = report.get('compile_api')
    require(isinstance(api, dict) and api.get('abi_superset_verified') is True,
            'Separate verified D8 compile API classpath missing')
    api_path = stage_path(compiled, api['path'])
    require(api['path'] == 'compile-api.jar' and api_path.is_file() and
            api_path.stat().st_size == api['bytes'] and file_sha(api_path) == api['sha256'],
            'Compile API classpath inventory mismatch')
    with zipfile.ZipFile(api_path) as archive:
        api_names = zip_inventory(archive)
        api_defs = set()
        for name in api_names:
            require(name.endswith('.class'), 'Non-class payload in compile API')
            internal = class_name(archive.read(name))
            require(internal + '.class' == name and
                    internal.startswith(('com/project7/localmanager/', 'com/netease/neox/')),
                    'Unexpected compile API definition')
            api_defs.add('L' + internal + ';')
        require(not api_defs.intersection(descriptors), 'Compile API leaked own program definitions')
    require({p.relative_to(compiled).as_posix() for p in compiled.rglob('*') if p.is_file()} ==
            {'compile-inputs.json', api['path']} | {'production-classes/' + name for name in names},
            'Unexpected compiled output/stub directory')
    return report, descriptors, allowed, api_path


def preflight(original, stage, compiled, output, root=ROOT):
    original, stage, compiled, output, root = map(Path, (original, stage, compiled, output, root))
    require(original.is_file() and not original.is_symlink() and file_sha(original) == PINS['official_apk'],
            'Unsupported original official APK')
    require(stage.is_dir() and compiled.is_dir() and not stage.is_symlink() and not compiled.is_symlink(),
            'Stage/compiled directory missing or symlinked')
    metadata_hashes = {str((stage / 'build-inputs.json').resolve()): file_sha(stage / 'build-inputs.json'),
                       str((compiled / 'compile-inputs.json').resolve()): file_sha(compiled / 'compile-inputs.json')}
    generated = verify_stage(stage)
    report = read_json(stage / 'build-inputs.json')
    require(report.get('format') == 'forever7-project7-build-inputs-v2' and
            report.get('component_sha256') == COMPONENT_SHA256 and
            report.get('game_inputs') == {key: PINS[key] for key in ('official_apk', 'official640')} and
            report.get('manual_login_definitions_removed') == 24 and
            report.get('collection_catalog_extended') is True and report.get('resource_snapshot_bundled') is True and
            report.get('ordinary_draw_policy_rule') == 'normal-ordinal-reserve-on-group-v1' and
            report.get('ordinary_draw_policy_catalog_sha256') == DRAW_CATALOG_SHA and
            report.get('historical_draw_seams') is True and
            report.get('historical_draw_catalog_sha256') == HISTORY_CATALOG_SHA and
            report.get('request_event_dispatch') is True and
            report.get('request_event_catalog_sha256') == REQUEST_EVENT_CATALOG_SHA and
            report.get('ending_trigger_catalog_sha256') == ENDING_TRIGGER_CATALOG_SHA and
            report.get('historical_furniture_seams') is True and
            report.get('selector_draw_seams') is True and
            report.get('reliable_sequence_scope_seam') is True and
            report.get('selector_catalog_sha256') == SELECTOR_CATALOG_SHA and
            report.get('baiye_transactions') is True and
            report.get('baiye_catalog_sha256') == BAIYE_CATALOG_SHA and
            report.get('baiye_fragments_sha256') == BAIYE_FRAGMENTS_SHA and
            report.get('baiye_shop') is True and
            report.get('story_basics') is True and
            report.get('story_mission_seams') is True and
            report.get('story_mission_catalog_sha256') == STORY_MISSION_CATALOG_SHA and
            report.get('trial_retry_seams') is True and
            report.get('trial_retry_policies') == ['trial-retry-total-attempts-v1', 'mandatory-trial-rearm-v1'] and
            report.get('wish_stopped_startup_seed') is True and
            report.get('story_asset_extensions') == FINAL_STORY_EXTENDED_ASSETS and
            report.get('wish_backend_candidate') is True and
            report.get('wish_catalog_sha256') == WISH_CATALOG_SHA and
            report.get('wish_ui_ready_ids') == list(WISH_PUBLIC_READY_IDS) and
            report.get('baiye_shop_catalog_sha256') == BAIYE_SHOP_CATALOG_SHA and
            report.get('dynamic_draw_candidate') is True and
            report.get('dynamic_catalog_sha256') == DYNAMIC_CATALOG_SHA and
            report.get('dynamic_ui_ready_ids') == list(DYNAMIC_PUBLIC_READY_IDS) and
            report.get('historical_furniture_catalog_sha256') == FURNITURE_CATALOG_SHA and
            report.get('event_reset_week_seams') is True and
            report.get('event_reset_catalog_sha256') == EVENT_RESET_CATALOG_SHA and
            report.get('dream_lifecycle_seams') is True and
            report.get('dream_mechanism_seams') is True and
            report.get('dream_catalog_sha256') == DREAM_CATALOG_SHA,
            'Stage provenance/feature contract mismatch')
    files = {row['path']: stage_path(stage, row['path']) for row in report['files']}
    require(set(DEXES) | {'classes7.dex', 'AndroidManifest.xml', 'assets/script.npk', 'assets/project7_local.npk',
            'assets/offline/project7-cg-reward-plan.json', DRAW_CATALOG, HISTORY_CATALOG, REQUEST_EVENT_CATALOG, ENDING_TRIGGER_CATALOG, FURNITURE_CATALOG, DREAM_CATALOG, EVENT_RESET_CATALOG, SELECTOR_CATALOG, BAIYE_CATALOG, BAIYE_FRAGMENTS, DYNAMIC_CATALOG, BAIYE_SHOP_CATALOG, WISH_CATALOG, STORY_MISSION_CATALOG, STORY_MENU_SHARED_CATALOG, MENU10_ENTRY_CATALOG} | set(STORY_EXTENDED_ASSETS) | set(STORY_CITY_EXTENDED_ASSETS) | {'assets/project7_story_city/catalog-v1.json.gz','assets/project7_story_city_virtual/virtual-data-v1.json','assets/event_graph.tsv'} <= set(files) and
            'classes6.dex' not in files and RESOURCE_MANIFEST not in files,
            'Stage required/restricted files mismatch')
    require(all(name in DEXES or name in ('classes7.dex', 'AndroidManifest.xml') or name.startswith('assets/')
                for name in files), 'Unexpected stage output path')
    require(all(not name.endswith(('.class', '.java', '.jar')) for name in files), 'Compile artifacts in stage')
    require({p.relative_to(stage).as_posix() for p in stage.rglob('*') if p.is_file()} ==
            set(files) | {row['path'] for row in report['generated_sources']} | {'build-inputs.json'},
            'Uninventoried stage payload')
    require(file_sha(files['classes7.dex']) == MANAGER_SHA and file_sha(files['assets/script.npk']) == PINS['official640'] and
            file_sha(files['assets/offline/project7-cg-reward-plan.json']) == PLAN_SHA and
            file_sha(files[DRAW_CATALOG]) == DRAW_CATALOG_SHA and
            file_sha(files[HISTORY_CATALOG]) == HISTORY_CATALOG_SHA and
            file_sha(files[SELECTOR_CATALOG]) == SELECTOR_CATALOG_SHA and
            file_sha(files[BAIYE_CATALOG]) == BAIYE_CATALOG_SHA and
            file_sha(files[WISH_CATALOG]) == WISH_CATALOG_SHA and
            file_sha(files[STORY_MISSION_CATALOG]) == STORY_MISSION_CATALOG_SHA and
            file_sha(files[STORY_MENU_SHARED_CATALOG]) == STORY_MENU_SHARED_CATALOG_SHA and
            file_sha(files[MENU10_ENTRY_CATALOG]) == MENU10_ENTRY_CATALOG_SHA and
            file_sha(files[BAIYE_FRAGMENTS]) == BAIYE_FRAGMENTS_SHA and
            file_sha(files[DYNAMIC_CATALOG]) == DYNAMIC_CATALOG_SHA and
            file_sha(files[BAIYE_SHOP_CATALOG]) == BAIYE_SHOP_CATALOG_SHA and
            file_sha(files[FURNITURE_CATALOG]) == FURNITURE_CATALOG_SHA and
            file_sha(files[DREAM_CATALOG]) == DREAM_CATALOG_SHA and
            file_sha(files[EVENT_RESET_CATALOG]) == EVENT_RESET_CATALOG_SHA and
            file_sha(files[REQUEST_EVENT_CATALOG]) == REQUEST_EVENT_CATALOG_SHA and
            file_sha(files[ENDING_TRIGGER_CATALOG]) == ENDING_TRIGGER_CATALOG_SHA and
            file_sha(files['assets/project7_story_city/catalog-v1.json.gz']) == 'af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069' and
            file_sha(files['assets/project7_story_city_virtual/virtual-data-v1.json']) == '83fae3199e308db88513f4a6e6bf6af2288ca749258e3d81b5c81451f8fec6de' and
            file_sha(files['assets/event_graph.tsv']) == 'dabe8f6ed779137cdcad221ee7a4867f552a0c8ef591b40c6af9e7bf9aa0f2bb', 'Pinned stage component mismatch')
    verify_manager_field_opcodes(files['classes7.dex'].read_bytes(), 'stage/classes7.dex')
    verify_coc_wrapper_entry(files['classes7.dex'].read_bytes(), 'stage/classes7.dex')
    require(all(file_sha(files[name]) == digest for name, digest in FINAL_STORY_EXTENDED_ASSETS.items()),
            'Source-bound story asset extension differs')
    require(all(file_sha(files[name]) == digest for name, digest in GAME_SHA256.items()), 'Pinned patched/filtered game DEX changed')
    validate_loader(files['assets/neox.xml'].read_bytes())
    base, overlay = npk(files['assets/script.npk'].read_bytes()), npk(files['assets/project7_local.npk'].read_bytes())
    require(len(base) == 28754 and len(overlay) == 21 and set(overlay) <= set(base) and 0xacb9b80e in overlay,
            'Wrong startup script baseline/overlay')
    hook = report['python_startup_hook']
    require(hook.get('collection_visibility_embedded') is True and
            hook.get('shadow_capacity_embedded') is True and
            hook.get('shadow_capacity_target_manifest_sha256') == '7e3849b6ed316b7cdc2ef9f103b90e0bc8e20f9b5da70ab3b585fbd72c0da62d' and
            hook.get('draw_ui_embedded') is True and
            hook.get('history_ui_policy_embedded') is True and
            hook.get('history_ui_catalog_sha256') == HISTORY_CATALOG_SHA and
            hook.get('history_ui_policy_sha256') == hashlib.sha256(history_ui_policy(root).encode('ascii')).hexdigest() and
            hook.get('friend_ui_embedded') is True and
            hook.get('tutorial_completion_embedded') is True and
            hook.get('trial_retry_compat_embedded') is True and
            hook.get('trial_retry_ui_policy_sha256') == 'f972b71641a864afd90606d697bcc09fcc031c6b28064159d147025acb8ed08a' and
            hook.get('selector_ui_embedded') is True and
            hook.get('selector_ui_catalog_sha256') == SELECTOR_CATALOG_SHA and
            hook.get('selector_ui_policy_sha256') == hashlib.sha256(selector_ui_policy(root).encode('ascii')).hexdigest() and
            hook.get('dynamic_ui_embedded') is True and
            hook.get('dynamic_ui_owner') == 'project7_dynamic_ui_families.py' and
            hook.get('dynamic_ui_policy_sha256') == hashlib.sha256(dynamic_ui_policy(root).encode('ascii')).hexdigest() and
            hook.get('dynamic_ui_catalog_sha256') == DYNAMIC_CATALOG_SHA and
            hook.get('dynamic_ui_base_sha256') == HISTORY_CATALOG_SHA and
            hook.get('dynamic_ui_public_ready_ids') == list(DYNAMIC_PUBLIC_READY_IDS) and
            hook.get('wish_ui_embedded') is True and
            hook.get('wish_transport_embedded') is True and
            hook.get('wish_ui_policy_sha256') == hashlib.sha256(wish_ui_policy(root).encode('ascii')).hexdigest() and
            hook.get('wish_ui_catalog_sha256') == WISH_CATALOG_SHA and
            hook.get('wish_ui_public_ready_ids') == list(WISH_PUBLIC_READY_IDS) and
            hook.get('furniture_ui_embedded') is True and
            hook.get('furniture_ui_catalog_sha256') == FURNITURE_CATALOG_SHA and
            hook.get('furniture_ui_policy_sha256') == hashlib.sha256(furniture_ui_policy(root).encode('ascii')).hexdigest(),
            'Collection/draw UI script policy not embedded')
    for name, key in STARTUP_SOURCE_HASHES:
        require(file_sha(_startup_source(root, name)) == hook[key], 'Startup script source changed since staging')
    resource_manifest = root / 'offline/current/java/android_resource_init/resource_manifest.json'
    require(file_sha(resource_manifest) == RESOURCE_MANIFEST_SHA, 'Original resource manifest changed')
    compiled_report, expected, allowed, api_path = verify_compiled(stage, compiled, generated, root)
    game = [set(definitions(files[name].read_bytes())) for name in DEXES]
    manager = set(definitions(files['classes7.dex'].read_bytes()))
    require(len(manager) == 650 and not set().union(*game).intersection(REMOVE), 'Manager/login family inventory mismatch')
    require(not expected.intersection(manager.union(*game)), 'Compiled own definitions collide with game/manager')
    with zipfile.ZipFile(original) as archive:
        original_inventory = zip_inventory(archive)
        require(files['AndroidManifest.xml'].read_bytes() == patch_manifest(archive.read('AndroidManifest.xml')),
                'Stage manifest differs from original-preserving initializer/API26 patch')
    require({name for name in original_inventory if re.fullmatch(r'classes(?:[0-9]+)?\.dex', name)} == set(DEXES),
            'Original APK DEX inventory changed')
    paths = [original, stage / 'build-inputs.json', compiled / 'compile-inputs.json', api_path, resource_manifest]
    paths += list(files.values()) + generated + [compiled / 'production-classes' / row['path'] for row in compiled_report['classes']]
    paths += [Path(p) if Path(p).is_absolute() else root / p for p in compiled_report['source_hashes']]
    paths += [_startup_source(root, name) for name in ('project7_startup_hook.py', 'offline_tutorials.py', 'project7_shadow_capacity.py', 'project7_shadow_capacity/policy.json')]
    reject_output_alias(output, paths, (stage, compiled))
    # Pin the values actually validated, rather than blessing a mutation that
    # happens between an earlier check and a later hash-inventory collection.
    fingerprints = dict(metadata_hashes)
    def remember(path, digest):
        key = str(path.resolve())
        require(key not in fingerprints or fingerprints[key] == digest, 'Inconsistent input hash contracts')
        fingerprints[key] = digest
    remember(original, PINS['official_apk'])
    remember(resource_manifest, RESOURCE_MANIFEST_SHA)
    remember(api_path, compiled_report['compile_api']['sha256'])
    for row in report['files'] + report['generated_sources']:
        remember(stage / row['path'], row['sha256'])
    for row in compiled_report['classes']:
        remember(compiled / 'production-classes' / row['path'], row['sha256'])
    for path, digest in compiled_report['source_hashes'].items():
        path = Path(path) if Path(path).is_absolute() else root / path
        remember(path, digest)
    for name, key in STARTUP_SOURCE_HASHES:
        remember(_startup_source(root, name), hook[key])
    assert_unchanged(fingerprints)
    return {'stage': report, 'compiled': compiled_report, 'files': files, 'original_inventory': original_inventory,
            'expected': expected, 'allowed': allowed, 'game': game, 'manager': manager,
            'api_path': api_path, 'resource_manifest': resource_manifest, 'fingerprints': fingerprints}


def assert_unchanged(fingerprints):
    for path, digest in fingerprints.items():
        require(Path(path).is_file() and file_sha(path) == digest, 'Build input changed during assembly: ' + path)



NEOX_ROOT_ABSOLUTE = b'/sdcard/netease/qrzd'
NEOX_ROOT_RELATIVE = b'././././netease/qrzd'


def patch_neox_root_resource(original, directory):
    """Normalize the single resource-table neox_root value without changing its byte length."""
    with zipfile.ZipFile(original) as archive:
        data = archive.read('resources.arsc')
    count = data.count(NEOX_ROOT_ABSOLUTE)
    require(count == 1, 'Unexpected resources.arsc neox_root occurrence count')
    require(len(NEOX_ROOT_ABSOLUTE) == len(NEOX_ROOT_RELATIVE), 'neox_root replacement changes resource length')
    patched = data.replace(NEOX_ROOT_ABSOLUTE, NEOX_ROOT_RELATIVE)
    require(patched.count(NEOX_ROOT_RELATIVE) == 1, 'neox_root replacement missing')
    path = directory / 'resources.arsc'
    path.write_bytes(patched)
    return path

def _write_unsigned(original, output, replacements):
    """Future assembly only. All replacement paths are an explicit preflight set."""
    emitted = set()
    with zipfile.ZipFile(original) as source, zipfile.ZipFile(output, 'w', allowZip64=False) as target:
        for record in source.infolist():
            name = record.filename
            if is_signature(name):
                continue
            require(name not in emitted, 'Duplicate original ZIP path')
            emitted.add(name)
            replacement = copy.copy(record)
            with target.open(replacement, 'w') as destination:
                if name in replacements:
                    with replacements[name].open('rb') as stream:
                        shutil.copyfileobj(stream, destination, 1024 * 1024)
                else:
                    with source.open(record) as stream:
                        shutil.copyfileobj(stream, destination, 1024 * 1024)
        for name, path in sorted(replacements.items()):
            if name in emitted:
                continue
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            with target.open(info, 'w') as destination, path.open('rb') as stream:
                shutil.copyfileobj(stream, destination, 1024 * 1024)
            emitted.add(name)


def signing_certificate_sha256(java, signer_jar, apk):
    result = subprocess.run([str(java), '-jar', str(signer_jar), 'verify', '--print-certs', str(apk)],
                            capture_output=True, text=True, check=True)
    values = []
    for line in result.stdout.splitlines():
        if 'certificate SHA-256 digest:' in line:
            values.append(line.rsplit(':', 1)[1].strip().replace(':', '').lower())
    if not values:
        raise ValueError('APK signing certificate digest missing')
    if len(set(values)) != 1:
        raise ValueError('APK signing certificate digest ambiguous')
    return values[0]


def require_expected_certificate(actual, expected):
    if expected is None:
        return actual
    normalized = expected.replace(':', '').lower()
    if actual.replace(':', '').lower() != normalized:
        raise ValueError('APK signing certificate mismatch')
    return actual


def embedded_render_mode(apk):
    init_fid = 0xacb9b80e
    with zipfile.ZipFile(apk) as archive, tempfile.NamedTemporaryFile(suffix='.npk') as temporary:
        temporary.write(archive.read('assets/project7_local.npk'))
        temporary.flush()
        script = ScriptArchive(temporary.name)
        index = next((i for i, row in enumerate(script.entries) if row[0] == init_fid), None)
        if index is None:
            raise ValueError('Embedded init FID missing')
        decoded = script.read(index)
    modes = re.findall(rb"render_mode='(astc|png)'", decoded)
    if len(modes) != 1:
        raise ValueError('Embedded render mode missing or ambiguous')
    return modes[0].decode('ascii')


def build(original, stage, compiled, output, toolchains, keystore=None, key_alias='forever7-local', password=None, expected_certificate_sha256=None):
    """Future explicit build operation; tests/preflight never call this function."""
    original, stage, compiled, output, toolchains = map(Path, (original, stage, compiled, output, toolchains))
    ready = preflight(original, stage, compiled, output)
    java_bin = toolchains / 'java/jdk-17.0.21+9/Contents/Home/bin'
    sdk = toolchains / 'build-tools/android-37.0'
    android = toolchains / 'android-sdk/platforms/android-32/android.jar'
    tools = [java_bin / 'java', java_bin / 'keytool', sdk / 'zipalign', sdk / 'lib/d8.jar', sdk / 'lib/apksigner.jar', android]
    require(all(path.is_file() for path in tools), 'Required Android/JDK build tools missing')
    fingerprints = dict(ready['fingerprints'], **{str(path.resolve()): file_sha(path) for path in tools})
    keystore = Path(keystore) if keystore is not None else toolchains / 'signing/offline-dev.p12'
    require(not keystore.is_symlink() and (not keystore.exists() or keystore.is_file()), 'Unsafe signing keystore path')
    reject_output_alias(output, [Path(path) for path in fingerprints] + [keystore], (stage, compiled))
    for path in map(Path, fingerprints):
        require(keystore.resolve() != path.resolve() and
                (not keystore.exists() or not os.path.samefile(keystore, path)), 'Keystore aliases immutable build input')
    require(isinstance(key_alias, str) and key_alias and '\0' not in key_alias, 'Invalid signing alias')
    require(password is None or isinstance(password, str), 'Signing password must be text')
    if keystore.exists():
        fingerprints[str(keystore.resolve())] = file_sha(keystore)
    secret_env = dict(os.environ, F7_BUILD_KEY_PASSWORD=password if password is not None else DEV_PASSWORD)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='p7-build-', dir=output.parent) as directory:
        work = Path(directory)
        snapshot, dex_dir = work / 'inputs', work / 'own-dex'
        snapshot.mkdir()
        dex_dir.mkdir()
        replacements = {}
        for name, path in ready['files'].items():
            destination = snapshot / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
            require(file_sha(destination) == ready['fingerprints'][str(path.resolve())], 'Stage changed during snapshot')
            replacements[name] = destination
        manifest_copy = snapshot / RESOURCE_MANIFEST
        manifest_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ready['resource_manifest'], manifest_copy)
        require(file_sha(manifest_copy) == RESOURCE_MANIFEST_SHA, 'Resource manifest changed during snapshot')
        replacements[RESOURCE_MANIFEST] = manifest_copy
        class_dir = work / 'program-classes'
        classes = []
        for row in ready['compiled']['classes']:
            destination = class_dir / row['path']
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(compiled / 'production-classes' / row['path'], destination)
            require(file_sha(destination) == row['sha256'], 'Class changed during snapshot')
            classes.append(destination)
        api_copy = work / 'compile-api.jar'
        shutil.copyfile(ready['api_path'], api_copy)
        require(file_sha(api_copy) == ready['compiled']['compile_api']['sha256'], 'API changed during snapshot')
        assert_unchanged(fingerprints)
        subprocess.run([str(java_bin / 'java'), '-cp', str(sdk / 'lib/d8.jar'), 'com.android.tools.r8.D8',
                        '--min-api', '26', '--lib', str(android), '--classpath', str(api_copy),
                        '--output', str(dex_dir)] + [str(path) for path in sorted(classes)], check=True)
        require(sorted(p.name for p in dex_dir.iterdir()) == ['classes.dex'], 'Own code must produce exactly one classes6 DEX')
        own_dex = dex_dir / 'classes.dex'
        own = set(definitions(own_dex.read_bytes()))
        collision_report = check_collisions(own, ready['game'], ready['manager'], ready['expected'], ready['allowed'])
        replacements['classes6.dex'] = own_dex
        replacements['resources.arsc'] = patch_neox_root_resource(original, work)
        expected = {name: row for name, row in ready['original_inventory'].items() if not is_signature(name)}
        expected.update({name: {'bytes': path.stat().st_size, 'sha256': file_sha(path)} for name, path in replacements.items()})
        unsigned, aligned, signed = (work / name for name in ('unsigned.apk', 'aligned.apk', 'signed.apk'))
        _write_unsigned(original, unsigned, replacements)
        subprocess.run([str(sdk / 'zipalign'), '-f', '-P', '16', '4', str(unsigned), str(aligned)], check=True)
        # Alignment succeeded; signing consumes only aligned. Avoid retaining
        # three full-size APKs at the signing peak on a nearly full disk.
        unsigned.unlink()  # aligned is now the source; keep peak storage bounded
        if not keystore.exists():
            keystore.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run([str(java_bin / 'keytool'), '-genkeypair', '-storetype', 'PKCS12', '-keystore', str(keystore),
                            '-storepass:env', 'F7_BUILD_KEY_PASSWORD', '-alias', key_alias, '-keyalg', 'RSA', '-keysize', '2048',
                            '-validity', '3650', '-dname', 'CN=Forever7 Local Development'], check=True, env=secret_env)
        keystore.chmod(0o600)
        if str(keystore.resolve()) not in fingerprints:
            fingerprints[str(keystore.resolve())] = file_sha(keystore)
        signer = [str(java_bin / 'java'), '-jar', str(sdk / 'lib/apksigner.jar')]
        subprocess.run(signer + ['sign', '--ks', str(keystore), '--ks-key-alias', key_alias,
                                '--ks-pass', 'env:F7_BUILD_KEY_PASSWORD', '--key-pass', 'env:F7_BUILD_KEY_PASSWORD',
                                '--out', str(signed), str(aligned)], check=True, env=secret_env)
        subprocess.run(signer + ['verify', '--verbose', str(signed)], check=True)
        subprocess.run([str(sdk / 'zipalign'), '-c', '-P', '16', '4', str(signed)], check=True)
        actual_certificate = signing_certificate_sha256(java_bin / 'java', sdk / 'lib/apksigner.jar', signed)
        require_expected_certificate(actual_certificate, expected_certificate_sha256)
        actual_render_mode = embedded_render_mode(signed)
        requested_render_mode = ready['stage'].get('render_mode')
        require(actual_render_mode == requested_render_mode, 'Embedded render mode mismatch')
        aligned.unlink()  # signed APK retained; drop aligned intermediate
        with zipfile.ZipFile(signed) as archive:
            require(zip_inventory(archive, ignore_signatures=True) == expected, 'Signed APK payload inventory mismatch')
        assert_unchanged(fingerprints)
        # Repeat inventories (including new untracked files), not only old hashes.
        preflight(original, stage, compiled, output)
        reject_output_alias(output, [Path(path) for path in fingerprints] + [keystore], (stage, compiled))
        with signed.open('rb') as stream:
            os.fsync(stream.fileno())
        signed.replace(output)
    return {'format': 'project7-original-apk-build-v1', 'file': str(output), 'bytes': output.stat().st_size,
            'sha256': file_sha(output), 'original_sha256': PINS['official_apk'], 'backend': 'project7',
            'manager_sha256': MANAGER_SHA, 'minimum_android_api': 26, 'payloads_verified': len(expected),
            'signature_verified': True, 'signature_certificate_sha256': actual_certificate, 'render_mode': actual_render_mode, 'zip_alignment_page_kib': 16, 'development_build': True,
            'compile_stubs_packaged': False, 'native_runtime_verified': False, **collision_report}
