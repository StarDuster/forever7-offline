"""Prepare official-APK Project7 build inputs without executing or assembling APKs.

The fixed component is a project dependency, not an extra user-supplied game.
The legacy LocalProxy bootstrap must never be injected into this script base.
"""
import _bootstrap  # noqa: E402,F401
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from android_resource_init import PROJECT7_ENTRY, _attribute, _chunks, _strings, _tag, patch_resource_manifest
from project7_component import COMPONENT_SHA256, DEXES, materialize, npk, restore, sha
from project7_catalog_extension import extend_catalog
from project7_dex_filter import REMOVE as LOGIN_CLASSES, remove_manual_login
from project7_resource_bundle import create_bundle
from project7_script_hook import build_startup_overlay
from project7_manager_hook import apply_manager_hook
from project7_draw_hook import apply_draw_hook
from project7_newbie_hook import apply_newbie_hook
from project7_feature_hooks import (apply_history_hook, apply_request_event_hook,
                                    apply_furniture_hook, apply_dream_hook, apply_dream_lifecycle_hook,
                                    apply_event_reset_week_hook, apply_selector_hook,
                                    apply_reliable_scope_hook, apply_story_mission_hook, apply_trial_retry_hook)
from project7_story_mission_catalog import extend_asset as extend_story_asset
from project7_bson_fast_patch import apply_bson_fast
from project7_manager_rpc_projection_patch import apply_manager_rpc_projection
from project7_story_city_suppression import extend_asset as extend_story_city_suppression
from project7_story_city_economy import extend_asset as extend_story_city_economy
from project7_story_city_puzzle import merged_bytes as merge_story_city_puzzle
from project7_feature_assets import (feature_assets, HISTORY_CATALOG_SHA, REQUEST_EVENT_CATALOG_SHA,
                                     ENDING_TRIGGER_CATALOG_SHA,
                                     FURNITURE_CATALOG_SHA, DREAM_CATALOG_SHA, EVENT_RESET_CATALOG_SHA,
                                     SELECTOR_CATALOG_SHA, BAIYE_CATALOG_SHA, BAIYE_FRAGMENTS_SHA,
                                     DYNAMIC_CATALOG_SHA, BAIYE_SHOP_CATALOG_SHA,
                                     DYNAMIC_PUBLIC_READY_IDS, WISH_CATALOG_SHA, WISH_PUBLIC_READY_IDS,
                                     STORY_MISSION_CATALOG_SHA, STORY_EXTENDED_ASSETS,
                                     STORY_CITY_EXTENDED_ASSETS, STORY_CITY_SUPPRESSION_SHA)

from _bootstrap import ROOT
DEFAULT_COMPONENT = ROOT / 'vendor/project7/component-v2.10.1.zip'


def patch_manifest(data, minimum=26):
    """Keep original manifest semantics, add our entry and require DEX038's API."""
    if minimum != 26:
        raise ValueError('Only the pinned manager API26 contract is supported')
    chunks = list(_chunks(data))
    if not chunks or chunks[0][0] != 1:
        raise ValueError('Expected binary manifest string pool')
    strings = _strings(chunks[0][1])
    found = 0
    for index, (kind, body) in enumerate(chunks):
        if kind != 0x102 or strings[_tag(body)] != 'uses-sdk':
            continue
        updated = bytearray(body)
        offsets = list(_attribute(body, strings, 'minSdkVersion'))
        if len(offsets) != 1:
            raise ValueError('Expected one original minimum SDK')
        offset = offsets[0]
        if body[offset + 15] not in (0x10, 0x11):
            raise ValueError('Minimum SDK must be an integer')
        value = struct.unpack_from('<I', body, offset + 16)[0]
        if value < minimum:
            struct.pack_into('<I', updated, offset + 8, 0xffffffff)
            updated[offset + 15] = 0x10
            struct.pack_into('<I', updated, offset + 16, minimum)
        chunks[index] = (kind, bytes(updated))
        found += 1
    if found != 1:
        raise ValueError('Expected one original uses-sdk declaration')
    body = b''.join(chunk for _, chunk in chunks)
    raised = struct.pack('<HHI', 3, 8, len(body) + 8) + body
    return patch_resource_manifest(raised, entry=PROJECT7_ENTRY)


def validate_loader(xml):
    if len(xml) > 128 * 1024:
        raise ValueError('Oversized native loader configuration')
    document = ET.fromstring(xml)
    scripts = document.findall("./filesystems/filesystem[@name='script']")
    if len(scripts) != 1:
        raise ValueError('Expected one script filesystem')
    loaders = [dict(node.attrib) for node in scripts[0]]
    expected = [{'name': 'npk', 'opener': 'asset', 'root': 'project7_local'},
                {'name': 'npk', 'opener': 'asset', 'root': 'script'}]
    if loaders != expected:
        raise ValueError('Unexpected script loader order or document override')
    return loaders


def project_files(component_files, original_script, original_manifest):
    """Map component stages into their exact final APK paths; no file writes."""
    if 'classes6.dex' in component_files or 'assets/script.npk' in component_files:
        raise ValueError('Component cannot replace the resource initializer or script baseline')
    if 'assets/project7_local.npk' in component_files:
        raise ValueError('Ambiguous Project7 overlay source')
    required = set(DEXES) | {'classes7.dex', 'assets/neox.xml', 'project7-script-overlay.npk'}
    if not required.issubset(component_files):
        raise ValueError('Incomplete fixed component')
    loaders = validate_loader(component_files['assets/neox.xml'])
    base, overlay = npk(original_script), npk(component_files['project7-script-overlay.npk'])
    if len(base) != 28754 or len(overlay) != 20 or not set(overlay).issubset(base):
        raise ValueError('Unexpected official640/Project7 script domain')
    if 0xfb54f059 not in base or 0xfb54f059 in overlay:
        raise ValueError('Original native redirect must remain in the official baseline')
    result = dict(component_files)
    result['classes3.dex'] = remove_manual_login(result['classes3.dex'])
    result['classes7.dex'], manager_hook = apply_manager_hook(result['classes7.dex'])
    result['classes7.dex'], draw_hook = apply_draw_hook(result['classes7.dex'])
    result['classes7.dex'], newbie_hook = apply_newbie_hook(result['classes7.dex'])
    result['classes7.dex'], history_hook = apply_history_hook(result['classes7.dex'])
    result['classes7.dex'], request_event_hook = apply_request_event_hook(result['classes7.dex'])
    result['classes7.dex'], furniture_hook = apply_furniture_hook(result['classes7.dex'])
    result['classes7.dex'], dream_hook = apply_dream_hook(result['classes7.dex'])
    result['classes7.dex'], dream_lifecycle_hook = apply_dream_lifecycle_hook(result['classes7.dex'])
    result['classes7.dex'], event_reset_week_hook = apply_event_reset_week_hook(result['classes7.dex'])
    result['classes7.dex'], selector_hook = apply_selector_hook(result['classes7.dex'])
    result['classes7.dex'], reliable_scope_hook = apply_reliable_scope_hook(result['classes7.dex'])
    result['classes7.dex'], story_mission_hook = apply_story_mission_hook(result['classes7.dex'])
    result['classes7.dex'], trial_retry_hook = apply_trial_retry_hook(result['classes7.dex'])
    # Bind the reviewed StoryCity/Gateway/Puzzle manager delta after every
    # existing manager hook. The source hash is the exact final manager DEX,
    # so this is not a helper-only or parallel candidate.
    puzzle_graph_sha = '50d211e2108524dbce10e9babf9de77cf9faf9e331f8a70f8d1a8f6d771f927f'
    city_catalog_sha = 'af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069'
    city_virtual_sha = '83fae3199e308db88513f4a6e6bf6af2288ca749258e3d81b5c81451f8fec6de'
    city_contract = json.loads((ROOT / 'project7_bridge/runtime/project7_story_city_patch/contract.json').read_text())
    city_patch = (ROOT / 'project7_bridge/runtime/project7_story_city_patch/seams.xor-zlib').read_bytes()
    city_source = city_contract.get('source', {}).get('sha256')
    city_target = city_contract.get('target', {}).get('sha256')
    city_bytes = city_contract.get('target', {}).get('bytes')
    if sha(result['classes7.dex']) != city_source:
        raise ValueError('StoryCity manager source is not the current post-hook DEX')
    if sha(city_patch) != city_contract.get('patch', {}).get('sha256'):
        raise ValueError('StoryCity manager patch pin mismatch')
    result['classes7.dex'] = restore(result['classes7.dex'], city_patch, city_bytes)
    if sha(result['classes7.dex']) != city_target:
        raise ValueError('StoryCity manager target DEX mismatch')
    ledger_contract = json.loads((ROOT / 'project7_bridge/runtime/project7_action_ledger_code20_patch/contract.json').read_text())
    ledger_patch = (ROOT / 'project7_bridge/runtime/project7_action_ledger_code20_patch/seams.xor-zlib').read_bytes()
    ledger_source = ledger_contract['source']['sha256']
    ledger_target = ledger_contract['target']['sha256']
    ledger_bytes = ledger_contract['target']['bytes']
    init_contract = json.loads((ROOT / 'project7_bridge/runtime/project7_action_ledger_init_patch/contract.json').read_text())
    init_patch = (ROOT / 'project7_bridge/runtime/project7_action_ledger_init_patch/seams.xor-zlib').read_bytes()
    if sha(result['classes7.dex']) != ledger_source:
        raise ValueError('action ledger source is not the StoryCity target')
    if sha(ledger_patch) != ledger_contract['patch']['sha256']:
        raise ValueError('action ledger patch pin mismatch')
    result['classes7.dex'] = restore(result['classes7.dex'], ledger_patch, ledger_bytes)
    if sha(result['classes7.dex']) != ledger_target:
        raise ValueError('action ledger target DEX mismatch')
    init_contract = json.loads((ROOT / 'project7_bridge/runtime/project7_action_ledger_init_patch/contract.json').read_text())
    init_patch = (ROOT / 'project7_bridge/runtime/project7_action_ledger_init_patch/seams.xor-zlib').read_bytes()
    if sha(result['classes7.dex']) != init_contract['source']['sha256']:
        raise ValueError('action ledger init source is not v1 target')
    if sha(init_patch) != init_contract['patch']['sha256']:
        raise ValueError('action ledger init patch pin mismatch')
    result['classes7.dex'] = restore(result['classes7.dex'], init_patch, init_contract['target']['bytes'])
    if sha(result['classes7.dex']) != init_contract['target']['sha256']:
        raise ValueError('action ledger init target DEX mismatch')
    opcode_contract = json.loads((ROOT / 'project7_bridge/runtime/project7_field_opcode_fix_patch/contract.json').read_text())
    opcode_patch = (ROOT / 'project7_bridge/runtime/project7_field_opcode_fix_patch/seams.xor-zlib').read_bytes()
    if sha(result['classes7.dex']) != opcode_contract['source']['sha256']:
        raise ValueError('field opcode repair source is not the final manager DEX')
    if sha(opcode_patch) != opcode_contract['patch']['sha256']:
        raise ValueError('field opcode repair patch pin mismatch')
    result['classes7.dex'] = restore(result['classes7.dex'], opcode_patch, opcode_contract['target']['bytes'])
    if sha(result['classes7.dex']) != opcode_contract['target']['sha256']:
        raise ValueError('field opcode repair target DEX mismatch')
    wrapper_contract = json.loads((ROOT / 'project7_bridge/runtime/project7_coc_wrapper_patch/contract.json').read_text())
    wrapper_patch = (ROOT / 'project7_bridge/runtime/project7_coc_wrapper_patch/seams.xor-zlib').read_bytes()
    if sha(result['classes7.dex']) != wrapper_contract['source']['sha256']:
        raise ValueError('COC wrapper source is not the repaired manager DEX')
    if sha(wrapper_patch) != wrapper_contract['patch']['sha256']:
        raise ValueError('COC wrapper patch pin mismatch')
    result['classes7.dex'] = restore(result['classes7.dex'], wrapper_patch, wrapper_contract['target']['bytes'])
    if sha(result['classes7.dex']) != wrapper_contract['target']['sha256']:
        raise ValueError('COC wrapper target DEX mismatch')
    result['classes7.dex'], bson_fast_hook = apply_bson_fast(result['classes7.dex'])
    if sha(result['classes7.dex']) != bson_fast_hook['target']['sha256']:
        raise ValueError('Bson fast target DEX mismatch')
    result['classes7.dex'], manager_rpc_projection = apply_manager_rpc_projection(result['classes7.dex'])
    if sha(result['classes7.dex']) != manager_rpc_projection['target']['sha256']:
        raise ValueError('Manager RPC projection target DEX mismatch')
    for name in ('economy.tsv', 'suppression.tsv'):
        key = 'assets/' + name
        result[key] = extend_story_asset(result[key], name)
        if sha(result[key]) != STORY_EXTENDED_ASSETS[key]:
            raise ValueError('Story mission extension output differs: ' + name)
    result['assets/economy.tsv'] = extend_story_city_economy(result['assets/economy.tsv'])
    result['assets/suppression.tsv'] = extend_story_city_suppression(result['assets/suppression.tsv'])
    if sha(result['assets/suppression.tsv']) != STORY_CITY_EXTENDED_ASSETS['assets/suppression.tsv']:
        raise ValueError('Story city COC suppression extension output differs')
    result.update(feature_assets())
    puzzle_extra = (ROOT / 'offline/current/data/project7_story_city_catalog/puzzle-extra.tsv').read_bytes()
    result['assets/event_graph.tsv'] = merge_story_city_puzzle(result['assets/event_graph.tsv'], puzzle_extra)
    trigger_extras = [
        ('offline/current/data/project7_event_auto_trigger_candidate/trigger-extra-v1.tsv', '597ddb4cc68503cc0046092a40248defa98bfdd738aecd75de139261f8d9caa7', 222),
        ('offline/current/data/project7_event_auto_trigger_condition_candidate/trigger-extra-conditions-v1.tsv', '9008d9ef48f96ff15d10feb84c678b45871f7fb28f4bc627e6f4845e3105fb99', 16),
        ('offline/current/data/project7_action_ledger_integration_candidate/trigger-extra-code20-v1.tsv', 'a898aea3ebaa3605bc6b6fcc1a2fd9c3eb2064f7c3bd4c1ac6eea4a8ac795c7a', 17),
    ]
    seen = set(result['assets/event_graph.tsv'].decode('ascii').splitlines())
    for path, pin, count in trigger_extras:
        data = (ROOT / path).read_bytes()
        if sha(data) != pin:
            raise ValueError('trigger candidate hash mismatch: ' + path)
        rows = [line for line in data.decode('ascii').splitlines() if line and not line.startswith('#')]
        if len(rows) != count or any(not line.startswith('@trigger\t') for line in rows):
            raise ValueError('trigger candidate shape mismatch: ' + path)
        if any(line in seen for line in rows):
            raise ValueError('duplicate trigger candidate row: ' + path)
        seen.update(rows)
        result['assets/event_graph.tsv'] += ('\n'.join(rows) + '\n').encode('ascii')
    # Final reproducible event graph, including the complete original-derived
    # @cityEffect projection. Keep this runtime asset authoritative so fresh
    # prepare never depends on analysis/v49 or decompiled-source directories.
    full_graph = (ROOT / 'offline/current/data/project7_story_city_events/event_graph.tsv').read_bytes()
    full_graph_sha = 'dabe8f6ed779137cdcad221ee7a4867f552a0c8ef591b40c6af9e7bf9aa0f2bb'
    if sha(full_graph) != full_graph_sha:
        raise ValueError('Story city full event graph pin mismatch')
    result['assets/event_graph.tsv'] = full_graph
    puzzle_graph_sha = sha(result['assets/event_graph.tsv'])
    city_catalog = (ROOT / 'offline/current/data/project7_story_city_catalog/catalog-v1.json.gz').read_bytes()
    city_catalog_sha = 'af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069'
    if sha(city_catalog) != city_catalog_sha:
        raise ValueError('StoryCity catalog pin mismatch')
    result['assets/project7_story_city/catalog-v1.json.gz'] = city_catalog
    city_virtual = (ROOT / 'offline/current/data/project7_story_city_virtual/virtual-data-v1.json').read_bytes()
    city_virtual_sha = '83fae3199e308db88513f4a6e6bf6af2288ca749258e3d81b5c81451f8fec6de'
    if sha(city_virtual) != city_virtual_sha:
        raise ValueError('StoryCity virtual-data pin mismatch')
    result['assets/project7_story_city_virtual/virtual-data-v1.json'] = city_virtual
    result['assets/resources.tsv'] = extend_catalog(result['assets/resources.tsv'])
    result['assets/project7_catalog/target-manifest.json'] = (
        ROOT / 'offline/current/data/project7_catalog/target-manifest.json').read_bytes()
    cg_plan = (ROOT / 'offline/current/data/project7_cg_rewards/public-data.json').read_bytes()
    if sha(cg_plan) != '647a1ec62aa56d87a291ce1b9121cbd3a97cf5c00fa71e97d1f6e1d283080675':
        raise ValueError('CG reward plan hash mismatch')
    result['assets/offline/project7-cg-reward-plan.json'] = cg_plan
    draw_catalog = (ROOT / 'offline/current/data/project7_draw_ir/data/android-catalog-v2.tsv').read_bytes()
    if sha(draw_catalog) != 'e250ace8d74eaf87769a709532e5a4e1ae69eb2d1acfedf520b79e0323136319':
        raise ValueError('Ordinary draw catalog hash mismatch')
    result['assets/project7_draw_policy/catalog-v2.tsv'] = draw_catalog
    result['assets/project7_local.npk'] = result.pop('project7-script-overlay.npk')
    result['assets/script.npk'] = original_script
    # The fixed component's qualification asset assumed a module-level class
    # named HeroTestMember; the original 640 module exports Member. Keep this
    # runtime seam source-bound and replace the component copy at prepare time.
    result['assets/client_qualification_compat.py'] = (
        ROOT / 'project7_bridge/runtime/project7_compat/client_qualification_compat.py').read_bytes()
    result['AndroidManifest.xml'] = patch_manifest(original_manifest)
    return result, loaders


def prepare(original, official640, output, component=DEFAULT_COMPONENT, render_mode='astc'):
    original, official640, output, component = map(Path, (original, official640, output, component))
    if output.exists() or output.is_symlink():
        raise ValueError('Build-input directory already exists')
    manifest, component_files = materialize(component, original, official640)
    with zipfile.ZipFile(original) as archive:
        if archive.namelist().count('AndroidManifest.xml') != 1:
            raise ValueError('Expected one official Android manifest')
        final, loaders = project_files(component_files, official640.read_bytes(),
                                       archive.read('AndroidManifest.xml'))
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=output.name + '.script-', dir=output.parent) as directory:
        directory = Path(directory)
        local = directory / 'project7-base-overlay.npk'
        patched = directory / 'project7-startup-overlay.npk'
        local.write_bytes(final['assets/project7_local.npk'])
        hook_report = build_startup_overlay(official640, local, patched, render_mode=render_mode)
        final['assets/project7_local.npk'] = patched.read_bytes()
    hook_report['output'] = 'assets/project7_local.npk'
    puzzle_graph_sha = sha(final['assets/event_graph.tsv'])
    city_catalog_sha = 'af2328b97372c27fd392b5b399d03daa17fa73acdd35d2b1ad5b0a8f07218069'
    ledger_contract = json.loads((ROOT / 'project7_bridge/runtime/project7_action_ledger_code20_patch/contract.json').read_text())
    ledger_patch = (ROOT / 'project7_bridge/runtime/project7_action_ledger_code20_patch/seams.xor-zlib').read_bytes()
    ledger_source = ledger_contract['source']['sha256']
    ledger_target = ledger_contract['target']['sha256']
    ledger_bytes = ledger_contract['target']['bytes']
    init_contract = json.loads((ROOT / 'project7_bridge/runtime/project7_action_ledger_init_patch/contract.json').read_text())
    init_patch = (ROOT / 'project7_bridge/runtime/project7_action_ledger_init_patch/seams.xor-zlib').read_bytes()
    city_virtual_sha = '83fae3199e308db88513f4a6e6bf6af2288ca749258e3d81b5c81451f8fec6de'
    city_contract = json.loads((ROOT / 'project7_bridge/runtime/project7_story_city_patch/contract.json').read_text())
    city_patch = (ROOT / 'project7_bridge/runtime/project7_story_city_patch/seams.xor-zlib').read_bytes()
    city_source = city_contract['source']['sha256']
    city_target = city_contract['target']['sha256']
    city_bytes = city_contract['target']['bytes']
    resource_assets, resource_source, resource_binding = create_bundle(
        final['assets/script.npk'], final['assets/project7_local.npk'])
    if set(resource_assets) & set(final):
        raise ValueError('Bundled resource metadata collision')
    final.update(resource_assets)
    generated = {'generated-java/com/forever7/offline/Project7BundledResources.java': resource_source}
    report = {
        'format': 'forever7-project7-build-inputs-v2', 'backend': 'project7',
        'component_sha256': COMPONENT_SHA256, 'minimum_android_api': manifest['min_api'],
        'resource_initializer_dex': 'classes6.dex', 'manager_dex': 'classes7.dex',
        'legacy_gateway_enabled': False, 'native_loader_order': loaders,
        'manual_login_definitions_removed': len(LOGIN_CLASSES),
        'collection_catalog_extended': True,
        'full_collection_profile_initialized': False,
        'headless_login_replacement_required': True,
        'manager_core_rpc_prefix': True,
        'core_rpc_helper_compilation_required': True,
        'ordinary_draw_policy': True,
        'ordinary_draw_policy_rule': 'normal-ordinal-reserve-on-group-v1',
        'ordinary_draw_policy_catalog_sha256': 'e250ace8d74eaf87769a709532e5a4e1ae69eb2d1acfedf520b79e0323136319',
        'ordinary_draw_helpers_compilation_required': True,
        'beginner_new_groups_blocked': True,
        'historical_draw_seams': True,
        'historical_draw_catalog_sha256': HISTORY_CATALOG_SHA,
        'selector_draw_seams': True,
        'reliable_sequence_scope_seam': True,
        'selector_catalog_sha256': SELECTOR_CATALOG_SHA,
        'baiye_transactions': True,
        'baiye_catalog_sha256': BAIYE_CATALOG_SHA,
        'baiye_fragments_sha256': BAIYE_FRAGMENTS_SHA,
        'baiye_shop': True,
        'story_basics': True,
        'story_mission_seams': True,
        'story_mission_catalog_sha256': STORY_MISSION_CATALOG_SHA,
        'trial_retry_seams': True,
        'trial_retry_policies': ['trial-retry-total-attempts-v1', 'mandatory-trial-rearm-v1'],
        'wish_stopped_startup_seed': True,
        'story_asset_extensions': dict(STORY_EXTENDED_ASSETS, **STORY_CITY_EXTENDED_ASSETS),
        'story_city_suppression_sha256': STORY_CITY_SUPPRESSION_SHA,
        'story_city_event_graph': {'merged_sha256': puzzle_graph_sha, 'source': 'component event_graph + puzzle-extra + 222 trigger + 16 condition + 17 code20', 'trigger_extra_count': 255},
        'story_city_catalog_sha256': city_catalog_sha,
        'story_city_virtual_sha256': city_virtual_sha,
        'action_ledger_init_binding': {'source_sha256': init_contract['source']['sha256'], 'target_sha256': init_contract['target']['sha256'], 'bytes': init_contract['target']['bytes'], 'patch_sha256': sha(init_patch)},
        'action_ledger_manager_binding': {'source_sha256': ledger_source, 'target_sha256': ledger_target, 'bytes': ledger_bytes, 'patch_sha256': sha(ledger_patch)},
        'story_city_manager_binding': {'source_sha256': city_source, 'target_sha256': city_target, 'bytes': city_bytes, 'patch_sha256': sha(city_patch), 'format': city_contract.get('format')},
        'baiye_shop_catalog_sha256': BAIYE_SHOP_CATALOG_SHA,
        'dynamic_draw_candidate': True,
        'wish_backend_candidate': True,
        'wish_catalog_sha256': WISH_CATALOG_SHA,
        'wish_ui_ready_ids': list(WISH_PUBLIC_READY_IDS),
        'dynamic_catalog_sha256': DYNAMIC_CATALOG_SHA,
        'dynamic_ui_ready_ids': list(DYNAMIC_PUBLIC_READY_IDS),
        'historical_draw_native_verified': False,
        'request_event_dispatch': True,
        'request_event_catalog_sha256': REQUEST_EVENT_CATALOG_SHA,
        'request_event_native_verified': False,
        'ending_trigger_catalog_sha256': ENDING_TRIGGER_CATALOG_SHA,
        'ending_trigger_native_verified': False,
        'historical_furniture_seams': True,
        'historical_furniture_catalog_sha256': FURNITURE_CATALOG_SHA,
        'dream_mechanism_seams': True,
        'dream_lifecycle_seams': True,
        'event_reset_week_seams': True,
        'event_reset_catalog_sha256': EVENT_RESET_CATALOG_SHA,
        'dream_catalog_sha256': DREAM_CATALOG_SHA,
        'dream_native_verified': False,
        'resource_snapshot_bundled': True,
        'resource_snapshot_verified_on_device': False,
        'resource_script_binding': resource_binding['scripts'],
        'python_startup_hook': hook_report,
        'render_mode': render_mode,
        'render_loader_option': True,
        'frida_required': False,
        'game_inputs': {'official_apk': manifest['pins']['official_apk'],
                        'official640': manifest['pins']['official640']},
        'files': [{'path': name, 'bytes': len(data), 'sha256': sha(data)}
                  for name, data in sorted(final.items())],
        'generated_sources': [{'path': name, 'bytes': len(data), 'sha256': sha(data)}
                              for name, data in sorted(generated.items())],
        'required_before_apk_delivery': [
            'Compile the real resource initializer, process owner and stable identity bootstrap into classes6.dex; never package compile stubs',
            'Complete resource snapshot, prestart collection initialization and automatic native login wiring',
            'Sign and verify the final original-APK build after the complete static/code gates close'],
        'apk_built': False, 'native_runtime_verified': False, 'goal_complete': False}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=output.name + '.part-', dir=output.parent))
    try:
        for name, data in sorted(final.items()):
            target = temporary / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        for name, data in sorted(generated.items()):
            target = temporary / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        (temporary / 'build-inputs.json').write_text(json.dumps(report, indent=2) + '\n')
        if output.exists():
            raise ValueError('Build-input destination appeared during preparation')
        temporary.rename(output)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('--official640', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--component', type=Path, default=DEFAULT_COMPONENT)
    args = parser.parse_args()
    report = prepare(args.original, args.official640, args.output, args.component)
    print(json.dumps({key: value for key, value in report.items()
                      if key not in ('files', 'python_startup_hook')}, indent=2))


if __name__ == '__main__':
    main()
