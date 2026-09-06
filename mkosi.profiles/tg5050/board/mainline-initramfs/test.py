#!/usr/bin/env python3
"""Check the packed ARM64 binary and init control flow without host mounts."""
import gzip
import os
from pathlib import Path
import platform
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parents[3] / 'build/mainline-initramfs.cpio.gz'
RUNNER = [] if platform.machine() == 'aarch64' else ['qemu-aarch64-static']

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    subprocess.run(['cpio', '-idmu', '--quiet'], cwd=root,
                   input=gzip.decompress(ARCHIVE.read_bytes()), check=True)
    busybox = root / 'bin/busybox'
    def run(*args):
        return subprocess.run([*RUNNER, str(busybox), *args], text=True,
                              capture_output=True, timeout=10)
    applets = run('--list-full')
    assert applets.returncode == 0, applets.stderr
    for name in applets.stdout.splitlines():
        assert (root / name).is_symlink(), name
        assert (root / name).resolve() == busybox, name
    for name in ['proc', 'sys', 'dev', 'newroot']:
        assert (root / name).is_dir(), name
    source = (root / 'init').read_text()
    assert source == (HERE / 'init').read_text()
    assert '\nmdev -s' not in source
    assert run('ash', '-n', str(root / 'init')).returncode == 0
    for name in ['mount', 'mkdir', 'sleep', 'switch_root']:
        result = run(name, '--help')
        # This stripped BusyBox emits no help text, but successful dispatch
        # proves the applet is compiled in (an absent applet exits 127).
        assert result.returncode == 0, (name, result)
    print('PASS: packed directories, applet links, ARM64 command dispatch, init syntax')

    # Mock only privileged operations and device readiness. Execute the actual
    # packed script's branches in its own ARM64 ash, not the host shell.
    body = source[source.index('mkdir -p /proc'):]
    body = body.replace('[ -b /dev/mmcblk0p4 ]', 'device_ready')
    body = body.replace('[ ! -b /dev/mmcblk0p4 ]', '! device_ready')
    body = body.replace('[ -x /newroot/sbin/init ]', 'init_ready')
    body = body.replace('cd /newroot', 'cdroot')
    body = body.replace('exec switch_root -c /dev/console /newroot /sbin/init', 'handoff')

    prelude = '''
set -u
n=0
mkdir() { echo "mkdir $*"; }
sleep() { n=$((n + 1)); }
cat() { [ "$mode" = break ] && echo 'rd.break=pre-switch-root'; return 0; }
device_ready() { [ "$mode" != absent ] && [ "$n" -ge 2 ]; }
init_ready() { [ "$mode" != missing_init ]; }
cdroot() { return 0; }
mount() {
    echo "mount $*"
    case "$*" in
        *devtmpfs*) [ "$mode" != dev_failure ] || return 1 ;;
        *rw,noatime*) [ "$mode" != mount_failure ] || return 1 ;;
    esac
    return 0
}
rescue() { echo "RESCUE $*"; exit 42; }
handoff() { echo "HANDOFF waits=$n"; exit 0; }
'''
    cases = {
        'success': (0, 'HANDOFF waits=2'),
        'absent': (42, 'did not appear within 20 seconds'),
        'mount_failure': (42, 'exists but mounting it failed'),
        'dev_failure': (42, 'cannot mount devtmpfs'),
        'missing_init': (42, 'rootfs /sbin/init is missing or not executable'),
        'break': (42, 'requested pre-switch-root break; root mounted at /newroot'),
    }
    for mode, (status, message) in cases.items():
        script = root / 'case.sh'
        script.write_text(f'mode={mode}\n' + prelude + body)
        result = run('ash', str(script))
        assert result.returncode == status, result
        assert message in result.stdout + result.stderr, result
        print(f'PASS: {mode}')
