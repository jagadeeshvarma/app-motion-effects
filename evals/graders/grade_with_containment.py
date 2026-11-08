#!/usr/bin/env python3
"""Opt-in GA02: run unchanged legacy assertions behind submitted-tree guards."""
from __future__ import annotations
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
from containment import preflight_workspace, UnsafeSubmittedTree


def execute_legacy(legacy, legacy_args, workspace, prior_workspace=None, *, native_readiness=None, native_scenario=False):
    """Preflight before legacy code reads/hashes submitted files; transport only changes."""
    if native_scenario:
        from native_grading import check_readiness
        check_readiness(native_readiness)
    audits = {"workspace": preflight_workspace(workspace)}
    if prior_workspace:
        audits["prior_workspace"] = preflight_workspace(prior_workspace)
    expected_web = legacy.parent / "web.mjs"
    preload = Path(__file__).with_name("safe-web-preload.mjs")
    original_run = subprocess.run
    original_argv = sys.argv
    redirects = []
    native_transports = []

    def guarded_run(command, *args, **kwargs):
        if isinstance(command, (list, tuple)) and command and str(command[0]) == "flutter":
            if not native_scenario:
                raise RuntimeError("Unexpected native execution outside the reviewed native scenario route")
            from native_grading import sandbox_command
            command, safe_env, metadata = sandbox_command(command, kwargs.get("cwd") or os.getcwd(), kwargs.get("env") or os.environ, native_readiness, submitted_workspace=workspace)
            kwargs["env"] = safe_env
            native_transports.append(metadata)
            redirects.append("flutter-least-privilege-sandbox")
        if isinstance(command, (list, tuple)) and len(command) > 1 and Path(str(command[1])).absolute() == expected_web.absolute():
            command = [command[0], "--import", str(preload), *command[1:]]
            redirects.append(expected_web.name)
        return original_run(command, *args, **kwargs)

    output = io.StringIO()
    try:
        subprocess.run = guarded_run
        sys.argv = [str(legacy), *legacy_args]
        with contextlib.redirect_stdout(output):
            try:
                from frozen_assertions import archived_source
                frozen = archived_source(legacy)
                if frozen is None:
                    # Trusted synthetic unit fixtures only; CLI accepts registered paths.
                    runpy.run_path(str(legacy), run_name="__main__")
                else:
                    exec(compile(frozen, str(legacy) + ":frozen-archive", "exec"), {"__name__": "__main__", "__file__": str(legacy), "__builtins__": __builtins__})
            except SystemExit as error:
                if error.code not in (None, 0, 1, 2):
                    raise RuntimeError("Legacy grader exited outside the documented result contract") from error
    finally:
        subprocess.run = original_run
        sys.argv = original_argv
    result = json.loads(output.getvalue())
    result["grading_containment"] = {
        "id": "GA02-submitted-tree-and-static-transport",
        "preflight": audits,
        "transport_redirects": redirects,
        "native_transports": native_transports,
        "frozen_assertions_changed": False,
        "source_outputs_changed": False,
        "legacy_grader_sha256": __import__("frozen_assertions").source_sha256(legacy),
        "historical_entrypoint_sha256": hashlib.sha256(legacy.read_bytes()).hexdigest(),
        "historical_quarantine": "GA03",
        "infrastructure_sha256": {str(path.relative_to(BASE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in [BASE / "containment.py", Path(__file__), preload, preload.with_name("safe-static-server.mjs")]},
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument("--legacy-grader", type=Path, required=True)
    parser.add_argument("--native-grading-readiness", type=Path)
    known, remaining = parser.parse_known_args()
    legacy = known.legacy_grader.resolve()
    allowed = {BASE / "graders/grade.py", BASE / "supplemental/graders/grade.py"}
    if legacy not in allowed:
        parser.error("Only the unchanged registered legacy graders may be selected")
    inputs = argparse.ArgumentParser(add_help=False)
    inputs.add_argument("--workspace", type=Path, required=True)
    inputs.add_argument("--prior-workspace", type=Path)
    inputs.add_argument("--scenario", required=True)
    args, _ = inputs.parse_known_args(remaining)
    try:
        result = execute_legacy(legacy, remaining, args.workspace, args.prior_workspace, native_readiness=known.native_grading_readiness, native_scenario=args.scenario in {"C", "D"})
    except UnsafeSubmittedTree as error:
        result = {
            "scenario": args.scenario, "status": "fail",
            "checks": [{"id": "submitted-tree-contained", "pass": False, "detail": str(error)}],
            "blockers": [], "ui_checks": "NOT RUN: submitted-tree violation rejected before legacy reads",
            "grading_containment": {"id": "GA02-submitted-tree-and-static-transport", "preflight": "rejected", "violation": True, "frozen_assertions_changed": False, "source_outputs_changed": False},
        }
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        result = {"scenario": args.scenario, "status": "blocked", "checks": [], "blockers": [f"GA02 containment unavailable: {error}"], "ui_checks": "NOT RUN: preflight unavailable", "grading_containment": {"id": "GA02-submitted-tree-and-static-transport", "preflight": "unavailable", "violation": None, "frozen_assertions_changed": False, "source_outputs_changed": False}}
    print(json.dumps(result, indent=2))
    raise SystemExit(2 if result["status"] == "blocked" else 0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
