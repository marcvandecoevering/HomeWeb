# Release maintenance

Source: [marcvandecoevering/HomeWeb](https://github.com/marcvandecoevering/HomeWeb). Images: `ghcr.io/marcvandecoevering/homeweb`. The canonical Unraid template is maintained in [unraid-templates](https://github.com/marcvandecoevering/unraid-templates), with a copy in this repository.

## Release pipeline

1. Run `python scripts/validate.py --release`. Check descriptions, icon, links and the Unraid template.
2. Push to main. GitHub Actions builds, integration-tests and scans a single image. Publication uses the tested archive and does not rebuild it. PR jobs only have read permissions.
3. Inspect the `evidence` artifact: integration results, scan, SBOM, base digest and tested-image metadata. Fixable HIGH/CRITICAL findings block publication.
4. The separate publish job uses GitHub's short-lived `GITHUB_TOKEN` with package-write permission. It rejects stale main commits and older runs. No personal token is required.
5. If the release fingerprint differs, it publishes `latest`, the compatibility alias `php8.5`, and a unique `build-RUN_ID-ATTEMPT-COMMIT` tag. If the content and both channel tags already match, the stable tags stay unchanged and the `publication` artifact records `unchanged`.
6. For a new GHCR package, set package visibility to **Public** and verify an anonymous pull using an empty Docker config directory. Compare its config digest with `tested-image.json`; engine image IDs can differ between storage drivers.
7. Follow the [Unraid test protocol](unraid-test.md) using isolated test folders and a free port.

## Community Applications

Keep `templates/thuisweb.xml` (the legacy filename keeps existing template links working) in sync with the central template repository. Do not submit duplicate source repositories. Validate the canonical template through the [submission portal](https://ca.unraid.net/submit), then check actual search visibility and installation in Unraid Apps. An approved submission is not proof that a catalog build has indexed the app.

Historical ThuisWeb submission and acceptance results are documented in [test results](test-results.md). They do not establish current HomeWeb catalog visibility.

## Ongoing checks

Review failed Actions runs, scheduled-run activity, PHP advisories, pinned actions and the pinned scanner. Scheduled runs can be delayed or disabled by GitHub for inactive public repositories. Update `security-policy.json` when new PHP fixes require it. A failed build or scan leaves the last published image available.

Evidence artifacts last 90 days; tested image archives last 7 days. Archive release evidence separately if longer retention is needed. Branch protection and review rules are account settings; this workflow does not configure them.

On 21 October 2026, GitHub Actions email notifications were set to failed workflows only. Delivery was not tested; check your notification settings and mailbox when a real failure occurs.

References: [Unraid starter repository](https://github.com/unraid/unraid-community-apps-starter), [profile schema](https://ca.unraid.net/submit/help/repository-info-xml), [template schema](https://ca.unraid.net/submit/help/repository-xml).
