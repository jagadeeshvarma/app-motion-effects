#!/usr/bin/env python3
"""Quarantined historical entrypoint. Use the guarded evaluation runner."""
import json
raise SystemExit(print(json.dumps({"status":"blocked","checks":[],"blockers":["Direct frozen grading is quarantined. Use evals/run.py or evals/regrade.py; existing outputs require the guarded companion and trusted external before manifest."],"ui_checks":"NOT RUN: historical entrypoint quarantined","grading_entrypoint":"GA03-safe-defaults"})) or 2)
