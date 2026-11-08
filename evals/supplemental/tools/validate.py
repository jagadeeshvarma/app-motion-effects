#!/usr/bin/env python3
import hashlib,json,py_compile,subprocess,tempfile,sys
from pathlib import Path
base=Path(__file__).resolve().parents[1];data=json.loads((base/'scenarios.json').read_text())
assert [case['id'] for case in data['cases']]==['M','N']
assert data['authoring_phase']=='after-candidate-freeze-before-model-outputs'
assert data['candidate_freeze_sha256']=='ef8a65d8bdfd7f41be3a727d2f9161ccb219ecd4eefc048b74aaa5776baa00ff'
for case in data['cases']:
 assert (base/case['task']).is_file() and (base/case['fixture']/case['app_root']/'index.html').is_file()
 assert case['limits']['model_task_timeout_seconds']==240
 assert set(case['trigger_cases'])=={'positive','negative','ambiguous'}
with tempfile.TemporaryDirectory() as tmp:
 for p in list((base/'tools').glob('*.py'))+list((base/'graders').glob('*.py')):py_compile.compile(str(p),cfile=str(Path(tmp)/(p.name+'c')),doraise=True)
subprocess.run(['node','--check',str(base/'graders/web.mjs')],check=True,capture_output=True)
amendments=sorted(base.glob('frozen-amendment-*.json'),key=lambda p:int(p.stem.rsplit('-',1)[-1]))
manifest=amendments[-1] if amendments else base/'frozen.json'
if manifest.exists():
 for name,sha in json.loads(manifest.read_text())['files'].items():assert hashlib.sha256((base/name).read_bytes()).hexdigest()==sha,name
sys.path.insert(0,str(base.parent))
from frozen_assertions import verify_registry
verify_registry()
print(json.dumps({'status':'pass','ids':['M','N'],'frozen':(base/'frozen.json').exists(),'model_runs':0}))
