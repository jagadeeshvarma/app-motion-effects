"""Containment regressions use disposable fixtures and synthetic canaries only."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile


SOURCE = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((SOURCE / "scripts/skill-manifest.json").read_text())
VERSION = json.loads((SOURCE / "package.json").read_text())["version"]


class PackageSafety(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="motion-package-test-")
        self.addCleanup(self.temporary.cleanup)
        self.scratch = Path(self.temporary.name)
        self.repo = self.scratch / "repo"
        self.repo.mkdir()
        (self.repo / "scripts").mkdir()
        for name in ("package.py", "validate.mjs", "skill-manifest.json"):
            shutil.copyfile(SOURCE / "scripts" / name, self.repo / "scripts" / name)
        self.skill = self.repo / "skills/app-motion-effects"
        shutil.copytree(SOURCE / "skills/app-motion-effects", self.skill, symlinks=True)
        (self.repo / "package.json").write_text(json.dumps({"version": VERSION}))
        for name in ("LICENSE", "CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md", "THIRD_PARTY_NOTICES.md"):
            (self.repo / name).write_text("Synthetic test fixture.\n")
        self.docs = self.repo / "docs"
        (self.docs / "demos").mkdir(parents=True)
        (self.docs / "index.html").write_text('<script src="demos/interaction.js"></script>')
        (self.docs / "full-repo-prompt.txt").write_text("Synthetic audit prompt.\n")
        (self.repo / "README.md").write_text("```text\nSynthetic audit prompt.\n```\n")
        (self.docs / "demos/interaction.js").write_text("// Synthetic local fixture.\n")
        for name in ("studio", "dispatch"):
            for variant in ("before", "after"):
                (self.docs / f"demos/{name}-{variant}.html").write_text("<title>Synthetic local fixture</title>")
        self.out = self.repo / "dist"
        self.archive = self.out / f"app-motion-effects-{VERSION}.zip"
        self.output_names = (self.archive.name, "integrity.json", "SHA256SUMS")

    def run_tool(self, tool):
        command = [sys.executable, "scripts/package.py"] if tool == "package" else ["node", "scripts/validate.mjs"]
        return subprocess.run(command, cwd=self.repo, capture_output=True, text=True, timeout=15)

    def assert_valid(self):
        for tool in ("structure", "package"):
            result = self.run_tool(tool)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_rejected(self, tools=("structure", "package")):
        self.out.mkdir(exist_ok=True)
        for name in self.output_names:
            (self.out / name).write_bytes(b"SYNTHETIC_PREVIOUS_RELEASE")
        for tool in tools:
            result = self.run_tool(tool)
            self.assertNotEqual(result.returncode, 0, f"{tool} accepted unsafe fixture")
            for name in self.output_names:
                self.assertEqual((self.out / name).read_bytes(), b"SYNTHETIC_PREVIOUS_RELEASE")

    def add_skill_link(self, reference, style="inline"):
        path = self.skill / "README.md"
        link = f"[Synthetic canary]({reference})"
        if style == "reference":
            link = f"[Synthetic canary][canary]\n\n[canary]: {reference}"
        if style == "html":
            link = f"<a href='{reference}'>Synthetic canary</a>"
        path.write_text(path.read_text() + "\n" + link + "\n")

    def test_clean_archive_has_exact_reviewed_bytes_and_integrity(self):
        self.assert_valid()
        expected = set(MANIFEST["files"])
        integrity = json.loads((self.out / "integrity.json").read_text())
        self.assertEqual(set(integrity["files"]), expected)
        with zipfile.ZipFile(self.archive) as bundle:
            self.assertEqual(bundle.namelist(), [f"app-motion-effects/{name}" for name in sorted(expected)])
            for item in bundle.infolist():
                name = item.filename.removeprefix("app-motion-effects/")
                data = bundle.read(item)
                self.assertEqual(data, (self.skill / name).read_bytes())
                self.assertEqual(hashlib.sha256(data).hexdigest(), integrity["files"][name])
                self.assertEqual(item.date_time, (2026, 1, 1, 0, 0, 0))
                self.assertEqual(item.external_attr >> 16, 0o100644)
            empty = self.scratch / "extracted"
            bundle.extractall(empty)
            self.assertEqual({p.relative_to(empty / "app-motion-effects").as_posix() for p in empty.rglob("*") if p.is_file()}, expected)
        for row in (self.out / "SHA256SUMS").read_text().splitlines():
            digest, name = row.split("  ", 1)
            self.assertEqual(digest, hashlib.sha256((self.out / name).read_bytes()).hexdigest())

    def test_packaging_is_reproducible_after_source_mtime_changes(self):
        self.assert_valid()
        original = {name: (self.out / name).read_bytes() for name in self.output_names}
        for name in MANIFEST["files"]:
            os.utime(self.skill / name, (1_700_000_000, 1_700_000_000))
        result = self.run_tool("package")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(original, {name: (self.out / name).read_bytes() for name in self.output_names})

    def test_hidden_configuration_is_rejected_without_replacing_release(self):
        (self.skill / ".env.audit").write_text("AUDIT_TOKEN=SYNTHETIC_ONLY\n")
        self.assert_rejected()

    def test_unexpected_visible_file_is_rejected(self):
        (self.skill / "unexpected.md").write_text("Synthetic only.\n")
        self.assert_rejected()

    def test_unexpected_empty_directory_is_rejected(self):
        (self.skill / "unexpected").mkdir()
        self.assert_rejected()

    def test_missing_approved_file_is_rejected(self):
        (self.skill / "LICENSE").unlink()
        self.assert_rejected()

    def test_external_file_symlink_is_rejected(self):
        canary = self.scratch / "synthetic-canary.txt"
        canary.write_text("SYNTHETIC_EXTERNAL_CANARY\n")
        (self.skill / "README.md").unlink()
        (self.skill / "README.md").symlink_to(canary)
        self.assert_rejected()

    def test_broken_file_symlink_is_rejected(self):
        (self.skill / "README.md").unlink()
        (self.skill / "README.md").symlink_to(self.scratch / "synthetic-missing")
        self.assert_rejected()

    def test_directory_symlink_is_rejected(self):
        (self.skill / "references").rename(self.scratch / "synthetic-references")
        (self.skill / "references").symlink_to(self.scratch / "synthetic-references", target_is_directory=True)
        self.assert_rejected()

    def test_skills_parent_symlink_is_rejected(self):
        (self.repo / "skills").rename(self.scratch / "synthetic-skills")
        (self.repo / "skills").symlink_to(self.scratch / "synthetic-skills", target_is_directory=True)
        self.assert_rejected()

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO test requires POSIX")
    def test_special_file_is_rejected_without_reading_or_hanging(self):
        (self.skill / "README.md").unlink()
        os.mkfifo(self.skill / "README.md")
        self.assert_rejected()

    def test_package_local_link_cannot_use_checkout_file(self):
        self.add_skill_link("../../README.md")
        self.assert_rejected()

    def test_encoded_package_escape_is_rejected(self):
        self.add_skill_link("%2e%2e/%2e%2e/README.md")
        self.assert_rejected()

    def test_reference_style_escape_is_rejected(self):
        self.add_skill_link("../../README.md", "reference")
        self.assert_rejected()

    def test_embedded_html_escape_is_rejected(self):
        self.add_skill_link("../../README.md", "html")
        self.assert_rejected()

    def test_absolute_unix_reference_is_rejected(self):
        self.add_skill_link("/synthetic-canary.txt")
        self.assert_rejected()

    def test_absolute_windows_reference_is_rejected(self):
        self.add_skill_link("C:/synthetic-canary.txt")
        self.assert_rejected()

    def test_file_scheme_reference_is_rejected(self):
        self.add_skill_link("file:///synthetic-canary.txt")
        self.assert_rejected()

    def test_broken_package_reference_is_rejected(self):
        self.add_skill_link("references/synthetic-missing.md")
        self.assert_rejected()

    def test_local_query_and_fragment_reference_remains_valid(self):
        self.add_skill_link("references/verification.md?synthetic=1#section")
        self.assert_valid()

    def test_repository_documentation_cannot_escape_checkout(self):
        (self.scratch / "synthetic-canary.txt").write_text("SYNTHETIC_ONLY\n")
        readme = self.repo / "README.md"
        readme.write_text(readme.read_text() + "\n[Synthetic canary](../synthetic-canary.txt)\n")
        self.assert_rejected(("structure",))

    def test_html_reference_cannot_escape_checkout(self):
        (self.scratch / "synthetic-canary.txt").write_text("SYNTHETIC_ONLY\n")
        (self.docs / "index.html").write_text("<a href='../../synthetic-canary.txt'>Canary</a>")
        self.assert_rejected(("structure",))

    def test_docs_symlink_is_rejected_before_reading(self):
        canary = self.scratch / "synthetic-canary.txt"
        canary.write_text("SYNTHETIC_ONLY\n")
        (self.docs / "synthetic-canary.md").symlink_to(canary)
        self.assert_rejected(("structure",))

    def test_output_directory_symlink_does_not_write_external_target(self):
        external = self.scratch / "synthetic-output"
        external.mkdir()
        self.out.symlink_to(external, target_is_directory=True)
        result = self.run_tool("package")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(external.iterdir()), [])

    def test_output_file_symlink_does_not_overwrite_external_target(self):
        self.out.mkdir()
        canary = self.scratch / "synthetic-output.txt"
        canary.write_text("SYNTHETIC_KEEP\n")
        self.archive.symlink_to(canary)
        result = self.run_tool("package")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(canary.read_text(), "SYNTHETIC_KEEP\n")

    def test_manifest_path_escape_is_rejected(self):
        manifest = dict(MANIFEST, files=MANIFEST["files"] + ["../synthetic-canary.txt"])
        (self.repo / "scripts/skill-manifest.json").write_text(json.dumps(manifest))
        self.assert_rejected()

    def test_duplicate_manifest_path_is_rejected(self):
        manifest = dict(MANIFEST, files=MANIFEST["files"] + [MANIFEST["files"][0]])
        (self.repo / "scripts/skill-manifest.json").write_text(json.dumps(manifest))
        self.assert_rejected()


if __name__ == "__main__":
    unittest.main()
