from app.constants import ShiftType
from app.models import EmployeeProfile, Shift


def calculate_personalized_workload_score(
    shift: Shift,
    profile: EmployeeProfile,
) -> float:
    score = float(shift.workload_score)

    if shift.shift_type == ShiftType.NIGHT:
        score += calculate_tolerance_penalty(profile.night_tolerance)

    if shift.shift_type == ShiftType.EVENING:
        score += calculate_tolerance_penalty(profile.late_tolerance)

    if shift.shift_type == profile.preferred_shift:
        score -= 0.25

    return max(score, 0.0)


def calculate_tolerance_penalty(tolerance: float) -> float:
    normalized_tolerance = clamp(tolerance, minimum=0.0, maximum=1.0)

    return 1.0 - normalized_tolerance


def clamp(value: float, minimum: float, maximum: float) -> float:
    if value < minimum:
        return minimum

    if value > maximum:
        return maximum

    return value