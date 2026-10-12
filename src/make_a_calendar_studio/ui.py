"""GTK4/Libadwaita native desktop workspace."""

from __future__ import annotations

import calendar
import os
from datetime import date, timedelta
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GLib, Gtk

from . import __version__
from .calendar_engine import month_grid
from .converters import date_to_excel_serial, date_to_unix_timestamp, unix_timestamp_to_date
from .exporters import THEMES, export_csv, export_ics, export_json, export_pdf, export_svg
from .holidays import federal_holidays
from .resources import RESOURCES
from .scheduling import (
    add_business_days,
    business_days,
    fiscal_months,
    payroll_dates,
    retail_periods,
    retail_year_weeks,
    shift_days,
)
from .storage import ProjectStore


NAVIGATION = (
    ("overview", "Overview", "view-grid-symbolic"),
    ("designer", "Calendar Designer", "x-office-calendar-symbolic"),
    ("year", "Year Planner", "view-calendar-symbolic"),
    ("print", "Print Studio", "document-print-symbolic"),
    ("business", "Business Days", "work-day-symbolic"),
    ("fiscal", "Fiscal Studio", "view-list-symbolic"),
    ("payroll", "Payroll & Shifts", "system-users-symbolic"),
    ("dates", "Date Tools", "preferences-system-time-symbolic"),
    ("projects", "Local Projects", "folder-symbolic"),
    ("resources", "Online Resources", "web-browser-symbolic"),
    ("preferences", "Preferences", "preferences-system-symbolic"),
)

CSS = """
window { background: #f6f7f5; color: #172b3a; }
.sidebar { background: #f0f2ef; border-right: 1px solid #dce2de; }
.brand { padding: 24px 18px 18px; }
.brand-title { font-size: 19px; font-weight: 700; letter-spacing: -0.3px; }
.brand-subtitle { color: #687a7c; font-size: 11px; }
.nav-list { background: transparent; padding: 4px 10px; }
.nav-list row { background: transparent; border-radius: 9px; margin: 2px 0; }
.nav-list row:selected { background: #dcebe6; color: #173d39; }
.nav-item { padding: 8px 8px; font-size: 13px; }
.page { padding: 28px 34px 34px; }
.page-title { font-size: 27px; font-weight: 700; letter-spacing: -0.6px; }
.page-subtitle { color: #687a7c; font-size: 13px; }
.card { background: #ffffff; border: 1px solid #e0e5e1; border-radius: 14px; padding: 18px; }
.card-title { font-size: 15px; font-weight: 650; }
.muted { color: #687a7c; font-size: 12px; }
.metric { font-size: 28px; font-weight: 700; color: #1c514b; }
.calendar-cell { background: #ffffff; border: 1px solid #e6eae7; border-radius: 6px; padding: 6px 5px; min-height: 55px; }
.calendar-weekend { background: #f0f5f2; }
.calendar-adjacent { color: #a8b1ae; }
.calendar-holiday { color: #287f78; font-weight: 650; }
.status { color: #287f78; font-size: 12px; }
.section-heading { margin-top: 6px; margin-bottom: 4px; font-size: 16px; font-weight: 650; }
button.suggested-action { background: #287f78; }
"""


def _data_directory() -> Path:
    root = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    path = Path(root) / "make-a-calendar-studio"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _dropdown(items, selected=0):
    control = Gtk.DropDown.new_from_strings(list(items))
    control.set_selected(selected)
    return control


def _selected_text(control):
    item = control.get_selected_item()
    return item.get_string() if item else ""


class CalendarStudioApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.makeacalendar.Studio", flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.store = ProjectStore(_data_directory() / "studio.sqlite3")
        self.window = None
        self.active_page = "overview"
        self.project_status = None
        self.designer_grid = None
        self.designer_year = None
        self.designer_month = None
        self.designer_week = None
        self.designer_title = None
        self.status_label = None

    def do_activate(self):
        if self.window:
            self.window.present()
            return
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode("utf-8"))
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        self.window = Adw.ApplicationWindow(
            application=self, title="Make a Calendar Studio", default_width=1280, default_height=860
        )
        self.window.set_size_request(900, 640)
        self._build_window()
        self.window.present()

    def _build_window(self):
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Make a Calendar Studio"))
        new_button = Gtk.Button(label="New project")
        new_button.add_css_class("suggested-action")
        new_button.connect("clicked", lambda *_: self._create_project())
        header.pack_end(new_button)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_position(245)
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sidebar.add_css_class("sidebar")
        sidebar.set_size_request(215, -1)
        brand = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        brand.add_css_class("brand")
        title = Gtk.Label(label="MAKE A CALENDAR", xalign=0)
        title.add_css_class("brand-title")
        subtitle = Gtk.Label(label="Offline planning studio", xalign=0)
        subtitle.add_css_class("brand-subtitle")
        brand.append(title)
        brand.append(subtitle)
        sidebar.append(brand)
        nav = Gtk.ListBox()
        nav.add_css_class("nav-list")
        nav.set_selection_mode(Gtk.SelectionMode.SINGLE)
        nav.set_activate_on_single_click(True)
        self.nav_rows = []
        for page_id, label, icon in NAVIGATION:
            row = Gtk.ListBoxRow()
            item = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            item.add_css_class("nav-item")
            item.append(Gtk.Image.new_from_icon_name(icon))
            item.append(Gtk.Label(label=label, xalign=0, hexpand=True))
            row.set_child(item)
            nav.append(row)
            self.nav_rows.append(row)
        nav.connect("row-selected", self._navigation_changed)
        self.nav = nav
        sidebar.append(nav)
        foot = Gtk.Label(label=f"Version {__version__} · local by default", xalign=0)
        foot.add_css_class("muted")
        foot.set_margin_start(18)
        foot.set_margin_bottom(16)
        sidebar.append(foot)

        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE, transition_duration=140)
        self.stack.set_hexpand(True)
        self.stack.set_vexpand(True)
        page_builders = {
            "overview": self._overview_page,
            "designer": self._designer_page,
            "year": self._year_page,
            "print": self._print_page,
            "business": self._business_page,
            "fiscal": self._fiscal_page,
            "payroll": self._payroll_page,
            "dates": self._date_tools_page,
            "projects": self._projects_page,
            "resources": self._resources_page,
            "preferences": self._preferences_page,
        }
        for page_id, label, _icon in NAVIGATION:
            self.stack.add_named(self._scroll(page_builders[page_id]()), page_id)
        paned.set_start_child(sidebar)
        paned.set_end_child(self.stack)
        paned.set_resize_start_child(False)
        paned.set_shrink_start_child(False)
        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header)
        toolbar_view.set_content(paned)
        self.window.set_content(toolbar_view)
        start_page = os.environ.get("MCS_START_PAGE", "overview")
        start_index = next((index for index, entry in enumerate(NAVIGATION) if entry[0] == start_page), 0)
        self.nav.select_row(self.nav_rows[start_index])

    def _scroll(self, child):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(child)
        return scroll

    def _page(self, title, subtitle):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.add_css_class("page")
        head = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        title_label = Gtk.Label(label=title, xalign=0)
        title_label.add_css_class("page-title")
        sub = Gtk.Label(label=subtitle, xalign=0, wrap=True)
        sub.add_css_class("page-subtitle")
        head.append(title_label)
        head.append(sub)
        box.append(head)
        return box

    def _card(self, title, subtitle=None):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        card.add_css_class("card")
        heading = Gtk.Label(label=title, xalign=0)
        heading.add_css_class("card-title")
        card.append(heading)
        if subtitle:
            sub = Gtk.Label(label=subtitle, xalign=0, wrap=True)
            sub.add_css_class("muted")
            card.append(sub)
        return card

    def _navigation_changed(self, _list, row):
        if row is None:
            return
        index = self.nav_rows.index(row)
        self.active_page = NAVIGATION[index][0]
        self.stack.set_visible_child_name(self.active_page)
        if self.active_page == "designer":
            self._refresh_designer()
        if self.active_page == "projects":
            self._refresh_projects()

    def _set_status(self, text):
        if self.status_label:
            self.status_label.set_text(text)

    def _button(self, label, callback, *, suggested=False):
        button = Gtk.Button(label=label)
        if suggested:
            button.add_css_class("suggested-action")
        button.connect("clicked", lambda *_: callback())
        return button

    def _field_row(self, pairs):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        for label, widget in pairs:
            col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            label_widget = Gtk.Label(label=label, xalign=0)
            label_widget.add_css_class("muted")
            col.append(label_widget)
            col.append(widget)
            row.append(col)
        return row

    def _overview_page(self):
        page = self._page(
            "Overview", "A quiet workspace for printable calendars, date math, and local plans."
        )
        today = date.today()
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        current = self._card("Today", today.strftime("%A, %B %-d, %Y"))
        month_count = business_days(
            date(today.year, today.month, 1),
            date(today.year, today.month, calendar.monthrange(today.year, today.month)[1]),
            holidays=federal_holidays(today.year),
        )
        metric = Gtk.Label(label=str(month_count), xalign=0)
        metric.add_css_class("metric")
        current.append(metric)
        current.append(
            Gtk.Label(
                label="business days this month · excluding observed US federal holidays",
                xalign=0,
                wrap=True,
                css_classes=["muted"],
            )
        )
        row.append(current)
        holiday_card = self._card("Upcoming federal holidays", "Observed dates calculated locally")
        upcoming = [(d, n) for d, n in federal_holidays(today.year).items() if d >= today][:3]
        if not upcoming and today.month == 12:
            upcoming = list(federal_holidays(today.year + 1).items())[:3]
        for day, name in upcoming:
            holiday_card.append(Gtk.Label(label=f"{day.strftime('%b %-d')}  ·  {name}", xalign=0))
        if not upcoming:
            holiday_card.append(Gtk.Label(label="No remaining holiday dates in this year.", xalign=0))
        row.append(holiday_card)
        page.append(row)
        quick = self._card(
            "Quick actions", "Choose a task to start. Projects and events are stored on this device."
        )
        actions = Gtk.FlowBox()
        actions.set_selection_mode(Gtk.SelectionMode.NONE)
        actions.set_max_children_per_line(3)
        actions.set_min_children_per_line(1)
        actions.set_row_spacing(8)
        actions.set_column_spacing(8)
        for page_id, label in (
            ("designer", "New monthly calendar"),
            ("year", "Plan a year"),
            ("business", "Count business days"),
            ("payroll", "Generate a shift plan"),
            ("print", "Export a document"),
            ("projects", "Open local projects"),
        ):
            actions.insert(self._button(label, lambda p=page_id: self._go(p)), -1)
        quick.append(actions)
        page.append(quick)
        recent = self._card("Recent projects", "Your local projects are available even when you are offline.")
        projects = self.store.list_projects()[:4]
        if projects:
            for project in projects:
                recent.append(
                    Gtk.Label(label=f"{project['name']}  ·  updated {project['updated_at'][:10]}", xalign=0)
                )
        else:
            recent.append(
                Gtk.Label(
                    label="No projects yet. Create one from the New project button above.",
                    xalign=0,
                    wrap=True,
                )
            )
        page.append(recent)
        event_card = self._card(
            "Upcoming local events and deadlines",
            "Personal records from your saved projects; nothing is fabricated for an empty workspace.",
        )
        future = self.store.list_events(today.isoformat(), (today + timedelta(days=90)).isoformat())[:6]
        if future:
            for event in future:
                event_card.append(
                    Gtk.Label(
                        label=f"{event['event_date']}  ·  {event['title']}  ·  {event['layer']} / {event['project_name']}",
                        xalign=0,
                        wrap=True,
                    )
                )
        else:
            event_card.append(Gtk.Label(label="No upcoming saved events.", xalign=0))
        page.append(event_card)
        return page

    def _go(self, page_id):
        for row, entry in zip(self.nav_rows, NAVIGATION):
            if entry[0] == page_id:
                self.nav.select_row(row)
                return

    def _designer_page(self):
        page = self._page(
            "Calendar Designer",
            "Build a clean civil calendar grid, then send the same dates to print or data export.",
        )
        controls = self._card("Calendar setup", "Dates follow the proleptic Gregorian calendar.")
        now = date.today()
        self.designer_year = Gtk.SpinButton.new_with_range(1, 9999, 1)
        self.designer_year.set_value(now.year)
        self.designer_month = _dropdown(calendar.month_name[1:], now.month - 1)
        self.designer_week = _dropdown(("Monday start", "Sunday start"), 0)
        self.designer_title = Gtk.Entry()
        self.designer_title.set_placeholder_text("Optional calendar title")
        self.fixed_rows = Gtk.CheckButton(label="Fixed six-row layout")
        self.fixed_rows.set_active(True)
        self.designer_adjacent = Gtk.CheckButton(label="Show adjacent-month dates")
        self.designer_adjacent.set_active(True)
        self.designer_holidays = Gtk.CheckButton(label="Federal holiday layer")
        self.designer_holidays.set_active(True)
        self.designer_events = Gtk.CheckButton(label="Personal event layer")
        self.designer_events.set_active(True)
        controls.append(
            self._field_row(
                (
                    ("Year", self.designer_year),
                    ("Month", self.designer_month),
                    ("Week begins", self.designer_week),
                )
            )
        )
        controls.append(self.designer_title)
        layout_options = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        for option in (self.fixed_rows, self.designer_adjacent, self.designer_holidays, self.designer_events):
            layout_options.append(option)
        controls.append(layout_options)
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        actions.append(self._button("Refresh preview", self._refresh_designer, suggested=True))
        actions.append(self._button("Export PDF", lambda: self._choose_export("pdf")))
        actions.append(self._button("Export SVG", lambda: self._choose_export("svg")))
        actions.append(self._button("Export CSV", lambda: self._choose_export("csv")))
        controls.append(actions)
        page.append(controls)
        preview = self._card(
            "Month preview", "The week-start choice changes the columns, not the underlying dates."
        )
        self.designer_grid = Gtk.Grid(column_spacing=7, row_spacing=6)
        self.designer_grid.set_column_homogeneous(True)
        self.designer_grid.set_row_homogeneous(True)
        preview.append(self.designer_grid)
        page.append(preview)
        self._refresh_designer()
        return page

    def _refresh_designer(self):
        if not self.designer_grid:
            return
        child = self.designer_grid.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.designer_grid.remove(child)
            child = nxt
        year = int(self.designer_year.get_value())
        month = self.designer_month.get_selected() + 1
        week_start = 0 if self.designer_week.get_selected() == 0 else 6
        event_start = date(year, month, 1)
        event_end = date(year, month, calendar.monthrange(year, month)[1])
        events_by_date = {}
        if self.designer_events.get_active():
            for event in self.store.list_events(event_start.isoformat(), event_end.isoformat()):
                events_by_date.setdefault(date.fromisoformat(event["event_date"]), []).append(event["title"])
        weekdays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        names = weekdays[week_start:] + weekdays[:week_start]
        for col, name in enumerate(names):
            label = Gtk.Label(label=name)
            label.add_css_class("muted")
            self.designer_grid.attach(label, col, 0, 1, 1)
        for ri, row in enumerate(
            month_grid(year, month, week_start, fixed_six_rows=self.fixed_rows.get_active())
        ):
            for col, cell in enumerate(row):
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
                box.add_css_class("calendar-cell")
                if (week_start + col) % 7 in (5, 6):
                    box.add_css_class("calendar-weekend")
                if not cell.in_month:
                    box.add_css_class("calendar-adjacent")
                if cell.day:
                    number = Gtk.Label(label=str(cell.day.day), xalign=0)
                    box.append(number)
                    holiday = (
                        federal_holidays(cell.day.year).get(cell.day)
                        if self.designer_holidays.get_active()
                        else None
                    )
                    if holiday and cell.in_month:
                        name = Gtk.Label(label=holiday, xalign=0, wrap=True)
                        name.add_css_class("calendar-holiday")
                        box.append(name)
                    if cell.in_month:
                        for event_title in events_by_date.get(cell.day, []):
                            event_label = Gtk.Label(label=event_title, xalign=0, wrap=True)
                            event_label.add_css_class("calendar-holiday")
                            box.append(event_label)
                self.designer_grid.attach(box, col, ri + 1, 1, 1)

    def _print_page(self):
        page = self._page(
            "Print Studio",
            "Export sharp vector documents with a paper size and visual system chosen for the page.",
        )
        card = self._card(
            "Page and style",
            "Five layouts change spacing, rules, and hierarchy. The local export engine draws vector paths and text.",
        )
        self.print_year = Gtk.SpinButton.new_with_range(1, 9999, 1)
        self.print_year.set_value(date.today().year)
        self.print_month = _dropdown(calendar.month_name[1:], date.today().month - 1)
        self.print_paper = _dropdown(("Letter", "A4", "A3"), 0)
        self.print_margin = Gtk.SpinButton.new_with_range(14, 80, 2)
        self.print_margin.set_value(34)
        self.print_theme = _dropdown(tuple(THEMES), 0)
        self.print_orientation = _dropdown(("Portrait", "Landscape"), 0)
        self.print_week = _dropdown(("Monday start", "Sunday start"), 0)
        card.append(
            self._field_row(
                (
                    ("Year", self.print_year),
                    ("Month", self.print_month),
                    ("Paper", self.print_paper),
                    ("Margin (points)", self.print_margin),
                )
            )
        )
        card.append(
            self._field_row(
                (
                    ("Theme", self.print_theme),
                    ("Orientation", self.print_orientation),
                    ("Week begins", self.print_week),
                )
            )
        )
        self.print_title = Gtk.Entry()
        self.print_title.set_placeholder_text("Optional header")
        self.print_notes = Gtk.Entry()
        self.print_notes.set_placeholder_text("Optional footer note")
        card.append(self.print_title)
        card.append(self.print_notes)
        self.print_grayscale = Gtk.CheckButton(label="Grayscale-friendly")
        self.print_large = Gtk.CheckButton(label="Large print")
        self.print_holidays = Gtk.CheckButton(label="US federal holidays")
        self.print_holidays.set_active(True)
        self.print_week_numbers = Gtk.CheckButton(label="ISO week numbers")
        self.print_weekends = Gtk.CheckButton(label="Shade weekends")
        self.print_weekends.set_active(True)
        self.print_adjacent = Gtk.CheckButton(label="Adjacent-month dates")
        self.print_adjacent.set_active(True)
        opts = Gtk.FlowBox()
        opts.set_selection_mode(Gtk.SelectionMode.NONE)
        opts.set_max_children_per_line(3)
        opts.set_min_children_per_line(1)
        for option in (
            self.print_grayscale,
            self.print_large,
            self.print_holidays,
            self.print_week_numbers,
            self.print_weekends,
            self.print_adjacent,
        ):
            opts.insert(option, -1)
        card.append(opts)
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for fmt in ("pdf", "svg", "csv", "json"):
            actions.append(
                self._button(
                    f"Export {fmt.upper()}", lambda f=fmt: self._choose_export(f), suggested=(fmt == "pdf")
                )
            )
        card.append(actions)
        self.status_label = Gtk.Label(label="", xalign=0)
        self.status_label.add_css_class("status")
        card.append(self.status_label)
        page.append(card)
        info = self._card(
            "Export details",
            "PDF output is a real vector document with embedded page geometry and standard vector text/line operators. SVG stays editable as vector markup.",
        )
        page.append(info)
        return page

    def _export_options(self):
        return {
            "year": int(self.print_year.get_value()),
            "month": self.print_month.get_selected() + 1,
            "theme": _selected_text(self.print_theme),
            "paper": _selected_text(self.print_paper),
            "landscape": self.print_orientation.get_selected() == 1,
            "week_start": 0 if self.print_week.get_selected() == 0 else 6,
            "title": self.print_title.get_text(),
            "notes": self.print_notes.get_text(),
            "grayscale": self.print_grayscale.get_active(),
            "large_print": self.print_large.get_active(),
            "holidays": federal_holidays(int(self.print_year.get_value()))
            if self.print_holidays.get_active()
            else {},
            "margin": self.print_margin.get_value(),
            "show_week_numbers": self.print_week_numbers.get_active(),
            "weekend_shading": self.print_weekends.get_active(),
            "adjacent_dates": self.print_adjacent.get_active(),
        }

    def _choose_export(self, fmt):
        if self.active_page == "designer":
            year = int(self.designer_year.get_value())
            month = self.designer_month.get_selected() + 1
            opts = {
                "title": self.designer_title.get_text(),
                "week_start": 0 if self.designer_week.get_selected() == 0 else 6,
                "holidays": federal_holidays(year) if self.designer_holidays.get_active() else {},
                "adjacent_dates": self.designer_adjacent.get_active(),
            }
        else:
            opts = self._export_options()
            year = opts.pop("year")
            month = opts.pop("month")
        dialog = Gtk.FileDialog.new()
        dialog.set_title(f"Export {fmt.upper()}")
        dialog.set_initial_name(f"calendar-{year}-{month:02d}.{fmt}")

        def saved(file_dialog, result):
            try:
                file = file_dialog.save_finish(result)
                target = file.get_path()
                if not target:
                    raise OSError("The selected location did not provide a local path.")
                fn = {"pdf": export_pdf, "svg": export_svg, "csv": export_csv, "json": export_json}[fmt]
                if fmt in ("csv", "json"):
                    fn(target, year, month, holidays=opts.get("holidays"))
                else:
                    fn(target, year, month, **opts)
                self._set_status(f"Saved {Path(target).name}")
            except GLib.Error:
                return
            except (OSError, ValueError) as error:
                self._set_status(f"Export failed: {error}")

        dialog.save(self.window, None, saved)

    def _year_page(self):
        page = self._page(
            "Year Planner",
            "See twelve month grids together. Change the week start without altering civil dates.",
        )
        controls = self._card("Year view")
        self.year_value = Gtk.SpinButton.new_with_range(1, 9999, 1)
        self.year_value.set_value(date.today().year)
        self.year_week = _dropdown(("Monday start", "Sunday start"), 0)
        controls.append(self._field_row((("Year", self.year_value), ("Week begins", self.year_week))))
        self.year_grid = Gtk.Grid(column_spacing=12, row_spacing=12)
        self.year_grid.set_column_homogeneous(True)
        controls.append(self.year_grid)
        controls.append(self._button("Refresh year", self._refresh_year, suggested=True))
        page.append(controls)
        self._refresh_year()
        return page

    def _refresh_year(self):
        if not hasattr(self, "year_grid"):
            return
        child = self.year_grid.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            self.year_grid.remove(child)
            child = nxt
        year = int(self.year_value.get_value())
        week_start = 0 if self.year_week.get_selected() == 0 else 6
        for month in range(1, 13):
            card = self._card(calendar.month_name[month])
            grid = Gtk.Grid(column_spacing=3, row_spacing=2)
            grid.set_column_homogeneous(True)
            labels = ("M", "T", "W", "T", "F", "S", "S")
            ordered = labels[week_start:] + labels[:week_start]
            for col, label in enumerate(ordered):
                name = Gtk.Label(label=label)
                name.add_css_class("muted")
                grid.attach(name, col, 0, 1, 1)
            for ri, row in enumerate(month_grid(year, month, week_start)):
                for col, cell in enumerate(row):
                    label = Gtk.Label(label=str(cell.day.day) if cell.day and cell.in_month else "")
                    grid.attach(label, col, ri + 1, 1, 1)
            card.append(grid)
            self.year_grid.attach(card, (month - 1) % 3, (month - 1) // 3, 1, 1)

    def _business_page(self):
        page = self._page(
            "Business Days",
            "Count weekdays across inclusive date ranges. Federal holidays are an optional exclusion layer.",
        )
        card = self._card("Workday count", "Saturday and Sunday are treated as the default weekend.")
        self.biz_start = Gtk.Entry()
        self.biz_start.set_text(date.today().replace(day=1).isoformat())
        self.biz_end = Gtk.Entry()
        self.biz_end.set_text(date.today().isoformat())
        card.append(self._field_row((("Start date", self.biz_start), ("End date", self.biz_end))))
        self.biz_holidays = Gtk.CheckButton(label="Exclude observed US federal holidays")
        self.biz_holidays.set_active(True)
        card.append(self.biz_holidays)
        self.biz_weekend_checks = []
        weekdays = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        for weekday, name in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")):
            check = Gtk.CheckButton(label=name)
            check.set_active(weekday in (5, 6))
            self.biz_weekend_checks.append(check)
            weekdays.append(check)
        card.append(Gtk.Label(label="Treat as weekend", xalign=0, css_classes=["muted"]))
        card.append(weekdays)
        result = Gtk.Label(label="", xalign=0)
        result.add_css_class("metric")

        def calculate():
            try:
                start = date.fromisoformat(self.biz_start.get_text())
                end = date.fromisoformat(self.biz_end.get_text())
                holidays = {}
                if self.biz_holidays.get_active():
                    for year in range(start.year, end.year + 1):
                        holidays.update(federal_holidays(year))
                weekend = tuple(
                    index for index, check in enumerate(self.biz_weekend_checks) if check.get_active()
                )
                count = business_days(start, end, holidays=holidays, weekend=weekend)
                result.set_text(str(count) + " business days")
            except ValueError as error:
                result.set_text(str(error))

        card.append(self._button("Calculate", calculate, suggested=True))
        card.append(result)
        page.append(card)
        note = self._card(
            "Calculation rule",
            "The start and end dates are included when each is a weekday and is not excluded. This is a date-only calculation; it does not model local employer closures or regional holidays.",
        )
        page.append(note)
        add_card = self._card(
            "Add or subtract workdays",
            "The starting date is not counted; the result is the date reached after the requested number of working days.",
        )
        self.add_start = Gtk.Entry()
        self.add_start.set_text(date.today().isoformat())
        self.add_count = Gtk.SpinButton.new_with_range(-3650, 3650, 1)
        self.add_result = Gtk.Label(label="", xalign=0)
        self.add_result.add_css_class("metric")
        add_card.append(self._field_row((("Start date", self.add_start), ("Workdays", self.add_count))))

        def add_workdays():
            try:
                start = date.fromisoformat(self.add_start.get_text())
                excluded = {}
                if self.biz_holidays.get_active():
                    year_span = abs(int(self.add_count.get_value())) // 365 + 1
                    for year in range(max(1, start.year - year_span), min(9999, start.year + year_span) + 1):
                        excluded.update(federal_holidays(year))
                weekend = tuple(
                    index for index, check in enumerate(self.biz_weekend_checks) if check.get_active()
                )
                result = add_business_days(
                    start, int(self.add_count.get_value()), weekend=weekend, holidays=excluded
                )
                self.add_result.set_text(result.isoformat())
            except (ValueError, OverflowError) as error:
                self.add_result.set_text(str(error))

        add_card.append(self._button("Calculate due date", add_workdays, suggested=True))
        add_card.append(self.add_result)
        page.append(add_card)
        return page

    def _fiscal_page(self):
        page = self._page(
            "Fiscal Studio",
            "Explore Sunday-nearest-February retail years and the three common 12-period week patterns.",
        )
        card = self._card("Retail year")
        self.fiscal_year = Gtk.SpinButton.new_with_range(1900, 9998, 1)
        self.fiscal_year.set_value(date.today().year)
        self.fiscal_pattern = _dropdown(("4-4-5", "4-5-4", "5-4-4"), 0)
        self.fiscal_mode = _dropdown(("Retail week periods", "Civil fiscal months"), 0)
        self.fiscal_start_month = _dropdown(calendar.month_name[1:], 9)
        card.append(
            self._field_row((("Start year", self.fiscal_year), ("Retail pattern", self.fiscal_pattern)))
        )
        card.append(
            self._field_row(
                (("Fiscal view", self.fiscal_mode), ("Civil start month", self.fiscal_start_month))
            )
        )
        self.fiscal_output = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        card.append(self.fiscal_output)
        card.append(self._button("Calculate periods", self._refresh_fiscal, suggested=True))
        page.append(card)
        self._refresh_fiscal()
        return page

    def _refresh_fiscal(self):
        while self.fiscal_output.get_first_child():
            self.fiscal_output.remove(self.fiscal_output.get_first_child())
        year = int(self.fiscal_year.get_value())
        if self.fiscal_mode.get_selected() == 1:
            month = self.fiscal_start_month.get_selected() + 1
            self.fiscal_output.append(
                Gtk.Label(
                    label=f"12 civil months · fiscal year starts {calendar.month_name[month]}", xalign=0
                )
            )
            for n, start, end in fiscal_months(year, month):
                quarter = (n - 1) // 3 + 1
                self.fiscal_output.append(
                    Gtk.Label(
                        label=f"FY month {n:02d} · Q{quarter}   {start:%b %-d, %Y} – {end:%b %-d, %Y}",
                        xalign=0,
                    )
                )
        else:
            pattern = _selected_text(self.fiscal_pattern)
            weeks = retail_year_weeks(year)
            self.fiscal_output.append(
                Gtk.Label(label=f"{weeks}-week year · Sunday-nearest February 1", xalign=0)
            )
            for n, start, end in retail_periods(year, pattern):
                self.fiscal_output.append(
                    Gtk.Label(label=f"Period {n:02d}   {start:%b %-d} – {end:%b %-d, %Y}", xalign=0)
                )

    def _payroll_page(self):
        page = self._page(
            "Payroll & Shifts",
            "Generate repeating date schedules locally. Results are planning aids, not payroll advice.",
        )
        payroll = self._card(
            "Pay-date schedule", "Weekly, biweekly, semimonthly, and monthly dates with month-end clamping."
        )
        self.pay_start = Gtk.Entry()
        self.pay_start.set_text(date.today().replace(day=1).isoformat())
        self.pay_end = Gtk.Entry()
        self.pay_end.set_text((date.today() + timedelta(days=180)).isoformat())
        self.pay_frequency = _dropdown(("weekly", "biweekly", "semimonthly", "monthly"), 1)
        self.pay_anchor = Gtk.Entry()
        self.pay_anchor.set_text(date.today().isoformat())
        payroll.append(
            self._field_row(
                (
                    ("From", self.pay_start),
                    ("Through", self.pay_end),
                    ("Frequency", self.pay_frequency),
                    ("First pay date", self.pay_anchor),
                )
            )
        )
        self.pay_output = Gtk.Label(label="", xalign=0, wrap=True)

        def calc_pay():
            try:
                dates = payroll_dates(
                    date.fromisoformat(self.pay_start.get_text()),
                    date.fromisoformat(self.pay_end.get_text()),
                    _selected_text(self.pay_frequency),
                    anchor=date.fromisoformat(self.pay_anchor.get_text()),
                )
                self.pay_output.set_text(
                    "   ·   ".join(d.isoformat() for d in dates) or "No pay dates in this range."
                )
            except ValueError as error:
                self.pay_output.set_text(str(error))

        payroll.append(self._button("Generate pay dates", calc_pay, suggested=True))
        payroll.append(self.pay_output)
        page.append(payroll)
        shift = self._card("Rotating shift", "Track work and off days in an anchored repeating cycle.")
        self.shift_start = Gtk.Entry()
        self.shift_start.set_text(date.today().isoformat())
        self.shift_end = Gtk.Entry()
        self.shift_end.set_text((date.today() + timedelta(days=27)).isoformat())
        self.shift_anchor = Gtk.Entry()
        self.shift_anchor.set_text(date.today().isoformat())
        self.shift_pattern = _dropdown(("4-on-3-off", "5-on-2-off", "2-2-3"), 2)
        shift.append(
            self._field_row(
                (
                    ("From", self.shift_start),
                    ("Through", self.shift_end),
                    ("Cycle anchor", self.shift_anchor),
                    ("Pattern", self.shift_pattern),
                )
            )
        )
        self.shift_output = Gtk.Label(label="", xalign=0, wrap=True)

        def calc_shift():
            try:
                days = shift_days(
                    date.fromisoformat(self.shift_start.get_text()),
                    date.fromisoformat(self.shift_end.get_text()),
                    anchor=date.fromisoformat(self.shift_anchor.get_text()),
                    pattern=_selected_text(self.shift_pattern),
                )
                self.shift_output.set_text(
                    "   ·   ".join(f"{d:%b %-d} {'WORK' if on else 'OFF'}" for d, on in days)
                )
            except ValueError as error:
                self.shift_output.set_text(str(error))

        shift.append(self._button("Generate shift plan", calc_shift))
        shift.append(self.shift_output)
        page.append(shift)
        return page

    def _date_tools_page(self):
        page = self._page(
            "Date Tools",
            "Convert common date formats and inspect ISO week numbers without sending data anywhere.",
        )
        card = self._card(
            "Date format converter", "Enter a date, Unix timestamp, Excel serial, or FILETIME tick count."
        )
        self.date_input = Gtk.Entry()
        self.date_input.set_text(date.today().isoformat())
        self.date_type = _dropdown(("ISO date", "Unix timestamp", "Excel serial", "FILETIME ticks"), 0)
        card.append(self._field_row((("Value", self.date_input), ("Format", self.date_type))))
        self.date_output = Gtk.Label(label="", xalign=0, wrap=True)
        self.date_output.add_css_class("metric")

        def convert():
            raw = self.date_input.get_text().strip()
            kind = self.date_type.get_selected()
            try:
                if kind == 0:
                    value = date.fromisoformat(raw)
                    result = f"{value:%A, %B %-d, %Y}  ·  ISO week {value.isocalendar().week}  ·  Unix {date_to_unix_timestamp(value)}  ·  Excel {date_to_excel_serial(value)}"
                elif kind == 1:
                    value = unix_timestamp_to_date(int(raw))
                    result = f"{value.isoformat()}  ·  Excel {date_to_excel_serial(value)}"
                elif kind == 2:
                    from .converters import excel_serial_to_date

                    value = excel_serial_to_date(int(raw))
                    result = f"{value.isoformat()}  ·  Unix {date_to_unix_timestamp(value)}"
                else:
                    from .converters import filetime_to_datetime

                    result = filetime_to_datetime(int(raw)).isoformat()
                self.date_output.set_text(result)
            except (ValueError, OverflowError, OSError) as error:
                self.date_output.set_text(f"Could not convert: {error}")

        card.append(self._button("Convert", convert, suggested=True))
        card.append(self.date_output)
        page.append(card)
        return page

    def _projects_page(self):
        page = self._page(
            "Local Projects", "Projects and personal event records stay in a local SQLite database."
        )
        card = self._card(
            "Create a project",
            "Start with an empty workspace; no sample activity is added to your real data.",
        )
        self.project_name = Gtk.Entry()
        self.project_name.set_placeholder_text("Project name")
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.append(self.project_name)
        row.append(self._button("Create project", self._create_project, suggested=True))
        card.append(row)
        self.project_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.append(self.project_list)
        self.project_status = Gtk.Label(label="", xalign=0)
        self.project_status.add_css_class("status")
        card.append(self.project_status)
        page.append(card)
        events = self._card(
            "Add a personal event", "Events are all-day date labels stored in the selected local project."
        )
        self.event_project = _dropdown(("Create a project first",), 0)
        self.event_date = Gtk.Entry()
        self.event_date.set_text(date.today().isoformat())
        self.event_title = Gtk.Entry()
        self.event_title.set_placeholder_text("Event title")
        self.event_layer = _dropdown(("personal", "deadline", "custom"), 0)
        events.append(
            self._field_row(
                (
                    ("Project", self.event_project),
                    ("Date", self.event_date),
                    ("Title", self.event_title),
                    ("Layer", self.event_layer),
                )
            )
        )
        events.append(self._button("Save event", self._save_event, suggested=True))
        page.append(events)
        backup = self._card(
            "Storage",
            "The app stores projects under the user's application data directory. Snap confinement keeps the location within app-owned user data.",
        )
        page.append(backup)
        self._refresh_projects()
        return page

    def _create_project(self):
        name = self.project_name.get_text() if hasattr(self, "project_name") else ""
        if not name.strip():
            name = f"Calendar project {date.today():%Y-%m-%d}"
        try:
            self.store.create_project(
                name, {"week_start": "monday", "layers": {"personal": True, "federal_holidays": True}}
            )
            if hasattr(self, "project_name"):
                self.project_name.set_text("")
            if self.project_status:
                self.project_status.set_text(f"Created {name} on this device.")
            self._refresh_projects()
        except (ValueError, RuntimeError) as error:
            if self.project_status:
                self.project_status.set_text(str(error))

    def _refresh_projects(self):
        if not hasattr(self, "project_list"):
            return
        while self.project_list.get_first_child():
            self.project_list.remove(self.project_list.get_first_child())
        projects = self.store.list_projects()
        if hasattr(self, "event_project"):
            self.project_ids = [project["id"] for project in projects]
            names = [project["name"] for project in projects] or ["Create a project first"]
            self.event_project.set_model(Gtk.StringList.new(names))
            self.event_project.set_selected(0)
        if not projects:
            self.project_list.append(Gtk.Label(label="No projects yet.", xalign=0))
            return
        for project in projects:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            label = Gtk.Label(
                label=f"{project['name']}  ·  {len(self.store.get_project(project['id'])['events'])} events",
                xalign=0,
                hexpand=True,
            )
            row.append(label)
            export_button = Gtk.Button(label="Export ICS")
            export_button.connect("clicked", lambda *_args, p=project: self._export_project_ics(p))
            row.append(export_button)
            self.project_list.append(row)

    def _save_event(self):
        try:
            if not getattr(self, "project_ids", []):
                raise ValueError("Create a local project first.")
            project_id = self.project_ids[self.event_project.get_selected()]
            self.store.add_event(
                project_id,
                self.event_date.get_text(),
                self.event_title.get_text(),
                layer=_selected_text(self.event_layer),
            )
            self.event_title.set_text("")
            if self.project_status:
                self.project_status.set_text("Saved this event locally.")
            self._refresh_projects()
        except (KeyError, ValueError) as error:
            if self.project_status:
                self.project_status.set_text(str(error))

    def _export_project_ics(self, project):
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Export project events")
        dialog.set_initial_name("calendar-events.ics")

        def saved(file_dialog, result):
            try:
                file = file_dialog.save_finish(result)
                target = file.get_path()
                if not target:
                    raise OSError("The selected location did not provide a local path.")
                data = self.store.get_project(project["id"])
                events = [{"date": event["event_date"], "title": event["title"]} for event in data["events"]]
                export_ics(target, events)
                if self.project_status:
                    self.project_status.set_text(f"Exported {len(events)} all-day events.")
            except GLib.Error:
                return
            except (OSError, ValueError) as error:
                if self.project_status:
                    self.project_status.set_text(f"Export failed: {error}")

        dialog.save(self.window, None, saved)

    def _resources_page(self):
        page = self._page(
            "Online Resources",
            "Optional web tools from Make a Calendar. Links open in your default browser when you choose them.",
        )
        note = self._card(
            "Offline first",
            "The local calendar engine does not load these pages. A network connection is needed only when you open a link.",
        )
        page.append(note)
        for resource in RESOURCES:
            card = self._card(resource["title"], resource["scenario"])
            card.append(
                Gtk.Label(label=resource["implementation"], xalign=0, wrap=True, css_classes=["muted"])
            )
            button = Gtk.LinkButton.new_with_label(resource["url"], "Open online resource")
            card.append(button)
            meta = Gtk.Label(
                label=f"{resource['topic']}  ·  URL reviewed {resource['url'].split('/')[2]} on 2026-10-12",
                xalign=0,
            )
            meta.add_css_class("muted")
            card.append(meta)
            page.append(card)
        return page

    def _preferences_page(self):
        page = self._page("Preferences", "A few practical defaults for the current desktop session.")
        card = self._card(
            "Display and data", "Project data remains on this device. Calendar output is generated locally."
        )
        card.append(Gtk.Label(label="Application ID  ·  com.makeacalendar.Studio", xalign=0))
        card.append(
            Gtk.Label(label=f"Local database  ·  {_data_directory() / 'studio.sqlite3'}", xalign=0, wrap=True)
        )
        card.append(
            Gtk.Label(
                label="Week start and print theme are selected per document in this release.",
                xalign=0,
                wrap=True,
                css_classes=["muted"],
            )
        )
        page.append(card)
        attribution = self._card(
            "About Make a Calendar Studio",
            "Original desktop software inspired by practical date-planning workflows. Created by Ethan, the developer behind Make a Calendar. It does not call or reproduce the private implementation of the website.",
        )
        attribution.append(Gtk.Label(label=f"Version {__version__} · MIT License", xalign=0))
        page.append(attribution)
        return page


def main() -> int:
    app = CalendarStudioApp()
    return app.run(None)
