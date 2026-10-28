"""Real Docker integration tests, only UUID-named resources are cleaned up.
Run: python tests/integration.py homeweb:test
Requires a Linux Docker engine. No production mounts or ports are used.
"""
import json
import pathlib
import subprocess
import sys
import time
import uuid

IMAGE = sys.argv[1]
PREFIX = 'homeweb-test-' + uuid.uuid4().hex[:12]
containers, volumes, networks = [], [], []
results = []
completed = False

def docker(*args, check=True, input=None):
    p = subprocess.run(['docker', *args], input=input, text=True, capture_output=True)
    if check and p.returncode:
        raise RuntimeError(f'docker {args[:3]} failed: {p.stderr}\n{p.stdout}')
    return p.stdout.strip()

def passed(name):
    results.append(name)
    print('PASS:', name, flush=True)

def volume(suffix):
    name = PREFIX + '-' + suffix
    docker('volume', 'create', name)
    volumes.append(name)
    return name

def run(suffix, *args, image=IMAGE):
    name = PREFIX + '-' + suffix
    containers.append(name)
    docker('run', '-d', '--name', name, '--network', PREFIX, *args, image)
    return name

def exec_(name, *args):
    return docker('exec', name, *args)

def request(name, path='/', *args):
    return exec_(name, 'curl', '-sS', '--max-time', '15', *args, 'http://127.0.0.1:8080' + path)

def write(name, path, data):
    docker('exec', '-i', name, 'sh', '-c', 'cat > "$1"', 'sh', path, input=data)

def ready(name):
    for _ in range(60):
        info = json.loads(docker('inspect', name))[0]
        if info['State'].get('Health', {}).get('Status') == 'healthy':
            return
        if not info['State']['Running']:
            raise RuntimeError(docker('logs', name))
        time.sleep(1)
    raise RuntimeError('Health timeout: ' + docker('logs', name))

def expect_failure(suffix, *args, message):
    name = run(suffix, *args)
    for _ in range(20):
        state = json.loads(docker('inspect', name))[0]['State']
        if not state['Running']:
            assert state['ExitCode'] != 0
            assert message in docker('logs', name) + subprocess.run(['docker','logs',name], capture_output=True, text=True).stderr
            return
        time.sleep(0.5)
    raise AssertionError('Invalid configuration was accepted')

try:
    assert docker('info', '--format', '{{.OSType}}') == 'linux'
    docker('network', 'create', PREFIX); networks.append(PREFIX)
    web, config = volume('web'), volume('config')
    mounts = ('-v', web + ':/var/www/html', '-v', config + ':/config')
    app = run('app', *mounts)
    ready(app)
    assert 'Your web server is ready' in request(app)
    assert exec_(app, 'stat', '-c', '%u:%g', '/var/www/html') == '99:100'
    passed('empty directory landing and ownership')
    status = json.loads(request(app, '/__homeweb/status'))
    assert status['php'] == exec_(app, 'php', '-r', 'echo PHP_VERSION;')
    assert status['apache'] == exec_(app, 'cat', '/opt/homeweb/apache-version')
    assert status['apache'].startswith('2.4.') and status['opcacheEnabled'] is True
    assert set(status) == {'php', 'apache', 'opcache', 'opcacheEnabled', 'build'}
    assert 'Cache-Control: no-store' in request(app, '/__homeweb/status', '-D', '-')
    write(app, '/var/www/html/index.html', '<h1>My website</h1>')
    assert request(app, '/__homeweb/status', '-o', '/dev/null', '-w', '%{http_code}') == '404'
    # cat/strip removes the trailing newline, so restore from the shipped template.
    exec_(app, 'cp', '/opt/homeweb/index.html', '/var/www/html/index.html')
    assert json.loads(request(app, '/__homeweb/status'))['php'] == status['php']
    passed('live landing versions; replaced page disables version endpoint')
    # Legacy mounts retain their files and version opt-in after migration.
    exec_(app, 'mv', '/config/.homeweb-landing.sha256', '/config/.thuisweb-landing.sha256')
    assert json.loads(request(app, '/__thuisweb/status'))['php'] == status['php']
    assert json.loads(request(app, '/__homeweb/status'))['php'] == status['php']
    write(app, '/var/www/html/index.html', 'my-custom-page')
    assert request(app, '/__thuisweb/status', '-o', '/dev/null', '-w', '%{http_code}') == '404'
    exec_(app, 'cp', '/opt/homeweb/index.html', '/var/www/html/index.html')
    passed('legacy landing fingerprint and endpoint preserve version privacy')
    write(app, '/var/www/html/hello.html', 'hello-static')
    write(app, '/var/www/html/index.php', '<?php echo "php-first";')
    assert request(app) == 'php-first'
    assert request(app, '/__homeweb/status', '-o', '/dev/null', '-w', '%{http_code}') == '404'
    assert request(app, '/hello.html') == 'hello-static'
    write(app, '/var/www/html/.htaccess', 'RewriteEngine On\nRewriteRule ^rewritten$ hello.html [L]\n')
    assert request(app, '/rewritten') == 'hello-static'
    passed('HTML, PHP, index preference and rewrite')
    write(app, '/var/www/html/error.php', '<?php trigger_error("homeweb-test-error-sentinel", E_USER_WARNING); echo "safe-response";')
    assert request(app, '/error.php') == 'safe-response'
    logs = subprocess.run(['docker', 'logs', app], capture_output=True, text=True)
    assert 'homeweb-test-error-sentinel' in logs.stdout + logs.stderr
    headers = request(app, '/', '-I')
    assert 'X-Powered-By:' not in headers and 'PHP/' not in headers and 'Apache/' not in headers, headers
    passed('PHP errors logged but hidden; server version headers suppressed')
    write(app, '/var/www/html/session.php', '<?php session_start(); echo $_SESSION["n"] = ($_SESSION["n"] ?? 0) + 1;')
    assert request(app, '/session.php', '-c', '/tmp/cookies') == '1'
    assert request(app, '/session.php', '-b', '/tmp/cookies') == '2'
    passed('sessions across requests')
    write(app, '/var/www/html/progress.php', '<?php echo ini_get("session.upload_progress.enabled") ? "enabled" : "disabled";')
    assert request(app, '/progress.php') == 'disabled'
    write(app, '/var/www/html/identity.php', '<?php echo posix_geteuid().":".posix_getegid();')
    assert request(app, '/identity.php') == '99:100'
    exec_(app, 'mkdir', '/var/www/html/uploads')
    exec_(app, 'chown', '99:100', '/var/www/html/uploads')
    write(app, '/var/www/html/upload.php', '<?php if (($_FILES["file"]["error"] ?? -1) !== UPLOAD_ERR_OK) { http_response_code(413); exit("rejected"); } if(!move_uploaded_file($_FILES["file"]["tmp_name"], __DIR__."/uploads/result")) { http_response_code(500); exit("write failed"); } echo filesize(__DIR__."/uploads/result");')
    exec_(app, 'truncate', '-s', str(32*1024*1024), '/tmp/upload')
    assert request(app, '/upload.php', '-F', 'file=@/tmp/upload') == str(32*1024*1024)
    exec_(app, 'truncate', '-s', str(33*1024*1024), '/tmp/upload')
    assert request(app, '/upload.php', '-F', 'file=@/tmp/upload', '-w', '%{http_code}') == 'rejected413'
    exec_(app, 'truncate', '-s', str(42*1024*1024), '/tmp/upload')
    assert request(app, '/upload.php', '-F', 'file=@/tmp/upload', '-w', '%{http_code}') == 'rejected413'
    passed('worker identity, writable uploads, 32MiB acceptance and oversized rejection')
    version = exec_(app, 'php', '/opt/homeweb/check.php')
    assert version.startswith('8.5.')
    passed('PHP security floor and required extensions including GD features')
    write(app, '/var/www/html/sqlite.php', '<?php $db=new PDO("sqlite::memory:"); echo $db->query("SELECT 42")->fetchColumn();')
    assert request(app, '/sqlite.php') == '42'
    db1 = run('maria', '--network-alias', 'maria', '-e', 'MARIADB_ROOT_PASSWORD=test-only', '-e', 'MARIADB_DATABASE=test', '-e', 'MARIADB_USER=test', '-e', 'MARIADB_PASSWORD=test-only', image='mariadb:11.4')
    db2 = run('postgres', '--network-alias', 'postgres', '-e', 'POSTGRES_PASSWORD=test-only', '-e', 'POSTGRES_USER=test', '-e', 'POSTGRES_DB=test', image='postgres:17')
    write(app, '/var/www/html/db.php', '<?php try { $a=new PDO("mysql:host=maria;dbname=test", "test", "test-only"); $b=new PDO("pgsql:host=postgres;dbname=test", "test", "test-only"); echo $a->query("SELECT 21")->fetchColumn()+$b->query("SELECT 21")->fetchColumn(); } catch(Throwable $e) { http_response_code(503); echo "waiting"; }')
    for _ in range(90):
        if request(app, '/db.php') == '42': break
        time.sleep(1)
    else: raise AssertionError('database connections failed')
    passed('MariaDB, PostgreSQL and SQLite through web PHP')
    before = exec_(app, 'sh', '-c', 'find /var/www/html -type f -exec sha256sum {} + | sort')
    ownership = exec_(app, 'stat', '-c', '%u:%g:%a', '/var/www/html/index.php')
    docker('restart', app); ready(app)
    assert before == exec_(app, 'sh', '-c', 'find /var/www/html -type f -exec sha256sum {} + | sort')
    docker('rm', '-f', app)
    app = run('replacement', *mounts); ready(app)
    assert before == exec_(app, 'sh', '-c', 'find /var/www/html -type f -exec sha256sum {} + | sort')
    assert ownership == exec_(app, 'stat', '-c', '%u:%g:%a', '/var/www/html/index.php')
    passed('restart/replacement preserve contents and existing ownership')
    hidden = volume('hidden')
    docker('run', '--rm', '--entrypoint', 'sh', '-v', hidden+':/var/www/html', IMAGE, '-c', 'echo keep > /var/www/html/.keep')
    second = run('second', '-v', hidden+':/var/www/html', '-e', 'PUID=1234', '-e', 'PGID=1234'); ready(second)
    assert exec_(second, 'ls', '-A', '/var/www/html') == '.keep'
    write(second, '/var/www/html/index.php', '<?php echo posix_geteuid().":".posix_getegid();')
    assert request(second) == '1234:1234'
    assert request(app) == 'php-first'
    passed('hidden files suppress initialization; independent websites and custom IDs')
    assert exec_(app, 'curl', '-fsS', 'http://127.0.0.1:8081/') == 'ready'
    assert request(app, '/.keep', '-o', '/dev/null', '-w', '%{http_code}') in ('403','404')
    assert request(app, '/uploads/', '-o', '/dev/null', '-w', '%{http_code}') == '403'
    probe = subprocess.run(['docker','exec',second,'curl','-fsS','--max-time','3',f'http://{app}:8081/'], capture_output=True)
    assert probe.returncode != 0
    write(app, '/var/www/html/.htaccess', 'InvalidApacheDirective yes')
    assert request(app, '/', '-o', '/dev/null', '-w', '%{http_code}') == '500'
    assert exec_(app, 'curl', '-fsS', 'http://127.0.0.1:8081/') == 'ready'
    passed('internal independent health, external isolation, no listing or dotfiles')
    expect_failure('bad-uid', '-e', 'PUID=0', message='PUID')
    expect_failure('bad-gid', '-e', 'PGID=-1', message='PGID')
    expect_failure('bad-memory', '-e', 'PHP_MEMORY_LIMIT=garbage', message='PHP_MEMORY_LIMIT')
    expect_failure('bad-upload', '-e', 'PHP_UPLOAD_LIMIT=0M', message='PHP_UPLOAD_LIMIT')
    expect_failure('bad-tz', '-e', 'TZ=bad-zone', message='TZ')
    locked = volume('locked')
    docker('run', '--rm', '--entrypoint', 'sh', '-v', locked+':/var/www/html', IMAGE, '-c', 'touch /var/www/html/.keep; chmod 700 /var/www/html')
    expect_failure('locked', '-v', locked+':/var/www/html', message='not readable')
    empty_ro = volume('readonly')
    expect_failure('readonly', '-v', empty_ro+':/var/www/html:ro', message='Read-only')
    passed('invalid environment, inaccessible and read-only directories fail clearly')
    write(app, '/config/php.ini', 'memory_limit=512M\nsession.upload_progress.enabled=1\n')
    docker('restart', app); ready(app)
    assert exec_(app, 'php', '-r', 'echo ini_get("memory_limit");') == '512M'
    exec_(app, 'rm', '/var/www/html/.htaccess')
    assert request(app, '/progress.php') == 'disabled'
    passed('HTTP upload-progress mitigation survives custom php.ini override')
    write(app, '/config/php.ini', 'memory_limit="unterminated\n')
    docker('restart', app)
    for _ in range(20):
        state = json.loads(docker('inspect', app))[0]['State']
        if not state['Running']: break
        time.sleep(0.5)
    assert not state['Running'] and state['ExitCode'] != 0
    passed('custom php.ini override and invalid syntax rejection')
    # Remove only files created by this test, leaving initialization marker intact.
    docker('run', '--rm', '--entrypoint', 'sh', *mounts, IMAGE, '-c', 'find /var/www/html -mindepth 1 -delete; rm /config/php.ini')
    docker('restart', app); ready(app)
    assert exec_(app, 'ls', '-A', '/var/www/html') == ''
    passed('initialization marker prevents landing resurrection')
    exec_(app, 'mv', '/config/.homeweb-initialized', '/config/.thuisweb-initialized')
    docker('restart', app); ready(app)
    assert exec_(app, 'ls', '-A', '/var/www/html') == ''
    passed('legacy initialization marker prevents landing resurrection')
    completed = True
finally:
    pathlib.Path('artifacts').mkdir(exist_ok=True)
    pathlib.Path('artifacts/integration.json').write_text(json.dumps({'image': IMAGE, 'completed': completed, 'passed': results}, indent=2))
    for name in containers:
        logs = subprocess.run(['docker','logs',name], text=True, capture_output=True)
        pathlib.Path(f'artifacts/{name}.log').write_text(logs.stdout + logs.stderr)
        docker('rm', '-f', '-v', name, check=False)
    for name in volumes: docker('volume', 'rm', name, check=False)
    for name in networks: docker('network', 'rm', name, check=False)
