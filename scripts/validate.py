"""Offline validation. --release additionally refuses unresolved publication fields."""
import ast
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parents[1]
for path in root.rglob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
for path in [root / 'templates/thuisweb.xml', root / 'ca_profile.xml', root / 'assets/icon.svg']:
    ET.parse(path)
    if '--release' in sys.argv and 'REPLACE_' in path.read_text():
        raise SystemExit(f'Unresolved publication field: {path}')
t = ET.parse(root / 'templates/thuisweb.xml').getroot()
assert t.findtext('Network') == 'bridge'
assert t.findtext('Privileged') == 'false'
assert t.findtext('WebUI') == 'http://[IP]:[PORT:8080]'
assert t.findtext('Repository').endswith(':php8.5')
assert {e.attrib['Target'] for e in t.findall('Config')} >= {'8080', '/var/www/html', '/config', 'PUID', 'PGID', 'PHP_MEMORY_LIMIT', 'PHP_UPLOAD_LIMIT', 'TZ'}
policy = json.loads((root / 'security-policy.json').read_text())
assert policy['series'] == '8.5'
workflow = (root / '.github/workflows/release.yml').read_text()
for action in re.findall(r'uses:\s*([^\s]+)', workflow):
    assert re.fullmatch(r'[^@]+@[a-f0-9]{40}', action), action
assert 'pull_request_target' not in workflow
for path in [p for p in (root / 'runtime').rglob('*') if p.is_file()] + [root / 'Dockerfile']:
    assert b'\r' not in path.read_bytes(), f'CRLF in {path}'
print('PASS: Python syntax, XML structure, workflow action pins, security policy, LF line endings')
