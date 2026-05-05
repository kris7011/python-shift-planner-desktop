from scheduler import assign_shifts
from csv_loader import load_employees_from_csv, load_shifts_from_csv
from reporting import (
    print_assigned_shifts,
    print_shift_summary,
    print_unassigned_shifts,
    print_critical_unassigned_shifts,
)

employees = load_employees_from_csv("data/employees.csv")
shifts = load_shifts_from_csv("data/shifts.csv")
assigned = assign_shifts(employees, shifts)

print_assigned_shifts(assigned)
print_shift_summary(employees)
print_unassigned_shifts(assigned)
print_critical_unassigned_shifts(assigned)