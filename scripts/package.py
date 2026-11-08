"""Build only the reviewed skill files; validate all inputs before writing outputs."""

from pathlib import Path, PurePosixPath
import hashlib
import io
import json
import os
import re
import stat
import tempfile
from urllib.parse import unquote
import zipfile


ROOT = Path(__file__).resolve().parents[1]


def fail(message):
    raise ValueError(message)


def approved_files():
    manifest = json.loads((ROOT / "scripts/skill-manifest.json").read_text())
    if manifest.get("name") != "app-motion-effects":
        fail("Unexpected skill manifest name")
    files = manifest.get("files")
    if (not isinstance(files, list) or not files
            or not all(isinstance(name, str) for name in files)
            or len(set(files)) != len(files)):
        fail("The skill manifest must contain a nonempty unique file list")
    for name in files:
        if (not isinstance(name, str) or not name
                or PurePosixPath(name).is_absolute()
                or any(part in ("", ".", "..") for part in name.split("/"))
                or any(character in name for character in "\\:\x00")):
            fail(f"Unsafe manifest path: {name!r}")
    return sorted(files)


def require_directory(path):
    if not stat.S_ISDIR(path.lstat().st_mode):
        fail(f"Expected a real directory, not a symlink/special file: {path.name}")


def read_package(skill, expected):
    require_directory(skill.parent)
    require_directory(skill)
    allowed = set(expected)
    directories = {str(parent) for name in expected
                   for parent in PurePosixPath(name).parents if str(parent) != "."}
    found = set()

    def visit(directory):
        for path in sorted(directory.iterdir()):
            relative = path.relative_to(skill).as_posix()
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                fail(f"Symlinks are not allowed in the skill: {relative}")
            if stat.S_ISDIR(mode):
                if relative not in directories:
                    fail(f"Unexpected skill directory: {relative}")
                visit(path)
            elif stat.S_ISREG(mode):
                if relative not in allowed:
                    fail(f"Unexpected skill file: {relative}")
                found.add(relative)
            else:
                fail(f"Special files are not allowed in the skill: {relative}")

    visit(skill)
    if found != allowed:
        fail(f"Missing skill files: {', '.join(sorted(allowed - found))}")
    return {name: (skill / name).read_bytes() for name in expected}


def local_references(text):
    # Inline/image links, reference-style links and embedded HTML attributes.
    patterns = [
        r'!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))',
        r'^\s{0,3}\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))',
        r'(?:src|href|poster)\s*=\s*["\']([^"\']+)["\']',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE):
            yield next(group for group in match.groups() if group is not None)


def validate_references(skill, files):
    for name, data in files.items():
        if not name.endswith(".md"):
            continue
        for reference in local_references(data.decode("utf-8")):
            if re.match(r"^(?:https?:|mailto:|data:|#)", reference, re.IGNORECASE):
                continue
            local = unquote(re.split(r"[?#]", reference, maxsplit=1)[0], errors="strict")
            if not local or local.startswith("/") or any(c in local for c in "\\:\x00"):
                fail(f"Unsafe local reference in {name}: {reference}")
            target = (skill / name).parent / local
            resolved = target.resolve()
            if not resolved.is_relative_to(skill):
                fail(f"Local reference escapes the skill in {name}: {reference}")
            if not resolved.exists():
                fail(f"Broken local reference in {name}: {reference}")


def build():
    skill = ROOT / "skills/app-motion-effects"
    files = read_package(skill, approved_files())
    validate_references(skill, files)
    version_match = re.search(
        r'^  version: "(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?)"$',
        files["SKILL.md"].decode("utf-8"), re.MULTILINE,
    )
    if not version_match:
        fail("Expected a semantic version in SKILL.md metadata")
    version = version_match.group(1)
    if json.loads((ROOT / "package.json").read_text())["version"] != version:
        fail("package.json and SKILL.md versions differ")
    manifest = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    archive_name = f"app-motion-effects-{version}.zip"
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in files.items():
            info = zipfile.ZipInfo(f"app-motion-effects/{name}", (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            bundle.writestr(info, data, compresslevel=9)
    outputs = {
        archive_name: archive.getvalue(),
        "integrity.json": (json.dumps({"version": version, "files": manifest}, indent=2)
                           + "\n").encode(),
    }
    outputs["SHA256SUMS"] = "".join(
        f"{hashlib.sha256(data).hexdigest()}  {name}\n"
        for name, data in outputs.items()
    ).encode()

    out = ROOT / "dist"
    if out.is_symlink():
        fail("The output directory must not be a symlink")
    out.mkdir(exist_ok=True)
    require_directory(out)
    for name in outputs:
        destination = out / name
        if destination.is_symlink() or (destination.exists() and not destination.is_file()):
            fail(f"Unsafe output path: {name}")
    # Stage every result before replacing any existing release file.
    with tempfile.TemporaryDirectory(prefix=".package-", dir=out) as staging:
        for name, data in outputs.items():
            (Path(staging) / name).write_bytes(data)
        for name in outputs:
            os.replace(Path(staging) / name, out / name)
    print(f"Packaged {len(files)} files in {archive_name}; SHA256SUMS written.")


if __name__ == "__main__":
    try:
        build()
    except (ValueError, OSError, KeyError, UnicodeError) as error:
        raise SystemExit(f"Packaging failed: {error}") from error
