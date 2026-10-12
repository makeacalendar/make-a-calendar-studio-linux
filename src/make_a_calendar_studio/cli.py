"""Command-line entry point for headless calendar work."""

from __future__ import annotations

import argparse
import calendar
import json
from datetime import date

from .calendar_engine import month_grid
from .converters import (
    excel_serial_to_date,
    filetime_to_datetime,
    unix_timestamp_to_date,
)
from .exporters import export_csv, export_ics, export_json, export_pdf, export_svg
from .holidays import federal_holidays
from .scheduling import business_days, fiscal_months, payroll_dates, retail_periods, shift_days


def _date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from error


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="make-calendar-studio", description="Offline calendar and schedule tools"
    )
    sub = root.add_subparsers(dest="command", required=True)
    cal = sub.add_parser("calendar", help="print a month grid")
    cal.add_argument("year", type=int)
    cal.add_argument("month", type=int)
    cal.add_argument("--week-start", choices=("monday", "sunday"), default="monday")
    work = sub.add_parser("business-days", help="count weekdays in an inclusive range")
    work.add_argument("start", type=_date)
    work.add_argument("end", type=_date)
    work.add_argument("--holidays", action="store_true", help="exclude US federal observed holidays")
    fiscal = sub.add_parser("fiscal", help="show Sunday-nearest-February retail periods")
    fiscal.add_argument("year", type=int)
    fiscal.add_argument("--pattern", choices=("4-4-5", "4-5-4", "5-4-4"), default="4-4-5")
    fiscal_month = sub.add_parser("fiscal-months", help="show civil fiscal months from a chosen start month")
    fiscal_month.add_argument("year", type=int)
    fiscal_month.add_argument("--start-month", type=int, choices=range(1, 13), default=10)
    payroll = sub.add_parser("payroll", help="list recurring pay dates")
    payroll.add_argument("start", type=_date)
    payroll.add_argument("end", type=_date)
    payroll.add_argument(
        "--frequency", choices=("weekly", "biweekly", "semimonthly", "monthly"), default="biweekly"
    )
    payroll.add_argument("--anchor", type=_date)
    shifts = sub.add_parser("shifts", help="list a repeating work/off pattern")
    shifts.add_argument("start", type=_date)
    shifts.add_argument("end", type=_date)
    shifts.add_argument("--anchor", type=_date, required=True)
    shifts.add_argument("--pattern", choices=("4-on-3-off", "5-on-2-off", "2-2-3"), default="2-2-3")
    convert = sub.add_parser("convert", help="convert common date serials")
    convert.add_argument("kind", choices=("unix", "excel", "filetime"))
    convert.add_argument("value", type=int)
    export = sub.add_parser("export", help="export a month as PDF, SVG, CSV, or JSON")
    export.add_argument("year", type=int)
    export.add_argument("month", type=int)
    export.add_argument("path")
    export.add_argument("--format", choices=("pdf", "svg", "csv", "json"), default="pdf")
    export.add_argument(
        "--theme",
        choices=(
            "Editorial Minimal",
            "Corporate Planner",
            "Academic Weekly",
            "Classic Monochrome",
            "Modern Seasonal",
        ),
        default="Editorial Minimal",
    )
    ics = sub.add_parser("ics", help="export a simple all-day event from JSON input")
    ics.add_argument("path")
    ics.add_argument("--date", type=_date, required=True)
    ics.add_argument("--title", required=True)
    return root


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    if args.command == "calendar":
        week_start = 0 if args.week_start == "monday" else 6
        grid = month_grid(args.year, args.month, week_start, fixed_six_rows=True)
        print(f"{calendar.month_name[args.month]} {args.year}")
        weekdays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        ordered = weekdays[week_start:] + weekdays[:week_start]
        print(" ".join(f"{name:>3}" for name in ordered))
        for row in grid:
            print(" ".join(f"{cell.day.day:3}" if cell.day and cell.in_month else "   " for cell in row))
    elif args.command == "business-days":
        excluded = {}
        if args.holidays:
            for year in range(args.start.year, args.end.year + 1):
                excluded.update(federal_holidays(year))
        print(business_days(args.start, args.end, holidays=excluded))
    elif args.command == "fiscal":
        print(
            json.dumps(
                {
                    "year": args.year,
                    "pattern": args.pattern,
                    "periods": [
                        {"period": n, "start": s.isoformat(), "end": e.isoformat()}
                        for n, s, e in retail_periods(args.year, args.pattern)
                    ],
                },
                indent=2,
            )
        )
    elif args.command == "fiscal-months":
        print(
            json.dumps(
                {
                    "start_year": args.year,
                    "start_month": args.start_month,
                    "periods": [
                        {"period": n, "start": s.isoformat(), "end": e.isoformat()}
                        for n, s, e in fiscal_months(args.year, args.start_month)
                    ],
                },
                indent=2,
            )
        )
    elif args.command == "payroll":
        print(
            "\n".join(
                d.isoformat() for d in payroll_dates(args.start, args.end, args.frequency, anchor=args.anchor)
            )
        )
    elif args.command == "shifts":
        print(
            "\n".join(
                f"{day.isoformat()} {'WORK' if work else 'OFF'}"
                for day, work in shift_days(args.start, args.end, anchor=args.anchor, pattern=args.pattern)
            )
        )
    elif args.command == "convert":
        result = {
            "unix": lambda: unix_timestamp_to_date(args.value).isoformat(),
            "excel": lambda: excel_serial_to_date(args.value).isoformat(),
            "filetime": lambda: filetime_to_datetime(args.value).isoformat(),
        }[args.kind]()
        print(result)
    elif args.command == "export":
        if args.format == "pdf":
            result = export_pdf(args.path, args.year, args.month, theme=args.theme)
        elif args.format == "svg":
            result = export_svg(args.path, args.year, args.month, theme=args.theme)
        elif args.format == "csv":
            result = export_csv(args.path, args.year, args.month, holidays=federal_holidays(args.year))
        else:
            result = export_json(args.path, args.year, args.month, holidays=federal_holidays(args.year))
        print(result)
    elif args.command == "ics":
        print(export_ics(args.path, [{"date": args.date.isoformat(), "title": args.title}]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
