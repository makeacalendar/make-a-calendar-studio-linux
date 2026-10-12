"""Gregorian calendar grid and date helpers."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, Tuple


@dataclass(frozen=True)
class CalendarCell:
    day: Optional[date]
    in_month: bool


def month_grid(year: int, month: int, week_start: int = 0, *, fixed_six_rows: bool = False,
               adjacent_dates: bool = True) -> Tuple[Tuple[CalendarCell, ...], ...]:
    """Return a 4–6 row month grid. week_start uses datetime.weekday(): Mon=0, Sun=6."""
    if not 1 <= year <= 9999:
        raise ValueError("year must be between 1 and 9999")
    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")
    if week_start not in range(7):
        raise ValueError("week_start must be a weekday number from 0 to 6")
    first = date(year, month, 1)
    days = calendar.monthrange(year, month)[1]
    leading = (first.weekday() - week_start) % 7
    rows = 6 if fixed_six_rows else (leading + days + 6) // 7
    start_ordinal = first.toordinal() - leading
    last_ordinal = date.max.toordinal()
    result = []
    for row in range(rows):
        cells = []
        for col in range(7):
            ordinal = start_ordinal + row * 7 + col
            current = date.fromordinal(ordinal) if 1 <= ordinal <= last_ordinal else None
            in_month = current is not None and current.year == year and current.month == month
            cells.append(CalendarCell(current if current and (in_month or adjacent_dates) else None, in_month))
        result.append(tuple(cells))
    return tuple(result)


def month_dates(year: int, month: int) -> Tuple[date, ...]:
    return tuple(date(year, month, d) for d in range(1, calendar.monthrange(year, month)[1] + 1))


def year_months(year: int, week_start: int = 0):
    return tuple((month, month_grid(year, month, week_start)) for month in range(1, 13))


def iso_week(value: date) -> Tuple[int, int]:
    iso = value.isocalendar()
    return iso.year, iso.week


def add_months(value: date, months: int) -> date:
    """Add calendar months while clamping to the destination month's last day."""
    index = value.year * 12 + value.month - 1 + months
    year, zero_month = divmod(index, 12)
    month = zero_month + 1
    return date(year, month, min(value.day, calendar.monthrange(year, month)[1]))
