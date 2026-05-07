import csv
from app.constants import ShiftType
from app.models import Employee, Shift, EmployeeProfile

def parse_int(value: str | None, default: int, field_name: str) -> int:
    """Helper to validate integers from CSV strings."""
    if not value or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Field '{field_name}' must be a number, but got: '{value}'")

def load_employees_from_csv(file_path: str) -> list[Employee]:
    employees = []
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row.get("name", "").strip()
            skills_raw = row.get("skills", "").strip()
            
            if not name:
                raise ValueError(f"Invalid CSV row: 'name' cannot be empty. Row context: {row}")
            if not skills_raw:
                raise ValueError(f"Invalid CSV row: 'skills' cannot be empty. Row context: {row}")
            
            max_shifts_raw = row.get("max_shifts", "").strip()

            if not max_shifts_raw:
                raise ValueError(f"Invalid CSV row: 'max_shifts' cannot be empty. Row context: {row}")

            max_shifts = parse_int(max_shifts_raw, 0, "max_shifts")
            skills = [skill.strip() for skill in skills_raw.split(";") if skill.strip()]
            
            if not skills:
                raise ValueError(f"Invalid CSV row: Employee '{name}' must have at least one skill.")

            employees.append(Employee(name, max_shifts, skills))

    return employees

def load_shifts_from_csv(file_path: str) -> list[Shift]:
    shifts = []
    
    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            date = row.get("date", "").strip()
            shift_type_raw = row.get("shift_type", "").strip()
            required_skill = row.get("required_skill", "").strip()
            
            if not date:
                raise ValueError(f"Invalid CSV row: 'date' cannot be empty. Row context: {row}")
            if not shift_type_raw:
                raise ValueError(f"Invalid CSV row: 'shift_type' cannot be empty. Row context: {row}")
            if not required_skill:
                raise ValueError(f"Invalid CSV row: 'required_skill' cannot be empty. Row context: {row}")
            
            required_staff = parse_int(row.get("required_staff"), 1, "required_staff")
            priority = parse_int(row.get("priority"), 2, "priority")
            workload_score = parse_int(row.get("workload_score"), 1, "workload_score")
            
            try:
                shift = Shift(
                    date=date,
                    shift_type=shift_type_raw,
                    required_skill=required_skill,
                    required_staff=required_staff,
                    priority=priority,
                    workload_score=workload_score,
                )
                shifts.append(shift)
            except ValueError as e:
                raise ValueError(f"Error in CSV row for date {date}: {e}")
    
    return shifts

def parse_float(value: str | None, default: float, field_name: str) -> float:
    if not value or value.strip() == "":
        return default

    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Field '{field_name}' must be a number, but got: '{value}'")


def load_employee_profiles_from_csv(file_path: str) -> list[EmployeeProfile]:
    profiles = []

    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            employee_id = row.get("employee_id", "").strip()
            name = row.get("name", "").strip()
            preferred_shift = row.get("preferred_shift", "").strip()

            if not employee_id:
                raise ValueError(f"Invalid CSV row: 'employee_id' cannot be empty. Row context: {row}")

            if not name:
                raise ValueError(f"Invalid CSV row: 'name' cannot be empty. Row context: {row}")

            if not preferred_shift:
                raise ValueError(f"Invalid CSV row: 'preferred_shift' cannot be empty. Row context: {row}")

            try:
                preferred_shift_type = ShiftType(preferred_shift.title())
            except ValueError:
                raise ValueError(f"Invalid preferred_shift '{preferred_shift}' for employee '{name}'")

            profile = EmployeeProfile(
                employee_id=employee_id,
                name=name,
                night_tolerance=parse_float(row.get("night_tolerance"), 0.5, "night_tolerance"),
                weekend_tolerance=parse_float(row.get("weekend_tolerance"), 0.5, "weekend_tolerance"),
                late_tolerance=parse_float(row.get("late_tolerance"), 0.5, "late_tolerance"),
                max_weekly_load=parse_float(row.get("max_weekly_load"), 37.0, "max_weekly_load"),
                preferred_shift=preferred_shift_type,
            )

            profiles.append(profile)

    return profiles