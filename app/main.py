from scheduler import assign_shifts
from csv_loader import load_employees_from_csv, load_shifts_from_csv
from reporting import (
    print_assigned_shifts,
    print_shift_summary,
    print_unassigned_shifts,
    print_critical_unassigned_shifts,
    print_employee_details,
    print_employees_at_capacity,
    print_overloaded_employees,
    print_workload_score_report,
    print_average_workload_score,
    print_average_workload_ranking,
    print_risk_report,
)

employees = load_employees_from_csv("data/employees.csv")
shifts = load_shifts_from_csv("data/shifts.csv")
assigned = assign_shifts(employees, shifts)

print_assigned_shifts(assigned)
print_shift_summary(employees)
print_unassigned_shifts(assigned)
print_critical_unassigned_shifts(assigned)
print_employee_details(employees)
print_employees_at_capacity(employees)
print_overloaded_employees(employees, threshold=0.75)
print_workload_score_report(employees)
print_average_workload_score(employees)
print_average_workload_ranking(employees)
print_risk_report(employees)