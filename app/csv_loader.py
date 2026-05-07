import csv
from app.models import Employee, Shift

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
            name = row["name"]
            max_shifts = int(row["max_shifts"])
            skills = [skill.strip() for skill in row["skills"].split(";")]
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