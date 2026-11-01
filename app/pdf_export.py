"""PDF export of the current schedule.

The file is written to a temporary file next to the target and then moved into place, so a failed
export never leaves a half-written PDF or damages an existing file. An existing file is only
replaced when the caller says so (the GUI asks first through the save dialog).
"""

import os
import tempfile
from datetime import date, datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models import Employee, Shift
from app.schedule_editor import SHIFT_TYPE_ORDER

_MISSING_COLOUR = colors.HexColor("#fde2e2")
_HEADER_COLOUR = colors.HexColor("#1f3a5f")


def export_schedule_pdf(
    target: str | Path,
    shifts: list[Shift],
    employees: list[Employee],
    generated_at: datetime,
    manual_edit_count: int = 0,
    overwrite: bool = False,
    compress: bool = True,
) -> Path:
    target = Path(target)

    if target.suffix.lower() != ".pdf":
        raise ValueError("The file name must end with .pdf.")

    if target.exists() and not overwrite:
        raise FileExistsError(f"{target} already exists.")

    file_descriptor, temporary_name = tempfile.mkstemp(suffix=".pdf.tmp", dir=target.parent)
    os.close(file_descriptor)

    try:
        _build(Path(temporary_name), shifts, employees, generated_at, manual_edit_count, compress)
        os.replace(temporary_name, target)
    except BaseException:
        Path(temporary_name).unlink(missing_ok=True)
        raise

    return target


def _sort_key(shift: Shift):
    return (date.fromisoformat(shift.date), SHIFT_TYPE_ORDER.index(shift.shift_type), shift.required_skill)


def _build(
    path: Path,
    shifts: list[Shift],
    employees: list[Employee],
    generated_at: datetime,
    manual_edit_count: int,
    compress: bool,
) -> None:
    styles = getSampleStyleSheet()
    ordered = sorted(shifts, key=_sort_key)
    missing = [shift for shift in ordered if not shift.is_fully_staffed]

    first_day = ordered[0].date if ordered else "-"
    last_day = ordered[-1].date if ordered else "-"

    story = [
        Paragraph("Vagtplan", styles["Title"]),
        Paragraph(f"Periode: {first_day} til {last_day}", styles["Normal"]),
        Paragraph(f"Udskrevet: {generated_at:%Y-%m-%d %H:%M}", styles["Normal"]),
        Paragraph(
            f"{len(ordered)} vagter, {len(ordered) - len(missing)} fuldt bemandede, "
            f"{len(missing)} mangler personale. Manuelle ændringer: {manual_edit_count}.",
            styles["Normal"],
        ),
        Spacer(1, 6 * mm),
        Paragraph("Vagter", styles["Heading2"]),
        _schedule_table(ordered, styles["BodyText"]),
        Spacer(1, 6 * mm),
        Paragraph("Medarbejdere", styles["Heading2"]),
        _employee_table(employees),
    ]

    document = SimpleDocTemplate(
        str(path),
        pagesize=landscape(A4),
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="Vagtplan",
        author="Python Shift Planner Desktop",
        pageCompression=1 if compress else 0,
    )
    document.build(story)


def _schedule_table(shifts: list[Shift], cell_style) -> Table:
    rows = [["Dato", "Vagt", "Kompetence", "Tildelt", "Bemanding", "Prioritet"]]
    missing_rows = []

    for index, shift in enumerate(shifts, start=1):
        names = ", ".join(employee.name for employee in shift.assigned_employees) or "Ingen"
        staffing = f"{len(shift.assigned_employees)}/{shift.required_staff}"

        if not shift.is_fully_staffed:
            staffing += f" (mangler {shift.missing_staff_count})"
            missing_rows.append(index)

        # A paragraph wraps long name lists inside the column.
        rows.append(
            [shift.date, shift.shift_type.display_name, shift.required_skill, Paragraph(escape(names), cell_style), staffing, str(shift.priority)]
        )

    table = Table(rows, repeatRows=1, colWidths=[28 * mm, 22 * mm, 28 * mm, 110 * mm, 40 * mm, 20 * mm])
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), _HEADER_COLOUR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    style.extend(("BACKGROUND", (0, row), (-1, row), _MISSING_COLOUR) for row in missing_rows)
    table.setStyle(TableStyle(style))

    return table


def _employee_table(employees: list[Employee]) -> Table:
    rows = [["Medarbejder", "Vagter", "Maks.", "Belastningsscore", "Kompetencer"]]

    for employee in sorted(employees, key=lambda item: item.name.casefold()):
        rows.append(
            [
                employee.name,
                str(employee.assigned_shift_count),
                str(employee.max_shifts),
                str(employee.total_workload_score),
                ", ".join(employee.skills),
            ]
        )

    table = Table(rows, repeatRows=1, colWidths=[50 * mm, 22 * mm, 22 * mm, 38 * mm, 80 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _HEADER_COLOUR),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ]
        )
    )

    return table
