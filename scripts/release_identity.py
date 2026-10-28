"""Stable release identity; deliberately excludes timestamps, commits and run IDs."""
import hashlib
import json

LABEL = 'nl.homeweb.release-fingerprint'

def fingerprint(root, base, packages):
    paths = [root / 'Dockerfile', root / 'security-policy.json']
    for directory in ('runtime', 'apache', 'landing'):
        paths.extend(p for p in (root / directory).rglob('*') if p.is_file())
    sources = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
               for p in sorted(paths)}
    inventory = sorted(line.strip() for line in packages.splitlines() if line.strip())
    if not inventory:
        raise ValueError('Missing package inventory')
    payload = {'schema': 1, 'sources': sources, 'base': base, 'packages': inventory}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

def unchanged(labels, candidate):
    return labels.get(LABEL) == candidate
