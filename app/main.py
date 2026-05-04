from models import Employee, Shift
from scheduler import assign_shifts
from reporting import print_assigned_shifts, print_shift_summary, print_unassigned_shifts

employees = [
    Employee("Kris", 3, ["CT", "MR"]),
    Employee("Anna", 3, ["CT"]),
    Employee("Peter", 3, ["MR"]),
]

shifts = [
    Shift("2026-05-05", "Day", "CT", required_staff=2),
    Shift("2026-05-05", "Evening", "MR"),
    Shift("2026-05-06", "Day", "CT"),
    Shift("2026-05-06", "Evening", "MR"),
    Shift("2026-05-07", "Day", "CT"),
    Shift("2026-05-08", "Night", "MR", priority=1),
    Shift("2026-05-09", "Day", "MR"),
    Shift("2026-05-09", "Day", "UL", priority=1),
]

assigned = assign_shifts(employees, shifts)

print_assigned_shifts(assigned)
print_shift_summary(employees)
print_unassigned_shifts(assigned)