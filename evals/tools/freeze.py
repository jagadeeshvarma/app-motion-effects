#!/usr/bin/env python3
"""Freeze once before skill editing. Refuses to rewrite an existing freeze."""
import hashlib,json
from pathlib import Path
base=Path(__file__).resolve().parents[1];target=base/'frozen.json'
if target.exists():raise SystemExit('Freeze already exists. Do not silently change the acceptance criteria.')
paths=[base/'scenarios.json',base/'DESIGN.md']
for name in ['tasks','fixtures','graders','tools']:
 paths += [p for p in (base/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
files={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
aggregate=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
target.write_text(json.dumps({'schema_version':1,'phase':'before-improved-skill-edit','sha256':aggregate,'files':files},indent=2)+'\n')
print(json.dumps({'sha256':aggregate,'files':len(files)}))
