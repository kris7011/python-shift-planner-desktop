from config import (
    WORKLOAD_RATIO_LIMIT,
    AVERAGE_SCORE_LIMIT,
    HIGH_RISK_FLAG_COUNT,
    EMPLOYEES_CSV_PATH,
    SHIFTS_CSV_PATH
)
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
    print_unassigned_shift_reasons,
)

def main() -> None:
    employees = load_employees_from_csv(EMPLOYEES_CSV_PATH)
    shifts = load_shifts_from_csv(SHIFTS_CSV_PATH)
    assigned = assign_shifts(
        employees, 
        shifts, 
        workload_ratio_threshold=WORKLOAD_RATIO_LIMIT, 
        average_score_threshold=AVERAGE_SCORE_LIMIT,
        high_risk_flag_count=HIGH_RISK_FLAG_COUNT
    )

    print_assigned_shifts(assigned)
    print_shift_summary(employees)
    print_unassigned_shifts(assigned)
    print_critical_unassigned_shifts(assigned)
    print_employee_details(employees)
    print_employees_at_capacity(employees)
    print_overloaded_employees(employees, threshold=WORKLOAD_RATIO_LIMIT)
    print_workload_score_report(employees)
    print_average_workload_score(employees)
    print_average_workload_ranking(employees)
    print_risk_report(
        employees,
        workload_ratio_threshold=WORKLOAD_RATIO_LIMIT,
        average_score_threshold=AVERAGE_SCORE_LIMIT,
        high_risk_flag_count=HIGH_RISK_FLAG_COUNT,
    )
    print_unassigned_shift_reasons(shifts, employees)
    
if __name__ == "__main__":
    main()