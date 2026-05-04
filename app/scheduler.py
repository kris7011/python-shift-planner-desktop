def assign_shifts(employees, shifts):
    employee_index = 0

    for shift in shifts:
        attempts = 0
        assigned = False

        while attempts < len(employees):
            employee = employees[employee_index]

            if employee.can_take_shift(shift):
                shift.assigned_employee = employee
                employee.assigned_shifts.append(shift)
                assigned = True
                break

            employee_index = (employee_index + 1) % len(employees)
            attempts += 1

        if not assigned:
            shift.assigned_employee = None

        employee_index = (employee_index + 1) % len(employees)

    return shifts