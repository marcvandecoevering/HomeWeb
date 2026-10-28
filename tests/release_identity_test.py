from contextlib import chdir
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from release_identity import LABEL, fingerprint, unchanged

class IdentityTests(unittest.TestCase):
    def test_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('Dockerfile', 'security-policy.json', 'runtime/init.php', 'apache/site.conf', 'landing/index.html'):
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text('original')
            original = fingerprint(root, 'php@sha256:one', 'php 1 amd64\napache 2 amd64')
            (root / 'README.md').write_text('documentation change')
            self.assertEqual(original, fingerprint(root, 'php@sha256:one', 'apache 2 amd64\nphp 1 amd64\n'))
            self.assertNotEqual(original, fingerprint(root, 'php@sha256:two', 'php 1 amd64\napache 2 amd64'))
            self.assertNotEqual(original, fingerprint(root, 'php@sha256:one', 'php 1 amd64\napache 3 amd64'))
            (root / 'runtime/init.php').write_text('changed')
            self.assertNotEqual(original, fingerprint(root, 'php@sha256:one', 'php 1 amd64\napache 2 amd64'))
            self.assertFalse(unchanged({}, original))  # migrate legacy images once
            self.assertFalse(unchanged({LABEL: 'different'}, original))
            self.assertTrue(unchanged({LABEL: original, 'nl.thuisweb.run': 'older'}, original))
            with self.assertRaises(ValueError):
                fingerprint(root, 'base', '')

    def test_publisher_skips_without_login_or_push(self):
        import hashlib
        env = {'GITHUB_REPOSITORY':'owner/ThuisWeb', 'GH_TOKEN':'test', 'GITHUB_ACTOR':'owner',
               'GITHUB_REF':'refs/heads/main', 'GITHUB_EVENT_NAME':'schedule', 'GITHUB_SHA':'revision',
               'GITHUB_RUN_NUMBER':'2', 'GITHUB_RUN_ID':'100', 'GITHUB_RUN_ATTEMPT':'1'}
        cwd = Path.cwd()
        with patch.dict(os.environ, env):
            spec = importlib.util.spec_from_file_location('publish_test', ROOT / 'scripts/publish.py')
            pub = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pub)
        try:
            with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, env), chdir(tmp):
                Path('artifacts').mkdir()
                config = json.dumps({'config':{'Labels':{LABEL:'same'}}}).encode()
                digest = 'sha256:' + hashlib.sha256(config).hexdigest()
                for name in ('image.tar', 'loaded-image.tar'):
                    with tarfile.open('artifacts/'+name, 'w') as archive:
                        for path, data in [('config.json',config),('manifest.json',b'[{"Config":"config.json"}]')]:
                            info = tarfile.TarInfo(path); info.size = len(data)
                            archive.addfile(info, io.BytesIO(data))
                meta = {'revision':'revision','run':2,'attempt':1,'release_fingerprint':'same',
                        'config_digest':digest,'archive_sha256':hashlib.sha256(Path('artifacts/image.tar').read_bytes()).hexdigest()}
                Path('artifacts/tested-image.json').write_text(json.dumps(meta))
                responses = [{'object':{'sha':'revision'}},{'token':'test'},
                             {'config':{'Labels':{LABEL:'same','nl.thuisweb.run':'1','nl.thuisweb.attempt':'1'}}}]
                with patch.object(pub,'get',side_effect=responses), patch.object(pub,'platform_manifest',return_value={'config':{'digest':'previous'}}), patch.object(pub,'command') as command:
                    pub.main()
                    self.assertFalse(any(c.args[:2] in [('docker','push'),('docker','login'),('docker','tag')] for c in command.call_args_list))
                self.assertEqual(json.loads(Path('artifacts/published.json').read_text())['status'],'unchanged')
        finally:
            os.chdir(cwd)

if __name__ == '__main__':
    unittest.main()
