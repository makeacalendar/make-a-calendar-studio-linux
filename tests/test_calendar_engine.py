import unittest
from datetime import date

from make_a_calendar_studio.calendar_engine import add_months, iso_week, month_grid


class CalendarEngineTests(unittest.TestCase):
    def test_leap_year_and_century_rules(self):
        self.assertEqual(len(month_grid(2024, 2)), 5)
        self.assertEqual(
            sum(cell.day is not None and cell.in_month for row in month_grid(2024, 2) for cell in row), 29
        )
        self.assertEqual(
            sum(cell.day is not None and cell.in_month for row in month_grid(2100, 2) for cell in row), 28
        )

    def test_grid_alignment_sunday_and_monday(self):
        monday = month_grid(2027, 1, 0)
        sunday = month_grid(2027, 1, 6)
        self.assertEqual(monday[0][4].day, date(2027, 1, 1))
        self.assertEqual(sunday[0][5].day, date(2027, 1, 1))
        self.assertEqual(len(month_grid(2027, 1, 0, fixed_six_rows=True)), 6)

    def test_adjacent_dates_can_be_hidden(self):
        grid = month_grid(2026, 2, 0, adjacent_dates=False)
        self.assertTrue(all(cell.day is None or cell.in_month for row in grid for cell in row))

    def test_iso_boundary_and_month_clamp(self):
        self.assertEqual(iso_week(date(2027, 1, 1)), (2026, 53))
        self.assertEqual(add_months(date(2024, 1, 31), 1), date(2024, 2, 29))

    def test_supported_calendar_range_edges_do_not_overflow(self):
        earliest = month_grid(1, 1, 6, adjacent_dates=True)
        latest = month_grid(9999, 12, 0, adjacent_dates=True)
        self.assertTrue(any(cell.day is None for row in earliest for cell in row))
        self.assertTrue(any(cell.day is None for row in latest for cell in row))
        self.assertEqual(sum(cell.in_month for row in latest for cell in row), 31)


if __name__ == "__main__":
    unittest.main()
