"""Reconstruct reviewed manager seams from pinned deltas, without Java tooling.

These functions do not build an APK or establish feature/runtime readiness.
The caller must package and prepare the corresponding production helpers.
"""
import _bootstrap  # noqa: E402,F401
import hashlib
import json
from pathlib import Path

from project7_component import restore
from project7_dex_filter import u32, validate_header

from _bootstrap import ROOT
PINS = {'history': {'directory': 'project7_history_patch',
             'format': 'project7-history-generic-seams-v1',
             'source': 'd16990dff71677c55ecd54225cd1fdc82f06c3785c3258e5053e069f24df341f',
             'target': 'a71aa19649feaa262332ec03ff1c42254fb21886c1a73767b336f0dbd0c23d3b',
             'patch': '5e0af0a847fae92f6ab718309654a4a9aca078de8d39a3eb381bdecd475109af',
             'contract': 'ef6a2ba7c633420a73161fdfe051c4e6f3460415b097c9551a9cae6d2df8a3ec',
             'bytes': 1156044},
 'request_events': {'directory': 'project7_request_event_patch',
                    'format': 'project7-request-event-dispatch-v1',
                    'source': 'a71aa19649feaa262332ec03ff1c42254fb21886c1a73767b336f0dbd0c23d3b',
                    'target': '075edbaaf62c1d777c1982850fad4b68db518eae9e75ec4e50fc80a7ab7d0863',
                    'patch': 'dab2080a12bb9df4a824b340fa49236a8ffc8d9563f4a7c2c0a59b3d2fcab2f8',
                    'contract': '1d830488b6d300ff6ec30bc3a366a21c6d4293b306f7e03c77e5980a6538cc2f',
                    'bytes': 1156292},
 'furniture': {'directory': 'project7_furniture_patch',
               'format': 'project7-history-furniture-seams-v1',
               'source': '075edbaaf62c1d777c1982850fad4b68db518eae9e75ec4e50fc80a7ab7d0863',
               'target': '5e0e6220e63e04fda492608f34ff16230d010b2f8641fd37a7e4aa7fce80eb19',
               'patch': '3d1b51be23987f24ba00405cf098f047e4509e022f2941c8b0098e03e50679af',
               'contract': 'c98f730655f3c7fe16b49eb972070dab140996838aad556a7d5c6866d4e6dcad',
               'bytes': 1156824},
 'dream': {'directory': 'project7_dream_patch',
           'format': 'project7-dream-mechanism-seams-v1',
           'source': '5e0e6220e63e04fda492608f34ff16230d010b2f8641fd37a7e4aa7fce80eb19',
           'target': '74e2a7bdc71b1b1d1f3989fe44dc27d47cad433ecd0eccf9168d1d288efb744c',
           'patch': '2eaecc51ad40f866cfd67b57290150941cb80afe61c2c94e85073aabe8f62188',
           'contract': '06daca7fe6ec75d3dcd6d39176b3060c8aef7eb0ea2e8c5b02f5fe37a975fb3d',
           'bytes': 1157260},
 'dream_lifecycle': {'directory': 'project7_dream_lifecycle_patch',
                     'format': 'project7-dream-lifecycle-seams-v1',
                     'source': '74e2a7bdc71b1b1d1f3989fe44dc27d47cad433ecd0eccf9168d1d288efb744c',
                     'target': '523aa97f00b098694437f88d46821a3c9fbbfb60c5ed78213c2b16ccd976170b',
                     'patch': '2007405fe554d9dcbdb2789260c32a9e5aa4ee522143fa3577e2d85892d93a37',
                     'contract': '3a8e5a94d6a9bc34897503aa7acd33106c6ca7e16bf06376863921d432a7cc17',
                     'bytes': 1157916},
 'event_reset_week': {'directory': 'project7_event_reset_week_patch',
                      'format': 'project7-event-reset-week-seams-v1',
                      'source': '523aa97f00b098694437f88d46821a3c9fbbfb60c5ed78213c2b16ccd976170b',
                      'target': 'b461f49531efd2ab7fb09eb71e22ade0085e92f7567d5fddcff1c534fc68b257',
                      'patch': '38fa1ad5afe2f772b9fe0e2a8019b4626361c392631f796cc9c0b5c5d1fda66c',
                      'contract': 'f168648ca89d63208b6f86199e8959b8dab4a33e74f95fca1a75e7191c705345',
                      'bytes': 1158180},
 'selector': {'directory': 'project7_selector_patch',
              'format': 'project7-selector-seams-v1',
              'source': 'b461f49531efd2ab7fb09eb71e22ade0085e92f7567d5fddcff1c534fc68b257',
              'target': 'bcffb77c8370f640ac6c9728855ba738b78029deacf8dd41fe1e3aa957df5515',
              'patch': 'b87d4b186fcfee4d1a4dcfdb749c2ee4fea22e38009c1d77e8af6ee87722d612',
              'contract': '4e2c437f9e75789491e50fdd36b7b5bb46f2ba4f1ed93842bf9bc6d69cf77645',
              'bytes': 1158240},
 'reliable_scope': {'directory': 'project7_reliable_scope_patch',
                    'format': 'project7-reliable-scope-seams-v1',
                    'source': 'bcffb77c8370f640ac6c9728855ba738b78029deacf8dd41fe1e3aa957df5515',
                    'target': '9506b09dc71f90e257ad99c371bb396d411e885a8dbc2dcc17a2d2e824aadd7b',
                    'patch': 'bf499d1aef4aa925946f1e3f9405852408c35013a77273ba8f522b17bd85e24e',
                    'contract': '411fd9e1347fdbfd917fa5c318d59626fab5ac3f86501b9f9b43ddb3ce5f1d78',
                    'bytes': 1158280},
 'story_missions': {'directory': 'project7_story_mission_patch',
                    'format': 'project7-story-mission-seams-v1',
                    'source': '9506b09dc71f90e257ad99c371bb396d411e885a8dbc2dcc17a2d2e824aadd7b',
                    'target': '9339898c6f7f6b3950ef06731b8e18d68fe6b84b5838670a792c4601527a371b',
                    'patch': '5bc4550bf6ece09b9f271b5319d0a8437ce925a0a73aa266a41a78f33843484e',
                    'contract': '8a0e27b180738f08a6bd3f07beb9627cdf43f45b098e67d54d80f1ee8e4e6b39',
                    'bytes': 1158744},
 'trial_retry': {'directory': 'project7_trial_retry_patch',
                 'format': 'project7-trial-retry-seams-v1',
                 'source': '9339898c6f7f6b3950ef06731b8e18d68fe6b84b5838670a792c4601527a371b',
                 'target': '7f13c24a613676ee520bf6ed2590a6bf33788cb6955c92f3e9f446dee89c0d82',
                 'patch': '52d0ea5ff9ff4ccc78e0e191a7648ec9d74c960f7ba6bd0a9bb49495b40c51c7',
                 'contract': '045586933ad8b04575dbc5c2aa370bc82bb33c45cb37d95b7c6eee4697750c7a',
                 'bytes': 1159096}}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def apply_feature_hook(manager, feature, *, patch=None, contract=None):
    pin = PINS[feature]
    if sha(manager) != pin['source']:
        raise ValueError('Unsupported manager baseline for ' + feature)
    directory = ROOT / 'project7_bridge/runtime' / pin['directory']
    patch = (directory / 'seams.xor-zlib').read_bytes() if patch is None else patch
    contract = (directory / 'contract.json').read_bytes() if contract is None else contract
    if sha(patch) != pin['patch'] or sha(contract) != pin['contract']:
        raise ValueError('Feature patch/contract pin mismatch: ' + feature)
    info = json.loads(contract)
    if (info['format'] != pin['format'] or
            info['source'] != {'bytes': len(manager), 'sha256': pin['source']} or
            info['target'] != {'bytes': pin['bytes'], 'sha256': pin['target']}):
        raise ValueError('Feature source/target contract mismatch: ' + feature)
    result = restore(manager, patch, pin['bytes'])
    if sha(result) != pin['target'] or result[:8] != b'dex\n038\0':
        raise ValueError('Feature reconstructed DEX mismatch: ' + feature)
    validate_header(result)
    if u32(result, 96) != 649:
        raise ValueError('Feature changed manager class definitions: ' + feature)
    return result, info


def apply_history_hook(manager, **kwargs):
    return apply_feature_hook(manager, 'history', **kwargs)


def apply_request_event_hook(manager, **kwargs):
    return apply_feature_hook(manager, 'request_events', **kwargs)


def apply_furniture_hook(manager, **kwargs):
    return apply_feature_hook(manager, 'furniture', **kwargs)


def apply_dream_hook(manager, **kwargs):
    return apply_feature_hook(manager, 'dream', **kwargs)


def apply_dream_lifecycle_hook(manager, **kwargs):
    return apply_feature_hook(manager, 'dream_lifecycle', **kwargs)


def apply_event_reset_week_hook(manager, **kwargs):
    return apply_feature_hook(manager, 'event_reset_week', **kwargs)


def apply_selector_hook(manager, **kwargs):
    return apply_feature_hook(manager, 'selector', **kwargs)


def apply_reliable_scope_hook(manager, **kwargs):
    return apply_feature_hook(manager, 'reliable_scope', **kwargs)


def apply_story_mission_hook(manager, **kwargs):
    return apply_feature_hook(manager, 'story_missions', **kwargs)


def apply_trial_retry_hook(manager, **kwargs):
    return apply_feature_hook(manager, 'trial_retry', **kwargs)
