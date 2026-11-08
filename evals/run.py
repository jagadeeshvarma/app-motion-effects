#!/usr/bin/env python3
"""Run fresh, equal-budget Codex tasks and keep grader/condition data outside workspaces.

Result artifacts are private audit data. Registry probes establish catalogue availability,
not that a model read the skill or that the separate app-server ignores user config.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
from datetime import datetime, timezone
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import random
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import uuid

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
MODEL = "gpt-6.1-sol"
REASONING = "high"
NATIVE_IDS = frozenset("CD")
NATIVE_LOCK = threading.Lock()
DISABLED = [
    "app-motion-effects", "computer-history:computer-history", "documents:documents",
    "pdf:pdf", "presentations:Presentations", "spreadsheets:Spreadsheets",
    "spreadsheets:excel-live-control", "template-creator:template-creator", "visualize:visualize",
]
CORE_ENV = {"PATH", "HOME", "USER", "LOGNAME", "TMPDIR", "LANG", "LC_ALL", "TERM", "SHELL", "SYSTEMROOT"}
NATIVE_ENV = {"PATH", "TMPDIR", "PUB_CACHE", "FLUTTER_ROOT", "XDG_CONFIG_HOME", "FLUTTER_SUPPRESS_ANALYTICS", "DART_SUPPRESS_ANALYTICS", "ZDOTDIR", "ANALYZER_STATE_LOCATION_OVERRIDE"}


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def digest_tree(path, *, include_git=False):
    """Hash files without following links; workspace metrics omit .git by default."""
    result = {}
    for item in sorted(Path(path).rglob("*")):
        if not include_git and ".git" in item.relative_to(path).parts:
            continue
        name = item.relative_to(path).as_posix()
        if item.is_symlink():
            result[name] = "symlink:" + os.readlink(item)
        elif item.is_file():
            result[name] = hashlib.sha256(item.read_bytes()).hexdigest()
    return result


def native_profile_values():
    """Exact local-only profile; never combine this with legacy sandbox flags."""
    return {
        "default_permissions": "motion-native",
        "features.network_proxy": True,
        "permissions.motion-native.extends": ":workspace",
        "permissions.motion-native.network.enabled": True,
        "permissions.motion-native.network.mode": "limited",
        "permissions.motion-native.network.allow_local_binding": True,
        "permissions.motion-native.network.domains": {"localhost": "allow", "127.0.0.1": "allow", "::1": "allow"},
    }


def native_profile_sha256():
    return canonical_hash(native_profile_values())


def toml_value(value):
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, dict):
        return "{" + ",".join(json.dumps(key) + "=" + toml_value(val) for key, val in sorted(value.items())) + "}"
    if isinstance(value, list):
        return "[" + ",".join(toml_value(item) for item in value) + "]"
    return json.dumps(value)


def config(skill, shell_set=None, *, native_profile=False):
    entries = [{"name": name, "enabled": False} for name in DISABLED]
    if skill:
        entries.append({"path": str(Path(skill) / "SKILL.md"), "enabled": True})
    values = {
        "skills.bundled.enabled": False,
        "skills.config": entries,
        "features.plugins": False,
        "features.apps": False,
        "features.memories": False,
        "web_search": "disabled",
        "shell_environment_policy.inherit": "core",
    }
    if shell_set:
        if set(shell_set) - NATIVE_ENV:
            raise ValueError("Only the nine reviewed macOS/zsh native environment keys may be explicitly propagated")
        values["shell_environment_policy.set"] = shell_set
    if native_profile:
        values.update(native_profile_values())
    return [part for key, value in values.items() for part in ("-c", key + "=" + toml_value(value))]


def base_environment():
    env = {key: value for key, value in os.environ.items() if key in CORE_ENV}
    # Launcher variables: shell inheritance remains 'core' unless native keys are explicitly set.
    env["NODE_PATH"] = str(ROOT / "node_modules")
    env["PLAYWRIGHT_CHANNEL"] = "chrome"
    return env


def stop_group(proc, *, force=False):
    try:
        os.killpg(proc.pid, signal.SIGKILL if force else signal.SIGTERM)
        return "process-group"
    except ProcessLookupError:
        return "already-exited"
    except PermissionError:
        try:
            proc.kill() if force else proc.terminate()
            return "child-only-fallback"
        except ProcessLookupError:
            return "already-exited"
        except PermissionError:
            return "denied"


def run_process(argv, *, cwd=None, timeout=60, env=None, input_text=None):
    """Bound all subprocesses and reap their process groups, including on exceptions."""
    started = time.monotonic()
    proc = None
    stdout = stderr = ""
    timed_out = False
    launch_error = None
    cleanup = []
    try:
        proc = subprocess.Popen(
            argv, cwd=cwd, env=env, stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace", start_new_session=True,
        )
        try:
            stdout, stderr = proc.communicate(input_text, timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            cleanup.append(stop_group(proc))
            try:
                stdout, stderr = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                cleanup.append(stop_group(proc, force=True))
                try:
                    stdout, stderr = proc.communicate(timeout=5)
                except subprocess.TimeoutExpired as error:
                    # A child that created another session can retain a pipe. Do not wait forever.
                    stdout = error.stdout or ""
                    stderr = error.stderr or ""
                    stdout = stdout.decode(errors="replace") if isinstance(stdout, bytes) else stdout
                    stderr = stderr.decode(errors="replace") if isinstance(stderr, bytes) else stderr
    except OSError as error:
        launch_error = str(error)
    finally:
        if proc is not None:
            # A successful CLI may leave a local server alive after closing its stdout.
            cleanup.append(stop_group(proc, force=True))
            if proc.poll() is None:
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    cleanup.append("unreaped-child")
            for stream in (proc.stdin, proc.stdout, proc.stderr):
                if stream is not None:
                    stream.close()
    return {
        "stdout": stdout, "stderr": stderr, "returncode": proc.returncode if proc else None,
        "timed_out": timed_out, "launch_error": launch_error, "cleanup": cleanup,
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }


def command(argv, cwd=None, timeout=60, env=None):
    """Compatibility wrapper used by local tooling; failures are checked by callers."""
    result = run_process(argv, cwd=cwd, timeout=timeout, env=env)
    if result["launch_error"] or result["timed_out"]:
        raise RuntimeError(result["launch_error"] or "Command timed out")
    return subprocess.CompletedProcess(argv, result["returncode"], result["stdout"], result["stderr"])


def events_and_metrics(stdout):
    events = []
    malformed = 0
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
            if isinstance(event, dict) and isinstance(event.get("type"), str):
                events.append(event)
            else:
                malformed += 1
        except json.JSONDecodeError:
            malformed += 1
    usage = [event["usage"] for event in events if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict)]
    totals = {}
    for entry in usage:
        for key, value in entry.items():
            if isinstance(value, int) and not isinstance(value, bool):
                totals[key] = totals.get(key, 0) + value
    tools = {}
    file_changes = {}
    types = {"command_execution", "mcp_tool_call", "web_search"}
    for index, event in enumerate(events):
        item = event.get("item", {})
        if not isinstance(item, dict):
            if event.get("type") in {"item.started", "item.completed"}:
                malformed += 1
            continue
        item_type = item.get("type") if isinstance(item.get("type"), str) else None
        item_id = item.get("id") if isinstance(item.get("id"), str) and item.get("id") else None
        if event.get("type") in {"item.started", "item.completed"} and item_type == "file_change":
            key = item_id or f"file-change-event-without-item-id-{index}"
            record = file_changes.setdefault(key, {"started": False, "completed": False, "failed": False})
            record["started" if event["type"] == "item.started" else "completed"] = True
            record["failed"] = record["failed"] or (isinstance(item.get("status"), str) and item["status"] in {"failed", "error"})
        if event.get("type") in {"item.started", "item.completed"} and item_type in types:
            key = item_id or f"event-without-item-id-{index}"
            record = tools.setdefault(key, {"started": False, "completed": False})
            record["started" if event["type"] == "item.started" else "completed"] = True
    completed = any(event.get("type") == "turn.completed" for event in events)
    failed = any(event.get("type") in {"turn.failed", "error"} for event in events)
    return {
        "usage": usage, "usage_totals": totals or None,
        "usage_note": "Sum of reported completed-turn usage only; missing/interrupted-turn usage is unknown.",
        "tool_calls": sum(record["completed"] for record in tools.values()),
        "command_mcp_search_items_completed": sum(record["completed"] for record in tools.values()),
        "file_change_items_observed": len(file_changes),
        "file_change_items_completed": sum(record["completed"] for record in file_changes.values()),
        "file_change_items_failed": sum(record["failed"] for record in file_changes.values()),
        "file_change_items_incomplete": sum(record["started"] and not record["completed"] for record in file_changes.values()),
        "file_change_note": "Observed file_change event items, not net changed files; shell writes/hidden operations may emit no such item.",
        "tool_calls_started": sum(record["started"] for record in tools.values()),
        "tool_calls_incomplete": sum(record["started"] and not record["completed"] for record in tools.values()),
        "tool_calls_note": "Unique observed item IDs for command_execution, mcp_tool_call, web_search; not hidden internal calls.",
        "turn_completed": completed, "turn_error_observed": failed, "malformed_event_lines": malformed,
    }


def process_status(process, metrics):
    if process["launch_error"]:
        return "LAUNCH_FAILED"
    if "denied" in process.get("cleanup", []) or "unreaped-child" in process.get("cleanup", []):
        return "CLEANUP_FAILED"
    if process["timed_out"]:
        return "TIMED_OUT"
    if process["returncode"] != 0:
        return "EXIT_FAILED"
    if metrics["turn_error_observed"] or not metrics["turn_completed"]:
        return "INCOMPLETE"
    return "COMPLETED"  # This is process completion, never artifact acceptance.


def corpus_metadata(supplemental=False):
    base = BASE / "supplemental" if supplemental else BASE
    amendments = sorted(base.glob("frozen-amendment-*.json"), key=lambda item: int(item.stem.rsplit("-", 1)[-1]))
    path = amendments[-1] if amendments else base / "frozen.json"
    return {"manifest": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "corpus_sha256": json.loads(path.read_text())["sha256"]}


NATIVE_READINESS_CHECKS = {
    "loopback_bind", "flutter_test", "disallowed_host_denied", "tmpdir_covers_tooling",
    "sdk_cache_write", "pub_cache_write", "config_write", "zsh_adapter_owned",
    "flutter_path_matches_clone", "flutter_version", "offline_pub_get", "analyze", "fixture_lock_unchanged", "analyzer_cache_write",
}
NATIVE_PROOF_CONTRACT = {
    "default_system_temp_parent_verified": True,
    "environment_placement": "default-system-temp",
    "environment_contract": "whole-owned-run-parent-tmpdir",
    "shell": "/bin/zsh -lc",
    "tested_host_adapter": "macOS-zsh-with-owned-ZDOTDIR",
    "environment_key_count": 9,
}


def check_native_readiness(seed, proof_path):
    if proof_path is None:
        raise ValueError("--native-seed requires --native-readiness with current placement/login/profile proof")
    proof = json.loads(Path(proof_path).read_text())
    if not isinstance(proof, dict) or not isinstance(proof.get("checks"), dict):
        raise ValueError("Native readiness proof must be a structured object with explicit checks")
    seed_hash = hashlib.sha256((Path(seed) / "seed-manifest.json").read_bytes()).hexdigest()
    helper_hash = hashlib.sha256((BASE / "tools/native-environment.py").read_bytes()).hexdigest()
    if proof.get("environment_helper_sha256") != helper_hash:
        raise ValueError("Native readiness proof does not match the current environment helper; old placement/login proofs are invalid")
    if any(proof.get(key) != value for key, value in NATIVE_PROOF_CONTRACT.items()):
        raise ValueError("Native readiness proof lacks actual default-temp whole-parent ownership and macOS/zsh login evidence")
    if proof.get("status", "").lower() != "pass" or proof.get("profile_sha256") != native_profile_sha256() or proof.get("seed_manifest_sha256") != seed_hash or any(proof.get("checks", {}).get(key) is not True for key in NATIVE_READINESS_CHECKS):
        raise ValueError("Native readiness proof does not establish this seed, ownership/login contract and exact local-only profile")
    return {"proof_sha256": hashlib.sha256(Path(proof_path).read_bytes()).hexdigest(), "seed_manifest_sha256": seed_hash, "profile_sha256": native_profile_sha256(), "environment_helper_sha256": helper_hash, "tested_host_adapter": NATIVE_PROOF_CONTRACT["tested_host_adapter"]}


def validate_native_environment(parent, values):
    """Validate the actual clone, not only a standalone readiness environment."""
    parent = Path(parent).resolve()
    if set(values) != NATIVE_ENV or any(not isinstance(value, str) for value in values.values()):
        raise ValueError("Native helper returned an unexpected exact-nine-key environment contract")
    expected = {
        "TMPDIR": parent, "PUB_CACHE": parent / "pub-cache", "FLUTTER_ROOT": parent / "flutter-sdk",
        "XDG_CONFIG_HOME": parent / "config", "ZDOTDIR": parent / "config/zsh",
        "ANALYZER_STATE_LOCATION_OVERRIDE": parent / "config/analyzer-state",
    }
    if any(Path(values[key]).resolve() != value for key, value in expected.items()):
        raise ValueError("Native TMPDIR must cover the whole unique parent; tooling/config/ZDOTDIR must stay at its owned paths")
    prefix = [parent / "flutter-sdk/bin", parent / "flutter-sdk/bin/cache/dart-sdk/bin"]
    if [Path(entry).resolve() for entry in values["PATH"].split(os.pathsep)[:2]] != prefix:
        raise ValueError("Native launcher PATH does not select the cloned SDK first")
    for name in (".zprofile", ".zlogin"):
        file = expected["ZDOTDIR"] / name
        if file.is_symlink() or not file.is_file():
            raise ValueError("Owned macOS/zsh startup files are missing or symlinked")
    return values


def check_native_grading_readiness(proof_path):
    if proof_path is None:
        raise ValueError("Native generated-code grading requires a separate least-privilege readiness proof")
    try:
        from native_grading import check_readiness
    except ImportError as error:
        raise ValueError("Least-privilege native grading transport is not ready; no native model calls may start") from error
    return check_readiness(Path(proof_path))


def sanitized_argv(argv, replacements):
    items = []
    for arg in argv:
        for source, replacement in sorted(replacements.items(), key=lambda item: -len(item[0])):
            arg = arg.replace(source, replacement)
        items.append(arg)
    return items


def run_case(spec, condition, trial, out, skill_source, timeout, *, native_seed=None, native_readiness=None, activation="explicit", trigger_kind="positive", registry_timeout=20, experiment_sha256=None, trusted_input_grading=True, safe_grading=True, native_grading_readiness=None):
    # Native tasks are serial even if the batch allows two web workers.
    guard = NATIVE_LOCK if spec["id"] in NATIVE_IDS else contextlib.nullcontext()
    with guard:
        if not trusted_input_grading or not safe_grading:
            raise ValueError("New runs always require trusted-input and contained grading; no unsafe bypass is supported")
        return _run_case(spec, condition, trial, out, skill_source, timeout, native_seed=native_seed, native_readiness=native_readiness, activation=activation, trigger_kind=trigger_kind, registry_timeout=registry_timeout, experiment_sha256=experiment_sha256, trusted_input_grading=trusted_input_grading, safe_grading=safe_grading, native_grading_readiness=native_grading_readiness)


def _run_case(spec, condition, trial, out, skill_source, timeout, *, native_seed, native_readiness, activation, trigger_kind, registry_timeout, experiment_sha256, trusted_input_grading, safe_grading, native_grading_readiness):
    ident = uuid.uuid4().hex[:12]
    folder = Path(out) / ident
    folder.mkdir()
    parent = Path(tempfile.mkdtemp(prefix="motion-case-"))
    work = parent / "app"
    case_base = BASE / "supplemental" if spec["id"] in {"M", "N"} else BASE
    result = {
        "schema_version": 2, "id": ident, "scenario": spec["id"], "condition": condition, "trial": trial,
        "model": MODEL, "reasoning": REASONING, "timeout_seconds": timeout,
        "activation_mode": activation, "trigger_kind": trigger_kind, "experiment_sha256": experiment_sha256,
        "trusted_input_grading": trusted_input_grading, "safe_grading": safe_grading,
        "started_utc": datetime.now(timezone.utc).isoformat(), "workspace": str(work),
        "agent_status": "SETUP_FAILED", "agent_exit": None, "grader_exit": None,
        "manual_status": "NOT RUN", "monetary_cost": None,
        "monetary_cost_note": "Authenticated ChatGPT quota; per-run monetary telemetry unavailable",
        "corpus": corpus_metadata(spec["id"] in {"M", "N"}),
    }
    total_started = time.monotonic()
    env = base_environment()
    unsafe_output = False
    try:
        if spec["id"] in NATIVE_IDS:
            if not safe_grading:
                raise ValueError("Native generated-code grading requires opt-in contained/least-privilege transport")
            result["native_grading_readiness"] = check_native_grading_readiness(native_grading_readiness)
        prep = command([sys.executable, str(case_base / "tools/prepare.py"), spec["id"], str(work)], env=env)
        if prep.returncode:
            raise RuntimeError("Fixture preparation failed: " + prep.stderr[-1000:])
        meta = json.loads(prep.stdout)
        result["task_sha256"] = meta["task_sha256"]
        result["fixture_sha256"] = meta["fixture_sha256"]
        init = command(["git", "init", "-q"], work, env=env)
        if init.returncode:
            raise RuntimeError("git init failed: " + init.stderr[-1000:])
        skill = None
        source_hashes = digest_tree(skill_source) if skill_source else None
        if skill_source:
            skill = work / ".agents/skills/app-motion-effects"
            skill.parent.mkdir(parents=True)
            shutil.copytree(skill_source, skill)
        result["skill_sha256"] = source_hashes
        shell_set = None
        use_native_profile = spec["id"] in NATIVE_IDS and native_seed is not None
        if use_native_profile:
            result["native_environment"] = check_native_readiness(native_seed, native_readiness)
            native = command([sys.executable, str(BASE / "tools/native-environment.py"), "run", "--seed", str(native_seed), str(parent)], timeout=120, env=env)
            if native.returncode:
                raise RuntimeError("Native environment preparation failed: " + native.stderr[-1000:])
            data = json.loads(native.stdout)
            shell_set = data["env"]
            validate_native_environment(parent, shell_set)
            if data["seed_manifest_sha256"] != result["native_environment"]["seed_manifest_sha256"]:
                raise RuntimeError("Native seed changed during preparation")
            env.update(shell_set)
            result["native_environment"]["propagated_keys"] = sorted(shell_set)
        elif spec["id"] in NATIVE_IDS:
            result["native_environment"] = {"mode": "legacy-host-environment", "note": "No prepared SDK/cache or local-only network profile; do not mix with prepared native trials."}
        overrides = config(skill, shell_set, native_profile=use_native_profile)
        from discovery import probe_registry
        registry_started = time.monotonic()
        result["registry"] = probe_registry(work, skill, config_args=overrides, env=env, timeout=registry_timeout)
        result["registry_seconds"] = round(time.monotonic() - registry_started, 3)
        if result["registry"]["status"] != "PASS":
            result["agent_status"] = "REGISTRY_BLOCKED"
            raise RuntimeError("Skill registry did not match the intended condition; no model call made")
        task = Path(meta["task_file"]).read_text()
        if trigger_kind != "positive":
            task = spec["trigger_cases"][trigger_kind]
        result["selected_task_sha256"] = hashlib.sha256(task.encode()).hexdigest()
        invoked = skill is not None and activation == "explicit"
        if invoked:
            task = "$app-motion-effects\n\n" + task
        result["explicit_skill_invocation"] = invoked
        result["model_input_sha256"] = hashlib.sha256(task.encode()).hexdigest()
        result["before_sha256"] = digest_tree(work)
        if trusted_input_grading:
            before_manifest = folder / "before-manifest.json"
            before_manifest.write_text(json.dumps({"schema_version": 1, "before_sha256": result["before_sha256"]}, indent=2) + "\n")
            result["trusted_before_manifest_sha256"] = hashlib.sha256(before_manifest.read_bytes()).hexdigest()
        argv = ["codex", "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check"]
        if not use_native_profile:
            argv += ["-s", "workspace-write"]
        argv += ["-m", MODEL, "-c", f'model_reasoning_effort="{REASONING}"', "-c", 'approval_policy="never"', *overrides, "--json", "-o", str(folder / "response.txt"), "-"]
        version = command(["codex", "--version"], timeout=10, env=env)
        result["cli_version"] = version.stdout.strip() if not version.returncode else "unavailable"
        invocation = {"argv": sanitized_argv(argv, {str(work): "{workspace}", str(parent): "{run_parent}", str(folder): "{artifact_folder}", str(ROOT): "{repository}"}), "actual_argv_sha256": canonical_hash(argv), "stdin_sha256": result["model_input_sha256"], "shell_environment_set_keys": sorted(shell_set or {}), "sandbox": "local-only-native-profile" if use_native_profile else "workspace-write", "registry_scope": "Skill catalogue probe only; app-server lacks exec --ignore-user-config; full config equality is not established."}
        (folder / "invocation.json").write_text(json.dumps(invocation, indent=2) + "\n")
        process = run_process(argv, cwd=work, timeout=timeout, env=env, input_text=task)
        (folder / "transcript.jsonl").write_text(process["stdout"])
        (folder / "stderr.txt").write_text(process["stderr"])
        metrics = events_and_metrics(process["stdout"])
        result.update(metrics)
        result.update({"agent_status": process_status(process, metrics), "agent_exit": process["returncode"], "elapsed_seconds": process["elapsed_seconds"], "agent_launch_error": process["launch_error"], "agent_timed_out": process["timed_out"], "agent_cleanup": process.get("cleanup", [])})
        if safe_grading:
            from containment import preflight_workspace, UnsafeSubmittedTree
            try:
                result["submitted_tree_preflight"] = preflight_workspace(work)
            except (OSError, ValueError) as error:
                unsafe_output = True
                result["condition_integrity"] = "NOT CHECKED: unsafe submitted tree"
                violation = isinstance(error, UnsafeSubmittedTree)
                result["grader_exit"] = 1 if violation else 2
                result["grader"] = {"status": "fail" if violation else "blocked", "checks": [{"id": "submitted-tree-contained", "pass": False, "detail": str(error)}] if violation else [], "blockers": [] if violation else [f"GA02 submitted tree preflight unavailable: {error}"], "ui_checks": "NOT RUN: submitted-tree preflight rejected", "grading_containment": {"violation": violation or None}}
                raise RuntimeError("GA02 output containment rejected; no submitted content hashes were read") from error
        if skill and digest_tree(skill) != source_hashes:
            result["condition_integrity"] = "FAILED: installed skill files changed"
        else:
            result["condition_integrity"] = "PASS"
        if trigger_kind == "positive":
            grade_path = BASE / "graders/grade_with_trusted_inputs.py" if trusted_input_grading else case_base / "graders/grade.py"
            grade_args = [sys.executable, str(grade_path), "--scenario", spec["id"], "--workspace", str(work), "--transcript", str(folder / "transcript.jsonl")]
            if trusted_input_grading:
                grade_args += ["--before-manifest", str(before_manifest), "--expected-manifest-sha256", result["trusted_before_manifest_sha256"]]
            if safe_grading:
                grade_args += ["--safe-grading"]
            if spec["id"] in NATIVE_IDS:
                grade_args += ["--native-grading-readiness", str(native_grading_readiness)]
            grade = run_process(grade_args, timeout=180, env=env)
            (folder / "grade.json").write_text(grade["stdout"])
            (folder / "grade-stderr.txt").write_text(grade["stderr"])
            result["grader_exit"] = grade["returncode"]
            result["grader_seconds"] = grade["elapsed_seconds"]
            try:
                result["grader"] = json.loads(grade["stdout"])
            except json.JSONDecodeError:
                result["grader"] = {"status": "blocked", "reason": grade["launch_error"] or ("Grader timed out" if grade["timed_out"] else "Grader did not return JSON")}
            if grade["launch_error"] or grade["timed_out"]:
                result["grader"]["status"] = "blocked"
                result["grader"]["runner_timeout"] = grade["timed_out"]
        else:
            result["grader"] = {"status": "not-run", "reason": "Trigger-routing task; primary functional graders intentionally not applied."}
    except Exception as error:
        result["runner_error"] = f"{type(error).__name__}: {error}"
    finally:
        if safe_grading and not unsafe_output and work.exists():
            try:
                from containment import preflight_workspace, UnsafeSubmittedTree
                preflight_workspace(work)
            except (OSError, ValueError) as error:
                unsafe_output = True
                result["submitted_tree_final_blocker"] = str(error)
                violation = isinstance(error, UnsafeSubmittedTree)
                result.setdefault("grader", {"checks": []})["status"] = "fail" if violation else "blocked"
                if violation:
                    result["grader"].setdefault("checks", []).append({"id": "submitted-tree-contained-final", "pass": False, "detail": str(error)})
                else:
                    result["grader"].setdefault("blockers", []).append(f"GA02 final submitted-tree preflight unavailable: {error}")
        result["after_sha256"] = digest_tree(work) if not unsafe_output and work.exists() else None
        result["total_elapsed_seconds"] = round(time.monotonic() - total_started, 3)
        result["ended_utc"] = datetime.now(timezone.utc).isoformat()
        (folder / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({key: result.get(key) for key in ("id", "scenario", "condition", "trial", "activation_mode", "trigger_kind", "agent_status", "grader_exit", "elapsed_seconds", "command_mcp_search_items_completed", "file_change_items_completed")}), flush=True)
    return result


def load_specs():
    specs = {case["id"]: case for case in json.loads((BASE / "scenarios.json").read_text())["scenarios"]}
    supplemental = BASE / "supplemental/scenarios.json"
    if supplemental.exists():
        specs.update({case["id"]: case for case in json.loads(supplemental.read_text())["cases"]})
    return specs


def original_snapshot(out):
    target = out / "original/skills/app-motion-effects"
    # Reusing a different tag snapshot under the same output directory is rejected.
    archive = subprocess.check_output(["git", "archive", "v2.0.0", "skills/app-motion-effects"], cwd=ROOT, timeout=30)
    archive_hash = hashlib.sha256(archive).hexdigest()
    marker = out / "original/archive.sha256"
    if any(path.is_symlink() for path in (out / "original", out / "original/skills", target, marker)):
        raise ValueError("Cached original path contains a symlink; refusing to inspect outside the trusted archive tree")
    if target.exists():
        if marker.exists() and marker.read_text().strip() != archive_hash:
            raise ValueError("v2.0.0 archive changed since this output directory was created")
        # A matching marker authenticates the archive identity, not cached files.
        # Always compare every cached file against a fresh trusted tag extraction.
        with tempfile.TemporaryDirectory(prefix="motion-original-check-") as temp:
            with tarfile.open(fileobj=io.BytesIO(archive)) as data:
                data.extractall(temp, filter="data")
            if digest_tree(target, include_git=True) != digest_tree(Path(temp) / "skills/app-motion-effects", include_git=True):
                raise ValueError("Existing original snapshot differs from v2.0.0 tag")
        if not marker.exists():
            marker.write_text(archive_hash + "\n")
    else:
        (out / "original").mkdir(exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(archive)) as data:
            data.extractall(out / "original", filter="data")
        marker.write_text(archive_hash + "\n")
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="ABCDEF", help="Scenario IDs, e.g. ABCDEF or MN; no prompt contents are printed")
    parser.add_argument("--conditions", default="no-skill,original-v2.0.0,improved")
    parser.add_argument("--trial", type=int, default=1)
    parser.add_argument("--output", required=True)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--jobs", type=int, choices=[1, 2], default=2)
    parser.add_argument("--native-seed", type=Path, help="Prepared public-only SDK/cache seed; enables reviewed local-only native profile")
    parser.add_argument("--native-readiness", type=Path, help="Passing proof for the exact seed/profile; required with --native-seed")
    parser.add_argument("--native-grading-readiness", type=Path, help="Separate deny-root/owned-path grading proof; required before any native model task")
    parser.add_argument("--activation", choices=["explicit", "implicit"], default="explicit")
    parser.add_argument("--trigger-kind", choices=["positive", "negative", "ambiguous"], default="positive")
    parser.add_argument("--registry-timeout", type=int, default=20)
    parser.add_argument("--order-seed", type=int, help="Deterministic shuffled schedule; omitted retains original ordered scheduling")
    parser.add_argument("--trusted-input-grading", action="store_true", default=True, help="Compatibility option: trusted-input verification is always enabled")
    parser.add_argument("--safe-grading", action="store_true", default=True, help="Compatibility option: contained grading is always enabled")
    parser.add_argument("--dry-run", action="store_true", help="Write/print plan metadata only; no model calls or native clones")
    args = parser.parse_args()
    if args.safe_grading and not args.trusted_input_grading:
        parser.error("--safe-grading requires --trusted-input-grading; legacy defaults are unchanged")
    if args.timeout <= 0 or args.timeout > 240 or args.trial <= 0 or args.registry_timeout <= 0:
        parser.error("Timeout must be 1–240 seconds, registry timeout positive and trial positive")
    conditions = args.conditions.split(",")
    if not conditions or len(set(conditions)) != len(conditions) or any(condition not in {"no-skill", "original-v2.0.0", "improved"} for condition in conditions):
        parser.error("Conditions must be unique known condition names")
    if "improved" in conditions and (not args.candidate or not (args.candidate / "SKILL.md").is_file()):
        parser.error("Improved condition requires --candidate pointing to the skill directory")
    if args.native_seed:
        try:
            check_native_readiness(args.native_seed, args.native_readiness)
        except (ValueError, OSError, json.JSONDecodeError) as error:
            parser.error(str(error))
    elif args.native_readiness:
        parser.error("--native-readiness requires --native-seed")
    specs = load_specs()
    if not args.cases or len(set(args.cases)) != len(args.cases) or any(case not in specs for case in args.cases):
        parser.error("Supply unique known scenario IDs")
    if any(ident in NATIVE_IDS for ident in args.cases):
        if not args.safe_grading:
            parser.error("Native cases require --safe-grading and separate least-privilege grading readiness")
        try:
            check_native_grading_readiness(args.native_grading_readiness)
        except (OSError, ValueError) as error:
            parser.error(str(error))
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    with (out / ".runner.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error("Another runner owns this output directory; use a separate output or wait")
        original = original_snapshot(out) if "original-v2.0.0" in conditions else None
        cli = command(["codex", "--version"], timeout=10, env=base_environment())
        experiment = {
            "host_cli_version": cli.stdout.strip() if cli.returncode == 0 else "unavailable",
            "python_version": sys.version.split()[0],
            "development_lock_sha256": hashlib.sha256((ROOT / "package-lock.json").read_bytes()).hexdigest(),
            "native_helper_sha256": hashlib.sha256((BASE / "tools/native-environment.py").read_bytes()).hexdigest() if args.native_seed else None,
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "discovery_sha256": hashlib.sha256((BASE / "discovery.py").read_bytes()).hexdigest(),
            "conditions": {condition: digest_tree(original if condition == "original-v2.0.0" else args.candidate) if condition != "no-skill" else None for condition in conditions},
            "corpus": corpus_metadata(), "supplemental": corpus_metadata(True) if any(case in "MN" for case in args.cases) else None,
            "model": MODEL, "reasoning": REASONING, "timeout": args.timeout,
            "activation": args.activation, "trigger_kind": args.trigger_kind,
            "trusted_input_grading": args.trusted_input_grading,
            "safe_grading": args.safe_grading,
            "containment_infrastructure_sha256": {name: hashlib.sha256((BASE / name).read_bytes()).hexdigest() for name in ["containment.py", "graders/grade_with_containment.py", "graders/safe-web-preload.mjs", "graders/safe-static-server.mjs"]} if args.safe_grading else None,
            "companion_grader_sha256": hashlib.sha256((BASE / "graders/grade_with_trusted_inputs.py").read_bytes()).hexdigest() if args.trusted_input_grading else None,
            "native_grading_readiness": check_native_grading_readiness(args.native_grading_readiness) if any(ident in NATIVE_IDS for ident in args.cases) else None,
            "native_seed": check_native_readiness(args.native_seed, args.native_readiness) if args.native_seed else None,
            "order_seed": args.order_seed, "jobs": args.jobs,
        }
        fingerprint = canonical_hash(experiment)
        existing = set()
        mismatched = set()
        legacy = 0
        for path in out.glob("*/result.json"):
            item = json.loads(path.read_text())
            if item.get("experiment_sha256") == fingerprint:
                existing.add((item["scenario"], item["condition"], item["trial"]))
            else:
                mismatched.add((item["scenario"], item["condition"], item["trial"]))
                if item.get("experiment_sha256") is None:
                    legacy += 1
        tasks = []
        for ident in args.cases:
            for condition in conditions:
                source = None if condition == "no-skill" else original if condition == "original-v2.0.0" else args.candidate
                key = (ident, condition, args.trial)
                if key not in existing and key in mismatched:
                    parser.error("Existing same-trial results have different or legacy settings. Choose a new --trial or --output; no model calls started.")
                if key not in existing:
                    tasks.append((specs[ident], condition, args.trial, out, source, args.timeout))
        if args.order_seed is not None:
            random.Random(args.order_seed).shuffle(tasks)
        plan = {
            "experiment_sha256": fingerprint, "experiment": experiment,
            "trial": args.trial, "schedule": [{"scenario": task[0]["id"], "condition": task[1]} for task in tasks],
            "legacy_results_not_reused": legacy,
            "note": "Fresh model contexts; registry is catalogue-only evidence. No process COMPLETED status implies acceptance.",
        }
        (out / f"plan-{uuid.uuid4().hex[:8]}.json").write_text(json.dumps(plan, indent=2) + "\n")
        if args.dry_run:
            print(json.dumps({"status": "DRY_RUN", "experiment_sha256": fingerprint, "scheduled_tasks": len(tasks), "model_calls": 0}))
            return
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = [pool.submit(run_case, *task, native_seed=args.native_seed, native_readiness=args.native_readiness, activation=args.activation, trigger_kind=args.trigger_kind, registry_timeout=args.registry_timeout, experiment_sha256=fingerprint, trusted_input_grading=args.trusted_input_grading, safe_grading=args.safe_grading, native_grading_readiness=args.native_grading_readiness) for task in tasks]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        (out / f"batch-{uuid.uuid4().hex[:8]}.json").write_text(json.dumps(results, indent=2) + "\n")


if __name__ == "__main__":
    main()
