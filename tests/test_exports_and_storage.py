import csv
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from pathlib import Path

from make_a_calendar_studio.converters import (
    date_to_excel_serial,
    date_to_filetime,
    date_to_unix_timestamp,
    datetime_to_filetime,
    excel_serial_to_date,
    filetime_to_datetime,
    unix_timestamp_to_date,
)
from make_a_calendar_studio.exporters import export_csv, export_ics, export_json, export_pdf, export_svg
from make_a_calendar_studio.storage import ProjectStore


class ExportAndStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_vector_pdf_and_svg_integrity(self):
        pdf = export_pdf(
            self.root / "month.pdf",
            2027,
            1,
            theme="Corporate Planner",
            paper="A4",
            landscape=True,
            margin=42,
            show_week_numbers=True,
            week_start=6,
            weekend_shading=False,
        )
        data = pdf.read_bytes()
        self.assertTrue(data.startswith(b"%PDF-1.4"))
        self.assertTrue(data.endswith(b"%%EOF\n"))
        xref = int(data.rsplit(b"startxref\n", 1)[1].splitlines()[0])
        self.assertEqual(data[xref : xref + 4], b"xref")
        self.assertIn(b"/MediaBox [0 0 841.89 595.28]", data)
        self.assertIn(b"(W52)", data)
        self.assertIn(b"January 2027", data)
        svg = export_svg(self.root / "month.svg", 2027, 1, theme="Academic Weekly", notes="Review & revise")
        parsed = ET.parse(svg)
        self.assertEqual(parsed.getroot().tag, "{http://www.w3.org/2000/svg}svg")
        self.assertIn("&amp;", svg.read_text())
        classic = export_svg(self.root / "classic.svg", 2027, 1, theme="Classic Monochrome").read_text()
        editorial = export_svg(self.root / "editorial.svg", 2027, 1, theme="Editorial Minimal").read_text()
        corporate = export_svg(self.root / "corporate.svg", 2027, 1, theme="Corporate Planner").read_text()
        seasonal = export_svg(self.root / "seasonal.svg", 2027, 1, theme="Modern Seasonal").read_text()
        self.assertIn('stroke-width="1.25"', classic)
        self.assertLess(editorial.count('x1="'), corporate.count('x1="'))
        self.assertIn('height="24" fill="#3276a8"', corporate)
        self.assertIn('fill="#fbfcfa"', seasonal)

    def test_csv_json_and_ics(self):
        csv_path = export_csv(
            self.root / "month.csv", 2026, 7, holidays={date(2026, 7, 3): "Independence, observed"}
        )
        with csv_path.open(encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        observed = next(row for row in rows if row["date"] == "2026-07-03")
        self.assertEqual(observed["holiday"], "Independence, observed")
        data = json.loads(export_json(self.root / "month.json", 2026, 7).read_text())
        self.assertEqual(len(data["days"]), 31)
        ics = export_ics(
            self.root / "events.ics",
            [{"date": "2026-07-04", "title": "A long event title, with a comma and \u2603 repeated " * 4}],
        )
        data = ics.read_bytes()
        self.assertIn(b"DTSTART;VALUE=DATE:20260704", data)
        self.assertTrue(data.endswith(b"END:VCALENDAR\r\n"))
        for line in data.split(b"\r\n"):
            self.assertLessEqual(len(line), 75)

    def test_common_converter_round_trips(self):
        sample = date(2026, 10, 12)
        self.assertEqual(unix_timestamp_to_date(date_to_unix_timestamp(sample)), sample)
        self.assertEqual(excel_serial_to_date(date_to_excel_serial(sample)), sample)
        self.assertEqual(excel_serial_to_date(1), date(1900, 1, 1))
        with self.assertRaises(ValueError):
            excel_serial_to_date(60)
        self.assertEqual(
            filetime_to_datetime(date_to_filetime(sample)), datetime(2026, 10, 12, tzinfo=timezone.utc)
        )
        instant = datetime(2020, 2, 29, 12, 34, 56, 123456, tzinfo=timezone.utc)
        self.assertEqual(filetime_to_datetime(datetime_to_filetime(instant)), instant)

    def test_project_event_crud_and_reopen(self):
        database = self.root / "data" / "studio.sqlite3"
        store = ProjectStore(database)
        project_id = store.create_project("FY planning", {"week_start": "monday"})
        event_id = store.add_event(project_id, "2026-11-03", "Budget review", layer="deadline", notes="Q4")
        project = store.get_project(project_id)
        self.assertEqual(project["events"][0]["title"], "Budget review")
        self.assertEqual(store.list_events("2026-11-01", "2026-11-30")[0]["project_name"], "FY planning")
        store.update_project(project_id, name="Budget FY")
        store.close()
        reopened = ProjectStore(database)
        self.assertEqual(reopened.get_project(project_id)["name"], "Budget FY")
        reopened.delete_event(event_id)
        self.assertEqual(reopened.get_project(project_id)["events"], [])
        reopened.close()


if __name__ == "__main__":
    unittest.main()
