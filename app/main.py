from models import Employee, Shift
from scheduler import assign_shifts

employees = [
    Employee("Kris", 2),
    Employee("Anna", 2),
    Employee("Peter", 2)
]

shifts = [
    Shift("2026-05-05", "CT"),
    Shift("2026-05-06", "MR"),
    Shift("2026-05-07", "CT"),
    Shift("2026-05-08", "MR"),
]

assigned = assign_shifts(employees, shifts)

for shift in assigned:
    if shift.assigned_employee:
        print(f"{shift.date} -> {shift.assigned_employee.name}")
    else:
        print(f"{shift.date} -> No assignment")