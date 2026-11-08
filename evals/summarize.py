#!/usr/bin/env python3
"""Publish bounded, path-redacted measurements; preserve raw results separately."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import statistics


def events(path):
    rows = []
    if path.exists():
        for line in path.read_text(errors='replace').splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                rows.append(event)
    return rows


def measurements(rows):
    seen = {}
    usage = []
    for event in rows:
        item = event.get('item')
        if isinstance(item, dict) and item.get('id') and event.get('type') in {'item.started', 'item.completed'}:
            if item.get('type') in {'command_execution', 'file_change', 'mcp_tool_call', 'web_search'}:
                record = seen.setdefault(item['id'], {'type': item['type'], 'completed': False})
                record['completed'] |= event['type'] == 'item.completed'
        if event.get('type') == 'turn.completed' and isinstance(event.get('usage'), dict):
            usage.append(event['usage'])
    counts = Counter(item['type'] for item in seen.values())
    tokens = Counter()
    for entry in usage:
        tokens.update({key: value for key, value in entry.items() if isinstance(value, int) and not isinstance(value, bool)})
    return {'observed_tool_items_by_type': dict(counts), 'observed_tool_items': len(seen),
            'incomplete_tool_items': sum(not item['completed'] for item in seen.values()),
            'reported_completed_turn_usage': dict(tokens) if usage else None,
            'turn_completed': any(row.get('type') == 'turn.completed' for row in rows),
            'turn_started': any(row.get('type') == 'turn.started' for row in rows),
            'turn_error_observed': any(row.get('type') in {'turn.failed', 'error'} for row in rows)}


def redact(value):
    text = str(value).replace(str(Path.home()), '{host-home}')
    text = re.sub(r'/(?:private/)?var/folders/[^\s"\']+', '{private-temp}', text)
    text = text.replace('/private/tmp/', '{temp}/')
    text = re.sub(r'(?:sk_live_|ghp_|github_pat_)[A-Za-z0-9_-]+', '{redacted-token}', text)
    return text[:700]


def gate_status(value):
    return {'pass': 'PASS', 'fail': 'FAIL', 'blocked': 'BLOCKED', 'not-run': 'NOT RUN'}.get(str(value).lower(), 'NOT RUN')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='append', required=True, metavar='LABEL=DIR')
    parser.add_argument('--regrades', type=Path, action='append', default=[])
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    replacements = {}
    for directory in args.regrades:
        for path in sorted(directory.glob('*.json')):
            data = json.loads(path.read_text())
            if isinstance(data, dict) and data.get('id') and isinstance(data.get('grader'), dict):
                replacements[data['id']] = data
    runs = []
    for entry in args.run:
        label, separator, raw = entry.partition('=')
        directory = Path(raw)
        if not separator or not directory.is_dir():
            parser.error('Each --run must name an existing LABEL=DIR')
        for path in sorted(directory.glob('*/result.json')):
            data = json.loads(path.read_text())
            measured = measurements(events(path.parent / 'transcript.jsonl'))
            grade = replacements.get(data['id'], data).get('grader', {})
            checks = grade.get('checks', [])
            failed = [{'id': redact(check.get('id', '')), 'detail': redact(check.get('detail', ''))}
                      for check in checks if check.get('pass') is False]
            native_provisional = data['scenario'] in {'C', 'D'} and label in {'initial', 'native-invalid-2'}
            row = {
                'id': data['id'], 'cohort': label, 'scenario': data['scenario'],
                'condition': data['condition'], 'trial': data['trial'],
                'raw_agent_status': data['agent_status'],
                'observed_turn_completed': measured['turn_completed'],
                'model_exit_code': data.get('agent_exit'),
                'artifact_status': gate_status(grade.get('status')),
                'failed_checks': failed,
                'blockers': [redact(item) for item in grade.get('blockers', [])],
                'model_elapsed_seconds': data.get('elapsed_seconds'),
                'model_timeout_seconds': data.get('timeout_seconds'),
                'grading_version': grade.get('grading_amendment', {}).get('id', 'legacy-frozen'),
                'regraded': data['id'] in replacements,
                'source_result_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'source_outputs_changed_by_grading': grade.get('source_outputs_changed', False),
                'skill_files_sha256': data.get('skill_sha256'),
                'condition_integrity': data.get('condition_integrity', 'NOT RUN in prototype harness'),
                'native_provisional': native_provisional,
                'eligibility_note': 'Excluded uniformly: native environment readiness was invalid; raw failures and passing exploratory runtime followups retained.' if native_provisional else 'Observed result; retain all failures. Candidate versions/cohorts are separate.',
                'manual_status': 'NOT RUN', 'measurements': measured,
                'monetary_cost': None,
            }
            runs.append(row)
    groups = []
    for key in sorted({(row['cohort'], row['condition']) for row in runs}):
        selected = [row for row in runs if (row['cohort'], row['condition']) == key]
        times = [row['model_elapsed_seconds'] for row in selected if isinstance(row['model_elapsed_seconds'], (int, float))]
        groups.append({'cohort': key[0], 'condition': key[1], 'records': len(selected),
                       'artifact_outcomes': dict(Counter(row['artifact_status'] for row in selected)),
                       'completed_turns': sum(row['observed_turn_completed'] for row in selected),
                       'observed_model_tasks_started': sum(row['measurements']['turn_started'] for row in selected),
                       'model_elapsed_median_seconds': statistics.median(times) if times else None,
                       'model_elapsed_range_seconds': [min(times), max(times)] if times else None})
    report = {
        'schemaVersion': 1, 'generatedUtc': datetime.now(timezone.utc).isoformat(),
        'model': 'gpt-6.1-sol', 'reasoning': 'high', 'timeoutSeconds': 240,
        'modelRevisionLimit': 'Advertised model alias was held constant; immutable provider revision is unavailable.',
        'statusPolicy': 'PASS/FAIL apply to selected executable assertions; process completion, manual judgement, native eligibility and release gates remain separate. No average waives a failed security/core gate.',
        'measurementLimits': ['Tool items are observed command_execution/file_change/MCP/web_search event IDs, not hidden internal calls.',
                              'Interrupted-turn token usage is unknown. Monetary telemetry is unavailable, not zero.',
                              'Elapsed times include provider/tool latency; heterogeneous tasks, host load and small samples do not establish causal performance improvement.',
                              'Prototype and audited harness versions, grading amendments and candidate snapshots are distinguished; original raw records are not overwritten.'],
        'groups': groups, 'runs': runs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'records': len(runs), 'groups': groups}, indent=2))


if __name__ == '__main__':
    main()
