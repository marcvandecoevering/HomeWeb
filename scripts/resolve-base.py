"""Resolve latest official PHP 8.3 patch and its linux/amd64 registry digest. Fail closed."""
import hashlib
import json
import pathlib
import re
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]

def fetch(url, headers=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=60) as r:
        return r.read()

def docker_digest(repo, tag):
    token = json.loads(fetch(f'https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull'))['token']
    raw = fetch(f'https://registry-1.docker.io/v2/{repo}/manifests/{tag}', {
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json'})
    data = json.loads(raw)
    if 'manifests' in data:
        found = [m['digest'] for m in data['manifests'] if m.get('platform', {}).get('architecture') == 'amd64' and m['platform'].get('os') == 'linux']
        if len(found) != 1:
            raise RuntimeError('Expected exactly one linux/amd64 manifest')
        return found[0]
    return 'sha256:' + hashlib.sha256(raw).hexdigest()

def main():
    policy = json.loads((ROOT / 'security-policy.json').read_text())
    release = json.loads(fetch('https://www.php.net/releases/index.php?json&version=8.3'))
    version = release['version']
    if not re.fullmatch(r'8\.3\.\d+', version):
        raise RuntimeError('Invalid PHP series')
    if tuple(map(int, version.split('.'))) < tuple(map(int, policy['minimum'].split('.'))):
        raise RuntimeError('Upstream PHP version below security minimum')
    tag = f'{version}-apache-bookworm'
    digest = docker_digest('library/php', tag)
    result = {'base_image': f'php:{tag}@{digest}', 'php_version': version, 'platform': 'linux/amd64', 'policy': policy, 'release': release}
    (ROOT / 'artifacts').mkdir(exist_ok=True)
    (ROOT / 'artifacts/base.json').write_text(json.dumps(result, indent=2) + '\n')
    print(result['base_image'])

if __name__ == '__main__':
    main()
