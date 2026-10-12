# Make a Calendar Studio

**A powerful offline calendar designer, scheduling workspace, and print studio for Linux.**

Make a Calendar Studio is an original GTK4/Libadwaita desktop application for monthly and yearly planning, local project notes, business-date arithmetic, retail fiscal periods, recurring pay dates, rotating shifts, and vector calendar exports. The calendar engine and saved projects work locally. Optional web links open only after you choose them.

Created by Ethan, the developer behind [Make a Calendar](https://make-a-calendar.com/). This is independent desktop software inspired by practical date workflows; it does not call or reproduce the website's private implementation.

## Current development release

The 0.1.0 source includes:

- Gregorian month grids, Sunday/Monday starts, adjacent dates, fixed or natural row counts, and a twelve-month view.
- A GTK4/Libadwaita workspace with calendar designer, year planner, print settings, business-day calculator, fiscal period view, payroll/shift planners, date converters, local projects, and optional resource links.
- Observed US federal holiday dates, local business-day arithmetic, Sunday-nearest-February retail year calculations for 4-4-5, 4-5-4, and 5-4-4, anchored payroll dates, and three rotating shift patterns.
- Vector PDF and SVG month exports, CSV/JSON month data, all-day ICS export of saved project events, and an offline CLI.
- SQLite project and event storage under the user's application-data directory.

This is an early development build. The Linux GUI and Snap have not yet been run in this macOS authoring environment. See [the verification record](docs/verification.md) for exactly what has and has not been checked. There is no ICS import, cloud sync, direct printer integration, or multi-month PDF export in 0.1.0.

## Run the command-line tools

Python 3.10 or newer is needed for the core and CLI:

```sh
PYTHONPATH=src python3 -m make_a_calendar_studio.cli calendar 2027 1 --week-start monday
PYTHONPATH=src python3 -m make_a_calendar_studio.cli business-days 2026-10-01 2026-10-31 --holidays
PYTHONPATH=src python3 -m make_a_calendar_studio.cli fiscal 2027 --pattern 4-4-5
PYTHONPATH=src python3 -m make_a_calendar_studio.cli export 2027 1 january.pdf --format pdf
```

For a native desktop development setup on Ubuntu 24.04 or a compatible distribution, install Python, GTK4, Libadwaita, and PyGObject from that distribution's packages, then run:

```sh
PYTHONPATH=src python3 -m make_a_calendar_studio
```

The supported Snap package is intended to bundle the GTK runtime and use strict confinement. The GTK app requires GTK 4, Libadwaita 1, and PyGObject; the pure date engine and CLI use only the Python standard library.

## Build, tests, and Snap

Run core tests with `PYTHONPATH=src python3 -m unittest discover -s tests`. The GitHub Actions workflow runs those tests, linting, CLI/export smoke checks, a Linux GTK startup smoke check, and captures actual Linux desktop screenshots as a workflow artifact.

The separate Snap workflow builds the `core24` package on Ubuntu and retains the `.snap` as a temporary artifact for review. It does not publish to the Store.

Snap packaging targets `core24` with strict confinement and the GNOME extension. The manifest is marked `grade: devel` until a Linux Snap build and GUI run pass. See [Snap publishing notes](docs/snap-publishing.md). Do not promote a revision to stable based on the macOS core tests alone.

## Online calendar resources

The app ships with a small set of contextual links: [monthly calendar pages](https://make-a-calendar.com/monthly-calendars), a [custom year-grid generator](https://make-a-calendar.com/calendar-generator), [business-day calculator](https://make-a-calendar.com/business-days-calculator), [4-4-5 retail calendar](https://make-a-calendar.com/445-calendar), [date tools](https://make-a-calendar.com/date-tools), and the site's [iCalendar generator](https://make-a-calendar.com/ical-generator). The app's own calculations stay offline; the website links are optional references.

The complete route-by-route review, which tools each route describes, and which parts are implemented locally are recorded in [docs/resource-links.md](docs/resource-links.md). The link strategy is contextual rather than a keyword-heavy backlink dump. Desktop links are not counted as crawlable website links.

## Privacy and storage

No account, server, telemetry, background service, or network permission is used by the date engine. Local project data is stored in SQLite under the platform's user-data directory. Opening an Online Resources link hands the selected URL to the operating system's default browser.

## License

MIT. See [LICENSE](LICENSE).
