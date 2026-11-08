#!/usr/bin/env python3
"""Prepare a public-only C/D Flutter seed, then APFS-clone isolated run tooling.

The tested native adapter is macOS/zsh. It adds owned ZDOTDIR startup files
so login path_helper cannot replace the cloned SDK prefix. Other host paths
are not certified by this adapter. JSON environment output is private runner input. Never
publish it. Neither HOME nor CODEX_HOME is changed. All writes stay below the
requested seed/run parent; the installed SDK is a read-only clone source.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import shlex
import subprocess
import sys
import time

EVALS = Path(__file__).resolve().parents[1]


def environment(parent):
    sdk = parent / "flutter-sdk"
    analyzer_state = parent / "config/analyzer-state"
    analyzer_state.mkdir(parents=True, exist_ok=True)
    values = {
        "PATH": str(sdk / "bin") + os.pathsep + str(sdk / "bin/cache/dart-sdk/bin") + os.pathsep + os.environ["PATH"],
        "TMPDIR": str(parent) + os.sep,
        "PUB_CACHE": str(parent / "pub-cache"),
        "FLUTTER_ROOT": str(sdk),
        "XDG_CONFIG_HOME": str(parent / "config"),
        "ANALYZER_STATE_LOCATION_OVERRIDE": str(analyzer_state),
        "FLUTTER_SUPPRESS_ANALYTICS": "true",
        "DART_SUPPRESS_ANALYTICS": "true",
    }
    if sys.platform == "darwin":
        zsh = parent / "config/zsh"
        zsh.mkdir(parents=True, exist_ok=True)
        prefix = str(sdk / "bin") + os.pathsep + str(sdk / "bin/cache/dart-sdk/bin")
        startup = "# Owned native-evaluation adapter; no personal dotfiles.\nexport PATH=" + shlex.quote(prefix) + ':"$PATH"\n'
        for name in (".zprofile", ".zlogin"):
            (zsh / name).write_text(startup)
        values["ZDOTDIR"] = str(zsh)
    return values


def clone(source, target):
    # macOS requests copy-on-write clones; other hosts use an ordinary copy.
    # Preparation remains outside every model task's fixed time budget.
    if sys.platform == "darwin":
        copier = shutil.which("cp")
        if not copier:
            raise SystemExit("macOS cp is unavailable; SDK clone preparation is blocked.")
        subprocess.run([copier, "-cR", str(source), str(target)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    else:
        shutil.copytree(source, target, symlinks=True)


def make_parent(path):
    path = path.resolve()
    if path.exists():
        raise SystemExit("Destination already exists; supply a unique new path.")
    path.mkdir(parents=True)
    for name in ("tmp", "config"):
        (path / name).mkdir()
    return path


def seed(destination, installed_sdk):
    parent = make_parent(destination)
    clone(installed_sdk.resolve(), parent / "flutter-sdk")
    (parent / "pub-cache").mkdir()
    values = environment(parent)
    env = dict(os.environ, **values, PUB_HOSTED_URL="https://pub.dev")
    report = {"kind": "native_public_seed", "created": time.time(),
              "installed_sdk_read_only_source": True,
              "personal_pub_cache_copied": False, "network": "Public pub.dev resolution only",
              "commands": [], "fixture_lock_hashes": {}}
    for scenario in ("C", "D"):
        work = parent / f"warmup-{scenario}"
        shutil.copytree(EVALS / f"fixtures/{scenario}", work)
        lock = (work / "pubspec.lock").read_bytes()
        if b'url: "https://pub.dev"' not in lock or b"source: git" in lock or b"source: path" in lock:
            raise SystemExit("Frozen fixture dependencies require review before public cache warming.")
        report["fixture_lock_hashes"][scenario] = hashlib.sha256(lock).hexdigest()
        commands = [[str(parent / "flutter-sdk/bin/flutter"), "pub", "get", "--enforce-lockfile"]]
        tests = work / "test"
        tests.mkdir()
        (tests / "tooling_smoke_test.dart").write_text("import 'package:flutter_test/flutter_test.dart';\nvoid main() { test('tooling warmup only, not product acceptance', () { expect(2 + 2, 4); }); }\n")
        commands += [[str(parent / "flutter-sdk/bin/flutter"), "test", "--no-pub", "test/tooling_smoke_test.dart"]]
        for index, command in enumerate(commands):
            log = parent / f"warmup-{scenario}-{index}.log"
            with log.open("w") as output:
                result = subprocess.run(command, cwd=work, env=env, stdout=output, stderr=subprocess.STDOUT, timeout=300)
            report["commands"].append({"scenario": scenario, "operation": command[1:], "exit_code": result.returncode, "log": log.name})
            (parent / "seed-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
            if result.returncode:
                raise SystemExit(f"Tooling seed warmup failed; see {log}")
        if (work / "pubspec.lock").read_bytes() != lock:
            raise SystemExit("Lockfile changed during seed warmup; seed rejected.")
    report["public_packages"] = sorted(path.name for path in (parent / "pub-cache/hosted/pub.dev").iterdir() if path.is_dir() and path.name != ".cache")
    report["status"] = "ready"
    (parent / "seed-manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"seed": str(parent), "status": "ready", "public_package_count": len(report["public_packages"])}))


def run_clone(seed_parent, destination):
    manifest = json.loads((seed_parent / "seed-manifest.json").read_text())
    if manifest.get("status") != "ready" or manifest.get("personal_pub_cache_copied") is not False:
        raise SystemExit("Seed is not a completed public-only warmup.")
    parent = destination.resolve()
    if any((parent / name).exists() for name in ("flutter-sdk", "pub-cache", "tmp", "config", "runner-environment.json")):
        raise SystemExit("Run environment paths already exist; refusing to overwrite.")
    parent.mkdir(parents=True, exist_ok=True)
    for name in ("tmp", "config"):
        (parent / name).mkdir()
    clone(seed_parent / "flutter-sdk", parent / "flutter-sdk")
    clone(seed_parent / "pub-cache", parent / "pub-cache")
    values = environment(parent)
    # The manifest is intentionally local runner state, not a public artifact.
    (parent / "runner-environment.json").write_text(json.dumps(values, indent=2) + "\n")
    print(json.dumps({"env": values, "seed_manifest_sha256": hashlib.sha256((seed_parent / "seed-manifest.json").read_bytes()).hexdigest()}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    make = modes.add_parser("seed")
    make.add_argument("destination", type=Path)
    make.add_argument("--installed-sdk", type=Path, help="Existing SDK root; otherwise discover from PATH flutter executable")
    run = modes.add_parser("run")
    run.add_argument("--seed", type=Path, required=True)
    run.add_argument("run_parent", type=Path)
    args = parser.parse_args()
    if args.mode == "seed":
        installed = args.installed_sdk
        if installed is None:
            executable = shutil.which("flutter")
            if executable is None:
                raise SystemExit("Flutter is not on PATH; supply --installed-sdk for an existing SDK.")
            installed = Path(executable).resolve().parents[1]
        if not any((installed / "bin" / name).is_file() for name in ("flutter", "flutter.bat")):
            raise SystemExit("The selected existing SDK root has no Flutter launcher in bin/.")
        seed(args.destination, installed)
    else:
        run_clone(args.seed.resolve(), args.run_parent)


if __name__ == "__main__":
    main()
