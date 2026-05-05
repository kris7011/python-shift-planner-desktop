import csv
from models import Employee, Shift

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
            date = row["date"]
            shift_type = row["shift_type"]
            required_skill = row["required_skill"]
            required_staff = int(row["required_staff"])
            priority = int(row["priority"])
            
            shifts.append(
                Shift(
                    date=date,
                    shift_type=shift_type,
                    required_skill=required_skill,
                    required_staff=required_staff,
                    priority=priority,
                )
            )
    
    return shifts