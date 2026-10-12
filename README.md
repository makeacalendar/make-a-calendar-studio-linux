# Make a Calendar Studio

**A powerful offline calendar designer, scheduling workspace, and print studio for Linux.**

Make a Calendar Studio is an original GTK4/Libadwaita desktop application for monthly and yearly planning, local project notes, business-date arithmetic, retail fiscal periods, recurring pay dates, rotating shifts, and vector calendar exports. The calendar engine and saved projects work locally. Optional web links open only after you choose them.

Created by Ethan, the developer behind [Make a Calendar](https://make-a-calendar.com/). This is independent desktop software inspired by practical date workflows; it does not call or reproduce the website's private implementation.

## Version 0.1.0

The 0.1.0 source includes:

- Gregorian month grids, Sunday/Monday starts, adjacent dates, fixed or natural row counts, and a twelve-month view.
- A GTK4/Libadwaita workspace with calendar designer, year planner, print settings, business-day calculator, fiscal period view, payroll/shift planners, date converters, local projects, and optional resource links.
- Observed US federal holiday dates, local business-day arithmetic, Sunday-nearest-February retail year calculations for 4-4-5, 4-5-4, and 5-4-4, anchored payroll dates, and three rotating shift patterns.
- Vector PDF and SVG month exports, CSV/JSON month data, all-day ICS export of saved project events, and an offline CLI.
- SQLite project and event storage under the user's application-data directory.

Version 0.1.0 is published on the Snap Store's `latest/edge` channel. GitHub Actions has run the Linux tests, lint, CLI/export checks, GTK startup check, and authentic Linux screenshot capture. Stable is not yet published: a new stable-grade Store revision still needs a successful build and Store approval. See [the verification record](docs/verification.md) for the exact status. There is no ICS import, cloud sync, direct printer integration, or multi-month PDF export in 0.1.0.

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

The supported Snap package bundles the GTK runtime and uses strict confinement. The GTK app requires GTK 4, Libadwaita 1, and PyGObject; the pure date engine and CLI use only the Python standard library.

## Build, tests, and Snap

Run core tests with `PYTHONPATH=src python3 -m unittest discover -s tests`. The GitHub Actions workflow runs those tests, linting, CLI/export smoke checks, a Linux GTK startup smoke check, and captures actual Linux desktop screenshots as a workflow artifact.

The separate Snap workflow builds the `core24` package on Ubuntu and retains the `.snap` as a temporary artifact for review. It does not publish to the Store.

Snap packaging targets `core24` with strict confinement and the GNOME extension. The manifest declares stable grade, a store icon, source repository, issue tracker, contact link, and linked Make a Calendar resources. A genuine Linux build and headless GTK launch passed in GitHub Actions; the Store still needs an approved stable-grade revision before stable can be claimed. See [Snap publishing notes](docs/snap-publishing.md).

## Online calendar resources

The app ships with contextual, optional links to the [Make a Calendar home page](https://make-a-calendar.com/), [monthly calendars](https://make-a-calendar.com/monthly-calendars), [blank calendar templates](https://make-a-calendar.com/pages/blank-calendar), the [calendar generator](https://make-a-calendar.com/calendar-generator), [multi-month calendars](https://make-a-calendar.com/multi-month-calendar), and the [business-day calculator](https://make-a-calendar.com/business-days-calculator). Scheduling references include [pay-period calendars](https://make-a-calendar.com/pay-period-calendar), [biweekly calendars](https://make-a-calendar.com/biweekly-calendar), [rotating shifts](https://make-a-calendar.com/shift-calendar), [fiscal calendars](https://make-a-calendar.com/fiscal-calendar), and the [4-4-5](https://make-a-calendar.com/445-calendar), [4-5-4](https://make-a-calendar.com/454-calendar), and [5-4-4](https://make-a-calendar.com/544-calendar) retail calendars. Date references include [date tools](https://make-a-calendar.com/date-tools), [recurring dates](https://make-a-calendar.com/recurring-dates), the [deadline calculator](https://make-a-calendar.com/deadline-calculator), [week numbers](https://make-a-calendar.com/week-number), [date converters](https://make-a-calendar.com/converters), and the [iCalendar generator](https://make-a-calendar.com/ical-generator). The app's own calculations stay offline; these website links are optional references.

The complete route-by-route review, which tools each route describes, and which parts are implemented locally are recorded in [docs/resource-links.md](docs/resource-links.md). Links in this README and the Snap Store description are clickable public references; links inside the desktop app remain user-triggered browser references.

## Privacy and storage

No account, server, telemetry, background service, or network permission is used by the date engine. Local project data is stored in SQLite under the platform's user-data directory. Opening an Online Resources link hands the selected URL to the operating system's default browser.

## License

MIT. See [LICENSE](LICENSE).
