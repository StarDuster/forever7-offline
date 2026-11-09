"""Central source-tree locations for the Forever 7 offline project.

All build tooling resolves the repository through this module instead of
assuming a fixed number of parent directories after source reorganization.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UPSTREAM_PROJECT7 = ROOT / 'upstream' / 'project7'
UPSTREAM_PROVENANCE = UPSTREAM_PROJECT7 / 'provenance'
PROJECT7_BRIDGE = ROOT / 'project7_bridge'
PROJECT7_BRIDGE_RUNTIME = PROJECT7_BRIDGE / 'runtime'
PROJECT7_BRIDGE_ANDROID = PROJECT7_BRIDGE / 'android'
PROJECT7_BRIDGE_TOOLS = PROJECT7_BRIDGE / 'tools'
OFFLINE = ROOT / 'offline'
OFFLINE_RUNTIME = OFFLINE / 'runtime'
OFFLINE_TOOLS = OFFLINE / 'tools'
OFFLINE_LEGACY = OFFLINE / 'legacy'
OFFLINE_CURRENT = OFFLINE / 'current'
OFFLINE_CURRENT_RUNTIME = OFFLINE_CURRENT / 'runtime'
OFFLINE_CURRENT_JAVA = OFFLINE_CURRENT / 'java'
OFFLINE_CURRENT_DATA = OFFLINE_CURRENT / 'data'
OFFLINE_CURRENT_TOOLS = OFFLINE_CURRENT / 'tools'
LEGACY_STARTUP_HOOK = ROOT / 'runtime' / 'project7_startup_hook.py'
COMPONENT_DESCRIPTOR = UPSTREAM_PROJECT7 / 'component.json'
OFFICIAL_640_MANIFEST = UPSTREAM_PROVENANCE / 'patch2.android.640.version'
EXTERNAL_COMPONENT = ROOT / 'vendor' / 'project7' / 'component-v2.10.1.zip'
BRIDGE_JAVA_MODULES = frozenset({'android_project7_startup', 'android_project7_repair'})


def java_module_root(root, name):
    root = Path(root)
    if name in BRIDGE_JAVA_MODULES:
        return root / 'project7_bridge/android' / name
    return root / 'offline/current/java' / name


# Single explicit mapping for every Python2 source embedded in the P7 startup
# loader.  Do not infer ownership from a project7_/android_ filename prefix.
EMBEDDED_RUNTIME_SOURCES = {
    'project7_startup_hook.py': 'runtime/project7_startup_hook.py',
    'offline_tutorials.py': 'offline/runtime/offline_tutorials.py',
    'project7_collection_visibility.py': 'offline/current/runtime/project7_collection_visibility.py',
    'project7_collection_visibility/policy.json': 'offline/current/data/project7_collection_visibility/policy.json',
    'project7_shadow_capacity.py': 'offline/current/runtime/project7_shadow_capacity.py',
    'project7_shadow_capacity/policy.json': 'offline/current/data/project7_shadow_capacity/policy.json',
    'project7_draw_ui.py': 'offline/current/runtime/project7_draw_ui.py',
    'project7_furniture_ui.py': 'offline/current/runtime/project7_furniture_ui.py',
    'project7_friend_ui.py': 'offline/current/runtime/project7_friend_ui.py',
    'project7_selector_ui.py': 'offline/current/runtime/project7_selector_ui.py',
    'project7_tutorial_completion.py': 'offline/current/runtime/project7_tutorial_completion.py',
    'project7_dynamic_ui_families.py': 'offline/current/runtime/project7_dynamic_ui_families.py',
    'project7_trial_retry_compat.py': 'offline/current/runtime/project7_trial_retry_compat.py',
    'android_trial_retry/trial-ui-policy-v1.json': 'offline/current/java/android_trial_retry/trial-ui-policy-v1.json',
    'project7_wish_ui.py': 'offline/current/runtime/project7_wish_ui.py',
    'project7_wish_transport.py': 'offline/current/runtime/project7_wish_transport.py',
    'project7_inventory_editor_ui.py': 'offline/current/runtime/project7_inventory_editor_ui.py',
}
EMBEDDED_RUNTIME_ORDER = tuple(EMBEDDED_RUNTIME_SOURCES)


def runtime_source(name):
    """Resolve an embedded runtime basename through the explicit mapping."""
    return ROOT / EMBEDDED_RUNTIME_SOURCES[name]


RECORDED_SOURCE_PATHS = {
    'runtime/android_history_draw/src/com/project7/localmanager/HistoryDrawPolicy.java':
        'offline/current/java/android_history_draw/src/com/project7/localmanager/HistoryDrawPolicy.java',
    'runtime/offline_battle.py': 'offline/runtime/offline_battle.py',
    'runtime/offline_conditions.py': 'offline/runtime/offline_conditions.py',
    'runtime/offline_stage.py': 'offline/runtime/offline_stage.py',
    'runtime/project7_action_ledger_code20_patch/seams.xor-zlib':
        'project7_bridge/runtime/project7_action_ledger_code20_patch/seams.xor-zlib',
    'runtime/project7_action_ledger_integration_candidate/trigger-extra-code20-v1.tsv':
        'offline/current/data/project7_action_ledger_integration_candidate/trigger-extra-code20-v1.tsv',
    'runtime/project7_bson_fast/BsonLite-fast.dex':
        'project7_bridge/runtime/project7_bson_fast/BsonLite-fast.dex',
    'runtime/project7_bson_fast/BsonLite.smali':
        'project7_bridge/runtime/project7_bson_fast/BsonLite.smali',
    'runtime/project7_event_auto_trigger_candidate/trigger-extra-v1.tsv':
        'offline/current/data/project7_event_auto_trigger_candidate/trigger-extra-v1.tsv',
    'runtime/project7_event_auto_trigger_condition_candidate/trigger-extra-conditions-v1.tsv':
        'offline/current/data/project7_event_auto_trigger_condition_candidate/trigger-extra-conditions-v1.tsv',
    'runtime/project7_mainline32_data_candidate/catalog-v1.json.gz':
        'offline/current/data/project7_mainline32_data_candidate/catalog-v1.json.gz',
    'runtime/project7_mainline32_data_candidate/contract-v1.json':
        'offline/current/data/project7_mainline32_data_candidate/contract-v1.json',
    'runtime/project7_manager_rpc_projection_patch/LocalGatewayServer.smali':
        'project7_bridge/runtime/project7_manager_rpc_projection_patch/LocalGatewayServer.smali',
}

def resolve_recorded_path(path):
    """Resolve a historical path recorded in a pinned contract.

    Contract bytes remain unchanged so their pins stay valid; only path lookup
    follows the explicit source partition.
    """
    recorded = Path(path)
    if recorded.is_absolute():
        return recorded
    text = recorded.as_posix()
    if text in RECORDED_SOURCE_PATHS:
        return ROOT / RECORDED_SOURCE_PATHS[text]
    if text == 'runtime/project7_startup_hook.py':
        return LEGACY_STARTUP_HOOK
    if text == 'runtime/project7_component.json':
        return COMPONENT_DESCRIPTOR
    if text.startswith('runtime/android_'):
        rest = text[len('runtime/'):]
        module, _, tail = rest.partition('/')
        candidate = java_module_root(ROOT, module) / tail
        if candidate.exists():
            return candidate
    if text.startswith('runtime/'):
        rest = text[len('runtime/'):]
        candidates = [PROJECT7_BRIDGE_RUNTIME / rest,
                      OFFLINE_CURRENT_DATA / rest,
                      OFFLINE_CURRENT_RUNTIME / rest,
                      OFFLINE_RUNTIME / rest]
        for candidate in candidates:
            if candidate.exists():
                return candidate
    if text.startswith('tools/'):
        rest = text[len('tools/'):]
        for root in (OFFLINE_CURRENT_TOOLS, PROJECT7_BRIDGE_TOOLS, OFFLINE_TOOLS):
            candidate = root / rest
            if candidate.exists():
                return candidate
    return ROOT / recorded
