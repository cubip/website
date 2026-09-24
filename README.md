# cubip.com

The website for cubip: landing page, terms of use, privacy policy and support.
Plain HTML and one stylesheet. GitHub Pages and the Pages workflow are disabled
until launch; publishing requires a separate decision to enable both. The app
itself lives in the private `cubip/cubip` repository.

## Checks before merging

Pull requests to `main` run short Linux checks: a redacted credential scan of the
fetched Git history, workflow linting, and local page/asset/link validation. No
deployment credentials, caches or published artifacts are used. External URLs
are not fetched. The site currently contains no JavaScript or build dependencies.

Run the site checks locally with Python 3.10 or later:

```sh
python3 scripts/check-site.py
python3 scripts/test-check-site.py
```

The `main` ruleset requires the stable `Ready to merge` GitHub Actions check and
an up-to-date branch, alongside PR and history protections. The check fails when
validation fails, is cancelled, or the pull request is still a draft. Redundant
runs are cancelled when a pull request changes. The owner reviews and squash
merges through GitHub. CODEOWNERS assigns ownership; required approvals stay at
zero while there is only one maintainer, who cannot approve their own PR.

The disabled Pages workflow packages only the public files listed in
`scripts/check-site.py` and its tar command. Keep both lists aligned when adding
new public directories. Repository metadata, scripts and documentation are not
part of the deployment archive. The validator checks HTML structure, image alt
attributes, local links/fragments and CSS delimiters; visual and full CSS
standards review remain part of reviewing changes to the site.
