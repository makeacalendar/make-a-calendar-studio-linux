# Snap packaging and release notes

## Package

The Snap uses the `core24` base, strict confinement, and the GNOME extension for the GTK4 desktop app. The calendar engine and stored projects work offline; optional Make a Calendar links open only when selected. The package declares the store icon, homepage, source repository, support contact, issue tracker, MIT license, and product description.

The stable-grade manifest and complete listing copy are prepared locally. The user accepted the GitHub invitation and is signed in to the browser as `karencohenjw`; the repository editor now offers the normal commit action. The local Git push has not yet been confirmed, so the public `main` branch is still the source of truth until a push and Actions run are verified. Do not release the old development-grade revision to stable.

## Verified Store state

- Public page: [Make a Calendar Studio on the Snap Store](https://snapcraft.io/make-a-calendar-studio)
- Publisher: Karen Cohen (`jwcalendar`)
- Current release: `0.1.0`, revision 1, `latest/edge`
- Automated review: 43 passes, no warnings, no failures
- Revision 2: rejected because the repacked archive had mismatched checksums and unusual symlink permissions; do not release it

The successful GitHub Linux CI and Snap build artifacts are recorded in [the verification report](verification.md). An uploaded Snap revision must be reviewed by the Store before release. Stable should only be reported after the Store confirms the stable channel.

## Store listing content

The local Snap manifest has a concise summary, a feature-focused description with Make a Calendar links, an icon, and homepage/source/support/issue links. The standalone [listing-copy sheet](store-listing-copy.md) contains every field. In Snapcraft's preview, custom Markdown link labels displayed literally, so the listing copy now uses descriptive list labels followed by direct URLs; all 15 URLs appeared as real clickable anchors in the preview. The editor also shows the icon, featured banner, and five selected Linux screenshots. However, the listing API returned “There was a problem saving listing data” during save. The public listing still shows the older description and does not show the prepared gallery. Treat the preview as unsaved until the public page confirms the new copy and media.

Prepared store media:

- `assets/make-a-calendar-studio-store-icon.png` — 512×512 PNG logo
- `assets/make-a-calendar-studio-featured.png` — 1920×640 featured banner
- `screenshots/01-overview.png` — overview and quick actions
- `screenshots/02-calendar-designer.png` — calendar design workspace
- `screenshots/03-year-planner.png` — annual planning view
- `screenshots/04-print-studio.png` — print and export settings
- `screenshots/05-fiscal-studio.png` — retail fiscal periods
- `screenshots/06-payroll-shifts.png` — payroll and shift schedules
- `screenshots/07-date-tools.png` — date converters
- `screenshots/08-online-resources.png` — optional Make a Calendar links

The icon and featured banner are separate listing fields. The gallery allows up to five media items; the editor currently contains five genuine Linux screenshots from the set above. The screenshots are real application captures, not generated UI. Public visibility remains unconfirmed because the listing save failed.

## Next release sequence

1. Commit and push the prepared source and listing changes using the authenticated Karen account; verify the new GitHub commit and Actions run.
2. Wait for GitHub Actions to pass and produce a new Linux `.snap` artifact.
3. Upload that build artifact through the authenticated Karen Snapcraft account. Do not use a manually repacked Snap.
4. Confirm the new revision is approved, then release it to `latest/stable` and verify the Store's channel status.
5. Resolve the listing API save failure. Verify the icon, banner, five screenshots, and clickable description links on the public listing page.
6. Test a clean Store install on Linux and record the result here.
