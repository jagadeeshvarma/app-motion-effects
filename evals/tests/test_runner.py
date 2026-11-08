"""Runner regression tests. Fake CLI scripts only; no model/network calls."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import tomllib
import unittest
from unittest.mock import patch

EVALS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EVALS))
import run
import discovery


FAKE_CODEX = '''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
if '--version' in sys.argv:
 print('fake-codex-test-1');raise SystemExit()
if 'app-server' in sys.argv:
 for line in sys.stdin:
  message=json.loads(line)
  if message.get('method')=='initialize':
   sys.stdout.write(json.dumps({'id':1,'result':{}})+'\\n'+json.dumps({'method':'notice'})+'\\n');sys.stdout.flush()
  if message.get('method')=='skills/list':
   print(json.dumps({'id':2,'result':{'data':[{'skills':[],'errors':['test-error'] if os.getenv('FAKE_REGISTRY_ERROR') else []}]}}),flush=True);break
 raise SystemExit()
if 'exec' in sys.argv:
 Path('fake-model-invoked').write_text(sys.stdin.read())
 print(json.dumps({'type':'turn.completed','usage':{'input_tokens':7,'output_tokens':3}}))
 raise SystemExit()
raise SystemExit(3)
'''


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='motion-runner-unit-')
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'; self.bin.mkdir()
        executable = self.bin / 'codex'; executable.write_text(FAKE_CODEX); executable.chmod(0o755)
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ['PATH'])

    def tearDown(self):
        self.temp.cleanup()

    def test_config_is_valid_toml_and_only_reviewed_native_keys(self):
        args = run.config(self.root/'skill', {'PATH':'/tmp/quoted " path','PUB_CACHE':'/tmp/cache'}, native_profile=True)
        values = tomllib.loads('\n'.join(args[1::2]))
        self.assertEqual(values['shell_environment_policy']['set']['PUB_CACHE'],'/tmp/cache')
        self.assertEqual(values['default_permissions'],'motion-native')
        self.assertNotIn('sandbox_mode',values)
        self.assertEqual(values['permissions']['motion-native']['network']['domains'],{'localhost':'allow','127.0.0.1':'allow','::1':'allow'})
        self.assertTrue(values['permissions']['motion-native']['network']['allow_local_binding'])
        with self.assertRaises(ValueError):run.config(None,{'HOME':'/tmp/forbidden'})

    def test_metrics_count_interrupted_items_and_do_not_invent_usage(self):
        lines = [
            {'type':'item.started','item':{'id':'one','type':'command_execution'}},
            {'type':'item.completed','item':{'id':'one','type':'command_execution'}},
            {'type':'item.started','item':{'id':'two','type':'mcp_tool_call'}},
            {'type':'turn.completed','usage':{'input_tokens':10,'output_tokens':3}},
            {'type':'turn.completed','usage':{'input_tokens':20,'cached_input_tokens':4,'output_tokens':7}},
        ]
        result = run.events_and_metrics('\n'.join(json.dumps(line) for line in lines))
        self.assertEqual(result['tool_calls'],1);self.assertEqual(result['tool_calls_incomplete'],1)
        self.assertEqual(result['usage_totals'],{'input_tokens':30,'output_tokens':10,'cached_input_tokens':4})
        self.assertIsNone(run.events_and_metrics('')['usage_totals'])

    def test_file_change_events_are_separate_from_command_tool_metric(self):
        events=[{'type':'item.started','item':{'id':'edit-1','type':'file_change'}},{'type':'item.completed','item':{'id':'edit-1','type':'file_change','status':'completed','changes':[{'path':'example.js','kind':'update'}]}},{'type':'item.started','item':{'id':'edit-2','type':'file_change'}},{'type':'item.completed','item':{'id':'edit-3','type':'file_change','status':'failed'}},{'type':'item.completed','item':None}]
        result=run.events_and_metrics('\n'.join(json.dumps(event) for event in events))
        self.assertEqual(result['tool_calls'],0);self.assertEqual(result['command_mcp_search_items_completed'],0)
        self.assertEqual(result['file_change_items_observed'],3);self.assertEqual(result['file_change_items_completed'],2)
        self.assertEqual(result['file_change_items_failed'],1);self.assertEqual(result['file_change_items_incomplete'],1)
        self.assertEqual(result['malformed_event_lines'],1)

    def test_malformed_optional_event_fields_do_not_crash_metrics(self):
        events=[{'type':'turn.completed','item':None,'usage':{'input_tokens':1}},{'type':'item.completed','item':{'id':{'bad':True},'type':'file_change','status':[]}}]
        result=run.events_and_metrics('\n'.join(json.dumps(event) for event in events))
        self.assertTrue(result['turn_completed']);self.assertEqual(result['file_change_items_completed'],1)

    def test_native_model_scheduling_is_held_without_grading_containment(self):
        out=self.root/'native-held';out.mkdir()
        with patch.object(run,'command') as command,patch.object(run,'corpus_metadata',return_value={}),contextlib.redirect_stdout(io.StringIO()):
            result=run.run_case({'id':'C'},'no-skill',3,out,None,240)
        command.assert_not_called();self.assertEqual(result['agent_status'],'SETUP_FAILED')
        self.assertIn('grading',result['runner_error'])

    def test_original_cache_is_compared_even_with_matching_archive_marker(self):
        import tarfile,io
        archive=io.BytesIO()
        with tarfile.open(fileobj=archive,mode='w') as tar:
            payload=b'Trusted version two skill content'
            info=tarfile.TarInfo('skills/app-motion-effects/SKILL.md');info.size=len(payload);tar.addfile(info,io.BytesIO(payload))
        out=self.root/'original-check';out.mkdir()
        with patch.object(run.subprocess,'check_output',return_value=archive.getvalue()):
            target=run.original_snapshot(out)
            self.assertTrue((out/'original/archive.sha256').exists())
            (target/'SKILL.md').write_text('Tampered after the marker was written')
            with self.assertRaises(ValueError):run.original_snapshot(out)
            (target/'SKILL.md').write_bytes(payload)
            (target/'.git').mkdir();(target/'.git/config').write_text('Unexpected cached input')
            with self.assertRaises(ValueError):run.original_snapshot(out)

    def test_exit_zero_without_completed_turn_is_incomplete(self):
        process={'returncode':0,'timed_out':False,'launch_error':None}
        self.assertEqual(run.process_status(process,run.events_and_metrics('')),'INCOMPLETE')
        process['timed_out']=True
        self.assertEqual(run.process_status(process,run.events_and_metrics('')),'TIMED_OUT')

    def test_timeout_is_bounded_and_captured(self):
        started=time.monotonic()
        result=run.run_process([sys.executable,'-c','import time;print("before",flush=True);time.sleep(20)'],timeout=.15)
        self.assertTrue(result['timed_out'])
        self.assertLess(time.monotonic()-started,3)

    def test_completed_process_output_is_captured(self):
        result=run.run_process([sys.executable,'-c','print("captured",flush=True)'],timeout=5)
        self.assertFalse(result['timed_out']);self.assertEqual(result['returncode'],0)
        self.assertIn('captured',result['stdout'])

    def test_launch_error_is_data_not_uncaught_exception(self):
        result=run.run_process([str(self.root/'missing-command')])
        self.assertIsNotNone(result['launch_error']);self.assertIsNone(result['returncode'])

    def test_catalogue_probe_handles_multiple_buffered_lines(self):
        result=discovery.probe_registry(self.root,config_args=[],env=self.env,timeout=3)
        self.assertEqual(result['status'],'PASS');self.assertEqual(result['model_calls'],0)
        self.assertEqual(result['enabled_count'],0)

    def test_catalogue_errors_fail_closed(self):
        result=discovery.probe_registry(self.root,config_args=[],env=dict(self.env,FAKE_REGISTRY_ERROR='1'),timeout=3)
        self.assertEqual(result['status'],'FAIL');self.assertEqual(result['registry_error_count'],1)

    def test_native_proof_must_match_profile_seed_and_all_checks(self):
        seed=self.root/'seed';seed.mkdir();(seed/'seed-manifest.json').write_text('{}')
        import hashlib
        proof={'status':'pass','profile_sha256':run.native_profile_sha256(),'seed_manifest_sha256':hashlib.sha256(b'{}').hexdigest(),'environment_helper_sha256':hashlib.sha256((run.BASE/'tools/native-environment.py').read_bytes()).hexdigest(),'checks':{key:True for key in run.NATIVE_READINESS_CHECKS},**run.NATIVE_PROOF_CONTRACT}
        path=self.root/'proof.json';path.write_text(json.dumps(proof))
        self.assertEqual(run.check_native_readiness(seed,path)['profile_sha256'],run.native_profile_sha256())
        proof['checks']['loopback_bind']=False;path.write_text(json.dumps(proof))
        with self.assertRaises(ValueError):run.check_native_readiness(seed,path)

    def test_native_proof_rejects_old_masked_placement_and_missing_zsh_contract(self):
        seed=self.root/'seed';seed.mkdir();(seed/'seed-manifest.json').write_text('{}')
        import hashlib
        proof={'status':'pass','profile_sha256':run.native_profile_sha256(),'seed_manifest_sha256':hashlib.sha256(b'{}').hexdigest(),'environment_helper_sha256':hashlib.sha256((run.BASE/'tools/native-environment.py').read_bytes()).hexdigest(),'checks':{key:True for key in run.NATIVE_READINESS_CHECKS},**run.NATIVE_PROOF_CONTRACT}
        proof['environment_placement']='private-tmp';path=self.root/'proof.json';path.write_text(json.dumps(proof))
        with self.assertRaises(ValueError):run.check_native_readiness(seed,path)
        proof['environment_placement']='default-system-temp';proof['environment_key_count']=7;path.write_text(json.dumps(proof))
        with self.assertRaises(ValueError):run.check_native_readiness(seed,path)

    def test_actual_native_environment_requires_whole_parent_and_owned_zsh(self):
        parent=self.root/'native';(parent/'config/zsh').mkdir(parents=True)
        for name in ['.zprofile','.zlogin']:(parent/'config/zsh'/name).write_text('export PATH=synthetic')
        values={'PATH':str(parent/'flutter-sdk/bin')+os.pathsep+str(parent/'flutter-sdk/bin/cache/dart-sdk/bin')+os.pathsep+'/usr/bin','TMPDIR':str(parent),'PUB_CACHE':str(parent/'pub-cache'),'FLUTTER_ROOT':str(parent/'flutter-sdk'),'XDG_CONFIG_HOME':str(parent/'config'),'ZDOTDIR':str(parent/'config/zsh'),'FLUTTER_SUPPRESS_ANALYTICS':'true','DART_SUPPRESS_ANALYTICS':'true','ANALYZER_STATE_LOCATION_OVERRIDE':str(parent/'config/analyzer-state')}
        self.assertEqual(run.validate_native_environment(parent,values),values)
        values['TMPDIR']=str(parent/'tmp')
        with self.assertRaises(ValueError):run.validate_native_environment(parent,values)
        values['TMPDIR']=str(parent);values.pop('ZDOTDIR')
        with self.assertRaises(ValueError):run.validate_native_environment(parent,values)

    def test_setup_failure_still_writes_result(self):
        out=self.root/'out';out.mkdir()
        with patch.object(run,'command',side_effect=RuntimeError('synthetic setup failure')),patch.object(run,'corpus_metadata',return_value={}),contextlib.redirect_stdout(io.StringIO()):
            result=run.run_case({'id':'A'},'no-skill',1,out,None,1)
        self.assertEqual(result['agent_status'],'SETUP_FAILED')
        self.assertTrue(next(out.glob('*/result.json')).exists())
        self.assertIn('synthetic setup failure',result['runner_error'])

    def fake_run(self, *, trigger_kind='positive', grader_timeout=False, registry_status='PASS', trusted_input_grading=True):
        out=self.root/('out-'+trigger_kind);out.mkdir()
        actual_process=run.run_process
        def process(argv,**kwargs):
            if any(Path(str(arg)).name in {'grade.py','grade_with_trusted_inputs.py'} for arg in argv):
                if grader_timeout:return dict(stdout='',stderr='',returncode=-15,timed_out=True,launch_error=None,elapsed_seconds=.1)
                return dict(stdout=json.dumps({'status':'pass','checks':[]}),stderr='',returncode=0,timed_out=False,launch_error=None,elapsed_seconds=.1)
            return actual_process(argv,**kwargs)
        with patch.object(run,'base_environment',return_value=self.env),patch.object(run,'run_process',side_effect=process),patch.object(discovery,'probe_registry',return_value={'status':registry_status}),contextlib.redirect_stdout(io.StringIO()):
            result=run.run_case({'id':'A','trigger_cases':{'negative':'Translate this label only'}},'no-skill',1,out,None,2,trigger_kind=trigger_kind,trusted_input_grading=trusted_input_grading)
        self.addCleanup(__import__('shutil').rmtree,Path(result['workspace']).parent)
        return result

    def test_fake_cli_full_positive_flow_records_completion_not_acceptance(self):
        result=self.fake_run()
        self.assertEqual(result['agent_status'],'COMPLETED');self.assertEqual(result['grader']['status'],'pass')
        self.assertEqual(result['usage_totals'],{'input_tokens':7,'output_tokens':3})
        self.assertFalse(result['explicit_skill_invocation'])
        self.assertTrue((Path(result['workspace'])/'fake-model-invoked').exists())

    def test_trigger_task_never_receives_primary_functional_grader(self):
        result=self.fake_run(trigger_kind='negative')
        self.assertEqual(result['grader']['status'],'not-run');self.assertIsNone(result['grader_exit'])
        self.assertEqual((Path(result['workspace'])/'fake-model-invoked').read_text(),'Translate this label only')

    def test_grader_timeout_is_recorded_without_losing_model_result(self):
        result=self.fake_run(grader_timeout=True)
        self.assertEqual(result['agent_status'],'COMPLETED');self.assertEqual(result['grader']['status'],'blocked')
        self.assertTrue(result['grader']['runner_timeout'])

    def test_opt_in_companion_records_trusted_manifest_outside_workspace(self):
        result=self.fake_run(trusted_input_grading=True)
        self.assertTrue(result['trusted_input_grading']);self.assertIn('trusted_before_manifest_sha256',result)
        out=self.root/'out-positive';manifest=next(out.glob('*/before-manifest.json'))
        self.assertFalse(manifest.is_relative_to(Path(result['workspace'])))
        self.assertEqual(json.loads(manifest.read_text())['before_sha256'],result['before_sha256'])

    def test_registry_mismatch_prevents_model_call(self):
        result=self.fake_run(registry_status='FAIL')
        self.assertEqual(result['agent_status'],'REGISTRY_BLOCKED')
        self.assertFalse((Path(result['workspace'])/'fake-model-invoked').exists())

    def test_tree_hash_does_not_follow_external_symlink(self):
        tree=self.root/'tree';tree.mkdir();(tree/'regular').write_text('x')
        (tree/'link').symlink_to('/not-a-real-evaluation-path')
        self.assertEqual(run.digest_tree(tree)['link'],'symlink:/not-a-real-evaluation-path')


if __name__=='__main__':unittest.main()
