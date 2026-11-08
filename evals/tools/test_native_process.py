"""No-model regressions; only synthetic processes created by these tests."""
from pathlib import Path
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from native_process import stop_owned_group


@unittest.skipUnless(os.name == 'posix', 'Owned POSIX process groups required')
class OwnedCleanupTests(unittest.TestCase):
    def test_persistent_group_observation_denial_is_reported_as_incomplete(self):
        child = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(60)'], start_new_session=True)
        original = os.killpg
        def denied(pgid, sig):
            if sig == 0:
                raise PermissionError(1, 'synthetic persistent group observation denial')
            return original(pgid, sig)
        try:
            with patch('native_process.os.killpg', side_effect=denied):
                result = stop_owned_group(child, child.pid, term_grace=0.1, kill_grace=0.1)
            self.assertFalse(result['ok'])
            self.assertFalse(result['group_gone'])
            self.assertTrue(result['leader_reaped'])
            self.assertTrue(any('group check:' in error for error in result['errors']))
        finally:
            if child.poll() is None:
                original(child.pid, signal.SIGKILL)
                child.wait(timeout=2)

    def test_transient_group_observation_denial_is_retried_within_bound(self):
        child = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(60)'], start_new_session=True)
        original = os.killpg
        observations = []
        def transient(pgid, sig):
            if sig == 0 and not observations:
                observations.append(True)
                raise PermissionError(1, 'synthetic transient group observation denial')
            return original(pgid, sig)
        try:
            with patch('native_process.os.killpg', side_effect=transient):
                result = stop_owned_group(child, child.pid, term_grace=1, kill_grace=1)
            self.assertTrue(observations)
            self.assertTrue(result['ok'], result)
        finally:
            if child.poll() is None:
                original(child.pid, signal.SIGKILL)
                child.wait(timeout=2)

    def test_term_resistant_child_and_inherited_pipe_are_killed_and_reaped(self):
        with tempfile.TemporaryDirectory(prefix='motion-owned-cleanup-') as folder:
            ready = Path(folder) / 'ready'
            code = "import signal,time,pathlib;signal.signal(signal.SIGTERM,signal.SIG_IGN);pathlib.Path(%r).write_text('SYNTHETIC_READY');print('SYNTHETIC_OUTPUT',flush=True);time.sleep(60)" % str(ready)
            child = subprocess.Popen([sys.executable, '-c', code], start_new_session=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 3
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue(ready.exists())
                start = time.monotonic()
                result = stop_owned_group(child, child.pid, term_grace=0.15, kill_grace=2, drain_grace=1)
                self.assertTrue(result['ok'], result)
                self.assertTrue(result['kill_sent'])
                self.assertEqual(child.returncode, -signal.SIGKILL)
                self.assertLess(time.monotonic() - start, 4)
            finally:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=2)

    def test_term_resistant_descendant_cannot_keep_group_or_pipe_alive(self):
        with tempfile.TemporaryDirectory(prefix='motion-owned-descendant-') as folder:
            ready = Path(folder) / 'ready'
            descendant = "import signal,time,pathlib;signal.signal(signal.SIGTERM,signal.SIG_IGN);pathlib.Path(%r).write_text(str(__import__('os').getpid()));time.sleep(60)" % str(ready)
            code = "import signal,time,subprocess,sys;signal.signal(signal.SIGTERM,signal.SIG_IGN);subprocess.Popen([sys.executable,'-c',%r]);time.sleep(60)" % descendant
            child = subprocess.Popen([sys.executable, '-c', code], start_new_session=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 3
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue(ready.exists())
                result = stop_owned_group(child, child.pid, term_grace=0.15, kill_grace=3, drain_grace=1)
                self.assertTrue(result['ok'], result)
                self.assertTrue(result['kill_sent'])
            finally:
                if child.poll() is None:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=2)

    def test_unowned_group_argument_is_rejected_without_signals(self):
        child = subprocess.Popen([sys.executable, '-c', 'import time;time.sleep(60)'], start_new_session=True)
        try:
            with self.assertRaises(ValueError):
                stop_owned_group(child, child.pid + 1)
            self.assertIsNone(child.poll())
        finally:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=2)


if __name__ == '__main__':
    unittest.main()
