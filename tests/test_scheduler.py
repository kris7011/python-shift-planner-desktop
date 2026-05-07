from app.constants import ShiftType
from app.models import Employee, EmployeeProfile, Shift
from app.scheduler import assign_shifts

def test_assign_shifts_assigns_employee_with_matching_skill():
    # Arrange
    emp = Employee(name="Assistant-John", max_shifts=5, skills=["Assistant"])
    shift = Shift(date="2026-05-11", shift_type=ShiftType.DAY, required_skill="Assistant", required_staff=1)
    
    # Act
    assign_shifts(employees=[emp], shifts=[shift])

    # Assert
    assert emp in shift.assigned_employees
    assert shift in emp.assigned_shifts

def test_assign_shifts_skips_employee_without_skill():
    # Arrange
    emp = Employee(name="Not Qualified-Ib", max_shifts=5, skills=["Cleaning"])
    shift = Shift(date="2026-05-11", shift_type=ShiftType.DAY, required_skill="Assistant", required_staff=1)
    
    # Act
    assign_shifts(employees=[emp], shifts=[shift])

    # Assert
    assert len(shift.assigned_employees) == 0
    assert len(emp.assigned_shifts) == 0

def test_assign_shifts_respects_priority():
    # Arrange:
    emp = Employee(name="Alone-Arne", max_shifts=1, skills=["Assistant"])
    shift_low_priority = Shift(date="2026-05-11", shift_type=ShiftType.DAY, required_skill="Assistant", priority=3)
    shift_high_priority = Shift(date="2026-05-11", shift_type=ShiftType.EVENING, required_skill="Assistant", priority=1)
    
    # Act
    assign_shifts(employees=[emp], shifts=[shift_low_priority, shift_high_priority])

    # Assert
    assert emp in shift_high_priority.assigned_employees
    assert emp not in shift_low_priority.assigned_employees
    
def test_assign_shifts_uses_employee_profile_for_night_shift():
    low_tolerance_employee = Employee(
        name="Anna",
        max_shifts=5,
        skills=["MR"],
    )
    high_tolerance_employee = Employee(
        name="Peter",
        max_shifts=5,
        skills=["MR"],
    )

    night_shift = Shift(
        date="2026-05-11",
        shift_type=ShiftType.NIGHT,
        required_skill="MR",
        required_staff=1,
        workload_score=3,
    )

    profiles = [
        EmployeeProfile(
            employee_id="1",
            name="Anna",
            night_tolerance=0.2,
            weekend_tolerance=0.5,
            late_tolerance=0.5,
            max_weekly_load=37,
            preferred_shift=ShiftType.DAY,
        ),
        EmployeeProfile(
            employee_id="2",
            name="Peter",
            night_tolerance=0.9,
            weekend_tolerance=0.5,
            late_tolerance=0.5,
            max_weekly_load=37,
            preferred_shift=ShiftType.NIGHT,
        ),
    ]

    assign_shifts(
        employees=[low_tolerance_employee, high_tolerance_employee],
        shifts=[night_shift],
        employee_profiles=profiles,
    )

    assert high_tolerance_employee in night_shift.assigned_employees
    assert low_tolerance_employee not in night_shift.assigned_employees


def test_assign_shifts_uses_employee_profile_for_evening_shift():
    low_tolerance_employee = Employee(
        name="Anna",
        max_shifts=5,
        skills=["MR"],
    )
    high_tolerance_employee = Employee(
        name="Jonas",
        max_shifts=5,
        skills=["MR"],
    )

    evening_shift = Shift(
        date="2026-05-11",
        shift_type=ShiftType.EVENING,
        required_skill="MR",
        required_staff=1,
        workload_score=2,
    )

    profiles = [
        EmployeeProfile(
            employee_id="1",
            name="Anna",
            night_tolerance=0.5,
            weekend_tolerance=0.5,
            late_tolerance=0.2,
            max_weekly_load=37,
            preferred_shift=ShiftType.DAY,
        ),
        EmployeeProfile(
            employee_id="2",
            name="Jonas",
            night_tolerance=0.5,
            weekend_tolerance=0.5,
            late_tolerance=0.9,
            max_weekly_load=37,
            preferred_shift=ShiftType.EVENING,
        ),
    ]

    assign_shifts(
        employees=[low_tolerance_employee, high_tolerance_employee],
        shifts=[evening_shift],
        employee_profiles=profiles,
    )

    assert high_tolerance_employee in evening_shift.assigned_employees
    assert low_tolerance_employee not in evening_shift.assigned_employees


def test_assign_shifts_still_works_without_employee_profiles():
    employee = Employee(
        name="Anna",
        max_shifts=5,
        skills=["CT"],
    )

    shift = Shift(
        date="2026-05-11",
        shift_type=ShiftType.DAY,
        required_skill="CT",
        required_staff=1,
    )

    assign_shifts(
        employees=[employee],
        shifts=[shift],
        employee_profiles=None,
    )

    assert employee in shift.assigned_employees