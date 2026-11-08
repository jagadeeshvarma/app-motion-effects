#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
base=Path(__file__).resolve().parents[1];target=base/'frozen.json'
if target.exists():raise SystemExit('Supplemental corpus already frozen; do not rewrite criteria.')
paths=[p for p in base.rglob('*') if p.is_file() and p!=target and '__pycache__' not in p.parts]
files={str(p.relative_to(base)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
sha=hashlib.sha256(json.dumps(files,sort_keys=True,separators=(',',':')).encode()).hexdigest()
target.write_text(json.dumps({'schema_version':1,'phase':'after-candidate-freeze-before-supplemental-outputs','candidate_freeze_sha256':'ef8a65d8bdfd7f41be3a727d2f9161ccb219ecd4eefc048b74aaa5776baa00ff','sha256':sha,'files':files},indent=2)+'\n')
print(json.dumps({'sha256':sha,'files':len(files),'ids':['M','N']}))
