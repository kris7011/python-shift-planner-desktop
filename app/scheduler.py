from app.constants import RiskLevel
from app.models import Employee, Shift

def assign_shifts(
    employees: list[Employee],
    shifts: list[Shift],
    workload_ratio_threshold: float = 0.75,
    average_score_threshold: float = 2.0,
    high_risk_flag_count: int = 2,
) -> list[Shift]:
    risk_mapping = {
        RiskLevel.LOW: 0,
        RiskLevel.MEDIUM: 1,
        RiskLevel.HIGH: 2
    }
    
    sorted_shifts = sorted(shifts, key=lambda s: s.priority)
    
    for shift in sorted_shifts:
        sorted_employees = sorted(
            employees,
            key=lambda e: (
                risk_mapping[
                    e.get_risk_level(
                        workload_ratio_threshold,
                        average_score_threshold,
                        high_risk_flag_count,
                    )
                ],
                e.total_workload_score,
                e.assigned_shift_count,
                len(e.skills)
            )
        )

        for employee in sorted_employees:
            if shift.is_fully_staffed:
                break
            
            if employee.can_take_shift(shift):
                shift.assigned_employees.append(employee)
                employee.assigned_shifts.append(shift)

    return shifts