#!/usr/bin/env python3
"""Exercise documented copy/refusal/backup semantics in disposable host-shaped roots."""
import hashlib,shlex,shutil,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'skills/app-motion-effects'
def hashes(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
def install(source,destination):
    # Same guarded cp -R mechanism as README, without modifying host discovery paths.
    s,d=map(shlex.quote,[str(source),str(destination)])
    return subprocess.run(['sh','-c',f'test ! -e {d} && test ! -L {d} && cp -R {s} {d}'],capture_output=True)
class InstallSmoke(unittest.TestCase):
    def test_both_documented_host_locations(self):
        for client in ['.agents','.claude']:
            with self.subTest(client=client),tempfile.TemporaryDirectory(prefix='motion-install-') as temp:
                parent=Path(temp)/client/'skills';parent.mkdir(parents=True)
                sibling=parent/'unrelated';sibling.mkdir();(sibling/'keep.txt').write_text('UNRELATED_SYNTHETIC')
                dest=parent/'app-motion-effects'
                self.assertEqual(install(SOURCE,dest).returncode,0)
                self.assertEqual(hashes(dest),hashes(SOURCE))
                before=hashes(dest)
                self.assertNotEqual(install(SOURCE,dest).returncode,0)
                self.assertEqual(hashes(dest),before)
                backup=Path(temp)/'backups'/client/'app-motion-effects';backup.parent.mkdir(parents=True);dest.rename(backup)
                self.assertEqual(install(SOURCE,dest).returncode,0)
                self.assertEqual(hashes(backup),before)
                shutil.rmtree(dest);backup.rename(dest)
                self.assertEqual(hashes(dest),before)
                self.assertEqual((sibling/'keep.txt').read_text(),'UNRELATED_SYNTHETIC')
    def test_dangling_link_is_refused(self):
        with tempfile.TemporaryDirectory(prefix='motion-install-') as temp:
            dest=Path(temp)/'app-motion-effects';dest.symlink_to(Path(temp)/'missing',target_is_directory=True)
            self.assertNotEqual(install(SOURCE,dest).returncode,0)
            self.assertTrue(dest.is_symlink())
            self.assertFalse((Path(temp)/'missing').exists())
if __name__=='__main__':unittest.main()
