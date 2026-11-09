"""Materialize fixed resource metadata and bind it to the actual patched scripts.

End-user builds consume only project data, never maintainer analysis files or
downloaded .check objects. This metadata does not contain game material payloads.
"""
import _bootstrap  # noqa: E402,F401
import gzip
import hashlib
import io
import json
from pathlib import Path

from project7_component import PINS, npk

from _bootstrap import ROOT
DATA = ROOT / 'offline/current/data/project7_resources'
PACKED_SHA = '9ce83088f69bc7480140aef46581e9a8a1748dd3d3d9cf3808d50504a4992da0'
SNAPSHOT_SHA = 'b8cf01a3175f470f921441d077c2edcbac43ad5dd64de09af1ac011e27573471'
BINDING_SHA = '9f7ae46a414f45a5e955d045297842b62b6fe26cdf4def5a2b800cbe73eb1be9'
SNAPSHOT_SIZE = 17437832
SNAPSHOT_ASSET = 'offline/project7-resource-snapshot.json'
BINDING_ASSET = 'offline/project7-resource-binding.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fixed_snapshot(packed, binding):
    if digest(packed) != PACKED_SHA or digest(binding) != BINDING_SHA:
        raise ValueError('Fixed resource bundle pin mismatch')
    with gzip.GzipFile(fileobj=io.BytesIO(packed)) as stream:
        raw = stream.read(SNAPSHOT_SIZE + 1)
        if len(raw) != SNAPSHOT_SIZE or stream.read(1) or digest(raw) != SNAPSHOT_SHA:
            raise ValueError('Fixed resource snapshot size/hash mismatch')
    return raw, json.loads(binding)


def generated_contract(binding, binding_bytes):
    """Compile-time anchors; callers must never rebuild these from Documents."""
    asset = lambda name, size, sha: ('new Project7ResourceSnapshot.Asset("%s", %dL, "%s")' %
                                   (name, size, sha))
    scripts = ',\n                '.join(asset(row['name'], row['bytes'], row['sha256'])
                                        for row in binding['scripts'])
    return ('''package com.forever7.offline;

/** Generated from the pinned metadata and this build's actual script assets. */
public final class Project7BundledResources {
    private Project7BundledResources() { }
    public static Project7ResourceSnapshot.TrustedContract contract() {
        return new Project7ResourceSnapshot.TrustedContract(455, 640, "android",
            "%s",
            "%s",
            "%s", 312,
            %s,
            %s,
            java.util.Arrays.asList(
                %s));
    }
}
''' % (binding['sourceManifestSha256'], binding['resourceManifestSha256'],
       binding['entryManifestSha256'], asset(SNAPSHOT_ASSET, SNAPSHOT_SIZE, SNAPSHOT_SHA),
       asset(BINDING_ASSET, len(binding_bytes), digest(binding_bytes)), scripts)).encode('ascii')


def create_bundle(base_script, overlay_script):
    if digest(base_script) != PINS['official640']:
        raise ValueError('Unsupported official script baseline')
    base, overlay = npk(base_script), npk(overlay_script)
    if len(base) != 28754 or not overlay or not set(overlay) <= set(base):
        raise ValueError('Unexpected script overlay domain')
    raw, binding = fixed_snapshot((DATA / 'project7-resource-snapshot.json.gz').read_bytes(),
                                  (DATA / 'project7-resource-binding.json').read_bytes())
    binding['snapshotAsset'] = SNAPSHOT_ASSET
    binding['scripts'] = [{'name': name, 'bytes': len(payload), 'sha256': digest(payload)}
                          for name, payload in [('assets/script.npk', base_script),
                                                ('assets/project7_local.npk', overlay_script)]]
    binding_bytes = json.dumps(binding, separators=(',', ':'), ensure_ascii=True).encode('ascii')
    files = {'assets/' + SNAPSHOT_ASSET: raw, 'assets/' + BINDING_ASSET: binding_bytes}
    return files, generated_contract(binding, binding_bytes), binding
