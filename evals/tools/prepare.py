#!/usr/bin/env python3
"""Copy one fixture only; print the hidden task path for the host to read."""
import argparse,json,shutil,hashlib
from pathlib import Path
base=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('scenario',choices=list('ABCDEFGHIJKL'));p.add_argument('destination');args=p.parse_args()
spec=next(s for s in json.loads((base/'scenarios.json').read_text())['scenarios'] if s['id']==args.scenario)
dest=Path(args.destination).resolve()
if dest.exists():raise SystemExit('Refusing to overwrite an existing output workspace.')
shutil.copytree(base/spec['fixture'],dest)
fixture_files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.rglob('*')) if p.is_file()}
fixture_hash=hashlib.sha256(json.dumps(fixture_files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
print(json.dumps({'task_sha256':hashlib.sha256((base/spec['task']).read_bytes()).hexdigest(),'fixture_sha256':fixture_hash,'scenario':args.scenario,'workspace':str(dest),'task_file':str(base/spec['task']),'app_root':spec['app_root'],'platform':spec['platform']}))
