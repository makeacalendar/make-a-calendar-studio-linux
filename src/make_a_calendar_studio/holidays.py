"""US federal holiday dates with weekend observance."""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Dict


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + (n - 1) * 7)


def _last_weekday(year: int, month: int, weekday: int) -> date:
    last = date(year, month, calendar.monthrange(year, month)[1])
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def _observed(legal: date) -> date:
    if legal.weekday() == 5:
        return legal - timedelta(days=1)
    if legal.weekday() == 6:
        return legal + timedelta(days=1)
    return legal


def federal_holidays(year: int) -> Dict[date, str]:
    """Map observed holiday dates in `year` to names (11 federal holidays).

    New Year's Day can be observed on Dec 31 of the previous year, so adjacent
    legal years are considered when selecting observed dates.
    """
    if not 1 <= year <= 9999:
        raise ValueError("year must be between 1 and 9999")
    holidays: Dict[date, str] = {}
    for legal_year in (max(1, year - 1), year, min(9999, year + 1)):
        fixed = (
            (1, 1, "New Year's Day"), (6, 19, "Juneteenth National Independence Day"),
            (7, 4, "Independence Day"), (11, 11, "Veterans Day"), (12, 25, "Christmas Day"),
        )
        legal_dates = [(date(legal_year, m, d), name) for m, d, name in fixed]
        legal_dates += [
            (_nth_weekday(legal_year, 1, 0, 3), "Birthday of Martin Luther King, Jr."),
            (_nth_weekday(legal_year, 2, 0, 3), "Washington's Birthday"),
            (_last_weekday(legal_year, 5, 0), "Memorial Day"),
            (_nth_weekday(legal_year, 9, 0, 1), "Labor Day"),
            (_nth_weekday(legal_year, 10, 0, 2), "Columbus Day"),
            (_nth_weekday(legal_year, 11, 3, 4), "Thanksgiving Day"),
        ]
        for legal, name in legal_dates:
            observed = _observed(legal)
            if observed.year == year:
                holidays[observed] = name
    return dict(sorted(holidays.items()))
