# Snap packaging and release notes

The project targets `core24`, strict confinement, and the supported GNOME extension for the GTK4 desktop command. The Snap manifest currently has `grade: devel`; promote it to `stable` only after a Linux build, launch, portal file selection, project persistence, and exported PDF/SVG checks pass.

The application stores under the Snap's application data directory. It opens online references in the default browser only on user action, so the application itself does not request a network plug. It does not directly connect to CUPS. The GNOME extension supplies the desktop runtime integration; no broad home plug or classic confinement is requested. GTK 4.10+'s asynchronous `Gtk.FileDialog` provides portal-backed file selection.

## Build and review from Linux

1. Use current supported Snapcraft 9 tooling with the Ubuntu `core24` base.
2. Build for `amd64` and run the strict-confined Snap in a GNOME session.
3. Verify app menu registration, theme handling, GTK `FileDialog` portal behavior, XDG/Snap local storage, CLI output, and PDF/SVG validity.
4. Take authentic screenshots of the installed application in that Linux session. Do not substitute SVG mockups or browser captures.
5. Request `make-a-calendar-studio` in the Karen Cohen Snapcraft account. The request was submitted on 2026-10-12 and the Store indicated manual review may take up to 30 days. The Snap is not yet public.
6. Upload first to `edge` or another development channel, review the Store page and metadata, then move to stable after QA and any Store review.

The repository includes [a GitHub Actions Snap build workflow](../.github/workflows/snap-build.yml) that runs the official `snapcore/action-build` action on Ubuntu 24.04 and retains the `.snap` file as a short-lived build artifact. It does not upload to the Snap Store. It can run after the repository is created and connected; the workflow has not run yet. Canonical documents this action as a GitHub option for Snapcraft builds ([action source](https://github.com/snapcore/action-build), [Snapcraft build environment options](https://ubuntu.com/docs/snapcraft/9/reference/build-environment-options/)).

Current official references:

- [Snapcraft GTK4 app guide](https://ubuntu.com/docs/snapcraft/9/how-to/integrations/craft-a-gtk4-app/)
- [GNOME extension guide](https://ubuntu.com/docs/snapcraft/9/how-to/extensions/use-the-gnome-extension/)
- [Snapcraft publishing guide](https://ubuntu.com/docs/snapcraft/9/how-to/publishing/)
- [Remote build guide](https://ubuntu.com/docs/snapcraft/9/explanation/remote-build/)

The remote builder compiles on Linux through Launchpad. A successful remote build alone does not prove the graphical app launches; a real Linux desktop run remains necessary.

## Present status

Snapcraft is not installed on the current macOS host. The authenticated Snapcraft account identifies the publisher as Karen Cohen (`jwcalendar`) and currently lists two other published snaps. The `make-a-calendar-studio` name request returned to the account overview but is not listed among published snaps; Store approval is not confirmed. A Linux build, upload, Store review, public release, install check, and Store screenshots have not been completed or claimed.
