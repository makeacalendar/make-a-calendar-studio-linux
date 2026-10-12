# Snap packaging and release notes

## Package

The Snap uses the `core24` base, strict confinement, and the GNOME extension for the GTK4 desktop app. The calendar engine and saved projects work offline; optional Make a Calendar links open only when selected. The package declares its icon, homepage, source repository, support contact, issue tracker, MIT license, and product description.

The stable-grade manifest, expanded README, store artwork, and release documentation are committed to the public GitHub `main` branch under Karen Cohen (`karencohenjw`). Commit `1966139` changed the Snap description to use direct URLs because custom Markdown labels were not clickable in Snapcraft preview. Verify the resulting Actions run and artifact before uploading a new Snap.

## Verified Store state

- Public page: [Make a Calendar Studio on the Snap Store](https://snapcraft.io/make-a-calendar-studio)
- Publisher: Karen Cohen (`jwcalendar`)
- Current release: `0.1.0`, revision 1, `latest/edge`
- Revision 1 automated review: 43 passes, no warnings, no failures
- Revision 2 was rejected because the repacked archive had mismatched checksums and unusual symlink permissions. Do not release that revision.

An uploaded Snap revision must pass Store review before release. Stable should only be reported after the Store confirms the `latest/stable` channel.

## Store listing content and media

The manifest and standalone [listing-copy sheet](store-listing-copy.md) contain a descriptive summary, feature-focused copy, source/support/issue links, and 15 direct Make a Calendar URLs. The editor preview rendered all 15 URLs as clickable anchors. The icon, featured banner, and five authentic Linux screenshots were selected in the editor. Saving the listing returned “There was a problem saving listing data”; the public page still shows the old description and no confirmed gallery. Treat the preview as unsaved until the public page verifies it.

Prepared media:

- `assets/make-a-calendar-studio-store-icon.png` — 512×512 store icon
- `assets/make-a-calendar-studio-featured.png` — 1920×640 featured banner
- `screenshots/01-overview.png` — overview and quick actions
- `screenshots/02-calendar-designer.png` — calendar designer
- `screenshots/03-year-planner.png` — year planner
- `screenshots/04-print-studio.png` — print and export settings
- `screenshots/05-fiscal-studio.png` — fiscal periods
- `screenshots/06-payroll-shifts.png` — payroll and shift planning
- `screenshots/07-date-tools.png` — date converters
- `screenshots/08-online-resources.png` — optional web resources

The editor gallery accepts up to five screenshots; the selected shots are genuine Linux captures. Public gallery visibility remains unconfirmed because the listing save failed.

## Next release sequence

1. Verify that the current GitHub Snap workflow passes and provides a new `.snap` artifact.
2. Upload that Ubuntu-built artifact through Karen's authenticated Snapcraft account. Do not use a manually repacked package.
3. Confirm Store review, then release the approved revision to `latest/stable` and verify the channel status.
4. Retry saving the Snap listing. Verify the new clickable description, icon, banner, and five screenshots on the public page.
5. Confirm a clean Linux Store install and launch, then record the result here.
