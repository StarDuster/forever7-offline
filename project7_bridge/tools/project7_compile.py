"""Compile real Project7 adapter sources with disjoint compile-only API groups.

No APK/DEX assembly or game execution. Stub definitions never enter the merged
production output. No converted manager JAR or maintainer analysis is required.
"""
import _bootstrap  # noqa: E402,F401
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import zipfile

from project7_feature_hooks import PINS as FEATURE_HOOK_PINS
MANAGER_SHA = '0b4c41a5461840fb7bdb02529732a2c6849d604893b6a9390b9a9404618d0eb4'

from _bootstrap import ROOT
from forever7_paths import java_module_root


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def class_members(data, include_constructors=False):
    """Read JVM member descriptors/static shape, without loading API class bodies."""
    pos = 0
    def take(n):
        nonlocal pos
        if pos + n > len(data): raise ValueError('Truncated compile API class')
        value = data[pos:pos+n]; pos += n; return value
    def u2(): return struct.unpack('>H', take(2))[0]
    def u4(): return struct.unpack('>I', take(4))[0]
    if take(4) != b'\xca\xfe\xba\xbe': raise ValueError('Compile API class magic')
    take(4); count=u2(); cp=[None]*count; index=1
    while index<count:
        tag=take(1)[0]
        if tag==1: cp[index]=take(u2()).decode('utf-8')
        elif tag in (3,4): take(4)
        elif tag in (5,6): take(8); index+=1
        elif tag in (7,8,16,19,20): take(2)
        elif tag in (9,10,11,12,17,18): take(4)
        elif tag==15: take(3)
        else: raise ValueError('Compile API constant pool tag')
        index+=1
    take(6); take(2*u2()); result={}
    for kind in ('field','method'):
        for _ in range(u2()):
            access,name,descriptor=u2(),cp[u2()],cp[u2()]
            # Java creates empty placeholder ctors in narrow descriptor stubs.
            # No own program calls them; real constructors are checked separately
            # against the pinned manager during maintainer ABI verification.
            if name != '<clinit>' and (include_constructors or name != '<init>'):
                result[(kind,name,descriptor)] = bool(access & 8)
            for _ in range(u2()): take(2); take(u4())
    return result


def verify_api_superset(chosen, candidates, merged):
    for name, rows in candidates.items():
        if (merged / name).exists(): continue
        actual=class_members(chosen[name])
        for group,data in rows:
            for member,static in class_members(data).items():
                if member not in actual or actual[member] != static:
                    raise ValueError('Compile API is not a descriptor superset: '+name+' '+repr(member)+' from '+group)


def verify_stage(stage):
    report = json.loads((stage / 'build-inputs.json').read_text())
    if (report.get('backend') != 'project7' or report.get('legacy_gateway_enabled') is not False or
            report.get('manager_core_rpc_prefix') is not True or
            report.get('ordinary_draw_policy') is not True or
            report.get('beginner_new_groups_blocked') is not True or
            report.get('historical_draw_seams') is not True or
            report.get('request_event_dispatch') is not True or
            report.get('minimum_android_api') != 26):
        raise ValueError('Complete current Project7 static stage required')
    names = set()
    for row in report['files'] + report['generated_sources']:
        name = row['path']
        parts = Path(name).parts
        if Path(name).is_absolute() or '..' in parts or name in names:
            raise ValueError('Unsafe/duplicate stage member')
        names.add(name)
        path = stage / name
        if not path.is_file() or path.is_symlink() or path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise ValueError('Stage inventory mismatch: ' + name)
    if (report.get('historical_furniture_seams') is not True or
            report.get('baiye_transactions') is not True or
            report.get('baiye_shop') is not True or
            report.get('story_basics') is not True or
            report.get('wish_backend_candidate') is not True or
            report.get('story_mission_seams') is not True or
            report.get('dynamic_draw_candidate') is not True or
            report.get('reliable_sequence_scope_seam') is not True or
            report.get('selector_draw_seams') is not True or
            report.get('event_reset_week_seams') is not True or
            report.get('dream_lifecycle_seams') is not True or
            report.get('dream_mechanism_seams') is not True):
        raise ValueError('Complete current Project7 furniture/dream stage required')
    if sha(stage / 'classes7.dex') != MANAGER_SHA:
        raise ValueError('Manager RPC prefix not applied')
    generated = [stage / row['path'] for row in report['generated_sources']]
    if len(generated) != 1 or generated[0].name != 'Project7BundledResources.java':
        raise ValueError('Unexpected generated resource contract')
    return generated


def compile_sources(stage, output, toolchains=None, root=ROOT):
    stage, output, root = map(Path, (stage, output, root))
    if output.exists() or output.is_symlink():
        raise ValueError('Compilation output already exists')
    generated = verify_stage(stage)
    toolchains = Path(toolchains) if toolchains is not None else root / 'toolchains'
    javac = toolchains / 'java/jdk-17.0.21+9/Contents/Home/bin/javac'
    android = toolchains / 'android-sdk/platforms/android-32/android.jar'
    for path in (javac, android):
        if not path.is_file():
            raise ValueError('Missing compile tool: ' + str(path))
    groups = [
        ('startup', ['android_resource_init', 'android_single_package', 'android_autologin',
                     'android_collection', 'android_project7_startup', 'android_project7_repair'],
         [root / 'offline/current/java/android_single_package/compile_stubs/com/project7/localmanager/ManagerApiStubs.java',
          root / 'offline/current/java/android_autologin/compile_stubs/com/netease/neox/NativeInterface.java'], generated),
        ('core-rpc', ['android_core_rpc'],
         sorted((root / 'offline/current/java/android_core_rpc/compile_stubs').rglob('*.java')), []),
        ('draw-policy', ['android_draw_policy'],
         sorted((root / 'offline/current/java/android_draw_policy/compile_stubs').rglob('*.java')), []),
        ('history-draw', ['android_history_draw', 'android_selector_draw', 'android_dynamic_draw'],
         sorted((root / 'offline/current/java/android_dynamic_draw/compile_stubs').rglob('*.java')), []),
        ('request-events', ['android_request_events'],
         sorted((root / 'offline/current/java/android_request_events/compile_stubs').rglob('*.java')), []),
        ('dream-mode', ['android_dream_mode'],
         sorted((root / 'offline/current/java/android_dream_mode/compile_stubs').rglob('*.java')), []),
        ('week-reset', ['android_week_reset'],
         sorted((root / 'offline/current/java/android_week_reset/compile_stubs').rglob('*.java')), []),
        ('story-missions', ['android_story_missions'],
         sorted((root / 'offline/current/java/android_story_missions/compile_stubs').rglob('*.java')), []),
        ('trial-retry', ['android_trial_retry'],
         [root / 'offline/current/java/android_trial_retry/compile_stubs/com/project7/localmanager/TrialApiStubs.java'], []),
        ('baiye-transactions', ['android_baiye_transactions', 'android_baiye_shop', 'android_story_basics'],
         sorted((root / 'offline/current/java/android_baiye_shop/compile_stubs').rglob('*.java')), []),
        ('wish-draw', ['android_wish_draw'],
         sorted((root / 'offline/current/java/android_wish_draw/compile_stubs').rglob('*.java')), []),
        ('mechanism-gateway', ['android_mechanism_gateway'],
         sorted((root / 'offline/current/java/android_mechanism_gateway/compile_stubs').rglob('*.java')), []),
        ('story-city', ['android_story_city', 'android_story_shared'],
         sorted((root / 'offline/current/java/android_story_city/compile_stubs').rglob('*.java')), [])]
    inputs, work = [], []
    for name, directories, stubs, additional in groups:
        sources = sorted(p for directory in directories for p in (java_module_root(root, directory) / 'src').rglob('*.java')) + additional
        if not sources or not stubs or any(not p.is_file() for p in sources + stubs):
            raise ValueError('Incomplete production source/API group: ' + name)
        work.append((name, sources, stubs))
        inputs.extend(sources + stubs)
    before = {str(p): sha(p) for p in inputs}
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=output.name + '.part-', dir=output.parent))
    try:
        merged = temporary / 'production-classes'
        merged.mkdir()
        reports = []
        api_classes, api_candidates, api_sources = {}, {}, {}
        common = [str(javac), '-source', '8', '-target', '8', '-Xlint:-options', '-encoding', 'UTF-8']
        for name, sources, stubs in work:
            stub_output, production = temporary / (name + '-compile-only'), temporary / (name + '-production')
            stub_output.mkdir()
            production.mkdir()
            subprocess.run(common + ['-cp', str(android), '-d', str(stub_output)] + [str(p) for p in stubs], check=True)
            for path in sorted(stub_output.rglob('*.class')):
                # Keep startup's ProfileProvider hierarchy, core's complete
                # BSON/ResourceEngine API, and history's catalog/DrawEngine
                # supersets. Individual groups use
                # narrow compile stubs; D8 receives their reviewed superset.
                relative = path.relative_to(stub_output).as_posix()
                api_candidates.setdefault(relative, []).append((name, path.read_bytes()))
                preferred = ((relative.startswith('com/project7/localmanager/LocalEventCatalog') and name == 'week-reset') or
                             (relative == 'com/project7/localmanager/LocalResourceCatalog$Hero.class' and name == 'baiye-transactions') or
                             (relative.startswith('com/project7/localmanager/LocalResourceEngine') and name == 'core-rpc') or
                             (relative == 'com/project7/localmanager/LocalEventEngine.class' and name == 'dream-mode') or
                             (relative == 'com/project7/localmanager/BsonLite.class' and name == 'core-rpc') or
                             (relative.startswith('com/project7/localmanager/LocalResourceCatalog') and
                              name in ('draw-policy', 'history-draw')) or
                             (relative == 'com/project7/localmanager/LocalDrawEngine.class' and name == 'history-draw'))
                if relative not in api_classes or preferred:
                    api_classes[relative] = path.read_bytes()
                    api_sources[relative] = name
            production_classpath = [str(android), str(stub_output)]
            if name in ('wish-draw', 'trial-retry'):
                # Typed extension and Store mutation helper come from prior
                # production groups, never another copy of their API stubs.
                production_classpath.append(str(merged))
            subprocess.run(common + ['-cp', os.pathsep.join(production_classpath), '-d', str(production)] +
                           [str(p) for p in sources], check=True)
            allowed = {p.stem for p in sources}
            classes = sorted(production.rglob('*.class'))
            if not classes:
                raise ValueError('No production classes: ' + name)
            for path in classes:
                if path.stem.split('$')[0] not in allowed:
                    raise ValueError('Compile-only class leaked into production: ' + str(path))
                destination = merged / path.relative_to(production)
                if destination.exists():
                    raise ValueError('Production class collision: ' + str(destination))
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination)
            reports.append({'group': name, 'production_classes': len(classes),
                            'sources': [str(p.relative_to(root)) if p.is_relative_to(root) else str(p) for p in sources]})
            # Publication includes only production output and its inventory.
            shutil.rmtree(stub_output)
            shutil.rmtree(production)
        if before != {str(p): sha(p) for p in inputs}:
            raise ValueError('Source changed during compilation')
        required = ['com/forever7/offline/Project7ResourceInitActivity.class',
                    'com/forever7/offline/Project7BundledResources.class',
                    'com/forever7/offline/Project7RepairHost.class',
                    'com/forever7/offline/Project7RepairProtocol.class',
                    'com/netease/qrzd/Project7LoginDialog.class',
                    'com/project7/localmanager/CoreGapBridge.class',
                    'com/project7/localmanager/CoreDrawPolicy.class',
                    'com/project7/localmanager/HistoryDrawPolicy.class',
                    'com/project7/localmanager/SelectorPolicy.class',
                    'com/project7/localmanager/DynamicDrawPolicy.class',
                    'com/project7/localmanager/BaiyeGateway.class',
                    'com/project7/localmanager/BaiyeShopGateway.class',
                    'com/project7/localmanager/BaiyeTransactions.class',
                    'com/project7/localmanager/RequestEventGateway.class',
                    'com/project7/localmanager/DreamCoordinator.class',
                    'com/project7/localmanager/DreamRequestGateway.class',
                    'com/project7/localmanager/DreamEconomyPolicy.class',
                    'com/project7/localmanager/DreamPatrolGatewayHooks.class',
                    'com/project7/localmanager/OfflineMechanismGateway.class',
                    'com/project7/localmanager/EventResetWeekPolicy.class',
                    'com/project7/localmanager/EventResetWeekGateway.class',
                    'com/project7/localmanager/FullCollectionInitializer.class']
        required.append('com/project7/localmanager/TrialRetryGateway.class')
        if any(not (merged / name).is_file() for name in required):
            raise ValueError('Required startup/helper class missing')
        for name in ['com/netease/neox/NativeInterface.class', 'com/project7/localmanager/BsonLite.class',
                     'com/project7/localmanager/LocalGatewayServer.class', 'com/project7/localmanager/LocalProfileStore.class']:
            if (merged / name).exists():
                raise ValueError('Original manager/game API stub packaged')
        verify_api_superset(api_classes, api_candidates, merged)
        api_jar = temporary / 'compile-api.jar'
        with zipfile.ZipFile(api_jar, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(api_classes.items()):
                if (merged / name).exists():
                    # Startup may compile against the own policy's descriptor;
                    # its real definition is program input, never classpath too.
                    continue
                info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
        report = {'format': 'project7-compiled-inputs-v1', 'backend': 'project7',
                  'minimum_android_api': 26, 'groups': reports,
                  'source_hashes': before, 'stub_classes_packaged': False,
                  'stage_inventory_sha256': sha(stage / 'build-inputs.json'),
                  'compile_api': {'path': 'compile-api.jar', 'bytes': api_jar.stat().st_size,
                                  'sha256': sha(api_jar), 'use': 'D8 classpath only, NEVER program input or APK',
                                  'abi_superset_verified': True,
                                  'class_sources': {name: api_sources[name] for name in sorted(api_sources) if not (merged / name).exists()}},
                  'classes': [{'path': p.relative_to(merged).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p)}
                              for p in sorted(merged.rglob('*.class'))],
                  'dex_built': False, 'apk_built': False, 'native_verified': False}
        (temporary / 'compile-inputs.json').write_text(json.dumps(report, indent=2) + '\n')
        if output.exists():
            raise ValueError('Compilation output appeared during build')
        temporary.rename(output)
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--toolchains', type=Path, default=ROOT / 'toolchains')
    args = parser.parse_args()
    report = compile_sources(args.stage, args.output, args.toolchains)
    print(json.dumps({'production_classes': len(report['classes']), 'stub_classes_packaged': False,
                      'dex_built': False, 'apk_built': False}))


if __name__ == '__main__':
    main()
