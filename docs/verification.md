# Verification record

**Last checked:** 2026-10-12. This records what is actually published and tested; it is not a claim of a stable release.

## Confirmed

- The public source repository is [`makeacalendar/make-a-calendar-studio-linux`](https://github.com/makeacalendar/make-a-calendar-studio-linux).
- GitHub Actions run [38277010585](https://github.com/makeacalendar/make-a-calendar-studio-linux/actions/runs/38277010585) completed successfully. It ran the Linux tests, lint, Python compilation, CLI/export checks, a headless GTK startup, and capture of the real Linux UI.
- The separate Snap build run [38277010553](https://github.com/makeacalendar/make-a-calendar-studio-linux/actions/runs/38277010553) completed and produced an Ubuntu-built `amd64` Snap artifact.
- Snap `make-a-calendar-studio` is public under publisher Karen Cohen (`jwcalendar`). Version `0.1.0`, revision 1 is released on `latest/edge`. Its automated review reported 43 passes, 0 warnings, and 0 failures.
- The Store rejected revision 2. Its package did not match the Snap Store's expected pack checksums and included unusual symlink permissions. Revision 2 is not released and must not be promoted.
- Eight screenshots in `screenshots/` were captured from the real application running in Linux CI. They are not mockups. Five selected screenshots, the icon, and banner are present in the Snapcraft listing editor, but the public gallery is not yet confirmed.
- Twenty-two Make a Calendar routes were reviewed for `docs/resource-links.md`. The public README has 7 clickable links and this public route review has 22, for 29 visible placements across those two pages. This does not guarantee search indexing or ranking.
- A 512×512 store icon and a 1920×640 featured banner have been prepared from the existing icon and a genuine Linux screenshot. The local screenshot set meets the Store's published size rules. The Snapcraft editor preview displays the listing artwork.

## Still pending

- The GitHub `main` branch still has `grade: devel`. The local release manifest is prepared with stable grade and corrected listing metadata. The user accepted the invitation and GitHub is open as `karencohenjw`; the browser editor now offers the normal commit action. A local Git push and new Actions run still need verification.
- Stable has not been released. A new Linux-built stable-grade revision must pass Store review before it can be moved to `latest/stable`.
- The public Snap listing still has the old description and no confirmed media gallery. The editor preview shows the updated copy and real clickable URL anchors for all 15 Make a Calendar resources, plus the icon, featured banner, and five screenshots. The listing save API reports “There was a problem saving listing data”; the public page must be checked after that failure is resolved.
- A clean install and launch of the approved Snap revision on a Linux desktop have not been confirmed.
- The current public README has seven clickable Make a Calendar links. A revised README with 20 links and Snap listing copy with 15 direct clickable URLs are prepared locally, but are not published yet.

## Accurate release claims

The current public channel is `latest/edge`, not stable. The successful Linux GUI smoke check is not the same as verifying a clean install of the Store Snap. A backlink is only counted as published when its clickable link is visible in a public page; the in-app browser links are not public web backlinks.
