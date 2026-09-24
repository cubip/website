# cubip.com

The unpublished website for cubip: culture and sharing, terms of use, privacy,
support and provider identification. Plain HTML, one stylesheet and locally served
fonts; no scripts, trackers, external fonts or booking integration.

GitHub Pages and the publishing workflow are disabled until launch. A review of
legal wording, the operator postal address, actual retention settings and the App
Store destination is required before deliberately enabling publication.

The app lives in the private `cubip/cubip` repository. Its release documentation
records the matching privacy and product contracts. Preview locally with
`python3 -m http.server 8766 --bind 127.0.0.1`; check the landing and legal pages at
mobile and desktop widths. Local fonts retain their SIL Open Font License.

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
