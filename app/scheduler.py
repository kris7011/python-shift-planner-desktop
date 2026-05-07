from app.constants import RiskLevel
from app.models import Employee, EmployeeProfile, Shift
from app.personalized_workload import calculate_personalized_workload_score

def assign_shifts(
    employees: list[Employee],
    shifts: list[Shift],
    employee_profiles: list[EmployeeProfile] = None,
    workload_ratio_threshold: float = 0.75,
    average_score_threshold: float = 2.0,
    high_risk_flag_count: int = 2,
) -> list[Shift]:
    risk_mapping = {
        RiskLevel.LOW: 0,
        RiskLevel.MEDIUM: 1,
        RiskLevel.HIGH: 2
    }

    profiles_by_name = {
        profile.name: profile
        for profile in (employee_profiles or [])
    }

    sorted_shifts = sorted(shifts, key=lambda s: s.priority)

    for shift in sorted_shifts:
        eligible = [e for e in employees if e.can_take_shift(shift)]

        def sort_key(e: Employee):
            profile = profiles_by_name.get(e.name)

            personalized_score = (
                calculate_personalized_workload_score(shift, profile)
                if profile else shift.workload_score
            )

            return (
                risk_mapping[
                    e.get_risk_level(
                        workload_ratio_threshold,
                        average_score_threshold,
                        high_risk_flag_count,
                    )
                ],
                e.assigned_shift_count,
                personalized_score,
                len(e.skills),
            )

        sorted_employees = sorted(eligible, key=sort_key)

        for employee in sorted_employees:
            if shift.is_fully_staffed:
                break

            shift.assigned_employees.append(employee)
            employee.assigned_shifts.append(shift)

    return shifts