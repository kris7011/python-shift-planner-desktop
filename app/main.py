from models import Shift
from scheduler import assign_shifts
from csv_loader import load_employees_from_csv
from reporting import (
    print_assigned_shifts,
    print_shift_summary,
    print_unassigned_shifts,
    print_critical_unassigned_shifts,
)

employees = load_employees_from_csv("data/employees.csv")

shifts = [
    Shift("2026-05-05", "Day", "CT"),
    Shift("2026-05-05", "Evening", "MR"),
    Shift("2026-05-06", "Day", "CT"),
    Shift("2026-05-06", "Evening", "MR"),
    Shift("2026-05-07", "Day", "CT"),
    Shift("2026-05-08", "Night", "MR"),
    Shift("2026-05-09", "Day", "MR"),
    Shift("2026-05-09", "Day", "UL", priority=1),
]

assigned = assign_shifts(employees, shifts)

print_assigned_shifts(assigned)
print_shift_summary(employees)
print_unassigned_shifts(assigned)
print_critical_unassigned_shifts(assigned)