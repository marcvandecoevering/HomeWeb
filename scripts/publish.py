"""Publish only the tested artifact. Runs in an isolated main-branch CI job."""
import base64
import hashlib
import json
import os
import pathlib
import subprocess
import tarfile
import urllib.error
import urllib.parse
import urllib.request
from release_identity import LABEL, unchanged

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
repository = os.environ['GITHUB_REPOSITORY'].lower()
name = repository.split('/')[0] + '/homeweb'
image = 'ghcr.io/' + name
token = os.environ['GH_TOKEN']
actor = os.environ['GITHUB_ACTOR']

def command(*args, capture=False, input=None):
    p = subprocess.run(args, check=True, text=True, input=input, stdout=subprocess.PIPE if capture else None)
    return p.stdout.strip() if capture else None

def get(url, headers):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
        return json.load(r)

def platform_manifest(ref, headers):
    result = get(f'https://ghcr.io/v2/{name}/manifests/{ref}', headers)
    if 'manifests' in result:
        matches = [m for m in result['manifests'] if m.get('platform', {}).get('os') == 'linux' and m['platform'].get('architecture') == 'amd64']
        assert len(matches) == 1, 'Expected exactly one amd64 image'
        return platform_manifest(matches[0]['digest'], headers)
    return result

def main():
    assert os.environ['GITHUB_REF'] == 'refs/heads/main'
    assert os.environ['GITHUB_EVENT_NAME'] in ('push','schedule','workflow_dispatch')
    command('python', 'scripts/validate.py', '--release')
    meta = json.loads(pathlib.Path('artifacts/tested-image.json').read_text())
    assert meta['revision'] == os.environ['GITHUB_SHA']
    assert meta['run'] == int(os.environ['GITHUB_RUN_NUMBER'])
    head = get(f'https://api.github.com/repos/{repository}/git/ref/heads/main', {'Authorization':'Bearer '+token})['object']['sha']
    if head != meta['revision']:
        raise RuntimeError('Main has advanced; refusing stale release')
    auth = base64.b64encode(f'{actor}:{token}'.encode()).decode()
    registry_token = get('https://ghcr.io/token?'+urllib.parse.urlencode({'service':'ghcr.io','scope':f'repository:{name}:pull,push'}), {'Authorization':'Basic '+auth})['token']
    headers = {'Authorization':'Bearer '+registry_token, 'Accept':'application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.list.v2+json, application/vnd.oci.image.manifest.v1+json, application/vnd.docker.distribution.manifest.v2+json'}
    try:
        previous = platform_manifest('php8.5', headers)
    except urllib.error.HTTPError as error:
        if error.code != 404: raise
        previous = None
    labels = {}
    if previous:
        config = get(f'https://ghcr.io/v2/{name}/blobs/'+previous['config']['digest'], headers)
        labels = config['config']['Labels']
        old = (int(labels['nl.homeweb.run']), int(labels['nl.homeweb.attempt']))
        if old >= (meta['run'], meta['attempt']):
            raise RuntimeError('A same or newer release is already published')
    with pathlib.Path('artifacts/image.tar').open('rb') as f:
        assert hashlib.file_digest(f,'sha256').hexdigest() == meta['archive_sha256']
    command('docker', 'load', '-i', 'artifacts/image.tar')
    # Docker's classic and containerd stores report different .Id formats.
    # Verify the portable config digest, including rootfs layer diffIDs.
    command('docker', 'save', '-o', 'artifacts/loaded-image.tar', 'homeweb:test')
    with tarfile.open('artifacts/loaded-image.tar') as archive:
        entries = json.load(archive.extractfile('manifest.json'))
        assert len(entries) == 1
        digest = 'sha256:' + hashlib.sha256(archive.extractfile(entries[0]['Config']).read()).hexdigest()
        assert digest == meta['config_digest']
        tested_config = json.load(archive.extractfile(entries[0]['Config']))
        assert tested_config['config']['Labels'][LABEL] == meta['release_fingerprint']
    pathlib.Path('artifacts/loaded-image.tar').unlink()
    try:
        latest = platform_manifest('latest', headers)
    except urllib.error.HTTPError as error:
        if error.code != 404: raise
        latest = None
    if unchanged(labels, meta['release_fingerprint']) and latest and latest['config']['digest'] == previous['config']['digest']:
        pathlib.Path('artifacts/published.json').write_text(json.dumps({
            'status': 'unchanged', 'stable': image+':latest',
            'release_fingerprint': meta['release_fingerprint'],
            'retained_config_digest': previous['config']['digest'],
        }, indent=2))
        print('UNCHANGED: application, base image and packages match; no tags pushed')
        return
    unique = f"{image}:build-{os.environ['GITHUB_RUN_ID']}-{os.environ['GITHUB_RUN_ATTEMPT']}-{meta['revision'][:12]}"
    # Never overwrite a unique tag, including after a partially successful rerun.
    try:
        get(f'https://ghcr.io/v2/{name}/manifests/'+unique.split(':')[-1], headers)
    except urllib.error.HTTPError as error:
        if error.code != 404: raise
    else:
        raise RuntimeError('Unique build tag already exists')
    command('docker','login','ghcr.io','-u',actor,'--password-stdin',input=token)
    try:
        command('docker','tag','homeweb:test',unique)
        command('docker','push',unique)
        manifest = platform_manifest(unique.split(':')[-1], headers)
        assert manifest['config']['digest'] == meta['config_digest']
        command('docker','tag','homeweb:test',image+':php8.5')
        command('docker','push',image+':php8.5')
        stable = platform_manifest('php8.5', headers)
        assert stable['config']['digest'] == meta['config_digest']
        command('docker','tag','homeweb:test',image+':latest')
        command('docker','push',image+':latest')
        latest = platform_manifest('latest', headers)
        assert latest['config']['digest'] == meta['config_digest']
        pathlib.Path('artifacts/published.json').write_text(json.dumps({'unique':unique,'stable':image+':latest','aliases':[image+':php8.5'],'image_id':meta['image_id']},indent=2))
    finally:
        command('docker','logout','ghcr.io')

if __name__ == '__main__': main()
