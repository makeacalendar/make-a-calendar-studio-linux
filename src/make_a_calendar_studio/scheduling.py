"""Business-day, retail fiscal, payroll, and repeating shift calculations."""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Iterable, List, Sequence, Tuple


def business_days(start: date, end: date, *, weekend: Sequence[int] = (5, 6),
                  holidays: Iterable[date] = (), inclusive: bool = True) -> int:
    if end < start:
        raise ValueError("end must not be before start")
    if any(day not in range(7) for day in weekend):
        raise ValueError("weekend values must be weekday numbers from 0 to 6")
    if not inclusive and start == end:
        return 0
    excluded = set(holidays)
    cursor = start if inclusive else start + timedelta(days=1)
    count = 0
    while cursor <= end:
        if cursor.weekday() not in weekend and cursor not in excluded:
            count += 1
        if cursor == end:
            break
        cursor += timedelta(days=1)
    return count


def add_business_days(start: date, days: int, *, weekend: Sequence[int] = (5, 6),
                      holidays: Iterable[date] = ()) -> date:
    if days == 0:
        return start
    if any(day not in range(7) for day in weekend):
        raise ValueError("weekend values must be weekday numbers from 0 to 6")
    if len(set(weekend)) == 7:
        raise ValueError("at least one weekday must remain a working day")
    excluded = set(holidays)
    direction = 1 if days > 0 else -1
    remaining = abs(days)
    cursor = start
    while remaining:
        cursor += timedelta(days=direction)
        if cursor.weekday() not in weekend and cursor not in excluded:
            remaining -= 1
    return cursor


def nearest_sunday(value: date) -> date:
    """Sunday nearest to a date; ties select the earlier Sunday."""
    before = value - timedelta(days=(value.weekday() + 1) % 7)
    after = before + timedelta(days=7)
    return before if (value - before) <= (after - value) else after


def retail_year_start(year: int) -> date:
    return nearest_sunday(date(year, 2, 1))


def fiscal_months(start_year: int, start_month: int = 10) -> Tuple[Tuple[int, date, date], ...]:
    """Return twelve civil-month periods, labeled 1–12 from the chosen fiscal start."""
    if not 1 <= start_year <= 9998:
        raise ValueError("start_year must be between 1 and 9998")
    if not 1 <= start_month <= 12:
        raise ValueError("start_month must be between 1 and 12")
    periods=[]
    year, month = start_year, start_month
    for index in range(1,13):
        last_day=calendar.monthrange(year,month)[1]
        periods.append((index,date(year,month,1),date(year,month,last_day)))
        year,month=year+(month==12),month%12+1
    return tuple(periods)


def retail_year_weeks(year: int) -> int:
    if not 1 <= year <= 9998:
        raise ValueError("retail year must be between 1 and 9998")
    return (retail_year_start(year + 1) - retail_year_start(year)).days // 7


def retail_periods(year: int, pattern: str = "4-5-4") -> Tuple[Tuple[int, date, date], ...]:
    """Return numbered Sunday–Saturday periods for a Sunday-nearest-Feb-1 year."""
    if not 1 <= year <= 9998:
        raise ValueError("retail year must be between 1 and 9998")
    try:
        quarter = tuple(int(part) for part in pattern.split("-"))
    except (ValueError, AttributeError):
        raise ValueError("pattern must be 4-4-5, 4-5-4, or 5-4-4")
    if len(quarter) != 3 or quarter not in ((4, 4, 5), (4, 5, 4), (5, 4, 4)):
        raise ValueError("pattern must be 4-4-5, 4-5-4, or 5-4-4")
    start = retail_year_start(year)
    end = retail_year_start(year + 1)
    lengths = list(quarter) * 4
    if (end - start).days == 371:
        lengths[-1] += 1
    periods = []
    cursor = start
    for index, weeks in enumerate(lengths, 1):
        next_cursor = cursor + timedelta(weeks=weeks)
        periods.append((index, cursor, next_cursor - timedelta(days=1)))
        cursor = next_cursor
    return tuple(periods)


def payroll_dates(start: date, end: date, frequency: str = "biweekly", *,
                  anchor: date | None = None, day: int = 1) -> Tuple[date, ...]:
    if end < start:
        raise ValueError("end must not be before start")
    if frequency in ("weekly", "biweekly"):
        step = 7 if frequency == "weekly" else 14
        anchor = anchor or start
        cursor = anchor
        if cursor < start:
            cursor += timedelta(days=((start - cursor).days + step - 1) // step * step)
        while cursor > start:
            cursor -= timedelta(days=step)
        result = []
        while cursor <= end:
            if cursor >= start:
                result.append(cursor)
            if end - cursor < timedelta(days=step):
                break
            cursor += timedelta(days=step)
        return tuple(result)
    dates: List[date] = []
    cursor = date(start.year, start.month, 1)
    while cursor <= end:
        last = calendar.monthrange(cursor.year, cursor.month)[1]
        if frequency == "monthly":
            candidates = [date(cursor.year, cursor.month, min(day, last))]
        elif frequency == "semimonthly":
            candidates = [date(cursor.year, cursor.month, 15), date(cursor.year, cursor.month, last)]
        else:
            raise ValueError("frequency must be weekly, biweekly, semimonthly, or monthly")
        dates.extend(d for d in candidates if start <= d <= end)
        if cursor.year == 9999 and cursor.month == 12:
            break
        cursor = date(cursor.year + (cursor.month == 12), cursor.month % 12 + 1, 1)
    return tuple(dates)


SHIFT_PATTERNS = {
    "4-on-3-off": (1, 1, 1, 1, 0, 0, 0),
    "5-on-2-off": (1, 1, 1, 1, 1, 0, 0),
    "2-2-3": (1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0),
}


def shift_days(start: date, end: date, *, anchor: date, pattern: str = "2-2-3") -> Tuple[Tuple[date, bool], ...]:
    if end < start:
        raise ValueError("end must not be before start")
    cycle = SHIFT_PATTERNS.get(pattern)
    if cycle is None:
        raise ValueError("unknown shift pattern")
    result = []
    cursor = start
    while cursor <= end:
        result.append((cursor, bool(cycle[(cursor - anchor).days % len(cycle)])))
        cursor += timedelta(days=1)
    return tuple(result)
