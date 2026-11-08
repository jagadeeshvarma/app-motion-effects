"""GA02 synthetic containment regressions; no evaluated model calls."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

EVALS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVALS))
from containment import preflight_workspace, UnsafeSubmittedTree
spec = importlib.util.spec_from_file_location('contained_grading', EVALS / 'graders/grade_with_containment.py')
grading = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grading)


class ContainmentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='motion-ga02-unit-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root / 'app'
        self.work.mkdir()
        (self.work / 'regular.txt').write_text('SYNTHETIC_INSIDE')
        self.canary = self.root / 'outside.txt'
        self.canary.write_text('SYNTHETIC_OUTSIDE_MUST_NOT_BE_READ')

    def test_regular_tree_passes_without_reading_file_contents(self):
        with patch.object(Path, 'read_bytes', side_effect=AssertionError('content read')), patch.object(Path, 'read_text', side_effect=AssertionError('content read')):
            self.assertEqual(preflight_workspace(self.work)['regular_files'], 1)

    def test_links_are_rejected_inside_outside_broken_and_ignored_subtrees(self):
        for name, target in [('outside', self.canary), ('inside', self.work / 'regular.txt'), ('broken', self.root / 'missing'), ('.git/linked', self.canary), ('build/linked', self.canary)]:
            with self.subTest(name=name):
                link = self.work / name
                link.parent.mkdir(exist_ok=True)
                link.symlink_to(target)
                with self.assertRaises(UnsafeSubmittedTree): preflight_workspace(self.work)
                link.unlink()

    def test_directory_and_root_links_are_rejected(self):
        link = self.work / 'directory'
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(UnsafeSubmittedTree): preflight_workspace(self.work)
        link.unlink()
        root_link = self.root / 'root-link'
        root_link.symlink_to(self.work, target_is_directory=True)
        with self.assertRaises(UnsafeSubmittedTree): preflight_workspace(root_link)

    @unittest.skipUnless(hasattr(os, 'mkfifo'), 'POSIX FIFO required')
    def test_fifo_is_rejected_without_opening(self):
        os.mkfifo(self.work / 'pipe')
        with self.assertRaises(UnsafeSubmittedTree): preflight_workspace(self.work)

    def test_preflight_prevents_legacy_execution_before_reads_or_hashes(self):
        legacy = self.root / 'grade.py'
        legacy.write_text("raise AssertionError('Legacy must not run')")
        (self.work / 'linked').symlink_to(self.canary)
        with patch.object(grading.runpy, 'run_path', side_effect=AssertionError('Legacy executed')):
            with self.assertRaises(UnsafeSubmittedTree): grading.execute_legacy(legacy, [], self.work)

    def test_legacy_assertions_and_exit_outcome_are_preserved(self):
        legacy = self.root / 'grade.py'
        legacy.write_text("import json\nprint(json.dumps({'status':'fail','checks':[{'id':'frozen-ui-assertion','pass':False}]}))\nraise SystemExit(1)\n")
        result = grading.execute_legacy(legacy, [], self.work)
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(result['checks'], [{'id':'frozen-ui-assertion','pass':False}])
        self.assertFalse(result['grading_containment']['frozen_assertions_changed'])

    def test_only_exact_legacy_node_transport_is_redirected(self):
        legacy = self.root / 'grade.py'
        web = self.root / 'web.mjs'
        legacy.write_text("import json,subprocess\nsubprocess.run(['node'," + repr(str(web)) + ",'B','app'])\nsubprocess.run(['other-command','unchanged'])\nprint(json.dumps({'status':'pass','checks':[]}))\n")
        calls = []
        with patch.object(subprocess, 'run', side_effect=lambda command, *a, **kw: calls.append(command)):
            result = grading.execute_legacy(legacy, [], self.work)
        self.assertEqual(calls[0][0:2], ['node', '--import'])
        self.assertEqual(calls[0][3:], [str(web), 'B', 'app'])
        self.assertEqual(calls[1], ['other-command', 'unchanged'])
        self.assertEqual(result['grading_containment']['transport_redirects'], ['web.mjs'])

    def test_cli_rejects_before_legacy_reads_with_no_canary_content_in_report(self):
        (self.work / 'linked').symlink_to(self.canary)
        result = subprocess.run([sys.executable, str(EVALS / 'graders/grade_with_containment.py'), '--legacy-grader', str(EVALS / 'graders/grade.py'), '--scenario', 'B', '--workspace', str(self.work)], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'fail')
        self.assertTrue(report['grading_containment']['violation'])
        self.assertTrue(report['ui_checks'].startswith('NOT RUN'))
        self.assertNotIn(self.canary.read_text(), result.stdout + result.stderr)

    def test_missing_workspace_preflight_is_blocked_not_an_output_violation(self):
        result = subprocess.run([sys.executable, str(EVALS / 'graders/grade_with_containment.py'), '--legacy-grader', str(EVALS / 'graders/grade.py'), '--scenario', 'B', '--workspace', str(self.root / 'missing')], capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'blocked')
        self.assertIsNone(report['grading_containment']['violation'])
        self.assertEqual(report['checks'], [])

    def test_node_transport_preflight_and_request_guards(self):
        result = subprocess.run(['node', str(EVALS / 'tests/containment-server.mjs')], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('GA02 static transport passed', result.stdout)


if __name__ == '__main__': unittest.main()
