"""Date-only conversions useful in spreadsheets and system logs."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

UNIX_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
EXCEL_EPOCH = date(1899, 12, 30)  # Excel's compatibility serial, including its 1900 leap-year quirk.
FILETIME_EPOCH = datetime(1601, 1, 1, tzinfo=timezone.utc)


def unix_timestamp_to_date(value: int | float) -> date:
    return (UNIX_EPOCH + timedelta(seconds=value)).date()


def date_to_unix_timestamp(value: date) -> int:
    return int((datetime(value.year, value.month, value.day, tzinfo=timezone.utc) - UNIX_EPOCH).total_seconds())


def excel_serial_to_date(value: int | float) -> date:
    serial = int(value)
    if serial == 60:
        raise ValueError("Excel serial 60 represents the nonexistent date 1900-02-29")
    return EXCEL_EPOCH + timedelta(days=serial + (1 if 0 <= serial < 60 else 0))


def date_to_excel_serial(value: date) -> int:
    serial = (value - EXCEL_EPOCH).days
    return serial - (1 if value < date(1900, 3, 1) else 0)


def filetime_to_datetime(value: int) -> datetime:
    if value < 0:
        raise ValueError("FILETIME ticks cannot be negative")
    return FILETIME_EPOCH + timedelta(microseconds=value // 10)


def datetime_to_filetime(value: datetime) -> int:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    delta = value.astimezone(timezone.utc) - FILETIME_EPOCH
    return (delta.days * 86400 + delta.seconds) * 10_000_000 + delta.microseconds * 10


def date_to_filetime(value: date) -> int:
    return datetime_to_filetime(datetime(value.year, value.month, value.day, tzinfo=timezone.utc))


def parse_iso_date(value: str) -> date:
    return date.fromisoformat(value.strip())
