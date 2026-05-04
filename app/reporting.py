from models import Employee, Shift

def print_assigned_shifts(shifts: list[Shift]) -> None:
    for shift in shifts:
        if shift.assigned_employees:
            names = ", ".join(str(e) for e in shift.assigned_employees)
            print(f"{shift} -> {names}")
        else:
            print(f"{shift} -> No assignment")

def print_shift_summary(employees: list[Employee]) -> None:
    print("\nShift count:")
    for employee in employees:
        print(f"{employee}: {len(employee.assigned_shifts)}")

def print_unassigned_shifts(shifts: list[Shift]) -> None:
    unassigned = [s for s in shifts if not s.is_fully_staffed]

    if not unassigned:
        print("\nAll shifts assigned")
        return

    print("\nUnassigned shifts:")
    for shift in unassigned:
        print(f"{shift} [mangler {shift.missing_staff_count}/{shift.required_staff}]")

def print_critical_unassigned_shifts(shifts: list[Shift]) -> None:
    critical = [s for s in shifts if s.priority == 1 and not s.is_fully_staffed]

    if not critical:
        print("\nNo critical unassigned shifts")
        return

    print("\nCritical unassigned shifts:")
    for shift in critical:
        print(f"{shift} [mangler {shift.missing_staff_count}/{shift.required_staff}]")