import csv
from models import Employee

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