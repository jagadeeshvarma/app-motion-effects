#!/usr/bin/env python3
"""Automatic-selection evidence probes, separate from functional benchmark scores.

Direct body text returned by a successful path-bearing reader is positive evidence.
A missing read is unknown, never proof of inactivity. Audit quality, adherence,
indirect loading and ambiguous/overlapping selection still need manual review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest

from run import config, base_environment, digest_tree, run_process, events_and_metrics, process_status

BASE = Path(__file__).resolve().parent
CASES=[
 ('positive-motion','Audit only the selected repair inspector transition for draft/focus preservation, interruption and reduced motion. Do not edit files. Give concise observations.','activate'),
 ('positive-feedback','Review only this form’s save feedback for truthful pending, failure and success states. Preserve the existing app. Do not edit files. Give concise observations.','activate'),
 ('negative-copy','Report the exact visible text of the two repair-record buttons. Do not change or audit behaviour, motion or styling.','inactive'),
 ('negative-data','Explain the shape of the records data structure in public/app.js. Do not audit UI, animation or make changes.','inactive'),
 ('ambiguous-sluggish','This screen feels sluggish. Inspect and explain the likely cause before proposing any change. Do not edit.','judgement'),
 ('overlap-form','Audit the selected repair inspector for clear record-change feedback, preserved drafts during transitions and correct field labels. Do not edit. Keep observations concise.','compose')]
COMPANION = (
    '---\nname: fixture-form-check\ndescription: Review form labels and validation semantics when the user asks to audit form accessibility.\n---\n'
    'Inspect existing label/control associations and validation semantics only. Respect applicable repository instructions. '
    'Do not edit unless requested; do not repeat unrelated design or motion audits.\n'
)
READER = re.compile(r'\b(?:cat|sed|head|tail|less|more|bat|rg|grep|Get-Content|read_text|readFileSync|readFile|readFileText|open)\b', re.I)


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def value_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def normalized_events(stdout):
    """Reject valid JSON scalars and malformed item shapes before shared metrics."""
    events = []
    malformed = 0
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if not isinstance(event, dict):
            malformed += 1
            continue
        if event.get('type') in {'item.started', 'item.completed'} and not isinstance(event.get('item'), dict):
            malformed += 1
            continue
        events.append(event)
    return events, malformed


def body_anchors(text):
    """Use body excerpts, excluding catalogue-visible frontmatter/title alone."""
    if text.startswith('---\n') and '\n---' in text[4:]:
        text = text.split('\n---', 1)[1]
    lines = [re.sub(r'\s+', ' ', line.strip()) for line in text.splitlines()]
    return [line[:120] for line in lines if len(line) >= 45 and not line.startswith(('#', '```'))]


def read_evidence(events, relative_skill_path, skill_text):
    anchors = body_anchors(skill_text)
    references = []
    body_reads = []
    for event in events:
        item = event.get('item', {})
        if event.get('type') != 'item.completed' or not isinstance(item, dict) or item.get('type') != 'command_execution':
            continue
        command = item.get('command', '')
        if not isinstance(command, str) or relative_skill_path not in command.replace('\\', '/'):
            continue
        code = item.get('exit_code')
        successful = isinstance(code, int) and not isinstance(code, bool) and code == 0
        output = item.get('aggregated_output', '')
        output = re.sub(r'\s+', ' ', output) if isinstance(output, str) else ''
        body_observed = successful and bool(READER.search(command)) and any(anchor in output for anchor in anchors)
        entry = {'item_id': item.get('id'), 'successful': successful, 'plausible_reader': bool(READER.search(command)), 'body_text_observed': body_observed}
        references.append(entry)
        if body_observed:
            body_reads.append(entry)
    return {'path_reference_observed': bool(references), 'body_text_observed': bool(body_reads), 'path_reference_count': len(references), 'direct_body_read_count': len(body_reads), 'events': references}


def classify(expectation, observed_process, changed, target, companion):
    target_read = target['body_text_observed']
    companion_read = companion['body_text_observed']
    if changed:
        return 'FAIL', 'Audit-only workspace boundary violated; process state and routing evidence are retained separately.'
    if observed_process != 'COMPLETED':
        return 'BLOCKED', 'Process did not complete; selection is not scored.'
    if expectation == 'judgement':
        return 'NOT APPLICABLE', 'Ambiguous selection is explicitly unscored and requires manual judgement.'
    if expectation == 'inactive':
        if target_read:
            return 'REVIEW REQUIRED', 'Unexpected direct body-read evidence; inspect whether the workflow was actually imposed.'
        return 'REVIEW REQUIRED', 'No direct body read observed; this does not prove inactivity or correct task completion.'
    if expectation == 'activate' and target_read:
        return 'PASS', 'Expected direct body-read evidence observed; this is routing evidence, not instruction adherence or audit quality.'
    if expectation == 'compose' and target_read and companion_read:
        return 'PASS', 'Both bodies observed in one controlled companion probe; this does not establish general composition quality.'
    if expectation == 'compose':
        return 'REVIEW REQUIRED', 'Co-read evidence incomplete; overlapping coverage may permit a reasonable single-skill route.'
    return 'REVIEW REQUIRED', 'Expected direct read not observed; missing or indirect evidence cannot establish under-triggering.'


def reserve_output(output):
    output = Path(output).resolve()
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError('Refusing non-empty activation output; use a fresh directory before any model call.')
    output.mkdir(parents=True, exist_ok=True)
    # Exclusive creation closes the race between two callers observing an empty directory.
    with (output / '.activation-reserved').open('x') as stream:
        stream.write('Fresh output reserved; never overwrite activation results.\n')
    return output


def checked_process(argv, **kwargs):
    process = run_process(argv, **kwargs)
    if process['launch_error'] or process['timed_out'] or process['returncode'] != 0:
        raise RuntimeError(process['launch_error'] or ('Setup process timed out' if process['timed_out'] else 'Setup process failed'))
    return process


def run_probe(ident, task, expectation, output, snapshot, candidate_hashes, timeout):
    folder = output / ident
    folder.mkdir()
    work = Path(tempfile.mkdtemp(prefix='motion-trigger-')) / 'app'
    fixture = 'A' if ident == 'positive-feedback' else 'B'
    result = {
        'id': ident, 'task': task, 'task_sha256': hashlib.sha256(task.encode()).hexdigest(),
        'fixture': fixture, 'candidate_sha256': candidate_hashes,
        'expectation': expectation, 'status': 'BLOCKED', 'agent_process': 'SETUP_FAILED',
        'model': 'gpt-6.1-sol', 'reasoning': 'high', 'timeout_seconds': timeout,
        'activation_mode': 'implicit', 'functional_grader_applied': False, 'manual_review': 'NOT RUN',
        'limit': 'Positive direct body excerpts are evidence of a read, not full loading/adherence. Missing, indirect or host-injected reads remain unknown. Audit/task quality is unscored. Ambiguous/overlapping routing needs manual judgement. The companion probe is one synthetic case, not an ecosystem benchmark.',
        'change_check_scope': 'Workspace files/symlinks excluding .git only; outside-workspace writes are not observed.',
    }
    try:
        shutil.copytree(BASE / 'fixtures' / fixture, work)
        checked_process(['git', 'init', '-q'], cwd=work, env=base_environment(), timeout=20)
        skill = work / '.agents/skills/app-motion-effects'
        skill.parent.mkdir(parents=True)
        shutil.copytree(snapshot, skill)
        if digest_tree(skill) != candidate_hashes:
            raise RuntimeError('Installed probe skill differs from the captured candidate snapshot')
        if expectation == 'compose':
            companion = skill.parent / 'fixture-form-check'
            companion.mkdir()
            (companion / 'SKILL.md').write_text(COMPANION)
        before = digest_tree(work)
        argv = [
            'codex', 'exec', '--ignore-user-config', '--ephemeral', '--skip-git-repo-check',
            '-s', 'workspace-write', '-m', 'gpt-6.1-sol', '-c', 'model_reasoning_effort="high"',
            '-c', 'approval_policy="never"', *config(skill), '--json', '-o', str(folder / 'response.txt'), '-'
        ]
        result['invocation_sha256'] = value_hash(argv)
        result['model_input_sha256'] = hashlib.sha256(task.encode()).hexdigest()
        process = run_process(argv, cwd=work, env=base_environment(), input_text=task, timeout=timeout)
        (folder / 'transcript.jsonl').write_text(process['stdout'])
        (folder / 'stderr.txt').write_text(process['stderr'])
        events, malformed = normalized_events(process['stdout'])
        metrics = events_and_metrics('\n'.join(json.dumps(event) for event in events))
        metrics['malformed_event_lines'] += malformed
        target = read_evidence(events, 'app-motion-effects/SKILL.md', (snapshot / 'SKILL.md').read_text())
        companion = read_evidence(events, 'fixture-form-check/SKILL.md', COMPANION)
        observed = process_status(process, metrics)
        after = digest_tree(work)
        changed = sorted(name for name in set(before) | set(after) if before.get(name) != after.get(name))
        status, interpretation = classify(expectation, observed, changed, target, companion)
        result.update({
            'status': status, 'interpretation': interpretation, 'agent_process': observed,
            'observed_target_read': target['body_text_observed'], 'observed_companion_read': companion['body_text_observed'],
            'target_read_evidence': target, 'companion_read_evidence': companion,
            'changed_paths': changed, 'audit_only_boundary_pass': not changed, 'workspace_before_sha256': value_hash(before), 'workspace_after_sha256': value_hash(after),
            'elapsed_seconds': process['elapsed_seconds'], 'cleanup': process.get('cleanup', []), 'metrics': metrics,
        })
    except Exception as error:
        result['error'] = f'{type(error).__name__}: {error}'
    (folder / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result.get(key) for key in ['id', 'status', 'observed_target_read', 'observed_companion_read', 'elapsed_seconds']}), flush=True)
    return result


class ActivationSelfTests(unittest.TestCase):
    """Pure evidence/guard tests; temporary test files only, no model/subprocess calls."""
    text = '---\nname: sample\ndescription: Catalogue description does not count.\n---\n# Sample\nThis is a distinctive body instruction with enough content to identify an observed excerpt.\n'

    def event(self, command='cat .agents/skills/app-motion-effects/SKILL.md', code=0, output=None):
        return {'type':'item.completed','item':{'type':'command_execution','id':'1','command':command,'exit_code':code,'aggregated_output':output if output is not None else self.text}}

    def evidence(self, events):
        return read_evidence(events, 'app-motion-effects/SKILL.md', self.text)

    def test_successful_reader_and_body_excerpt_count(self):
        self.assertTrue(self.evidence([self.event()])['body_text_observed'])

    def test_path_listing_does_not_count_as_read(self):
        evidence=self.evidence([self.event('ls .agents/skills/app-motion-effects/SKILL.md',output='SKILL.md')])
        self.assertTrue(evidence['path_reference_observed']);self.assertFalse(evidence['body_text_observed'])

    def test_failed_read_does_not_count(self):
        self.assertFalse(self.evidence([self.event(code=1)])['body_text_observed'])

    def test_frontmatter_only_does_not_count(self):
        self.assertFalse(self.evidence([self.event(output='description: Catalogue description does not count.')])['body_text_observed'])

    def test_missing_exit_status_remains_unknown(self):
        event=self.event();del event['item']['exit_code']
        self.assertFalse(self.evidence([event])['body_text_observed'])

    def test_malformed_json_and_item_shapes_are_bounded(self):
        events,bad=normalized_events('null\n42\n[]\n{bad\n'+json.dumps({'type':'item.completed','item':None})+'\n'+json.dumps({'type':'turn.completed','usage':{'input_tokens':1}}))
        self.assertEqual(bad,5);self.assertEqual(len(events),1)
        self.assertTrue(events_and_metrics(json.dumps(events[0]))['turn_completed'])

    def test_absence_is_not_negative_success(self):
        empty=self.evidence([])
        self.assertEqual(classify('inactive','COMPLETED',[],empty,empty)[0],'REVIEW REQUIRED')

    def test_missing_positive_read_is_not_undertrigger_failure(self):
        empty=self.evidence([])
        self.assertEqual(classify('activate','COMPLETED',[],empty,empty)[0],'REVIEW REQUIRED')

    def test_ambiguous_selection_remains_unscored(self):
        evidence=self.evidence([self.event()])
        self.assertEqual(classify('judgement','COMPLETED',[],evidence,evidence)[0],'NOT APPLICABLE')

    def test_overlapping_coverage_is_not_forced_failure(self):
        yes=self.evidence([self.event()]);no=self.evidence([])
        self.assertEqual(classify('compose','COMPLETED',[],yes,no)[0],'REVIEW REQUIRED')

    def test_audit_file_change_fails_independently(self):
        yes=self.evidence([self.event()])
        self.assertEqual(classify('judgement','COMPLETED',['REVIEW.md'],yes,yes)[0],'FAIL')

    def test_observed_file_violation_survives_incomplete_process(self):
        empty=self.evidence([])
        self.assertEqual(classify('activate','TIMED_OUT',['REVIEW.md'],empty,empty)[0],'FAIL')

    def test_output_reservation_refuses_existing_content_and_race(self):
        with tempfile.TemporaryDirectory(prefix='activation-selftest-') as temp:
            output=Path(temp)/'fresh';reserve_output(output)
            with self.assertRaises(ValueError):reserve_output(output)
            other=Path(temp)/'existing';other.mkdir();(other/'results.json').write_text('preserve')
            with self.assertRaises(ValueError):reserve_output(other)
            self.assertEqual((other/'results.json').read_text(),'preserve')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--timeout', type=int, default=120)
    parser.add_argument('--self-test', action='store_true', help='Run pure evidence/guard tests only; no model/subprocess calls')
    args = parser.parse_args()
    if args.self_test:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ActivationSelfTests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    if not args.candidate or not (args.candidate/'SKILL.md').is_file() or not args.output:
        parser.error('Provide --candidate containing SKILL.md and a fresh --output directory')
    if args.timeout <= 0 or args.timeout > 240:
        parser.error('Timeout must be 1–240 seconds per probe')
    try:
        output=reserve_output(args.output)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    candidate_hashes=digest_tree(args.candidate)
    snapshot=output/'candidate-input'
    shutil.copytree(args.candidate,snapshot)
    if digest_tree(snapshot)!=candidate_hashes:
        raise SystemExit('Candidate changed during snapshot; no model calls made')
    (output/'plan.json').write_text(json.dumps({'script_sha256':file_hash(Path(__file__)),'candidate_sha256':candidate_hashes,'timeout_seconds':args.timeout,'model':'gpt-6.1-sol','reasoning':'high','cases':[{'id':ident,'expectation':expectation,'task_sha256':hashlib.sha256(task.encode()).hexdigest()} for ident,task,expectation in CASES],'activation':'implicit; no explicit skill invocation','manual_review_required':True,'max_model_calls':len(CASES)},indent=2)+'\n')
    results=[run_probe(ident,task,expectation,output,snapshot,candidate_hashes,args.timeout) for ident,task,expectation in CASES]
    with (output/'results.json').open('x') as stream:stream.write(json.dumps(results,indent=2)+'\n')


if __name__ == '__main__':
    main()
