# Unraid acceptance protocol

Use isolated test folders, a demonstrably free port and a separate container name. Never point a test at production website folders or a production database.

## Checks for a new release

| Check | Evidence |
| --- | --- |
| Install using the final template | Image digest, selected test port and separate www/config paths |
| WebUI | Opens the starter page from the Unraid container menu |
| HTML/PHP and writes | Actual PHP version, worker PUID/PGID, upload-directory write result |
| Logs and health | Healthy; internal 8081 returns ready and is not published |
| Restart | Checksums, hidden files, ownership and permissions preserved |
| Image replacement | Different image digest, same mounts and preserved data |
| Safe rollback | Only to an independently checked, still-safe previous release |
| Independent second website | Different name, port, www and config |
| Community Apps listing | Search visibility and installation from the actual catalog entry |

Run the full Docker integration suite for rewrite, sessions, upload limits, database connections, invalid configuration and privacy of the version endpoint. Do not represent those checks as separately repeated on Unraid unless they were.

## Historical acceptance — 21 October 2026

ThuisWeb PHP 8.3 baseline installation, update and rollback passed on Unraid 7.3.3 / Linux amd64 at 192.168.1.10. These results do not constitute HomeWeb PHP 8.5 acceptance.

Test containers were `ThuisWeb-acceptatie` and `ThuisWeb-acceptatie-twee`, using ports 18583/18584 and separate www/config folders under `/mnt/user/appdata/thuisweb-acceptatie-20261021/site1` and `site2`.

Template installation, WebUI, custom HTML/PHP, worker 99:100, writable uploads, logs, health, restart preservation, image replacement, rollback and the second independent site all passed. Rewrite and multipart-upload tests passed locally and in CI; they were not separately repeated on Unraid.

Tested config digests:

- Release 1, run 39663665343: `sha256:09a098325529cc170884ea86bfcb568ade48d41c2412ca4f3963b28c9980a7d9`.
- Release 2, run 39665014043: `sha256:0abfa01bc15de2b337e61685e2fb636e1e685a6ab17918319c0dd97f6ed24e3c`.

Update/rollback replaced the container through Unraid using different digests and the same test mounts. Both releases used PHP 8.3.36. Checksums, permissions, test backups and logs were saved in the test folder. At test completion, site 1 ran release 2 and displayed the starter page; its PHP probe was saved outside the webroot as `site1-test-index.php`. Site 2 displayed separate HTML. Autostart was disabled. These are historical observations, not a statement about currently running containers.

## Testing an existing application

An optional migration test for the separate vehicle-check website on port 8582 was not performed. A read-only inspection identified MySQL/PDO and external curl dependencies.

Before any application migration, record the old image, mounts, environment, network, PHP/extensions and database, write, cron or SMTP dependencies. Keep secrets out of Git and reports. Copy the website and database consistently into separate test resources. Change copied database configuration before starting and prevent real email, payments or other external side effects. Keep original containers, traffic routes and files unchanged during testing. Remove only identified test resources afterward.
