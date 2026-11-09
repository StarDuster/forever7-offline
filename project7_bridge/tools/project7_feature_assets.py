"""Fixed public feature catalogs required by the reviewed manager seams."""
import _bootstrap  # noqa: E402,F401
import hashlib
import json
from pathlib import Path

from _bootstrap import ROOT
CLIENT_EVENT_COMPAT = 'assets/client_event_compat.py'
CLIENT_EVENT_COMPAT_SHA = '2e71563c026873045c9516e8f2288142c2250a8220de4615d0377ecc28375272'
HISTORY_CATALOG = 'assets/project7_history/catalog-v3.tsv'
HISTORY_CATALOG_SHA = 'b439ab44280a959cab8836595b65489fee3fd8482609ed3caa55477a66fd5c16'
SELECTOR_CATALOG = 'assets/project7_selector/catalog-v1.tsv'
SELECTOR_CATALOG_SHA = '40a42441c3e55a179c931a4cb5e70a4e6e94e0913f4ef1eb654354a72341b6d7'
BAIYE_CATALOG = 'assets/project7_baiye/catalog-v1.tsv'
BAIYE_CATALOG_SHA = '0c2a8199eb0ff9ed2d678fc29128a95e267af94642af471f7050c5d0565e4141'
BAIYE_FRAGMENTS = 'assets/project7_baiye/fragments-v1.tsv'
BAIYE_FRAGMENTS_SHA = '61425f912e2bd5fc613aebc75ab43819b801e0b6a608afd37230bb7a37d4d5f1'
BAIYE_SHOP_CATALOG = 'assets/project7_baiye_shop/catalog-v1.tsv'
BAIYE_SHOP_CATALOG_SHA = 'ae6523fd78136fa7a1ef893911ca191ff764a1fe7866d9101b62a518216a0501'
DYNAMIC_CATALOG = 'assets/project7_dynamic/catalog-v1.json.gz'
DYNAMIC_CATALOG_SHA = '845e146b5fd19fc119ff79ebee6671755c35cfad9a41743003e1898e987b7c5e'
# Public UI admission is distinct from raw data and backend family eligibility.
DYNAMIC_PUBLIC_READY_IDS = (2, 3, 4, 16, 17, 32, 37, 42, 47, 52, 57, 62, 67, 72,
                            81, 88, 89, 101, 107, 175, 187, 203, 210, 222, 241, 253,
                            260, 270, 282, 283, 288, 295, 311, 323, 341, 362, 363,
                            382, 425, 433, 440, 485, 486, 487, 488, 491)
WISH_CATALOG = 'assets/project7_wish/catalog-v1.json'
WISH_CATALOG_SHA = '4abad0f105f6b2088632369e5ff86040791640c9724deb85d75c57660a168c91'
WISH_PUBLIC_READY_IDS = (5, 119, 126, 143, 154, 164, 397, 426, 445)
STORY_MISSION_CATALOG = 'assets/project7_story_missions/catalog-v1.tsv'
STORY_MISSION_CATALOG_SHA = 'ce54f931f6d462d0c6fabb1f03dabf47ddc54780d89e3ec78fe21d9a6d7ef0d9'
STORY_EXTENDED_ASSETS = {
    'assets/economy.tsv': '037e36ab1a517ba7a0972764eed25807c64139a2e9358ed72923d065f01ab0d9',
    'assets/suppression.tsv': 'b0f8cfa1637d65061f0f062ba78ef79e9fdee2b93889a9b832cb0cddd1160679',
}
STORY_CITY_SUPPRESSION_SHA = '958688e27cfbec4b897508d04612e6cce49fe82d917af727a3fe3bbfc43272cd'
STORY_CITY_EXTENDED_ASSETS = {
    'assets/economy.tsv': '4c504ae5fc5a431fb6eeffd6fb48df614bbfa00f0c2a8a949e23d1cd4363ed9a',
    'assets/suppression.tsv': '574d8c7e63a4ce648705b3f4d1cfbfced9e30fbf9cfd513cb09138290812bc86',
}
FURNITURE_CATALOG = 'assets/project7_history/furniture-v1.tsv'
FURNITURE_CATALOG_SHA = 'dd85b09e9f3094a2c5a9f72a3300e04ad85e63b9730c6cdd8ab2a32b54ba4a2d'
DREAM_CATALOG = 'assets/project7_dream/catalog-v1.tsv'
DREAM_CATALOG_SHA = 'b0c44413ecaad293b622933f8ece4b3199dfd6de7f63c64b4cc3655bea2ef8c1'
REQUEST_EVENT_CATALOG = 'assets/offline/request-events.tsv'
REQUEST_EVENT_CATALOG_SHA = '7088dabb1a5b84609f8b23154992660d6239389be0d54316549d2dfa94d7c475'
ENDING_TRIGGER_CATALOG = 'assets/offline/ending-trigger-v1.json'
ENDING_TRIGGER_CATALOG_SHA = '1792a804aba72c806a7bb73dce3a42baf52695ff0edc5b476fbbe05c89095431'
EVENT_RESET_CATALOG = 'assets/project7_week_reset/catalog-v1.tsv'
EVENT_RESET_CATALOG_SHA = 'dc43ebe5d922443100f3aa8ec55151ecd5f94b6c8ed85b780d3248338d3d3b4a'
STORY_MENU_SHARED_CATALOG = 'assets/project7_story_shared/special-selector-v1.json'
STORY_MENU_SHARED_CATALOG_SHA = '5b9d6b01f7fd77ed63f1f301b39ef31db4d7b8fb644383aa28aadcec000404aa'
MAINLINE32_ENTRY = 'assets/project7_story_shared/mainline32-entry-v1.json'
MAINLINE32_ENTRY_SHA = '3fac026a76a947f5bca4d60a7d70d619510f145fa253b9ee3429f3082ce5bd86'
MENU10_ENTRY_CATALOG = 'assets/project7_story_shared/menu10-entry-v1.json'
MENU10_ENTRY_CATALOG_SHA = '4bd8602a3999f142dfbdeb97aa3330f030c54f3099bb0ed36bde444bf85f9cae'
SOURCES = {
    CLIENT_EVENT_COMPAT: ('offline/current/data/project7_event_continuation/client_event_compat.py', CLIENT_EVENT_COMPAT_SHA),
    STORY_MENU_SHARED_CATALOG: ('offline/current/java/android_story_shared/catalog/special-selector-v1.json', STORY_MENU_SHARED_CATALOG_SHA),
    MAINLINE32_ENTRY: ('offline/current/java/android_story_shared/catalog/mainline32-entry-v1.json', MAINLINE32_ENTRY_SHA),
    MENU10_ENTRY_CATALOG: ('offline/current/java/android_story_shared/catalog/menu10-entry-v1.json', MENU10_ENTRY_CATALOG_SHA),
    STORY_MISSION_CATALOG: ('offline/current/data/project7_story_mission_catalog/catalog-v1.tsv', STORY_MISSION_CATALOG_SHA),
    WISH_CATALOG: ('offline/current/data/project7_wish_catalog/catalog-v1.json', WISH_CATALOG_SHA),
    BAIYE_SHOP_CATALOG: ('offline/current/data/project7_baiye_shop_catalog/catalog-v1.tsv', BAIYE_SHOP_CATALOG_SHA),
    DYNAMIC_CATALOG: ('offline/current/data/project7_dynamic_catalog/catalog-v1.json.gz', DYNAMIC_CATALOG_SHA),
    BAIYE_CATALOG: ('offline/current/data/project7_baiye_catalog/catalog-v1.tsv', BAIYE_CATALOG_SHA),
    BAIYE_FRAGMENTS: ('offline/current/data/project7_baiye_catalog/fragments-v1.tsv', BAIYE_FRAGMENTS_SHA),
    SELECTOR_CATALOG: ('offline/current/data/project7_selector_catalog/catalog-v1.tsv', SELECTOR_CATALOG_SHA),
    EVENT_RESET_CATALOG: ('offline/current/data/project7_week_reset/catalog-v1.tsv', EVENT_RESET_CATALOG_SHA),
    FURNITURE_CATALOG: ('offline/current/data/project7_history_catalog/furniture-v1.tsv', FURNITURE_CATALOG_SHA),
    DREAM_CATALOG: ('offline/current/data/project7_dream_catalog/catalog-v1.tsv', DREAM_CATALOG_SHA),
    HISTORY_CATALOG: ('offline/current/data/project7_history_catalog/catalog-v3.tsv', HISTORY_CATALOG_SHA),
    REQUEST_EVENT_CATALOG: ('offline/current/data/project7_request_events/request-events.tsv', REQUEST_EVENT_CATALOG_SHA),
    ENDING_TRIGGER_CATALOG: ('offline/current/data/project7_request_events/ending-trigger-v1.json', ENDING_TRIGGER_CATALOG_SHA),
}


def feature_assets(root=ROOT):
    result = {}
    for name, (source, expected) in SOURCES.items():
        data = (Path(root) / source).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('Feature catalog hash mismatch: ' + name)
        result[name] = data
    return result


def history_ui_policy(root=ROOT):
    """Static P rows plus the independently reviewed dynamic public UI scope."""
    data = feature_assets(root)[HISTORY_CATALOG]
    all_ids, ready_ids = [], []
    for line in data.decode('ascii').splitlines():
        fields = line.split('\t')
        if fields[0] != 'P':
            continue
        if len(fields) != 6 or fields[4] not in ('0', '1'):
            raise ValueError('Historical UI catalog pool row')
        identity = int(fields[1])
        if identity <= 0 or identity in (1, 354, 484) or identity in all_ids:
            raise ValueError('Historical UI reserved/duplicate pool')
        all_ids.append(identity)
        if fields[4] == '1':
            ready_ids.append(identity)
    if not ready_ids:
        raise ValueError('Historical UI has no supported pools')
    if not set(DYNAMIC_PUBLIC_READY_IDS).issubset(all_ids):
        raise ValueError('Dynamic public UI scope outside historical catalog')
    if DYNAMIC_PUBLIC_READY_IDS and set(DYNAMIC_PUBLIC_READY_IDS) != set(json.loads(dynamic_ui_policy(root))['publishable_ids']):
        raise ValueError('Dynamic public UI scope lacks its exact detail policy')
    if (set(WISH_PUBLIC_READY_IDS).intersection(DYNAMIC_PUBLIC_READY_IDS) or
            not set(WISH_PUBLIC_READY_IDS).issubset(all_ids) or
            set(WISH_PUBLIC_READY_IDS) != set(json.loads(wish_ui_policy(root))['verified_ids'])):
        raise ValueError('Wish public UI scope lacks its exact separate detail policy')
    ready_ids = sorted(set(ready_ids).union(DYNAMIC_PUBLIC_READY_IDS, WISH_PUBLIC_READY_IDS))
    return json.dumps({'schema': 'project7-history-ui-v1', 'asset_sha256': HISTORY_CATALOG_SHA,
                       'ready_ids': sorted(ready_ids), 'all_history_ids': sorted(all_ids)},
                      sort_keys=True, separators=(',', ':'))


def furniture_ui_policy(root=ROOT):
    """Project only the server's immutable historical furniture pool scopes."""
    data = feature_assets(root)[FURNITURE_CATALOG]
    ids = []
    for line in data.decode('ascii').splitlines():
        fields = line.split('\t')
        if fields[0] != 'F':
            continue
        if len(fields) != 3:
            raise ValueError('Furniture UI catalog row')
        identity = int(fields[1])
        if identity <= 0 or identity == 162 or identity in ids:
            raise ValueError('Furniture UI reserved/duplicate pool')
        ids.append(identity)
    if len(ids) != 40:
        raise ValueError('Furniture UI scope changed')
    return json.dumps({'schema': 'project7-history-furniture-ui-v1',
                       'asset_sha256': FURNITURE_CATALOG_SHA,
                       'ready_ids': sorted(ids), 'all_history_ids': sorted(ids)},
                      sort_keys=True, separators=(',', ':'))


def selector_ui_policy(root=ROOT):
    """Use the same pinned, public-only candidate projection as the backend."""
    from project7_selector_catalog import ui_policy
    data = ui_policy(Path(root) / 'offline/current/data/project7_selector_catalog')
    return json.dumps(data, sort_keys=True, separators=(',', ':'))


def dynamic_ui_policy(root=ROOT):
    """One source-bound family owner; publication requires the exact verified scope."""
    from project7_dynamic_ui_family_policy import ui_policy, canonical
    data = ui_policy(Path(root) / 'offline/current/data/project7_dynamic_catalog')
    scope = set(DYNAMIC_PUBLIC_READY_IDS)
    if (data['backend_sha256'] != DYNAMIC_CATALOG_SHA or
            data['base_sha256'] != HISTORY_CATALOG_SHA or
            scope != set(data['detail_ids']) or scope != set(data['verified_ids']) or
            scope != set(data['publishable_ids']) or
            scope != {row['id'] for row in data['pools']}):
        raise ValueError('Dynamic UI/backend catalog binding differs')
    return canonical(data).decode('ascii')


def wish_ui_policy(root=ROOT):
    """Fixed nine source scopes; Main publication is independent of its own manifest."""
    from project7_wish_ui_policy import ui_policy, canonical
    data = ui_policy(Path(root) / 'offline/current/data/project7_wish_catalog')
    scope = set(WISH_PUBLIC_READY_IDS)
    if (data['backend_sha256'] != WISH_CATALOG_SHA or
            data['base_sha256'] != HISTORY_CATALOG_SHA or
            scope != set(data['detail_ids']) or scope != set(data['verified_ids']) or
            scope != {row['id'] for row in data['pools']} or
            scope.intersection(DYNAMIC_PUBLIC_READY_IDS)):
        raise ValueError('Wish UI/backend catalog binding differs')
    return canonical(data).decode('ascii')
