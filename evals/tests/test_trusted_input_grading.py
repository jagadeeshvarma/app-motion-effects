"""GA01 trust/scope regression tests, synthetic trees only; no model/browser calls."""
import copy
import contextlib
import io
import sys
from unittest.mock import patch
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

EVALS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(EVALS))
spec=importlib.util.spec_from_file_location('trusted_grading',EVALS/'graders/grade_with_trusted_inputs.py')
grading=importlib.util.module_from_spec(spec);spec.loader.exec_module(grading)


class TrustedInputTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='motion-trusted-grade-unit-')
        self.root=Path(self.temp.name);self.work=self.root/'app'
        shutil.copytree(EVALS/'fixtures/H',self.work)
        self.skill=self.work/'.agents/skills/app-motion-effects';self.skill.mkdir(parents=True)
        (self.skill/'SKILL.md').write_text('Synthetic trusted host input\n')
        (self.skill/'references').mkdir();(self.skill/'references/check.md').write_text('Synthetic reference\n')
        before={str(p.relative_to(self.work)):hashlib.sha256(p.read_bytes()).hexdigest() for p in self.work.rglob('*') if p.is_file()}
        self.manifest=self.root/'before.json';self.manifest.write_text(json.dumps({'before_sha256':before}))
        self.raw={'scenario':'H','status':'fail','checks':[{'id':'tiny-change-boundary','pass':False,'detail':'injected inputs'},{'id':'ui-check','pass':True}],'blockers':[]}

    def tearDown(self):self.temp.cleanup()

    def audit(self):return grading.verify_host_inputs(self.work,self.manifest)

    def test_excludes_only_verified_tree_and_preserves_raw_grade(self):
        (self.work/'REVIEW.md').write_text('Observed synthetic checks\n')
        css=self.work/'public/styles.css';css.write_text(css.read_text().replace('1200ms','140ms'))
        audit=self.audit();self.assertTrue(audit['verified']);self.assertEqual(len(audit['verified_files']),2)
        result=grading.amended_grade(self.raw,'H',self.work,audit)
        self.assertEqual(result['status'],'pass');self.assertEqual(result['raw_legacy_grade'],self.raw)
        self.assertEqual(self.raw['status'],'fail')

    def test_modified_host_file_is_not_excluded(self):
        (self.skill/'SKILL.md').write_text('Changed by evaluated output')
        audit=self.audit();self.assertFalse(audit['verified']);self.assertEqual(audit['verified_files'],[])
        result=grading.amended_grade(self.raw,'H',self.work,audit);self.assertEqual(result['status'],'fail')
        self.assertIn('.agents/skills/app-motion-effects/SKILL.md',audit['modified'])

    def test_added_file_in_host_tree_fails(self):
        (self.skill/'extra.md').write_text('untrusted addition')
        audit=self.audit();self.assertFalse(audit['verified']);self.assertEqual(audit['added'],['.agents/skills/app-motion-effects/extra.md'])

    def test_missing_host_file_fails(self):
        (self.skill/'SKILL.md').unlink();self.assertFalse(self.audit()['verified'])

    def test_unrelated_agents_addition_remains_generated_change(self):
        (self.work/'.agents/untrusted.md').write_text('not a host input')
        result=grading.amended_grade(self.raw,'H',self.work,self.audit())
        self.assertEqual(result['status'],'fail')
        scope=next(check for check in result['checks'] if check['id']=='tiny-change-boundary')
        self.assertIn('.agents/untrusted.md',scope['detail'])

    def test_unrelated_ui_change_still_fails(self):
        (self.work/'public/app.js').write_text('window.changed=true;')
        self.assertEqual(grading.amended_grade(self.raw,'H',self.work,self.audit())['status'],'fail')

    def test_other_failed_assertion_is_preserved(self):
        raw=copy.deepcopy(self.raw);raw['checks'][1]['pass']=False
        self.assertEqual(grading.amended_grade(raw,'H',self.work,self.audit())['status'],'fail')

    def test_manifest_inside_workspace_is_rejected(self):
        path=self.work/'before.json';shutil.copyfile(self.manifest,path)
        with self.assertRaises(ValueError):grading.verify_host_inputs(self.work,path)

    def test_external_manifest_expected_hash_is_enforced(self):
        with self.assertRaises(ValueError):grading.verify_host_inputs(self.work,self.manifest,'0'*64)

    def test_no_skill_condition_cannot_invent_injected_inputs(self):
        before=json.loads(self.manifest.read_text())['before_sha256']
        before={key:value for key,value in before.items() if not key.startswith(grading.PREFIX)}
        self.manifest.write_text(json.dumps({'before_sha256':before}))
        self.assertFalse(self.audit()['verified'])

    def test_supplemental_routes_without_reading_task_or_assertion_text(self):
        import run
        for scenario in ['M','N']:
            for safe in [False,True]:
                argv=['grade_with_trusted_inputs.py','--scenario',scenario,'--workspace',str(self.work),'--before-manifest',str(self.manifest)]
                if safe:argv+=['--safe-grading']
                raw={'scenario':scenario,'status':'pass','checks':[{'id':'synthetic-routing-sentinel','pass':True}],'blockers':[]}
                process={'stdout':json.dumps(raw),'stderr':'','returncode':0,'timed_out':False,'launch_error':None,'cleanup':[]}
                output=io.StringIO()
                with patch.object(sys,'argv',argv),patch.object(run,'run_process',return_value=process) as call,contextlib.redirect_stdout(output),self.assertRaises(SystemExit) as exit:
                    grading.main()
                self.assertEqual(exit.exception.code,0)
                command=call.call_args.args[0]
                expected=str(EVALS/'supplemental/graders/grade.py')
                self.assertEqual(Path(command[1]).name,'grade_with_containment.py')
                self.assertEqual(command[command.index('--legacy-grader')+1],expected)
                self.assertEqual(json.loads(output.getvalue())['scenario'],scenario)

    def test_safe_preflight_runs_before_trusted_reads_or_legacy_process(self):
        import run
        target=self.root/'outside-canary';target.write_text('SYNTHETIC')
        (self.work/'public/escape.js').symlink_to(target)
        argv=['grade_with_trusted_inputs.py','--scenario','H','--workspace',str(self.work),'--before-manifest',str(self.manifest),'--safe-grading']
        output=io.StringIO()
        with patch.object(sys,'argv',argv),patch.object(grading,'verify_host_inputs',side_effect=AssertionError('No submitted reads before preflight')) as verify,patch.object(run,'run_process') as process,contextlib.redirect_stdout(output),self.assertRaises(SystemExit) as exit:
            grading.main()
        self.assertEqual(exit.exception.code,1);verify.assert_not_called();process.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())['status'],'fail')

    def test_native_grading_is_held_before_trust_reads_or_dart_execution(self):
        import run
        argv=['grade_with_trusted_inputs.py','--scenario','C','--workspace',str(self.work),'--before-manifest',str(self.manifest)]
        output=io.StringIO()
        with patch.object(sys,'argv',argv),patch.object(grading,'verify_host_inputs') as verify,patch.object(run,'run_process') as process,contextlib.redirect_stdout(output),self.assertRaises(SystemExit) as exit:
            grading.main()
        self.assertEqual(exit.exception.code,2);verify.assert_not_called();process.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())['status'],'blocked')

    def test_symlink_ancestor_is_rejected_without_reading_target(self):
        shutil.rmtree(self.work/'.agents');target=self.root/'external';target.mkdir()
        (self.work/'.agents').symlink_to(target,target_is_directory=True)
        audit=self.audit();self.assertFalse(audit['verified']);self.assertTrue(audit['issues'])


if __name__=='__main__':unittest.main()
