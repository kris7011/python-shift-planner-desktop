from app.constants import ShiftType
from app.models import EmployeeProfile, Shift
from app.personalized_workload import calculate_personalized_workload_score


def test_night_shift_is_heavier_for_low_night_tolerance():
    shift = Shift(
        date="2026-05-01",
        shift_type=ShiftType.NIGHT,
        required_skill="Nurse",
        workload_score=3,
    )

    profile = EmployeeProfile(
        employee_id="1",
        name="Anna",
        night_tolerance=0.4,
        weekend_tolerance=0.5,
        late_tolerance=0.5,
        max_weekly_load=37,
        preferred_shift=ShiftType.DAY,
    )

    score = calculate_personalized_workload_score(shift, profile)

    assert score == 3.6