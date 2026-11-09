"""Submit an opt-in local test command to the isolated development emulator.

The runtime must have offline_development.flag. This is not an installer or a
remote service and refuses physical device serials. Normal APK builds need no
such flag. Commands execute inside the local game's Python2 VM.
"""
import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = '/sdcard/Android/data/com.netease.qrzd/files/netease/qrzd/Documents'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--serial', default='emulator-5554')
    args = parser.parse_args()
    if not re.fullmatch(r'emulator-\d+', args.serial):
        raise ValueError('Development probes are restricted to the isolated emulator')
    source = args.source.read_text(encoding='ascii')
    adb = [str(ROOT / 'toolchains/android-sdk/platform-tools/adb'), '-s', args.serial]

    def shell(*command):
        return subprocess.check_output(adb + ['shell', *command], text=True).strip()

    shell('test', '-f', DOCUMENTS + '/offline_development.flag')
    package = shell('cmd', 'package', 'list', 'packages', '-U', 'com.netease.qrzd')
    match = re.search(r'package:com\.netease\.qrzd uid:(\d+)', package)
    if not match:
        raise ValueError('Cannot identify the test app owner')
    context = shell('ls', '-Z', DOCUMENTS + '/offline_boot_probe.txt').split()[0]
    if not context.startswith('u:object_r:media_rw_data_file:s0:'):
        raise ValueError('Cannot identify the native app-created resource context')
    staging = DOCUMENTS + '/offline_probe.py.part'
    subprocess.run(adb + ['push', str(args.source), staging], check=True)
    shell('chown', match[1] + ':1078', staging)
    shell('chcon', context, staging)
    shell('mv', staging, DOCUMENTS + '/offline_probe.py')
    print('Queued %s ASCII bytes for the local emulator' % len(source))


if __name__ == '__main__':
    main()
