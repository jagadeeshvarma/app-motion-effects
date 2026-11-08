"""GA03 frontdoor/archive controls; synthetic/metadata checks, no model calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from frozen_assertions import archived_source,verify_registry


class SafeDefaultsTests(unittest.TestCase):
    def test_archives_match_preserved_original_freezes(self):
        self.assertEqual(verify_registry(),2)
        index=json.loads((BASE/'historical_assertions/index.json').read_text())['graders']
        for name,entry in index.items():
            self.assertEqual(hashlib.sha256(archived_source(BASE/name)).hexdigest(),entry['source_sha256'])

    def test_direct_historical_entrypoints_never_run_submitted_code(self):
        for name in ['graders/grade.py','supplemental/graders/grade.py']:
            result=subprocess.run([sys.executable,str(BASE/name),'--scenario','B','--workspace','/not-a-real-submitted-tree'],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,2)
            self.assertEqual(json.loads(result.stdout)['grading_entrypoint'],'GA03-safe-defaults')

    def test_no_cli_disable_or_unsafe_bypass_option(self):
        for name in ['run.py','regrade.py','graders/grade_with_trusted_inputs.py']:
            source=(BASE/name).read_text()
            self.assertNotIn('--no-safe',source);self.assertNotIn('--unsafe',source)


if __name__=='__main__':unittest.main()
