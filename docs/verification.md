# Verification record

This is the development workspace record, not a release certification.

## Completed during this authoring pass

- Confirmed the GitHub connector account is `karencohenjw` / Karen Cohen. `karencohenjw/make-a-calendar-studio-linux` returned 404 and the available GitHub connection does not expose repository creation.
- Confirmed the local host is macOS arm64, not Linux. `snap`, `snapcraft`, Docker, Podman, Multipass, GTK/PyGObject, and pytest were not available on the host at the time of the check.
- Opened Make a Calendar website routes used by the resource manifest on 2026-10-12. The manifest distinguishes online references from local implementations.
- Read current Snapcraft 9 GTK4, GNOME extension, publishing, and remote-build documentation.
- Ran the standard-library core test suite: **15 tests passed** for month grids, observed federal dates, schedules, vector exports, converters, and SQLite project/event persistence.
- Ran compile checks and CLI smoke checks for fiscal periods, business days, and PDF export. The exported file was identified as a valid one-page PDF 1.4 document.
- Submitted the `make-a-calendar-studio` Snap name registration from the authenticated Karen Cohen account. Snapcraft states new name registrations require manual review and public release is unavailable until approval. The overview returned without displaying the requested name among its two already published snaps, so the registration is not treated as approved or published.
- Added an Ubuntu 24.04 GitHub Actions workflow using Snapcraft's official build action. It stores an `.snap` artifact and does not publish to the Store; it cannot run until the GitHub repository exists.

## Not yet verified

- Linux GTK4/Libadwaita application startup and visual layout.
- `snapcraft.yaml` build or strict-confinement behavior.
- Native file-chooser portal operation in a Snap.
- PDF visual clipping/typography in a Linux PDF viewer.
- Real installed-app screenshots.
- GitHub repository creation/publication, workflow status, and public indexing.
- Snap name approval, Linux package build, upload, review, release channel, clean installation, or public listing.
- Any crawlable backlink from GitHub or Snapcraft. The current code has not been published.

Run `PYTHONPATH=src python3 -m unittest discover -s tests` for the local core suite. A passing local suite does not replace Linux desktop or Snap verification.
