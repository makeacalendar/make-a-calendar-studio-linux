# Architecture and data boundaries

## Layers

- `calendar_engine.py` supplies Gregorian month rows and ISO-week helpers.
- `holidays.py` maps observed US federal holiday dates without a network call.
- `scheduling.py` computes business days, retail 52/53-week years, pay dates, and anchored shift patterns.
- `converters.py` handles date-only Unix/Excel values and UTC FILETIME timestamps.
- `exporters.py` writes vector PDF drawing operators, SVG, CSV, JSON, and all-day ICS.
- `storage.py` owns the SQLite schema for local projects and dated event layers.
- `ui.py` composes these modules into the native GTK4/Libadwaita workspace. The CLI calls the same core modules.

## Persistence

The database has `projects` and `events` tables. A project stores JSON preferences for its local workspace; dated events have a project ID, date, title, layer, and notes. SQLite foreign keys cascade event removal when a project is eventually deleted. This first release has no project deletion or backup-import screen, so it does not advertise those operations.

Data is written to the platform's XDG user-data location. In a Snap, `SNAP_USER_DATA` is used. The application does not ask for broad home-directory access, network access, or background execution. GTK's asynchronous `Gtk.FileDialog` asks the desktop portal to grant access only to the file the user selects.

## Calendar and business rules

Month grids use Python's Gregorian `datetime` and `calendar` rules. Monday is weekday 0 and Sunday 6 internally. The UI labels the user's chosen convention. Federal holiday observations use preceding Friday for Saturday fixed-date holidays and following Monday for Sunday fixed-date holidays. The bundled 11-holiday set reflects today's federal holiday rules and is a planning aid; it does not model when each holiday was first established for historical-year research. The 4-4-5 family starts on the Sunday nearest February 1; a 53rd week extends the final period. Retail weeks are not ISO weeks.

Business-day date ranges are inclusive by default and exclude Saturday/Sunday plus the caller-selected holiday dates. Payroll dates are planning schedules only. Shift cycles preserve a user-provided anchor date. None of these rules claim to implement a particular employer's policies or labor law.

## Export formats

PDF is constructed as a one-page PDF 1.4 document with vector text, strokes, filled shapes, a page media box, font references, and a valid xref table. SVG writes the corresponding printable grid as vector XML. CSV/JSON expose civil month dates. ICS events are all-day local dates represented using RFC 5545 `VALUE=DATE` entries; this app does not yet import ICS or model timed events/time zones.
