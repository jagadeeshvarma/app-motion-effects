#!/usr/bin/env python3
"""No-model probe for exact loopback-only native evaluation permissions.

The outer launcher must be allowed to start the sandbox. The child always runs
inside the named profile with managed requirements included. No full-access or
legacy sandbox fallback is attempted. A missing/unenforceable proxy is BLOCKED.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import shutil
import tempfile
import sys


CHILD = r'''
from pathlib import Path
import hashlib, json, os, socket, subprocess, tempfile, urllib.request, urllib.error
out = Path(os.environ['MOTION_NATIVE_PROBE_OUTPUT'])
checks = {'loopback_bind':False,'flutter_test':False,'disallowed_host_denied':False,
          'tmpdir_covers_tooling':False,'sdk_cache_write':False,'pub_cache_write':False,
          'config_write':False,'analyzer_cache_write':False,'zsh_adapter_owned':False,'flutter_path_matches_clone':False,'flutter_version':False,
          'offline_pub_get':False,'analyze':False,'fixture_lock_unchanged':False}
detail = {}
temp_root=Path(os.environ['TMPDIR']).resolve()
tooling=[Path(os.environ[name]).resolve() for name in ['FLUTTER_ROOT','PUB_CACHE','XDG_CONFIG_HOME']]
checks['tmpdir_covers_tooling']=all(path.is_relative_to(temp_root) for path in tooling)
zsh=Path(os.environ.get('ZDOTDIR','/')).resolve()
checks['zsh_adapter_owned']=zsh.is_relative_to(temp_root) and (zsh/'.zprofile').is_file() and (zsh/'.zlogin').is_file()
for key,folder in [('sdk_cache_write',tooling[0]/'bin/cache'),('pub_cache_write',tooling[1]),('config_write',tooling[2]),('analyzer_cache_write',Path(os.environ['ANALYZER_STATE_LOCATION_OVERRIDE']))]:
    try:
        with tempfile.NamedTemporaryFile(dir=folder,prefix='motion-synthetic-write-',delete=True) as probe:
            probe.write(b'SYNTHETIC_OWNED_CACHE_PROBE');probe.flush()
        checks[key]=True
    except Exception as error:
        detail[key+'_error']=repr(error)
commands=[('path','command -v flutter'),('version','flutter --version'),('pub','flutter pub get --offline'),('analyze','flutter analyze'),('test','flutter test --no-pub test/tooling_smoke_test.dart')]
lock=Path('pubspec.lock').read_bytes()
for name,command in commands:
    try:
        result=subprocess.run(['/bin/zsh','-lc',command],capture_output=True,text=True,timeout=180)
        (out.parent/('readiness-'+name+'.log')).write_text(result.stdout+result.stderr)
        detail[name+'_exit_code']=result.returncode
        if name=='path':
            selected=result.stdout.strip().splitlines()
            checks['flutter_path_matches_clone']=bool(selected) and Path(selected[-1]).resolve()==(tooling[0]/'bin/flutter').resolve()
        else:
            checks[{'version':'flutter_version','pub':'offline_pub_get','analyze':'analyze','test':'flutter_test'}[name]]=result.returncode==0
    except Exception as error:
        detail[name+'_error']=repr(error)
checks['fixture_lock_unchanged']=Path('pubspec.lock').read_bytes()==lock
try:
    server=socket.socket();server.bind(('127.0.0.1',0));server.listen(1)
    client=socket.create_connection(server.getsockname(),timeout=2)
    accepted,_=server.accept();accepted.sendall(b'SYNTHETIC_LOOPBACK')
    checks['loopback_bind']=client.recv(64)==b'SYNTHETIC_LOOPBACK'
    accepted.close();client.close();server.close()
except Exception as error:
    detail['loopback_error']=repr(error)
proxy_active=any(os.environ.get(name) for name in ['HTTPS_PROXY','https_proxy','HTTP_PROXY','http_proxy','ALL_PROXY','all_proxy'])
detail['proxy_environment_present']=proxy_active
try:
    response=urllib.request.urlopen('https://example.invalid/native-evaluation-readiness',timeout=5)
    detail['disallowed_host_unexpected_status']=response.status
except urllib.error.HTTPError as error:
    detail['disallowed_host_status']=error.code
    detail['disallowed_host_response']=error.read(2048).decode(errors='replace')
    checks['disallowed_host_denied']=proxy_active and error.code==403
except Exception as error:
    detail['disallowed_host_error']=repr(error)
    checks['disallowed_host_denied']=proxy_active and 'Tunnel connection failed: 403 Forbidden' in str(error)
report={'status':'pass' if all(checks.values()) else 'blocked','checks':checks,'detail':detail}
out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
raise SystemExit(0 if report['status']=='pass' else 2)
'''


def toml(value):
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(key) + '=' + toml(item) for key, item in value.items()) + '}'
    return json.dumps(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile-json', type=Path, required=True)
    parser.add_argument('--run-parent', type=Path, required=True)
    parser.add_argument('--seed', type=Path, required=True)
    parser.add_argument('--codex', help='Existing Codex CLI; otherwise discover from PATH')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--allow-local-binding', action='store_true', help='Explicit authorisation for synthetic native loopback listeners; literal allowlist remains mandatory')
    args = parser.parse_args()
    values = json.loads(args.profile_json.read_text())
    if values.get('default_permissions') != 'motion-native' or values.get('features.network_proxy') is not True:
        raise SystemExit('Refusing a profile without named native permissions and active proxy feature.')
    if values.get('permissions.motion-native.extends') != ':workspace':
        raise SystemExit('Native profile must extend workspace protection.')
    domains = values.get('permissions.motion-native.network.domains')
    if domains != {'localhost':'allow','127.0.0.1':'allow','::1':'allow'}:
        raise SystemExit('Refusing anything other than the exact loopback allowlist.')
    if values.get('permissions.motion-native.network.allow_local_binding', False) and not args.allow_local_binding:
        raise SystemExit('Additional local binding requires explicit authorisation flag.')
    allowed_keys={'default_permissions','features.network_proxy','permissions.motion-native.extends','permissions.motion-native.network.enabled','permissions.motion-native.network.mode','permissions.motion-native.network.allow_local_binding','permissions.motion-native.network.domains'}
    if (set(values)-allowed_keys or values.get('permissions.motion-native.network.enabled') is not True
            or values.get('permissions.motion-native.network.mode') != 'limited'):
        raise SystemExit('Refusing additional overrides or disabled network profile.')
    if any('dangerously' in key or key in ('sandbox_mode','sandbox_workspace_write.network_access') for key in values):
        raise SystemExit('Refusing sandbox bypass or legacy sandbox overrides.')
    profile_hash = hashlib.sha256(json.dumps(values, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    seed_hash = hashlib.sha256((args.seed / 'seed-manifest.json').read_bytes()).hexdigest()
    parent = args.run_parent.resolve()
    native_env = json.loads((parent/'runner-environment.json').read_text())
    if Path(native_env['TMPDIR']).resolve() != parent:
        raise SystemExit('TMPDIR must cover the whole uniquely owned run parent.')
    if not all(Path(native_env[name]).resolve().is_relative_to(parent) for name in ('FLUTTER_ROOT','PUB_CACHE','XDG_CONFIG_HOME','ANALYZER_STATE_LOCATION_OVERRIDE')):
        raise SystemExit('Tooling paths must remain beneath the uniquely owned TMPDIR.')
    if 'ZDOTDIR' not in native_env or not Path(native_env['ZDOTDIR']).resolve().is_relative_to(parent):
        raise SystemExit('The tested macOS/zsh adapter requires an owned ZDOTDIR beneath TMPDIR.')
    env = dict(os.environ, **native_env)
    codex = args.codex or shutil.which('codex')
    if codex is None:
        raise SystemExit('Codex CLI is not on PATH; supply --codex for an existing CLI.')
    child = parent/'native-readiness-child.py'
    child.write_text(CHILD)
    child_output = parent/'native-readiness-child.json'
    child_output.unlink(missing_ok=True)
    env['MOTION_NATIVE_PROBE_OUTPUT']=str(child_output)
    command=[codex]
    for key,value in values.items():
        command+=['-c',key+'='+toml(value)]
    command+=['sandbox','-P','motion-native','--include-managed-config','-C',str(parent/'app'),'--',sys.executable,str(child)]
    result=subprocess.run(command,env=env,capture_output=True,text=True,timeout=600)
    (parent/'native-readiness-launch.log').write_text(result.stdout+result.stderr)
    report={'status':'blocked','profile_sha256':profile_hash,'seed_manifest_sha256':seed_hash,
            'checks':{'flutter_test':False,'loopback_bind':False,'disallowed_host_denied':False},
            'sandbox_launch_exit_code':result.returncode,'model_calls':0,
            'managed_requirements_included':True,'legacy_sandbox_override':False,
            'allow_local_binding':values.get('permissions.motion-native.network.allow_local_binding',False),
            'domain_allowlist':domains,
            'environment_placement':'default-system-temp' if parent.parent==Path(tempfile.gettempdir()).resolve() else 'custom-owned-temp',
            'default_system_temp_parent_verified':parent.parent==Path(tempfile.gettempdir()).resolve(),
            'environment_contract':'whole-owned-run-parent-tmpdir',
            'shell':'/bin/zsh -lc',
            'tested_host_adapter':'macOS-zsh-with-owned-ZDOTDIR',
            'environment_key_count':len(native_env),
            'environment_helper_sha256':hashlib.sha256((Path(__file__).parent/'native-environment.py').read_bytes()).hexdigest()}
    if child_output.exists():
        report.update(json.loads(child_output.read_text()))
    else:
        report['blocker']='Native policy sandbox/proxy failed before child startup. See private launch log.'
        report['launch_error_excerpt']=(result.stdout+result.stderr)[-3000:]
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    raise SystemExit(0 if report['status']=='pass' else 2)


if __name__=='__main__':
    main()
