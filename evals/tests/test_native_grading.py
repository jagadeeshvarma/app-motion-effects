"""Fail-closed native grading policy tests; no model, SDK or sandbox subprocess."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

EVALS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(EVALS))
import native_grading
spec=importlib.util.spec_from_file_location('native_guarded_grading',EVALS/'graders/grade_with_containment.py')
grading=importlib.util.module_from_spec(spec);spec.loader.exec_module(grading)


class NativeGradingTests(unittest.TestCase):
    def test_policy_denies_root_general_tmp_and_submitted_source(self):
        values=native_grading.profile_values(Path('/synthetic/owned'),Path('/synthetic/submitted'))
        fs=values['permissions.motion-native-grading.filesystem']
        self.assertEqual(fs[':root'],'deny')
        self.assertEqual(fs[':slash_tmp'],'deny')
        self.assertEqual(fs[':minimal'],'read')
        self.assertEqual(fs['/synthetic/owned'],'write')
        self.assertEqual(fs['/synthetic/submitted'],'deny')
        self.assertNotIn('permissions.motion-native-grading.extends',values)
        self.assertEqual(values['permissions.motion-native-grading.network.domains'],{'localhost':'allow','127.0.0.1':'allow','::1':'allow'})
        self.assertTrue(values['features.network_proxy'])

    def test_missing_proof_and_explicit_hold_fail_closed(self):
        with self.assertRaises(ValueError): native_grading.check_readiness(None)
        with self.assertRaisesRegex(ValueError,'remains BLOCKED'):
            native_grading.check_readiness('not-opened-while-hold-active.json')

    def test_native_guard_blocks_before_legacy_execution_without_proof(self):
        with tempfile.TemporaryDirectory(prefix='motion-native-grade-unit-')as temp:
            work=Path(temp)/'app';work.mkdir()
            with patch.object(grading.runpy,'run_path',side_effect=AssertionError('legacy ran')):
                with self.assertRaises(ValueError):grading.execute_legacy(Path(temp)/'grade.py',[],work,native_scenario=True)

    def test_flutter_transport_preserves_arguments_and_uses_reviewed_environment(self):
        with tempfile.TemporaryDirectory(prefix='motion-native-grade-unit-')as temp:
            root=Path(temp);work=root/'app';work.mkdir();legacy=root/'grade.py'
            legacy.write_text("import subprocess,json\nsubprocess.run(['flutter','test','--reporter','json','test/evaluation_test.dart'],cwd='owned-copy',capture_output=True,text=True,timeout=120)\nprint(json.dumps({'status':'pass','checks':[]}))\n")
            calls=[]
            def transport(command,cwd,env,proof_path,**kwargs):
                self.assertEqual(command,['flutter','test','--reporter','json','test/evaluation_test.dart'])
                self.assertEqual(kwargs['submitted_workspace'],work)
                return ['codex','sandbox','--',*command],{'SYNTHETIC_REVIEWED_ENV':'only'},{'root_read_policy':'deny'}
            with patch.object(native_grading,'check_readiness',return_value={'status':'pass'}),patch.object(native_grading,'sandbox_command',side_effect=transport),patch.object(subprocess,'run',side_effect=lambda command,*args,**kwargs:calls.append((command,kwargs))):
                result=grading.execute_legacy(legacy,[],work,native_scenario=True,native_readiness='synthetic-proof.json')
            self.assertEqual(calls[0][0],['codex','sandbox','--','flutter','test','--reporter','json','test/evaluation_test.dart'])
            self.assertEqual(calls[0][1]['env'],{'SYNTHETIC_REVIEWED_ENV':'only'})
            self.assertEqual(calls[0][1]['timeout'],120)
            self.assertEqual(result['grading_containment']['transport_redirects'],['flutter-least-privilege-sandbox'])
            self.assertFalse(result['grading_containment']['frozen_assertions_changed'])


if __name__=='__main__':unittest.main()
