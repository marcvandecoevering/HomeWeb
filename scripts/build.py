"""Local and CI build/test/scan entry point. Does not publish anything."""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tarfile
from release_identity import LABEL, fingerprint

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.chdir(ROOT)
OUT = ROOT / 'artifacts'
OUT.mkdir(exist_ok=True)

def command(*args, capture=False):
    p = subprocess.run(args, text=True, check=True, stdout=subprocess.PIPE if capture else None)
    return p.stdout.strip() if capture else None

def main():
    # Never leave an earlier success marker beside a failed new build.
    (OUT/'tested-image.json').unlink(missing_ok=True)
    command(sys.executable, 'scripts/validate.py')
    command(sys.executable, 'tests/release_identity_test.py')
    assert command('docker', 'info', '--format', '{{.OSType}}', capture=True) == 'linux', 'Linux Docker engine required'
    base = command(sys.executable, 'scripts/resolve-base.py', capture=True)
    revision = command('git', 'rev-parse', 'HEAD', capture=True)
    run = os.environ.get('GITHUB_RUN_NUMBER', '0')
    attempt = os.environ.get('GITHUB_RUN_ATTEMPT', '0')
    command('docker', 'build', '--pull', '--no-cache', '--platform', 'linux/amd64', '--build-arg', 'BASE_IMAGE='+base,
            '--build-arg', 'SOURCE_REVISION='+revision,
            '--label', 'org.opencontainers.image.source=https://github.com/'+os.environ.get('GITHUB_REPOSITORY', 'unpublished/homeweb'),
            '--label', 'nl.homeweb.run='+run, '--label', 'nl.homeweb.attempt='+attempt,
            '-t', 'homeweb:test', '.')
    packages = command('docker', 'run', '--rm', '--entrypoint', 'dpkg-query', 'homeweb:test',
                       '-W', '-f=${Package}\t${Version}\t${Architecture}\n', capture=True)
    identity = fingerprint(ROOT, base, packages)
    # Add comparison metadata BEFORE testing; never modify the tested image afterward.
    container = command('docker', 'create', 'homeweb:test', capture=True)
    try:
        command('docker', 'commit', '--change', f'LABEL {LABEL}={identity}', container, 'homeweb:test')
    finally:
        command('docker', 'rm', container)
    image_id = command('docker', 'image', 'inspect', '--format', '{{.Id}}', 'homeweb:test', capture=True)
    version = command('docker', 'run', '--rm', '--entrypoint', 'php', image_id, '/opt/homeweb/check.php', capture=True)
    expected = json.loads((OUT/'base.json').read_text())['php_version']
    assert version == expected, (version, expected)
    command(sys.executable, 'tests/integration.py', image_id)
    command('docker', 'save', '-o', str(OUT/'image.tar'), 'homeweb:test')
    scanner = json.loads((ROOT/'scanner.json').read_text())['trivy_image']
    command('docker', 'pull', '--platform', 'linux/amd64', scanner)
    common = ['docker', 'run', '--rm', '--platform', 'linux/amd64', '--mount', f'type=bind,source={OUT},target=/reports', scanner]
    # A fresh cache and mandatory successful DB download on every scan; never skip DB updates.
    command(*common, 'image', '--input', '/reports/image.tar', '--scanners', 'vuln', '--list-all-pkgs', '--format', 'json', '--output', '/reports/scan.json')
    command(*common, 'image', '--input', '/reports/image.tar', '--format', 'cyclonedx', '--output', '/reports/sbom.cdx.json')
    report = json.loads((OUT/'scan.json').read_text(encoding='utf-8'))
    assert report.get('SchemaVersion') == 2 and report.get('Results'), 'Missing/incomplete scan results'
    assert report.get('Metadata', {}).get('OS', {}).get('Family') == 'debian', 'OS scan missing'
    assert any(r.get('Class') == 'os-pkgs' and r.get('Packages') for r in report['Results']), 'Package inventory missing'
    blocked = [v for r in report['Results'] for v in (r.get('Vulnerabilities') or []) if v.get('Severity') in ('HIGH','CRITICAL') and v.get('FixedVersion')]
    (OUT/'scan-gate.json').write_text(json.dumps({'blocked': blocked, 'passed': not blocked}, indent=2))
    if blocked:
        raise RuntimeError(f'{len(blocked)} fixable HIGH/CRITICAL vulnerabilities; publication blocked')
    with (OUT/'image.tar').open('rb') as f:
        checksum = hashlib.file_digest(f, 'sha256').hexdigest()
    with tarfile.open(OUT/'image.tar') as archive:
        entries = json.load(archive.extractfile('manifest.json'))
        assert len(entries) == 1, 'Expected one platform image in tested archive'
        config_digest = 'sha256:' + hashlib.sha256(archive.extractfile(entries[0]['Config']).read()).hexdigest()
    metadata = {'image_id': image_id, 'config_digest': config_digest, 'archive_sha256': checksum, 'revision': revision, 'php': version,
                'base_image': base, 'release_fingerprint': identity, 'scanner': scanner, 'run': int(run), 'attempt': int(attempt),
                'created': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (OUT/'tested-image.json').write_text(json.dumps(metadata, indent=2)+'\n')
    print('PASS: exact image built, integration-tested, scanned and inventoried:', image_id)

if __name__ == '__main__':
    main()
