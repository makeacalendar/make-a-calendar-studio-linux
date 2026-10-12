"""Open and cleanly exit the actual GTK application under a display server."""

from gi.repository import GLib

from make_a_calendar_studio.ui import CalendarStudioApp

app = CalendarStudioApp()
GLib.timeout_add_seconds(3, lambda: (app.quit(), False)[1])
raise SystemExit(app.run([]))
