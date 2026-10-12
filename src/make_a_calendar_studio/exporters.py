"""Real vector SVG/PDF and interoperable text calendar exports."""

from __future__ import annotations

import calendar
import json
import uuid
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Mapping

from .calendar_engine import month_grid

PAPER = {"Letter": (612.0, 792.0), "A4": (595.28, 841.89), "A3": (841.89, 1190.55)}
THEMES = {
    "Editorial Minimal": {
        "ink": "#172b3a",
        "accent": "#287f78",
        "muted": "#74818a",
        "rule": "#cbd4d5",
        "wash": "#f4f6f4",
    },
    "Corporate Planner": {
        "ink": "#17304b",
        "accent": "#3276a8",
        "muted": "#64758a",
        "rule": "#b9c6d2",
        "wash": "#eaf0f5",
    },
    "Academic Weekly": {
        "ink": "#29364a",
        "accent": "#8b5b37",
        "muted": "#687383",
        "rule": "#b7b1a8",
        "wash": "#f5efe5",
    },
    "Classic Monochrome": {
        "ink": "#111111",
        "accent": "#333333",
        "muted": "#555555",
        "rule": "#777777",
        "wash": "#eeeeee",
    },
    "Modern Seasonal": {
        "ink": "#253b39",
        "accent": "#497f70",
        "muted": "#6a7d78",
        "rule": "#c4d1c9",
        "wash": "#edf4ef",
    },
}


def _ascii(value: str) -> str:
    value = value.replace("—", "-").replace("–", "-").replace("’", "'").replace("•", "*")
    return value.encode("latin-1", "replace").decode("latin-1")


def _pdf_escape(value: str) -> str:
    return _ascii(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _svg_scene(
    year: int,
    month: int,
    *,
    title: str = "",
    week_start: int = 0,
    theme: str = "Editorial Minimal",
    paper: str = "Letter",
    landscape: bool = False,
    notes: str = "",
    holidays: Mapping[date, str] | None = None,
    grayscale: bool = False,
    large_print: bool = False,
    margin: float = 34.0,
    show_week_numbers: bool = False,
    weekend_shading: bool = True,
    adjacent_dates: bool = True,
) -> tuple[float, float, str]:
    if theme not in THEMES:
        raise ValueError("unknown print theme")
    if paper not in PAPER:
        raise ValueError("paper must be Letter, A4, or A3")
    width, height = PAPER[paper]
    if landscape:
        width, height = height, width
    colors = dict(THEMES[theme])
    if grayscale:
        colors = {
            key: (
                "#111111"
                if key in ("ink", "accent")
                else "#666666"
                if key == "muted"
                else "#bbbbbb"
                if key == "rule"
                else "#f3f3f3"
            )
            for key in colors
        }
    if margin < 14 or margin > min(width, height) / 3:
        raise ValueError("margin must be between 14 points and one third of the shorter page edge")
    grid_margin = margin + (28 if show_week_numbers else 0)
    top = 62.0
    grid_top = top + 36
    grid_height = min(height - grid_top - margin - (42 if notes else 12), width - 2 * grid_margin)
    cell_h = grid_height / 7.0
    cell_w = (width - 2 * grid_margin) / 7.0
    rows = month_grid(year, month, week_start, fixed_six_rows=True, adjacent_dates=adjacent_dates)
    month_label = f"{calendar.month_name[month]} {year}"
    heading = title.strip() or month_label
    paper_color = "#fbfcfa" if theme == "Modern Seasonal" else "#ffffff"
    body = [f'<rect width="{width:.2f}" height="{height:.2f}" fill="{paper_color}"/>']
    if theme == "Corporate Planner":
        body.append(
            f'<rect x="{margin}" y="{top - 25:.2f}" width="{width - 2 * margin:.2f}" height="42" fill="{colors["accent"]}"/>'
        )
        body.append(
            f'<text x="{margin + 12}" y="{top:.2f}" font-family="sans-serif" font-size="22" font-weight="600" fill="#ffffff">{_xml(heading)}</text>'
        )
        body.append(
            f'<text x="{margin + 12}" y="{top + 12:.2f}" font-family="sans-serif" font-size="8" letter-spacing="1.2" fill="#ffffff">{_xml(month_label.upper())}</text>'
        )
    else:
        if theme == "Modern Seasonal":
            body.append(
                f'<rect x="{margin}" y="{top - 24:.2f}" width="{width - 2 * margin:.2f}" height="35" fill="{colors["wash"]}"/>'
            )
            body.append(
                f'<rect x="{margin}" y="{top - 24:.2f}" width="5" height="35" fill="{colors["accent"]}"/>'
            )
        body.append(
            f'<text x="{margin}" y="{top:.2f}" font-family="sans-serif" font-size="22" font-weight="600" fill="{colors["ink"]}">{_xml(heading)}</text>'
        )
        body.append(
            f'<text x="{margin}" y="{top + 21:.2f}" font-family="sans-serif" font-size="9" letter-spacing="1.2" fill="{colors["muted"]}">{_xml(month_label.upper())}</text>'
        )
    weekdays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    ordered = weekdays[week_start:] + weekdays[:week_start]
    for col, weekday in enumerate(ordered):
        x = grid_margin + col * cell_w
        if weekend_shading and (week_start + col) % 7 in (5, 6) and theme != "Classic Monochrome":
            body.append(
                f'<rect x="{x:.2f}" y="{grid_top + cell_h:.2f}" width="{cell_w:.2f}" height="{cell_h * 6:.2f}" fill="{colors["wash"]}"/>'
            )
        if theme == "Corporate Planner":
            body.append(
                f'<rect x="{x:.2f}" y="{grid_top + cell_h - 24:.2f}" width="{cell_w:.2f}" height="24" fill="{colors["accent"]}"/>'
            )
        header_color = "#ffffff" if theme == "Corporate Planner" else colors["muted"]
        body.append(
            f'<text x="{x + 5:.2f}" y="{grid_top + cell_h - 8:.2f}" font-family="sans-serif" font-size="8" font-weight="600" letter-spacing="0.7" fill="{header_color}">{weekday.upper()}</text>'
        )
    for row_index, row in enumerate(rows):
        y = grid_top + cell_h * (row_index + 1)
        rule_width = 1.25 if theme == "Classic Monochrome" else 0.75 if theme == "Corporate Planner" else 0.45
        body.append(
            f'<line x1="{grid_margin:.2f}" y1="{y:.2f}" x2="{width - grid_margin:.2f}" y2="{y:.2f}" stroke="{colors["rule"]}" stroke-width="{rule_width}"/>'
        )
        if show_week_numbers and row[0].day:
            week = row[0].day.isocalendar().week
            body.append(
                f'<text x="{margin:.2f}" y="{y + 18:.2f}" font-family="sans-serif" font-size="7" font-weight="600" fill="{colors["muted"]}">W{week:02d}</text>'
            )
        for col, cell in enumerate(row):
            x = grid_margin + col * cell_w
            if col and theme != "Editorial Minimal":
                vertical_width = (
                    1.15 if theme == "Classic Monochrome" else 0.65 if theme == "Corporate Planner" else 0.45
                )
                body.append(
                    f'<line x1="{x:.2f}" y1="{grid_top + cell_h:.2f}" x2="{x:.2f}" y2="{grid_top + cell_h * 7:.2f}" stroke="{colors["rule"]}" stroke-width="{vertical_width}"/>'
                )
            if cell.day is None:
                continue
            color = colors["ink"] if cell.in_month else "#aab1b4"
            number_size = 15 if large_print else 11
            weight = ' font-weight="600"' if theme in ("Corporate Planner", "Classic Monochrome") else ""
            body.append(
                f'<text x="{x + 6:.2f}" y="{grid_top + cell_h * (row_index + 1) + 18:.2f}" font-family="sans-serif" font-size="{number_size}"{weight} fill="{color}">{cell.day.day}</text>'
            )
            if theme == "Academic Weekly" and cell.in_month:
                for note_line in (42, 57):
                    y_line = grid_top + cell_h * (row_index + 1) + note_line
                    body.append(
                        f'<line x1="{x + 6:.2f}" y1="{y_line:.2f}" x2="{x + cell_w - 6:.2f}" y2="{y_line:.2f}" stroke="{colors["rule"]}" stroke-width="0.35"/>'
                    )
            holiday = (holidays or {}).get(cell.day)
            if holiday and cell.in_month:
                body.append(
                    f'<text x="{x + 6:.2f}" y="{grid_top + cell_h * (row_index + 1) + 31:.2f}" font-family="sans-serif" font-size="7" fill="{colors["accent"]}">{_xml(holiday[:22])}</text>'
                )
    outer_width = 1.3 if theme == "Classic Monochrome" else 0.8 if theme == "Corporate Planner" else 0.6
    body.append(
        f'<rect x="{grid_margin:.2f}" y="{grid_top + cell_h:.2f}" width="{width - 2 * grid_margin:.2f}" height="{cell_h * 6:.2f}" fill="none" stroke="{colors["rule"]}" stroke-width="{outer_width}"/>'
    )
    if notes:
        note_y = height - margin - 25
        body.append(
            f'<line x1="{margin:.2f}" y1="{note_y:.2f}" x2="{width - margin:.2f}" y2="{note_y:.2f}" stroke="{colors["rule"]}" stroke-width="0.6"/>'
        )
        body.append(
            f'<text x="{margin:.2f}" y="{note_y + 16:.2f}" font-family="sans-serif" font-size="8" fill="{colors["muted"]}">{_xml(notes[:120])}</text>'
        )
    if theme == "Academic Weekly":
        body.append(
            f'<text x="{margin:.2f}" y="{height - margin / 2:.2f}" font-family="sans-serif" font-size="7" fill="{colors["muted"]}">WEEKLY PLANNING  ·  NOTES AND APPOINTMENTS</text>'
        )
    elif theme == "Modern Seasonal":
        body.append(
            f'<rect x="{width - margin - 22:.2f}" y="{top - 15:.2f}" width="22" height="4" rx="2" fill="{colors["accent"]}"/>'
        )
    return width, height, "\n".join(body)


def _xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def export_svg(path: str | Path, year: int, month: int, **options) -> Path:
    width, height, body = _svg_scene(year, month, **options)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.2f}pt" height="{height:.2f}pt" viewBox="0 0 {width:.2f} {height:.2f}">\n{body}\n</svg>\n',
        encoding="utf-8",
    )
    ET.parse(output)
    return output


def export_pdf(path: str | Path, year: int, month: int, **options) -> Path:
    """Create a one-page vector PDF using standard PDF drawing operators."""
    width, height, body = _svg_scene(year, month, **options)
    theme = THEMES[options.get("theme", "Editorial Minimal")]
    if options.get("grayscale"):
        theme = {
            key: "#111111"
            if key in ("ink", "accent")
            else "#666666"
            if key == "muted"
            else "#bbbbbb"
            if key == "rule"
            else "#f3f3f3"
            for key in theme
        }
    margin = float(options.get("margin", 34.0))
    show_week_numbers = options.get("show_week_numbers", False)
    weekend_shading = options.get("weekend_shading", True)
    adjacent_dates = options.get("adjacent_dates", True)
    grid_margin = margin + (28 if show_week_numbers else 0)
    top = 62.0
    grid_top = top + 36
    grid_height = min(
        height - grid_top - margin - (42 if options.get("notes") else 12), width - 2 * grid_margin
    )
    cell_h, cell_w = grid_height / 7, (width - 2 * grid_margin) / 7
    week_start = options.get("week_start", 0)
    rows = month_grid(year, month, week_start, fixed_six_rows=True, adjacent_dates=adjacent_dates)
    commands = []

    def rgb(hex_color):
        return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5))

    def set_fill(color):
        r, g, b = rgb(color)
        commands.append(f"{r:.3f} {g:.3f} {b:.3f} rg")

    def set_stroke(color):
        r, g, b = rgb(color)
        commands.append(f"{r:.3f} {g:.3f} {b:.3f} RG")

    def text(x, y_top, value, size, color, bold=False):
        set_fill(color)
        font = "F2" if bold else "F1"
        commands.append(
            f"BT /{font} {size:.2f} Tf 1 0 0 1 {x:.2f} {height - y_top:.2f} Tm ({_pdf_escape(value)}) Tj ET"
        )

    def line(x1, y1, x2, y2, color, thickness=0.6):
        set_stroke(color)
        commands.append(f"{thickness:.2f} w {x1:.2f} {height - y1:.2f} m {x2:.2f} {height - y2:.2f} l S")

    def rect(x, y, w, h, color):
        set_fill(color)
        commands.append(f"{x:.2f} {height - y - h:.2f} {w:.2f} {h:.2f} re f")

    if options.get("grayscale"):
        colors = {
            key: "#111111"
            if key in ("ink", "accent")
            else "#666666"
            if key == "muted"
            else "#bbbbbb"
            if key == "rule"
            else "#f3f3f3"
            for key in theme
        }
    else:
        colors = theme
    title = options.get("title", "").strip() or f"{calendar.month_name[month]} {year}"
    if options.get("theme") == "Modern Seasonal":
        rect(margin, top - 24, width - 2 * margin, 35, colors["wash"])
        rect(margin, top - 24, 5, 35, colors["accent"])
    if options.get("theme") == "Corporate Planner":
        rect(margin, top - 25, width - 2 * margin, 42, colors["accent"])
        text(margin + 12, top, title, 22, "#ffffff", True)
        text(margin + 12, top + 12, f"{calendar.month_name[month].upper()} {year}", 8, "#ffffff")
    else:
        text(margin, top, title, 22, colors["ink"], True)
        text(margin, top + 20, f"{calendar.month_name[month].upper()} {year}", 9, colors["muted"])
    weekdays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    ordered = weekdays[week_start:] + weekdays[:week_start]
    for col, wd in enumerate(ordered):
        x = grid_margin + col * cell_w
        if (
            weekend_shading
            and (week_start + col) % 7 in (5, 6)
            and options.get("theme") != "Classic Monochrome"
        ):
            rect(x, grid_top + cell_h, cell_w, cell_h * 6, colors["wash"])
        if options.get("theme") == "Corporate Planner":
            rect(x, grid_top + cell_h - 24, cell_w, 24, colors["accent"])
        text(
            x + 5,
            grid_top + cell_h - 8,
            wd.upper(),
            8,
            "#ffffff" if options.get("theme") == "Corporate Planner" else colors["muted"],
            True,
        )
    holiday_map = options.get("holidays") or {}
    for ri, row in enumerate(rows):
        y = grid_top + cell_h * (ri + 1)
        rule_width = (
            1.25
            if options.get("theme") == "Classic Monochrome"
            else 0.75
            if options.get("theme") == "Corporate Planner"
            else 0.45
        )
        line(grid_margin, y, width - grid_margin, y, colors["rule"], rule_width)
        if show_week_numbers and row[0].day:
            text(margin, y + 18, f"W{row[0].day.isocalendar().week:02d}", 7, colors["muted"], True)
        for col, cell in enumerate(row):
            x = grid_margin + col * cell_w
            if col and options.get("theme") != "Editorial Minimal":
                vertical_width = (
                    1.15
                    if options.get("theme") == "Classic Monochrome"
                    else 0.65
                    if options.get("theme") == "Corporate Planner"
                    else 0.45
                )
                line(x, grid_top + cell_h, x, grid_top + cell_h * 7, colors["rule"], vertical_width)
            day = cell.day
            if day is None:
                continue
            text(
                x + 6,
                grid_top + cell_h * (ri + 1) + 18,
                str(day.day),
                15 if options.get("large_print") else 11,
                colors["ink"] if cell.in_month else "#aab1b4",
                options.get("theme") in ("Corporate Planner", "Classic Monochrome"),
            )
            if options.get("theme") == "Academic Weekly" and cell.in_month:
                for note_line in (42, 57):
                    line(
                        x + 6,
                        grid_top + cell_h * (ri + 1) + note_line,
                        x + cell_w - 6,
                        grid_top + cell_h * (ri + 1) + note_line,
                        colors["rule"],
                        0.35,
                    )
            if day in holiday_map and cell.in_month:
                text(x + 6, grid_top + cell_h * (ri + 1) + 31, holiday_map[day][:22], 7, colors["accent"])
    line(grid_margin, grid_top + cell_h * 7, width - grid_margin, grid_top + cell_h * 7, colors["rule"], 0.7)
    if options.get("theme") != "Editorial Minimal":
        for col in range(8):
            x = grid_margin + col * cell_w
            vertical_width = (
                1.3
                if options.get("theme") == "Classic Monochrome" and col in (0, 7)
                else 0.8
                if options.get("theme") == "Corporate Planner" and col in (0, 7)
                else 0.45
            )
            line(x, grid_top + cell_h, x, grid_top + cell_h * 7, colors["rule"], vertical_width)
    note = options.get("notes", "")
    if note:
        y = height - margin - 25
        line(margin, y, width - margin, y, colors["rule"])
        text(margin, y + 16, note[:120], 8, colors["muted"])
    content = ("\n".join(commands)).encode("latin-1")
    objects = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width:.2f} {height:.2f}] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>".encode(
            "ascii"
        )
    )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    objects.append(b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream")
    pdf = bytearray(b"%PDF-1.4\n%Calendar Studio vector export\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{i} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(pdf)
    return output


def export_csv(path: str | Path, year: int, month: int, holidays: Mapping[date, str] | None = None) -> Path:
    import csv

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("date", "weekday", "day", "in_month", "holiday"))
        for row in month_grid(year, month, 0, fixed_six_rows=True):
            for cell in row:
                if cell.day:
                    writer.writerow(
                        (
                            cell.day.isoformat(),
                            cell.day.strftime("%A"),
                            cell.day.day,
                            cell.in_month,
                            (holidays or {}).get(cell.day, ""),
                        )
                    )
    return output


def export_json(path: str | Path, year: int, month: int, holidays: Mapping[date, str] | None = None) -> Path:
    days = []
    for row in month_grid(year, month, 0, fixed_six_rows=True):
        for cell in row:
            if cell.day and cell.in_month:
                days.append(
                    {
                        "date": cell.day.isoformat(),
                        "weekday": cell.day.strftime("%A"),
                        "iso_week": cell.day.isocalendar().week,
                        "holiday": (holidays or {}).get(cell.day),
                    }
                )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"year": year, "month": month, "days": days}, indent=2) + "\n", encoding="utf-8"
    )
    return output


def _fold_ics(value: str) -> str:
    encoded = value.encode("utf-8")
    lines = []
    while len(encoded) > 75:
        cut = 75
        while cut and encoded[cut] & 0xC0 == 0x80:
            cut -= 1
        lines.append(encoded[:cut].decode("utf-8"))
        encoded = encoded[cut:]
    lines.append(encoded.decode("utf-8"))
    return "\r\n ".join(lines)


def export_ics(path: str | Path, events: Iterable[Mapping[str, str]]) -> Path:
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Make a Calendar Studio//EN", "CALSCALE:GREGORIAN"]
    for item in events:
        start = date.fromisoformat(item["date"])
        end = start + timedelta(days=1)
        title = (
            item.get("title", "Untitled event")
            .replace("\\", "\\\\")
            .replace(";", r"\;")
            .replace(",", r"\,")
            .replace("\n", r"\n")
        )
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uuid.uuid4()}@make-a-calendar-studio",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{start:%Y%m%d}",
            f"DTEND;VALUE=DATE:{end:%Y%m%d}",
            _fold_ics(f"SUMMARY:{title}"),
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")
    return output
