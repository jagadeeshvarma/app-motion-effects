#!/usr/bin/env python3
"""Probe skills/list without a model turn or host configuration writes.

App-server has no exec --ignore-user-config flag in the installed CLI. This probe
checks the enabled skill catalogue under explicit overrides, not full exec config
or whether the model read the skill. Errors and unexpected skills fail closed.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import tempfile
import time


def probe_registry(workspace, skill=None, *, config_args=None, env=None, timeout=20):
    if config_args is None:
        from run import config
        config_args = config(skill)
    proc = None
    selector = selectors.DefaultSelector()
    output = {"status": "BLOCKED", "scope": "catalogue-only; app-server user-config behavior differs from exec --ignore-user-config", "model_calls": 0}
    started = time.monotonic()
    with tempfile.TemporaryFile() as stderr:
        try:
            proc = subprocess.Popen(["codex", "app-server", *config_args], cwd=workspace, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr, start_new_session=True)
            selector.register(proc.stdout, selectors.EVENT_READ)
            def send(value):
                proc.stdin.write((json.dumps(value) + "\n").encode())
                proc.stdin.flush()
            send({"id": 1, "method": "initialize", "params": {"clientInfo": {"name": "motion-audit", "version": "2.0"}}})
            buffer = b""
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                ready = selector.select(timeout=min(0.5, max(0, deadline - time.monotonic())))
                if not ready:
                    if proc.poll() is not None:
                        raise RuntimeError("app-server exited before skills/list response")
                    continue
                chunk = os.read(proc.stdout.fileno(), 65536)
                if not chunk:
                    raise RuntimeError("app-server stdout closed before skills/list response")
                buffer += chunk
                if len(buffer) > 4 * 1024 * 1024:
                    raise RuntimeError("Registry response exceeded bounded buffer")
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    try:
                        response = json.loads(line)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue
                    if response.get("id") == 1:
                        if "error" in response:
                            raise RuntimeError("App-server initialization rejected")
                        send({"method": "initialized", "params": {}})
                        send({"id": 2, "method": "skills/list", "params": {"cwds": [str(Path(workspace).resolve())], "forceReload": True}})
                    if response.get("id") == 2:
                        if "error" in response:
                            raise RuntimeError("skills/list rejected")
                        rows = response["result"]["data"]
                        skills = [item for row in rows for item in row["skills"]]
                        enabled = [item for item in skills if item.get("enabled")]
                        expected = [str((Path(skill) / "SKILL.md").resolve())] if skill else []
                        actual = [str(Path(item["path"]).resolve()) for item in enabled]
                        errors = [error for row in rows for error in row.get("errors", [])]
                        output.update({
                            "status": "PASS" if sorted(actual) == sorted(expected) and not errors else "FAIL",
                            "enabled_count": len(enabled), "expected_target": bool(skill), "registry_error_count": len(errors),
                            "enabled": [{"name": item["name"], "path": "fixture/.agents/skills/app-motion-effects/SKILL.md" if skill and Path(item["path"]).resolve() == (Path(skill) / "SKILL.md").resolve() else "unexpected-host-skill"} for item in enabled],
                        })
                        return output
            raise TimeoutError("skills/list timed out")
        except (OSError, RuntimeError, TimeoutError, KeyError, TypeError) as error:
            output["reason"] = f"{type(error).__name__}: {error}"
            return output
        finally:
            selector.close()
            if proc is not None:
                from run import stop_group
                cleanup = [stop_group(proc)]
                if proc.stdin is not None:
                    proc.stdin.close()
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    cleanup.append(stop_group(proc, force=True))
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        cleanup.append("unreaped-child")
                cleanup.append(stop_group(proc, force=True))
                for stream in (proc.stdin, proc.stdout):
                    if stream is not None:
                        stream.close()
                output["cleanup"] = cleanup
                if "denied" in cleanup or "unreaped-child" in cleanup:
                    output["status"] = "BLOCKED"
                    output["reason"] = "Registry process cleanup was denied or incomplete"
            output["elapsed_seconds"] = round(time.monotonic() - started, 3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--skill", type=Path)
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()
    from run import base_environment
    result = probe_registry(args.workspace, args.skill, env=base_environment(), timeout=args.timeout)
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
