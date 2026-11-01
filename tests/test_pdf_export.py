import hashlib
from datetime import datetime
from pathlib import Path

import pytest

import app.pdf_export as pdf_export
from app.config import EMPLOYEE_PROFILES_CSV_PATH, EMPLOYEES_CSV_PATH, SHIFTS_CSV_PATH
from app.csv_loader import load_employee_profiles_from_csv, load_employees_from_csv, load_shifts_from_csv
from app.pdf_export import export_schedule_pdf
from app.schedule_editor import ScheduleEditor
from app.scheduler import assign_shifts

GENERATED_AT = datetime(2026, 11, 1, 10, 30)


def load_sample_schedule():
    employees = load_employees_from_csv(EMPLOYEES_CSV_PATH)
    shifts = assign_shifts(
        employees,
        load_shifts_from_csv(SHIFTS_CSV_PATH),
        employee_profiles=load_employee_profiles_from_csv(EMPLOYEE_PROFILES_CSV_PATH),
    )
    return employees, shifts


def test_export_writes_a_pdf_with_the_schedule(tmp_path):
    employees, shifts = load_sample_schedule()
    target = tmp_path / "vagtplan.pdf"

    result = export_schedule_pdf(target, shifts, employees, GENERATED_AT, manual_edit_count=2, compress=False)

    content = target.read_bytes()
    assert result == target
    assert content.startswith(b"%PDF-")
    assert b"Vagtplan" in content
    assert b"Periode: 2026-05-05 til 2026-05-11" in content
    assert b"Manuelle \\346ndringer: 2." in content  # "æ" in the PDF's WinAnsi text encoding
    for employee in employees:
        assert employee.name.encode() in content


def test_export_refuses_to_overwrite_unless_asked(tmp_path):
    employees, shifts = load_sample_schedule()
    target = tmp_path / "vagtplan.pdf"
    target.write_bytes(b"existing report")

    with pytest.raises(FileExistsError):
        export_schedule_pdf(target, shifts, employees, GENERATED_AT)

    assert target.read_bytes() == b"existing report"

    export_schedule_pdf(target, shifts, employees, GENERATED_AT, overwrite=True)

    assert target.read_bytes().startswith(b"%PDF-")


def test_a_failed_export_keeps_the_existing_file_and_leaves_no_temporary_file(tmp_path, monkeypatch):
    employees, shifts = load_sample_schedule()
    target = tmp_path / "vagtplan.pdf"
    target.write_bytes(b"existing report")

    def failing_build(path, *args):
        Path(path).write_bytes(b"half written")
        raise RuntimeError("disk full")

    monkeypatch.setattr(pdf_export, "_build", failing_build)

    with pytest.raises(RuntimeError):
        export_schedule_pdf(target, shifts, employees, GENERATED_AT, overwrite=True)

    assert target.read_bytes() == b"existing report"
    assert [path.name for path in tmp_path.iterdir()] == ["vagtplan.pdf"]


def test_export_requires_a_pdf_file_name(tmp_path):
    employees, shifts = load_sample_schedule()

    with pytest.raises(ValueError):
        export_schedule_pdf(tmp_path / "data" / "shifts.csv", shifts, employees, GENERATED_AT)


def test_editing_and_exporting_never_change_the_input_files(tmp_path):
    inputs = [Path(EMPLOYEES_CSV_PATH), Path(SHIFTS_CSV_PATH), Path(EMPLOYEE_PROFILES_CSV_PATH)]
    before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}

    employees, shifts = load_sample_schedule()
    editor = ScheduleEditor(employees, shifts)
    shift = next(shift for shift in shifts if shift.assigned_employees)
    editor.unassign(shift, shift.assigned_employees[0])
    export_schedule_pdf(tmp_path / "vagtplan.pdf", shifts, employees, GENERATED_AT, editor.edit_count)

    assert {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs} == before
