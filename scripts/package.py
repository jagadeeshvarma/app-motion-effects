"""Build the installable skill only, with deterministic ZIP metadata and hashes."""
from pathlib import Path
import hashlib
import json
import re
import zipfile
root = Path(__file__).resolve().parents[1]
skill = root / "skills/app-motion-effects"
version = re.search(r'version: "([\d.]+)"', (skill / "SKILL.md").read_text()).group(1)
out = root / "dist"
out.mkdir(exist_ok=True)
archive = out / f"app-motion-effects-{version}.zip"
manifest = {}
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
    for path in sorted(skill.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(skill).as_posix()
        data = path.read_bytes()
        manifest[relative] = hashlib.sha256(data).hexdigest()
        info = zipfile.ZipInfo(f"app-motion-effects/{relative}", (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        bundle.writestr(info, data)
(out / "integrity.json").write_text(json.dumps({"version": version, "files": manifest}, indent=2) + "\n")
(out / "SHA256SUMS").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in [archive, out / "integrity.json"]))
print(f"Packaged {len(manifest)} files in {archive.name}; SHA256SUMS written.")
