#!/usr/bin/env python3
import argparse,hashlib,json,shutil
from pathlib import Path
base=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('scenario',choices=['M','N']);p.add_argument('destination');args=p.parse_args()
spec=next(case for case in json.loads((base/'scenarios.json').read_text())['cases'] if case['id']==args.scenario);dest=Path(args.destination).resolve()
if dest.exists():raise SystemExit('Refusing to overwrite an existing workspace')
shutil.copytree(base/spec['fixture'],dest)
files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.rglob('*')) if p.is_file()}
print(json.dumps({'scenario':args.scenario,'workspace':str(dest),'task_file':str(base/spec['task']),'app_root':spec['app_root'],'platform':spec['platform'],'task_sha256':hashlib.sha256((base/spec['task']).read_bytes()).hexdigest(),'fixture_sha256':hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()}))
