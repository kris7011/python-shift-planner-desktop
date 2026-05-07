from app.constants import ShiftType
from app.models import Employee, Shift

def test_shift_is_fully_staffed_when_requirement_met():
    # Arrange
    shift = Shift(date="2026-05-11", shift_type=ShiftType.DAY, required_skill="Assistant", required_staff=2)
    e1 = Employee("Henrik", 5, ["Assistant"])
    e2 = Employee("Mette", 5, ["Assistant"])
    
    # Act
    shift.assigned_employees.append(e1)
    status_before = shift.is_fully_staffed
    
    shift.assigned_employees.append(e2)
    status_after = shift.is_fully_staffed

    # Assert
    assert status_before is False
    assert status_after is True

def test_shift_missing_staff_count_calculations():
    # Arrange
    required = 3
    shift = Shift(date="2026-05-11", shift_type=ShiftType.DAY, required_skill="Assistant", required_staff=required)
    employee = Employee("Henrik", 5, ["Assistant"])
    
    # Act & Assert
    assert shift.missing_staff_count == 3
    
    shift.assigned_employees.append(employee)
    assert shift.missing_staff_count == 2

def test_shift_over_staffing_is_fully_staffed():
    # Arrange
    shift = Shift(date="2026-05-11", shift_type=ShiftType.DAY, required_skill="Assistant", required_staff=1)
    e1 = Employee("Henrik", 5, ["Assistant"])
    e2 = Employee("Mette", 5, ["Assistant"])
    
    # Act
    shift.assigned_employees.extend([e1, e2])

    # Assert
    assert shift.is_fully_staffed is True
    assert shift.missing_staff_count <= 0

def test_shift_string_representation():
    # Arrange
    shift = Shift(date="2026-05-11", shift_type=ShiftType.NIGHT, required_skill="Nurse", priority=1, workload_score=3)
    
    # Act
    result = str(shift)
    
    # Assert
    assert "2026-05-11" in result
    assert ShiftType.NIGHT.value in result
    assert "Nurse" in result
    assert "P1" in result
    assert "Score 3" in result