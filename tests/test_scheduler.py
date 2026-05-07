from app.constants import ShiftType
from app.models import Employee, Shift
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