from app.models import Employee, Shift

def test_employee_can_take_shift_with_correct_skill():
    # Arrange
    employee = Employee(name="Test-Henrik", max_shifts=3, skills=["Assistant"])
    shift = Shift(date="2026-05-11", shift_type="Day", required_skill="Assistant")

    # Act
    result = employee.can_take_shift(shift)

    # Assert
    assert result is True

def test_employee_cannot_take_shift_without_skill():
    # Arrange
    employee = Employee(name="Test-Henrik", max_shifts=3, skills=["Assistant"])
    shift = Shift(date="2026-05-11", shift_type="Day", required_skill="Nurse")

    # Act
    result = employee.can_take_shift(shift)

    # Assert
    assert result is False

def test_employee_cannot_take_shift_when_at_capacity():
    # Arrange
    employee = Employee(name="Maxed-Mette", max_shifts=1, skills=["Assistant"])
    shift1 = Shift(date="2026-05-11", shift_type="Day", required_skill="Assistant")
    shift2 = Shift(date="2026-05-12", shift_type="Day", required_skill="Assistant")

    employee.assigned_shifts.append(shift1)

    # Act
    result = employee.can_take_shift(shift2)

    # Assert
    assert result is False
    
def test_employee_cannot_take_day_shift_after_evening_shift():
    # Arrange
    employee = Employee(name="Rest-Hannah", max_shifts=5, skills=["Assistant"])
    
    evening_shift = Shift(date="2026-05-11", shift_type="Evening", required_skill="Assistant")
    next_day_shift = Shift(date="2026-05-12", shift_type="Day", required_skill="Assistant")

    employee.assigned_shifts.append(evening_shift)

    # Act
    result = employee.can_take_shift(next_day_shift)

    # Assert
    assert result is False, "Employees should not be able to take a day shift directly after an evening shift."

def test_employee_cannot_take_any_shift_day_after_night_shift():
    # Arrange
    employee = Employee(name="Night-Nick", max_shifts=5, skills=["Assistant"])
    
    night_shift = Shift(date="2026-05-11", shift_type="Night", required_skill="Assistant")
    next_evening_shift = Shift(date="2026-05-12", shift_type="Evening", required_skill="Assistant")

    employee.assigned_shifts.append(night_shift)

    # Act
    result = employee.can_take_shift(next_evening_shift)

    # Assert
    assert result is False, "A night shift should block all shifts the following day"

def test_employee_risk_level_changes_to_medium_at_threshold():
    # Arrange
    employee = Employee(name="Threshold-Tom", max_shifts=4, skills=["Assistant"])
    
    s1 = Shift("2026-05-11", "Day", "Assistant")
    s2 = Shift("2026-05-12", "Day", "Assistant")
    s3 = Shift("2026-05-13", "Day", "Assistant")
    
    employee.assigned_shifts.extend([s1, s2, s3])

    # Act
    level = employee.get_risk_level(
        workload_ratio_threshold=0.75, 
        average_score_threshold=2.0,
        high_risk_flag_count=2
    )

    # Assert
    assert level == "MEDIUM"
    
def test_employee_cannot_take_two_shifts_on_same_day():
    # Arrange
    employee = Employee(name="Double-Day-Diana", max_shifts=5, skills=["Assistant"])
    shift1 = Shift(date="2026-05-11", shift_type="Day", required_skill="Assistant")
    shift2 = Shift(date="2026-05-11", shift_type="Evening", required_skill="Assistant")
    
    employee.assigned_shifts.append(shift1)

    # Act
    result = employee.can_take_shift(shift2)

    # Assert
    assert result is False, "An employee may not have two shifts on the same date."