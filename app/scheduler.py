from datetime import date

from app.constants import RiskLevel, ShiftType
from app.models import Employee, EmployeeProfile, Shift
from app.personalized_workload import calculate_personalized_workload_score

def assign_shifts(
    employees: list[Employee],
    shifts: list[Shift],
    employee_profiles: list[EmployeeProfile] = None,
    workload_ratio_threshold: float = 0.75,
    average_score_threshold: float = 2.0,
    high_risk_flag_count: int = 2,
    historical_shifts_by_employee: dict[str, list[Shift]] | None = None,
    history_lookback_days: int = 28,
) -> list[Shift]:
    if history_lookback_days < 1:
        raise ValueError("history_lookback_days must be positive")

    historical = historical_shifts_by_employee or {}

    def historical_penalty(employee: Employee, shift: Shift) -> tuple[int, int]:
        target_day = date.fromisoformat(shift.date)
        same_type_count = 0
        weekend_count = 0
        is_weekend = target_day.weekday() >= 5

        for past_shift in historical.get(employee.name, []):
            past_day = date.fromisoformat(past_shift.date)
            age_days = (target_day - past_day).days
            if not (0 < age_days <= history_lookback_days):
                continue

            if (
                shift.shift_type in (ShiftType.NIGHT, ShiftType.EVENING)
                and past_shift.shift_type == shift.shift_type
            ):
                same_type_count += 1

            if is_weekend and past_day.weekday() >= 5:
                weekend_count += 1

        return (same_type_count, weekend_count)

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

        # Rotate only the final tie-breaker: risk, workload, preferences and
        # skill flexibility always take precedence. This avoids repeatedly
        # picking the first alphabetical name for otherwise equal shifts.
        names_in_order = sorted(eligible, key=lambda e: (e.name.casefold(), e.name))
        start_index = (
            (date.fromisoformat(shift.date) - date(1970, 1, 1)).days
            % len(names_in_order)
            if names_in_order else 0
        )
        rotating_rank = {
            id(employee): (index - start_index) % len(names_in_order)
            for index, employee in enumerate(names_in_order)
        }

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
                historical_penalty(e, shift),
                e.total_workload_score,
                len(e.skills),
                rotating_rank[id(e)],
            )

        sorted_employees = sorted(eligible, key=sort_key)

        for employee in sorted_employees:
            if shift.is_fully_staffed:
                break

            shift.assigned_employees.append(employee)
            employee.assigned_shifts.append(shift)

    return shifts