"""No-model structural native-input tests; original C/D fixtures are copied."""
from pathlib import Path
import importlib.util
import shutil
import tempfile
import unittest

MODULE = Path(__file__).with_name('native-runtime.py')
spec = importlib.util.spec_from_file_location('native_runtime_adapter', MODULE)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class NativeInputTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='motion-native-input-')
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / 'app'
        shutil.copytree(adapter.ROOT / 'fixtures/C', self.source)

    def test_only_dart_and_frozen_sdk_contracts_enter_build(self):
        inputs, excluded = adapter.native_inputs(self.source, 'C')
        self.assertEqual(set(inputs), {'lib/main.dart','lib/store.dart','pubspec.yaml','pubspec.lock','analysis_options.yaml'})
        self.assertIn('AGENTS.md', excluded)

    def test_submitted_platform_and_build_hooks_are_excluded_without_execution(self):
        for name in ('android/app/build.gradle.kts','ios/Runner/custom.sh','hook/build.dart'):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('SYNTHETIC_UNTRUSTED_HOOK_DO_NOT_EXECUTE')
        inputs, excluded = adapter.native_inputs(self.source, 'C')
        for name in ('android/app/build.gradle.kts','ios/Runner/custom.sh','hook/build.dart'):
            self.assertNotIn(name, inputs)
            self.assertIn(name, excluded)

    def test_extra_dependency_is_rejected_before_any_build(self):
        path = self.source / 'pubspec.yaml'
        path.write_text(path.read_text() + '\ndependency_overrides:\n  synthetic: {path: ../outside}\n')
        with self.assertRaisesRegex(ValueError, 'frozen SDK-only contract'):
            adapter.native_inputs(self.source, 'C')

    def test_changed_repository_contract_is_rejected(self):
        (self.source / 'lib/store.dart').write_text('SYNTHETIC_CHANGED_CONTRACT')
        with self.assertRaisesRegex(ValueError, 'read-only store contract'):
            adapter.native_inputs(self.source, 'C')

    def test_dart_symlink_is_rejected_without_following_it(self):
        (self.source / 'lib/external.dart').symlink_to(Path(self.temp.name) / 'synthetic-missing.dart')
        with self.assertRaisesRegex(ValueError, 'Linked Dart input'):
            adapter.native_inputs(self.source, 'C')


if __name__ == '__main__':
    unittest.main()
