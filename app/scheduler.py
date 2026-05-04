def assign_shifts(employees, shifts):
    employee_index = 0

    for shift in shifts:
        attempts = 0

        while attempts < len(employees):
            employee = employees[employee_index]

            if employee.can_take_shift():
                shift.assigned_employee = employee
                employee.assigned_shifts.append(shift)
                break

            employee_index = (employee_index + 1) % len(employees)
            attempts += 1

        employee_index = (employee_index + 1) % len(employees)

    return shifts