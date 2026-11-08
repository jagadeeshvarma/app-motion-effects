#!/usr/bin/env python3
"""GA01 companion grading: verify host-injected input before excluding its files.

Frozen graders remain unchanged. A trusted before manifest must be supplied by the
harness outside the evaluated workspace. No submitted file is removed or repaired.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parents[1]
PREFIX = ".agents/skills/app-motion-effects/"
IGNORED_PARTS = {".git", "node_modules", ".dart_tool", "build"}
AMENDMENT = "GA01-verified-host-input-scope"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def eligible_files(root):
    return {
        str(path.relative_to(root)): path
        for path in Path(root).rglob("*")
        if path.is_file() and not any(part in IGNORED_PARTS for part in path.relative_to(root).parts)
    }


def verify_host_inputs(workspace, manifest_path, expected_manifest_sha256=None):
    workspace = Path(workspace).resolve()
    manifest_path = Path(manifest_path).resolve()
    if manifest_path.is_relative_to(workspace):
        raise ValueError("Trusted before manifest must be outside the evaluated workspace")
    manifest_hash = sha256(manifest_path)
    if expected_manifest_sha256 and manifest_hash != expected_manifest_sha256:
        raise ValueError("Trusted before manifest does not match the externally recorded SHA-256")
    data = json.loads(manifest_path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Trusted manifest must be a JSON object")
    before = data.get("before_sha256")
    if not isinstance(before, dict):
        raise ValueError("Trusted manifest must contain the harness before_sha256 file map")
    for name, value in before.items():
        path = Path(name)
        if not isinstance(name, str) or path.is_absolute() or ".." in path.parts or path.as_posix() != name or not isinstance(value, str):
            raise ValueError("Invalid relative file entry in trusted before map")
    expected = {name: value for name, value in before.items() if name.startswith(PREFIX)}
    # Inspect the entire exact injected tree, not a blanket .agents exclusion.
    tree = workspace / PREFIX.rstrip("/")
    actual = {}
    issues = []
    if tree.is_symlink():
        issues.append("Injected tree root became a symlink")
    elif tree.exists() and not tree.is_dir():
        issues.append("Injected tree root is not a directory")
    for path in (workspace / ".agents", workspace / ".agents/skills"):
        if path.is_symlink():
            issues.append("Injected tree ancestor became a symlink")
    if tree.exists() and not issues:
        for path in tree.rglob("*"):
            name = path.relative_to(workspace).as_posix()
            if path.is_symlink():
                actual[name] = "symlink:" + os.readlink(path)
            elif path.is_file():
                actual[name] = sha256(path)
    missing = sorted(set(expected) - set(actual))
    added = sorted(set(actual) - set(expected))
    modified = sorted(name for name in set(expected) & set(actual) if actual[name] != expected[name])
    if any(not value or value.startswith("symlink:") or len(value) != 64 or any(char not in "0123456789abcdef" for char in value) for value in expected.values()):
        issues.append("Injected tree entries require ordinary-file SHA-256 values")
    passed = not (issues or missing or added or modified)
    return {
        "verified": passed, "manifest_sha256": manifest_hash,
        "verified_files": sorted(expected) if passed else [],
        "expected_file_count": len(expected), "actual_file_count": len(actual),
        "missing": missing, "added": added, "modified": modified, "issues": issues,
    }


def amended_grade(raw, scenario, workspace, audit):
    result = copy.deepcopy(raw)
    result["raw_legacy_grade"] = copy.deepcopy(raw)
    result.setdefault("checks", []).append({"id": "trusted-host-inputs-unchanged", "pass": audit["verified"], "detail": "Byte-for-byte comparison of the entire injected tree against the external before map."})
    if scenario == "H":
        original = eligible_files(BASE / "fixtures/H")
        submitted = eligible_files(workspace)
        verified = set(audit["verified_files"])
        changed = sorted(name for name, path in submitted.items() if name not in verified and (name not in original or sha256(path) != sha256(original[name])))
        allowed = {"public/styles.css", "REVIEW.md"}
        scope = {"id": "tiny-change-boundary", "pass": all(name in allowed for name in changed), "detail": ", ".join(changed), "excluded_verified_host_file_count": len(verified)}
        indices = [index for index, item in enumerate(result["checks"]) if item.get("id") == "tiny-change-boundary"]
        if len(indices) != 1:
            result["checks"].append({"id": "legacy-scope-assertion-present", "pass": False, "detail": "Expected exactly one original tiny-change-boundary assertion."})
        else:
            result["checks"][indices[0]] = scope
    if str(raw.get("status", "")).lower() == "blocked" or raw.get("blockers"):
        result["status"] = "blocked"
    else:
        result["status"] = "pass" if all(item.get("pass") is True for item in result["checks"]) else "fail"
    result["grading_amendment"] = {"id": AMENDMENT, "trusted_input_audit": audit, "source_outputs_changed": False, "tasks_and_thresholds_changed": False}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=list("ABCDEFGHIJKLMN"), required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--before-manifest", type=Path, required=True, help="External harness before-manifest or original result JSON containing before_sha256")
    parser.add_argument("--expected-manifest-sha256")
    parser.add_argument("--transcript", type=Path)
    parser.add_argument("--prior-workspace", type=Path)
    parser.add_argument("--timeout", type=int, default=150)
    parser.add_argument("--native-grading-readiness", type=Path, help="Separate least-privilege generated-Dart grading proof")
    parser.add_argument("--safe-grading", action="store_true", default=True, help="Compatibility option: GA02 preflight/transport is always enabled")
    args = parser.parse_args()
    if args.scenario in {"C", "D"}:
        sys.path.insert(0, str(BASE))
        try:
            from run import check_native_grading_readiness
            if not args.safe_grading:
                raise ValueError("Generated Dart grading requires the contained least-privilege native transport")
            check_native_grading_readiness(args.native_grading_readiness)
        except (ImportError, OSError, ValueError) as error:
            print(json.dumps({"scenario": args.scenario, "status": "blocked", "checks": [], "blockers": [f"Native generated-code grading held: {error}"], "ui_checks": "NOT RUN: least-privilege grading readiness unavailable"}))
            raise SystemExit(2)
    if args.safe_grading:
        sys.path.insert(0, str(BASE))
        try:
            from containment import preflight_workspace, UnsafeSubmittedTree
        except ImportError as error:
            print(json.dumps({"scenario": args.scenario, "status": "blocked", "checks": [], "blockers": [f"GA02 infrastructure unavailable: {error}"], "ui_checks": "NOT RUN: preflight unavailable"}))
            raise SystemExit(2)
        try:
            preflight_workspace(args.workspace)
            if args.prior_workspace:
                preflight_workspace(args.prior_workspace)
        except UnsafeSubmittedTree as error:
            print(json.dumps({"scenario": args.scenario, "status": "fail", "checks": [{"id": "submitted-tree-contained", "pass": False, "detail": str(error)}], "blockers": [], "ui_checks": "NOT RUN: submitted-tree violation rejected before legacy reads", "grading_amendment": {"id": AMENDMENT, "safe_grading": True}, "grading_containment": {"id": "GA02-submitted-tree-and-static-transport", "preflight": "rejected", "violation": True}}))
            raise SystemExit(1)
        except (OSError, ValueError) as error:
            print(json.dumps({"scenario": args.scenario, "status": "blocked", "checks": [], "blockers": [f"GA02 submitted-tree preflight unavailable: {error}"], "ui_checks": "NOT RUN: preflight unavailable", "grading_amendment": {"id": AMENDMENT, "safe_grading": True}, "grading_containment": {"id": "GA02-submitted-tree-and-static-transport", "preflight": "unavailable", "violation": None}}))
            raise SystemExit(2)
    try:
        audit = verify_host_inputs(args.workspace, args.before_manifest, args.expected_manifest_sha256)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({"scenario": args.scenario, "status": "blocked", "checks": [], "blockers": [f"Trusted-input verification unavailable: {error}"], "grading_amendment": {"id": AMENDMENT}}))
        raise SystemExit(2)
    base = BASE / "supplemental" if args.scenario in {"M", "N"} else BASE
    argv = [sys.executable, str(base / "graders/grade.py"), "--scenario", args.scenario, "--workspace", str(args.workspace)]
    if args.transcript:
        argv += ["--transcript", str(args.transcript)]
    if args.prior_workspace:
        argv += ["--prior-workspace", str(args.prior_workspace)]
    if args.safe_grading:
        argv = [sys.executable, str(BASE / "graders/grade_with_containment.py"), "--legacy-grader", str(base / "graders/grade.py"), *argv[2:]]
        if args.scenario in {"C", "D"}:
            argv += ["--native-grading-readiness", str(args.native_grading_readiness)]
    source_before = None
    try:
        # Import the bounded process helper without loading tasks or calling a model.
        sys.path.insert(0, str(BASE))
        from run import run_process, digest_tree, canonical_hash
        source_before = digest_tree(args.workspace)
        process = run_process(argv, timeout=args.timeout, env=dict(os.environ))
        if process["stderr"]:
            sys.stderr.write(process["stderr"])
        raw = json.loads(process["stdout"])
        if process["timed_out"] or process["launch_error"]:
            raw["status"] = "blocked"
            raw.setdefault("blockers", []).append(process["launch_error"] or "Legacy grader timed out")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raw = {"scenario": args.scenario, "status": "blocked", "checks": [], "blockers": [f"Legacy grader did not complete: {error}"]}
    result = amended_grade(raw, args.scenario, args.workspace, audit)
    if source_before is not None:
        source_after = digest_tree(args.workspace)
        unchanged = source_before == source_after
        result["checks"].append({"id": "grader-preserved-source-tree", "pass": unchanged})
        result["grading_amendment"]["source_outputs_changed"] = not unchanged
        result["grading_amendment"]["source_tree_before_sha256"] = canonical_hash(source_before)
        result["grading_amendment"]["source_tree_after_sha256"] = canonical_hash(source_after)
        if not unchanged and result["status"] != "blocked":
            result["status"] = "fail"
    result["grading_amendment"]["safe_grading"] = args.safe_grading
    result["grading_amendment"]["companion_sha256"] = sha256(Path(__file__))
    from frozen_assertions import source_sha256
    result["grading_amendment"]["legacy_grader_sha256"] = source_sha256(base / "graders/grade.py")
    print(json.dumps(result, indent=2))
    raise SystemExit(2 if result["status"] == "blocked" else 0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
