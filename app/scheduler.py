from models import Employee, Shift

def assign_shifts(employees: list[Employee], shifts: list[Shift]) -> list[Shift]:
    for shift in shifts:
        sorted_employees = sorted(employees, key=lambda e: len(e.assigned_shifts))

        for employee in sorted_employees:
            if shift.is_fully_staffed:
                break
            
            if employee.can_take_shift(shift):
                shift.assigned_employees.append(employee)
                employee.assigned_shifts.append(shift)

    return shifts