# Test results

## Historical ThuisWeb results — 21 October 2026

These results describe the earlier **ThuisWeb / PHP 8.3** releases, not the HomeWeb PHP 8.5 migration. Exact historical names, versions and digests are retained for traceability. Current releases have their own evidence artifacts in [GitHub Actions](https://github.com/marcvandecoevering/HomeWeb/actions).

### Starter page and live status

The green W logo introduced on this date was later replaced by the house-and-cloud logo. The starter page refreshed Apache/PHP/OPcache versions, actual OPcache state and source build every 30 seconds. The local container reported Apache 2.4.68 and PHP/OPcache 8.3.36. All 14 integration groups passed, including version reporting and disabling the endpoint after replacing the page or adding index.php. The JSON response contained exactly five fields.

Desktop and narrow layouts were visually checked. Disabled OPcache appeared amber; an unavailable status response appeared red and cleared stale versions. Existing website files were preserved.

### Initial local acceptance

The image was built on Docker Desktop, Linux/amd64. The initial 13 integration groups passed; exact digests and test names are in [local-validation.json](local-validation.json).

Coverage included empty/existing/hidden website files, HTML/PHP priority, rewrite, hidden PHP errors with logging, sessions, 32 MiB uploads and oversized request rejection, required extensions and GD features, MariaDB/PostgreSQL/SQLite, worker IDs and writable uploads, restart/replacement preservation, independent sites, isolated healthchecks, invalid environment settings, inaccessible/read-only folders, custom php.ini and initialization markers.

An initial test found Apache did not reliably drop privileges without a passwd entry for a numeric UID. Startup now creates missing user/group entries without modifying existing website files. Repeated HTTP tests verified workers running as 99:100 and 1234:1234.

Python, shell, XML and Actionlint checks passed. The page was checked on desktop and at 390px width without horizontal overflow.

### Historical vulnerability scan

Trivy 0.76.1 scanned the final image using a freshly downloaded database. It reported **0 fixable HIGH/CRITICAL findings**. Findings without available fixes remained:

| Severity | Package findings |
| --- | ---: |
| Critical | 7 |
| High | 319 |
| Medium | 1381 |
| Low | 616 |
| Unknown | 4 |

These are package findings, not unique CVEs or proven reachable attack paths. Passing the publication gate is not a security guarantee. PHP 8.3.36 and required extensions were verified independently. The two first public CI releases each reported 7 Critical, 314 High, 1389 Medium, 613 Low and 4 Unknown package findings, again with no fixable HIGH/CRITICAL findings. Consult each release's own scan and SBOM.

### First public release and Unraid tests

[Actions run 39663665343](https://github.com/marcvandecoevering/HomeWeb/actions/runs/39663665343) passed all 13 integration groups and the scan gate, then published the exact tested image. Anonymous GHCR download succeeded.

- Source commit: `6bedcfc71a0021895d636afe39ae707074f9e631`.
- Unique tag: `build-39663665343-1-6bedcfc71a00`.
- Registry digest: `sha256:df99023e89a90a1ef918b5468a554328c64a897c4c8d45d59995dead6f7e6659`.
- Config digest: `sha256:09a098325529cc170884ea86bfcb568ade48d41c2412ca4f3963b28c9980a7d9`.
- PHP: 8.3.36; same base digest as local acceptance.

XML-template installation succeeded on Unraid 7.3.3 with separate test folders and ports 18583/18584. WebUI opened the starter page. A custom PHP page verified PHP 8.3.36, worker 99:100 and upload-directory writes. Restart preserved checksums, ownership and hidden files. A second container independently served HTML. Production folders and existing containers were untouched.

The Community Applications scanner found a valid downloadable Docker app without template warnings. This scan alone did not establish catalog publication.

### Update and rollback

[Release 2](https://github.com/marcvandecoevering/HomeWeb/actions/runs/39665014043) passed the same checks. The test container was replaced through Unraid from release 1 to 2 and back to 1. Checksums, ownership, permissions, PHP writes and the second site were preserved. Both used PHP 8.3.36 and passed the scan gate; this does not establish that any arbitrary older image is safe. See [Unraid test details](unraid-test.md).

### Historical Community Applications submission

Submitted on 21 October 2026. At 21:55:10 Europe/Amsterdam the portal showed `auto_approved` and the note "Auto-approved for Docker apps (non-duplicated)." Repository display name: `marccoef's Repository`.

The portal said visibility would follow the next catalog build, but the immediate Unraid Apps check found no matching app and the portal showed zero visible apps. Catalog installation was therefore unverified; direct XML installation was tested. Current catalog status must be checked separately. The templates have since moved to [unraid-templates](https://github.com/marcvandecoevering/unraid-templates).

Limitations: Linux/amd64 only; sessions are not persistent across container replacement by default; no bundled database, TLS or administration panel; trusted custom php.ini can override defaults.
