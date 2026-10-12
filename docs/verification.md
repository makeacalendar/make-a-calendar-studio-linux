# Verification record

**Last checked:** 2026-10-12 (Europe/Istanbul). This records what is published and verified; it does not claim that a stable release is complete.

## Confirmed

- The public source repository is [makeacalendar/make-a-calendar-studio-linux](https://github.com/makeacalendar/make-a-calendar-studio-linux).
- The stable-grade manifest and direct-URL Snap description are committed to `main`. Linux verification run [38287082047](https://github.com/makeacalendar/make-a-calendar-studio-linux/actions/runs/38287082047), for manifest commit `19661393`, completed successfully.
- Snap build run [38287082039](https://github.com/makeacalendar/make-a-calendar-studio-linux/actions/runs/38287082039), for the same stable-grade manifest commit, was still running at the last check. Do not upload a replacement until a successful run provides its Ubuntu-built artifact.
- Snap `make-a-calendar-studio` is public under Karen Cohen (`jwcalendar`). Version `0.1.0`, revision 1, is released on `latest/edge`; its automated review reported 43 passes, no warnings, and no failures. Revision 2 was rejected for checksum and symlink-permission issues and must not be promoted.
- The public README contains 20 clickable Make a Calendar links. The route review in [docs/resource-links.md](resource-links.md) contains 22 more; that is 42 visible placements across these two public pages. They do not guarantee indexing, referral traffic, or ranking.
- The Snap manifest and listing-copy sheet include 15 direct Make a Calendar URLs. Snapcraft preview rendered them as clickable anchors, but the listing save failed. The public Store page still has the old description and no confirmed gallery.
- The 512×512 store icon and 1920×640 featured banner are committed under `assets/`. Five real Linux screenshots were selected in the Snapcraft editor preview; public gallery visibility is unconfirmed.

## Still pending

- The Snap build must finish successfully and expose a fresh Ubuntu-built `.snap` artifact. Upload that artifact through Karen's Snapcraft account, wait for Store review, and release it to `latest/stable` only after approval.
- Retry saving the Snap listing. Verify that the public page shows the 15 clickable resource URLs, icon, banner, and five screenshots.
- Confirm a clean Store install and launch on Linux.

## Accurate release claims

The published channel remains `latest/edge` until the Store confirms a stable release. A successful CI GUI smoke check does not confirm a clean Store install. Count a backlink only when its clickable link is visible on a public web page; links inside the desktop app are user-triggered references, not crawlable backlinks.
