from models import Employee, Shift
from scheduler import assign_shifts

employees = [
    Employee("Kris", 2, ["CT", "MR"]),
    Employee("Anna", 2, ["CT"]),
    Employee("Peter", 2, ["MR"]),
]

shifts = [
    Shift("2026-05-05", "Day", "CT"),
    Shift("2026-05-06", "Evening", "MR"),
    Shift("2026-05-07", "Day", "CT"),
    Shift("2026-05-08", "Night", "MR"),
    Shift("2026-05-09", "Day", "UL"),
]

assigned = assign_shifts(employees, shifts)

for shift in assigned:
    if shift.assigned_employee:
        print(f"{shift.date} {shift.shift_type} ({shift.required_skill}) -> {shift.assigned_employee.name}")
    else:
        print(f"{shift.date} {shift.shift_type} ({shift.required_skill}) -> No assignment")