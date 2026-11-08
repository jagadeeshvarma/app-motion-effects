#!/usr/bin/env python3
"""Least-privilege native grading adapter; no model calls or unsandboxed fallback.

Proofs/environment paths are private host evidence. The reviewed profile denies
root reads, admits minimal runtime + exact owned tooling paths, denies generic
/tmp and retains the literal loopback-only proxy policy.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PROFILE = "motion-native-grading"
ADMISSION_HOLD = "Strict Flutter bootstrap is unverified and protected fresh-toolchain-per-grade transport is not established."
ENV_KEYS = frozenset({"PATH", "TMPDIR", "PUB_CACHE", "FLUTTER_ROOT", "XDG_CONFIG_HOME", "ZDOTDIR", "ANALYZER_STATE_LOCATION_OVERRIDE", "FLUTTER_SUPPRESS_ANALYTICS", "DART_SUPPRESS_ANALYTICS"})
CORE_KEYS = frozenset({"HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TERM", "SHELL", "SYSTEMROOT"})
REQUIRED_CHECKS = frozenset({"outside_read_denied", "outside_write_denied", "owned_write", "loopback_bind", "disallowed_host_denied", "flutter_test", "offline_pub_get", "fixture_lock_unchanged", "submitted_source_read_denied", "submitted_source_write_denied"})
BASE = Path(__file__).resolve().parent


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def profile_values(owned_parent, submitted_workspace=None):
    root = str(Path(owned_parent).resolve())
    submitted = str(Path(submitted_workspace or (Path(root) / "app")).resolve())
    # No parent profile: do not inherit workspace-wide root/temp grants.
    return {
        "default_permissions": PROFILE,
        "features.network_proxy": True,
        f"permissions.{PROFILE}.filesystem": {
            ":root": "deny", ":minimal": "read", ":slash_tmp": "deny",
            root: "write", submitted: "deny", str(Path(sys.base_prefix).resolve()): "read", str(Path(sys.executable).resolve()): "read",
        },
        f"permissions.{PROFILE}.network.enabled": True,
        f"permissions.{PROFILE}.network.mode": "limited",
        f"permissions.{PROFILE}.network.allow_local_binding": True,
        f"permissions.{PROFILE}.network.domains": {"localhost": "allow", "127.0.0.1": "allow", "::1": "allow"},
    }


def template_hash():
    values = profile_values(Path("/") / "OWNED_NATIVE_GRADING_PARENT")
    fs = values[f"permissions.{PROFILE}.filesystem"]
    fs["{owned_parent}"] = fs.pop(str(Path("/") / "OWNED_NATIVE_GRADING_PARENT"))
    fs["{submitted_workspace}"] = fs.pop(str(Path("/") / "OWNED_NATIVE_GRADING_PARENT" / "app"))
    return digest(values)


def check_readiness(proof_path):
    if not proof_path:
        raise ValueError("Native grading requires a passing least-privilege grading proof")
    if ADMISSION_HOLD:
        raise ValueError("Native grading remains BLOCKED: " + ADMISSION_HOLD)
    proof = json.loads(Path(proof_path).read_text())
    expected = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if (proof.get("status") != "pass" or proof.get("adapter_sha256") != expected
            or proof.get("profile_template_sha256") != template_hash()
            or proof.get("platform") != sys.platform or sys.platform != "darwin"
            or proof.get("root_read_policy") != "deny"
            or proof.get("generic_tmp_policy") != "deny"
            or any(proof.get("checks", {}).get(key) is not True for key in REQUIRED_CHECKS)):
        raise ValueError("Native grading proof does not establish this adapter/profile/platform and required isolation checks")
    return {"proof_sha256": hashlib.sha256(Path(proof_path).read_bytes()).hexdigest(), "profile_template_sha256": template_hash(), "adapter_sha256": expected, "status": "pass"}


def validate_environment(env, cwd):
    if not ENV_KEYS.issubset(env) or any(not isinstance(env[key], str) or not env[key] for key in ENV_KEYS):
        raise ValueError("Native grading requires the nine reviewed environment values")
    parent = Path(env["TMPDIR"]).resolve()
    if parent == Path("/") or parent == Path.home() or parent.name in {"tmp", "T"} or not parent.name.startswith("motion-"):
        raise ValueError("Native grading TMPDIR must be a unique owned motion run parent")
    info = parent.lstat()
    if parent.is_symlink() or not parent.is_dir() or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("Native grading parent must be an ordinary private directory owned by the current user")
    expected = {"FLUTTER_ROOT": parent/"flutter-sdk", "PUB_CACHE": parent/"pub-cache", "XDG_CONFIG_HOME": parent/"config", "ZDOTDIR": parent/"config/zsh", "ANALYZER_STATE_LOCATION_OVERRIDE": parent/"config/analyzer-state"}
    for key, path in expected.items():
        if Path(env[key]).resolve() != path or not path.is_dir() or path.is_symlink():
            raise ValueError(f"Unexpected owned native grading environment path: {key}")
    prefix = [str(parent/"flutter-sdk/bin"), str(parent/"flutter-sdk/bin/cache/dart-sdk/bin")]
    if env["PATH"].split(os.pathsep)[:2] != prefix:
        raise ValueError("Native grading PATH must select the owned SDK first")
    if env["FLUTTER_SUPPRESS_ANALYTICS"] != "true" or env["DART_SUPPRESS_ANALYTICS"] != "true":
        raise ValueError("Native grading analytics must remain disabled")
    if not Path(cwd).resolve().is_relative_to(parent):
        raise ValueError("Generated native grading copy must remain inside the exact owned parent")
    return parent


def toml(value):
    if isinstance(value, bool): return str(value).lower()
    if isinstance(value, dict): return "{" + ",".join(json.dumps(key)+"="+toml(item) for key,item in sorted(value.items())) + "}"
    return json.dumps(value)


def sandbox_command(command, cwd, env, proof_path=None, *, proving=False, codex=None, submitted_workspace=None):
    if not proving: check_readiness(proof_path)
    parent = validate_environment(env, cwd)
    from containment import preflight_workspace
    preflight_workspace(cwd)
    executable = codex or shutil.which("codex")
    if not executable: raise ValueError("Codex sandbox launcher is unavailable")
    argv = [str(executable)]
    submitted = Path(submitted_workspace or (parent / "app")).resolve()
    if Path(cwd).resolve().is_relative_to(submitted):
        raise ValueError("Native execution must use a generated copy, not the retained submitted workspace")
    values = profile_values(parent, submitted)
    for key,value in values.items(): argv += ["-c", key+"="+toml(value)]
    argv += ["sandbox", "-P", PROFILE, "--include-managed-config", "-C", str(Path(cwd).resolve()), "--", *map(str,command)]
    clean = {key:value for key,value in env.items() if key in ENV_KEYS | CORE_KEYS}
    # Never read personal/system Git configuration while bootstrapping Flutter.
    clean.update(GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", ANDROID_HOME=str(parent/"config/android-sdk-unavailable"))
    clean["PATH"] = os.pathsep.join([str(parent/"flutter-sdk/bin"), str(parent/"flutter-sdk/bin/cache/dart-sdk/bin"), "/usr/bin", "/bin", "/usr/sbin", "/sbin"])
    return argv, clean, {"profile_sha256": digest(values), "profile_template_sha256": template_hash(), "managed_requirements_included": True, "legacy_sandbox_override": False, "root_read_policy": "deny", "generic_tmp_policy": "deny"}


PROBE = r'''
from pathlib import Path
import json,os,socket,subprocess,tempfile,urllib.request,urllib.error
parent=Path(os.environ['TMPDIR']).resolve()
canary=Path(os.environ['MOTION_GRADING_SYNTHETIC_CANARY'])
checks=dict(outside_read_denied=False,outside_write_denied=False,owned_write=False,loopback_bind=False,disallowed_host_denied=False,flutter_test=False,offline_pub_get=False,fixture_lock_unchanged=False,submitted_source_read_denied=False,submitted_source_write_denied=False)
detail={}
submitted=Path(os.environ['MOTION_GRADING_SUBMITTED_CANARY'])
try:
    submitted.read_bytes()
except PermissionError: checks['submitted_source_read_denied']=True
except OSError as error: detail['submitted_read_error']=type(error).__name__
try:
    submitted.write_text('SYNTHETIC_ATTEMPTED_SOURCE_CHANGE')
except PermissionError: checks['submitted_source_write_denied']=True
except OSError as error: detail['submitted_write_error']=type(error).__name__
try:
    canary.read_bytes()
except PermissionError: checks['outside_read_denied']=True
except OSError as error: detail['outside_read_error']=type(error).__name__
try:
    canary.with_name('outside-write-probe').write_text('SYNTHETIC_ONLY')
except PermissionError: checks['outside_write_denied']=True
except OSError as error: detail['outside_write_error']=type(error).__name__
with tempfile.NamedTemporaryFile(dir=parent,delete=True) as stream:
    stream.write(b'SYNTHETIC_OWNED_WRITE');stream.flush();checks['owned_write']=True
try:
    with socket.socket() as server:
        server.bind(('127.0.0.1',0));server.listen(1)
        with socket.create_connection(server.getsockname(),timeout=3) as client:
            peer,_=server.accept()
            with peer: peer.sendall(b'SYNTHETIC_LOOPBACK')
            checks['loopback_bind']=client.recv(32)==b'SYNTHETIC_LOOPBACK'
except OSError as error: detail['loopback_error']=str(error)
proxy=any(os.environ.get(key) for key in ['HTTPS_PROXY','https_proxy','HTTP_PROXY','http_proxy','ALL_PROXY','all_proxy'])
detail['proxy_environment_present']=proxy
try:
    denied=subprocess.run(['/usr/bin/curl','--disable','--silent','--show-error','--head','--max-time','5','https://example.invalid/native-grading-isolation'],capture_output=True,text=True,timeout=10)
    detail['disallowed_host_exit']=denied.returncode
    detail['disallowed_host_error']=denied.stderr[-500:]
    checks['disallowed_host_denied']=proxy and '403' in denied.stderr and ('CONNECT' in denied.stderr or 'tunnel' in denied.stderr.lower())
except Exception as error: detail['disallowed_host_error']=str(error)
lock=Path('pubspec.lock').read_bytes()
for name,command in [('offline_pub_get',['flutter','pub','get','--offline']),('flutter_test',['flutter','test','--no-pub','test/native_grading_probe_test.dart'])]:
    try:
        result=subprocess.run(command,capture_output=True,text=True,timeout=180)
        (parent/(name+'.log')).write_text(result.stdout+result.stderr)
        checks[name]=result.returncode==0;detail[name+'_exit']=result.returncode
    except Exception as error: detail[name+'_error']=str(error)
checks['fixture_lock_unchanged']=Path('pubspec.lock').read_bytes()==lock
report={'status':'pass' if all(checks.values()) else 'blocked','checks':checks,'detail':detail}
(parent/'native-grading-child.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
raise SystemExit(0 if report['status']=='pass' else 2)
'''


def prove(seed, output, codex=None):
    if output.exists(): raise ValueError("Refusing to overwrite an existing native grading proof")
    parent = Path(tempfile.mkdtemp(prefix="motion-native-grade-proof-"))
    helper = BASE / "tools/native-environment.py"
    setup = subprocess.run([sys.executable,str(helper),"run","--seed",str(seed),str(parent)],capture_output=True,text=True,timeout=180)
    if setup.returncode: raise RuntimeError("Public-only native clone preparation failed")
    values = json.loads(setup.stdout)["env"]
    source = parent / "app"
    shutil.copytree(BASE/"fixtures/C", source)
    source_canary = source/"synthetic-source-canary.txt"
    source_canary.write_text("SYNTHETIC_RETAINED_SOURCE")
    app = parent / "generated-grading-copy"
    shutil.copytree(BASE/"fixtures/C", app)
    (app/"test").mkdir()
    (app/"test/native_grading_probe_test.dart").write_text("import 'package:flutter_test/flutter_test.dart';\nvoid main(){test('least privilege tooling proof only',(){expect(2+2,4);});}\n")
    child = parent / "native-grading-child.py";child.write_text(PROBE)
    outside = Path(tempfile.mkdtemp(prefix="motion-native-grade-outside-"))
    canary = outside/"synthetic-canary.txt";canary.write_text("SYNTHETIC_OUTSIDE_OWNED_PARENT")
    env = {key:value for key,value in os.environ.items() if key in CORE_KEYS}
    env.update(values)
    argv,clean,profile = sandbox_command([str(Path(sys.executable).resolve()),str(child)],app,env,proving=True,codex=codex,submitted_workspace=source)
    clean["MOTION_GRADING_SYNTHETIC_CANARY"] = str(canary)
    clean["MOTION_GRADING_SUBMITTED_CANARY"] = str(source_canary)
    from run import run_process
    process = run_process(argv,cwd=app,env=clean,timeout=420)
    (parent/"sandbox-launch.log").write_text(process['stdout']+process['stderr'])
    report = {"status":"blocked","platform":sys.platform,"adapter_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"profile_template_sha256":template_hash(),"profile_instance":profile,"root_read_policy":"deny","generic_tmp_policy":"deny","checks":{},"model_calls":0,"owned_parent":str(parent),"seed_manifest_sha256":hashlib.sha256((seed/"seed-manifest.json").read_bytes()).hexdigest(),"launch_exit":process['returncode'],"launch_timed_out":process['timed_out'],"cleanup":process['cleanup']}
    child_output = parent/"native-grading-child.json"
    if child_output.exists(): report.update(json.loads(child_output.read_text()))
    else: report['blocker']='Least-privilege sandbox failed before probe startup; see private sandbox-launch.log'
    if process['returncode'] != 0 or process['timed_out'] or process['launch_error']: report['status']='blocked'
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ['status','checks','model_calls','launch_exit']}))
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--codex')
    args=parser.parse_args()
    report=prove(args.seed.resolve(),args.output,args.codex)
    raise SystemExit(0 if report['status']=='pass' else 2)


if __name__=='__main__': main()
