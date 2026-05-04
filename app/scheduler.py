from models import Employee, Shift

def assign_shifts(employees: list[Employee], shifts: list[Shift]) -> list[Shift]:
    for shift in shifts:
        assigned = False

        sorted_employees = sorted(employees, key=lambda e: len(e.assigned_shifts))

        for employee in sorted_employees:
            if employee.can_take_shift(shift):
                shift.assigned_employee = employee
                employee.assigned_shifts.append(shift)
                assigned = True
                break

        if not assigned:
            shift.assigned_employee = None

    return shifts