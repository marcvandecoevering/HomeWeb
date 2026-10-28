# HomeWeb user guide

HomeWeb runs one Apache/PHP website per container. It supports HTML, CSS, JavaScript, PHP, `.htaccess`, URL rewriting, sessions, uploads and PHP database connections. Install databases separately. It does not include a file manager, mail server, Node.js/Python hosting, automatic WordPress installation or TLS certificates.

## Unraid settings

Installation through **Apps** fills in the settings automatically. For manual installation through **Docker → Add Container**, follow the [exact field-by-field tables](../README.md#install-on-unraid), including every Port, Path and Variable entry.

Host ports and paths refer to your Unraid server and may be changed. Container port `8080`, container paths `/var/www/html` and `/config`, and environment variable keys must remain exactly as documented. A display name such as **PHP memory limit** is a label, not a key: its **Key** is `PHP_MEMORY_LIMIT` and its default **Value** is `256M`.

The image is `ghcr.io/marcvandecoevering/homeweb:php8.5`, with **Bridge** networking and **Privileged Off**. In Advanced View, enter `http://[IP]:[PORT:8080]` literally in **WebUI**; Unraid substitutes the address and host port. Do not enter arrows, backticks or quotation marks in any field.

Open WebUI after installation. Replace `index.html` or add `index.php`, which takes priority. Only a completely empty website directory receives a starter page; hidden files also count. Existing files and ownership are preserved.

For a second website, choose a different container name, free host port, website folder **and** configuration folder. Configure external access, DNS and HTTPS separately through your reverse proxy.

## Starter page status

The starter page reads Apache, PHP, OPcache and the source build every 30 seconds. Green indicates a responding component or enabled OPcache; amber indicates disabled OPcache. An unavailable status response does not prove that a service is down. Versions are cleared when a request fails.

The version endpoint only works while the original starter page is intact and no `index.php` exists. Your own website does not expose this diagnostic endpoint. The check does not test internet access or your database.

Updates preserve existing pages. See [migration](migration.md) to deliberately replace an old starter page.

## Permissions and configuration

Initialization and the Apache master run as root. Apache workers process web requests as the positive, non-root numeric PUID/PGID. Privileged mode, host networking and a Docker socket are unnecessary. New empty web directories receive the selected ownership; existing files are never recursively chowned. Existing directories must allow reading and traversal. Grant write access only to folders that need it, such as uploads.

`PHP_MEMORY_LIMIT` and `PHP_UPLOAD_LIMIT` accept positive integer sizes in M or G. `post_max_size` adds at least 8 MiB or 10% multipart overhead. Memory must cover that total. For a 32M upload limit, post_max_size is 40M. Applications must handle `UPLOAD_ERR_INI_SIZE` and empty POST/FILES for oversized requests.

An optional `/config/php.ini` is trusted administrator configuration copied on every restart. It can override defaults, including memory, upload and security settings. Syntax errors, unknown directives and PHP startup warnings prevent startup. Restart after changes; remove the file to restore defaults. PHP 8.5 already includes OPcache: remove any `zend_extension=opcache` or `zend_extension=opcache.so` line from old configuration.

Session upload progress is disabled for HTTP requests using an Apache administrator setting, following the [PHP advisory of 23 October 2026](https://www.php.net/archive/2026.php). Normal file uploads still work. A custom php.ini cannot re-enable this HTTP feature.

`/config/.homeweb-initialized` prevents the starter page from reappearing after all website files are removed. The older `.thuisweb-initialized` marker is also respected. Back up hidden files and use a separate config folder for each website. Sessions live inside the container and are lost on replacement unless you configure persistent session storage.

## Logs and health

In Unraid, open **Docker → HomeWeb → Logs**. Apache requests and server/PHP errors go to container logs. PHP errors are hidden from visitors by default. Directory listing and version headers are disabled. `.htaccess` supports rewrite, authentication and access rules, but cannot enable directory listing.

The healthcheck uses `127.0.0.1:8081` inside the container; do not publish this port. Its independent static virtual host does not use website files or `.htaccess`. Healthy means Apache responds, not that your website or database works. PHP and required extensions are checked separately at startup.

For permission errors, check mount paths, PUID/PGID and parent directory permissions. For PHP configuration errors, fix or rename php.ini and restart. Ensure the configuration mount's container path is exactly `/config`, including the leading slash.

## Updates, backups and recovery

1. Record the current image digest or unique build tag and container settings.
2. Stop the website briefly for a consistent backup. Copy `www` and `config`, including hidden files, permissions and ownership. Back up any database using its native dump/snapshot method.
3. Restart, install the update and check WebUI, logs, health and important website functions.
4. Test restores with separate folders and a free port. Restore website and database to a consistent state.
5. Roll back only to a still-safe release. If no safe rollback exists, take the site offline until a repaired image is available.

Publishing an image to GHCR does not install it on Unraid. You control installation through Unraid or your chosen updater. HomeWeb does not change router settings or update other containers.

## Build and security maintenance

With Git, Python 3.11+ and a Linux/amd64 Docker engine, run from this repository:

```powershell
python scripts/validate.py
python scripts/build.py
```

The resolver selects the newest official PHP 8.5 patch and pins its platform digest. It refuses versions below the reviewed security minimum, currently 8.5.12. It never switches PHP series automatically. PHP 8.5 receives upstream security support through 31 December 2029; see [supported versions](https://www.php.net/supported-versions.php).

The pipeline builds once, tests that image, exports it, scans it and creates an SBOM. Tests use UUID-named containers, volumes and networks without host ports or production mounts, then clean up their own resources. After an interrupted test, inspect resources with the `homeweb-test-` prefix before removing them; avoid a global Docker prune.

GitHub Actions runs daily, on main pushes, on pull requests and manually. Only successful main runs may publish. Fixable HIGH/CRITICAL findings, an unavailable scanner database or incomplete results block publication. Findings without available fixes remain in the report. Passing a scan is not a guarantee of security.

## When does an update appear?

A daily run still builds, tests and scans. It publishes only when the application files, Dockerfile, security policy, base image digest or installed package versions differ. Documentation, template changes, build numbers and a new scan alone do not trigger a new image.

If the release fingerprint is unchanged, the existing `php8.5` tag and build tags remain untouched; the `publication` artifact says `unchanged`. This does not change your Unraid automatic-update settings.

Actions are pinned to commits and the scanner to an image digest. Evidence and SBOM artifacts are retained for 90 days, image archives for 7 days. See [release maintenance](publishing.md) and the [Unraid test protocol](unraid-test.md).
