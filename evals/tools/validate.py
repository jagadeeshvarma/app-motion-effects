#!/usr/bin/env python3
"""Dependency-free corpus/schema/freeze checks. Does not run an evaluated model."""
import hashlib,json,py_compile,subprocess,sys,tempfile
from pathlib import Path
base=Path(__file__).resolve().parents[1];data=json.loads((base/'scenarios.json').read_text());cases=data['scenarios']
assert [s['id'] for s in cases]==list('ABCDEFGHIJKL')
assert sum(s['split']=='development' for s in cases)==6
assert sum(s['split']=='validation' for s in cases)==6
assert len(data['conditions'])==3
for case in cases:
 assert (base/case['task']).is_file()
 assert (base/case['fixture']/'AGENTS.md').is_file()
 assert all(case['trigger_cases'].get(kind) for kind in ['positive','negative','ambiguous'])
 app=base/case['fixture']/case['app_root']
 assert app.is_dir()
 assert (app/'index.html').is_file() if case['platform']=='web' else (app/'lib/main.dart').is_file()
 assert case['limits']['network']=='off' and not case['limits']['external_mutations']
 for f in (base/case['fixture']).rglob('*'):assert not f.is_symlink()
with tempfile.TemporaryDirectory() as temp:
 for f in list((base/'graders').glob('*.py'))+list((base/'tools').glob('*.py')):py_compile.compile(str(f),cfile=str(Path(temp)/(f.stem+'.pyc')),doraise=True)
for f in (base/'graders').glob('*.mjs'):subprocess.run(['node','--check',str(f)],check=True,capture_output=True)
amendments=sorted(base.glob('frozen-amendment-*.json'),key=lambda p:int(p.stem.rsplit('-',1)[-1]))
freeze=amendments[-1] if amendments else base/'frozen.json'
if freeze.exists():
 expected=json.loads(freeze.read_text())['files']
 for name,sha in expected.items():assert hashlib.sha256((base/name).read_bytes()).hexdigest()==sha,f'Frozen content drift: {name}'
sys.path.insert(0,str(base))
from frozen_assertions import verify_registry
verify_registry()
print(json.dumps({'status':'pass','scenarios':12,'development':6,'validation':6,'frozen':freeze.exists(),'model_runs':0}))
