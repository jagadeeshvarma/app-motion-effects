"""GA03: authenticated frozen assertion data, available only through guarded loaders."""
import gzip
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
INDEX=BASE/'historical_assertions/index.json'


def _hash(data):return hashlib.sha256(data).hexdigest()


def archived_source(path):
    path=Path(path).resolve()
    try:key=path.relative_to(BASE).as_posix()
    except ValueError:return None
    item=json.loads(INDEX.read_text())['graders'].get(key)
    if item is None:return None
    archive=(BASE/item['archive']).resolve()
    if not archive.is_relative_to(BASE) or archive.is_symlink():raise ValueError('Assertion archive path is invalid')
    packed=archive.read_bytes()
    if _hash(packed)!=item['archive_sha256']:raise ValueError('Assertion archive container changed')
    data=gzip.decompress(packed)
    if _hash(data)!=item['source_sha256']:raise ValueError('Frozen assertion source changed')
    manifest=BASE/item['frozen_manifest']
    raw=manifest.read_bytes()
    if _hash(raw)!=item['frozen_manifest_sha256'] or json.loads(raw)['files'][item['frozen_key']]!=item['source_sha256']:
        raise ValueError('Assertion archive differs from preserved original freeze')
    return data


def source_sha256(path):
    source=archived_source(path)
    return _hash(source if source is not None else Path(path).read_bytes())


def verify_registry():
    entries=json.loads(INDEX.read_text())['graders']
    for name,item in entries.items():
        if archived_source(BASE/name) is None:raise ValueError('Missing registered assertion archive')
        if _hash((BASE/name).read_bytes())!=item['entrypoint_sha256']:raise ValueError('Historical entrypoint wrapper changed')
    return len(entries)
