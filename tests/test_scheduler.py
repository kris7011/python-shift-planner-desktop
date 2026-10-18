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

def test_priority_order_does_not_bypass_rest_rules():
    employee = Employee(name="Priority-Rest", max_shifts=3, skills=["CT"])
    # Later calendar date has the higher scheduling priority.
    next_day = Shift(
        date="2026-05-12",
        shift_type=ShiftType.DAY,
        required_skill="CT",
        priority=1,
    )
    previous_night = Shift(
        date="2026-05-11",
        shift_type=ShiftType.NIGHT,
        required_skill="CT",
        priority=2,
    )

    assign_shifts([employee], [previous_night, next_day])

    assert employee in next_day.assigned_employees
    assert previous_night.assigned_employees == []
    assert employee.assigned_shifts == [next_day]


def test_equal_load_ties_do_not_depend_on_input_order():
    def chosen_name(order):
        employees = [Employee(name, 4, ["CT"]) for name in order]
        shift = Shift("2026-05-11", ShiftType.DAY, "CT")
        assign_shifts(employees, [shift])
        return shift.assigned_employees[0].name

    assert chosen_name(["Zoe", "Anna"]) == chosen_name(["Anna", "Zoe"])


def test_equal_assignment_count_prefers_lower_total_workload():
    lightly_loaded = Employee("Light", 5, ["CT"])
    heavily_loaded = Employee("Heavy", 5, ["CT"])
    lightly_loaded.assigned_shifts.append(
        Shift("2026-05-09", ShiftType.DAY, "CT", workload_score=1)
    )
    heavily_loaded.assigned_shifts.append(
        Shift("2026-05-09", ShiftType.DAY, "CT", workload_score=3)
    )
    next_shift = Shift("2026-05-11", ShiftType.DAY, "CT")

    assign_shifts(
        [heavily_loaded, lightly_loaded],
        [next_shift],
        workload_ratio_threshold=2.0,
        average_score_threshold=99.0,
    )

    assert next_shift.assigned_employees == [lightly_loaded]


def test_equal_priority_ties_rotate_across_consecutive_days():
    def assigned_name(day):
        employees = [Employee("Anna", 5, ["CT"]), Employee("Zoe", 5, ["CT"])]
        shift = Shift(day, ShiftType.DAY, "CT")
        assign_shifts(employees, [shift])
        return shift.assigned_employees[0].name

    monday = assigned_name("2026-05-11")
    tuesday = assigned_name("2026-05-12")

    assert {monday, tuesday} == {"Anna", "Zoe"}


def test_rotation_does_not_override_skill_requirements():
    anna = Employee("Anna", 4, ["MR"])
    zoe = Employee("Zoe", 4, ["CT"])
    shift = Shift("2026-05-12", ShiftType.DAY, "CT")

    assign_shifts([anna, zoe], [shift])

    assert shift.assigned_employees == [zoe]


def test_history_fairness_prefers_employee_with_fewer_recent_nights():
    anna = Employee("Anna", 5, ["CT"])
    zoe = Employee("Zoe", 5, ["CT"])
    night = Shift("2026-05-20", ShiftType.NIGHT, "CT")

    assign_shifts(
        [anna, zoe],
        [night],
        historical_shifts_by_employee={
            "Anna": [Shift("2026-05-13", ShiftType.NIGHT, "CT")],
            "Zoe": [],
        },
    )

    assert night.assigned_employees == [zoe]


def test_history_fairness_prefers_fewer_weekends_on_weekend_shifts():
    anna = Employee("Anna", 5, ["CT"])
    zoe = Employee("Zoe", 5, ["CT"])
    sunday = Shift("2026-05-24", ShiftType.DAY, "CT")

    assign_shifts(
        [anna, zoe],
        [sunday],
        historical_shifts_by_employee={
            "Anna": [Shift("2026-05-17", ShiftType.DAY, "CT")],
            "Zoe": [],
        },
    )

    assert sunday.assigned_employees == [zoe]


def test_historical_penalty_excludes_old_and_future_shifts():
    anna = Employee("Anna", 5, ["CT"])
    zoe = Employee("Zoe", 5, ["CT"])
    target = Shift("2026-05-20", ShiftType.NIGHT, "CT")

    with_history = {
        "Anna": [
            Shift("2026-03-01", ShiftType.NIGHT, "CT"),
            Shift("2026-05-27", ShiftType.NIGHT, "CT"),
        ],
        "Zoe": [],
    }
    # Old and future history is ignored; the result therefore matches
    # the normal deterministic rotation rather than imposing a penalty.
    reference = Shift("2026-05-20", ShiftType.NIGHT, "CT")
    reference_employees = [Employee("Anna", 5, ["CT"]), Employee("Zoe", 5, ["CT"])]
    assign_shifts(reference_employees, [reference])

    assign_shifts(
        [anna, zoe],
        [target],
        historical_shifts_by_employee=with_history,
    )
    assert target.assigned_employees[0].name == reference.assigned_employees[0].name


def test_history_does_not_override_skill_eligibility():
    qualified = Employee("Qualified", 5, ["MR"])
    other = Employee("Not qualified", 5, ["CT"])
    night = Shift("2026-05-20", ShiftType.NIGHT, "MR")

    assign_shifts(
        [qualified, other],
        [night],
        historical_shifts_by_employee={
            "Qualified": [Shift("2026-05-13", ShiftType.NIGHT, "MR")],
        },
    )

    assert night.assigned_employees == [qualified]


def test_invalid_history_window_is_rejected():
    import pytest

    with pytest.raises(ValueError, match="history_lookback_days"):
        assign_shifts([], [], history_lookback_days=0)
