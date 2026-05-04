from models import Employee, Shift

def print_assigned_shifts(shifts: list[Shift]) -> None:
    for shift in shifts:
        if shift.assigned_employees:
            names = ", ".join(e.name for e in shift.assigned_employees)
            print(f"{shift.date} {shift.shift_type} ({shift.required_skill}) -> {names}")
        else:
            print(f"{shift.date} {shift.shift_type} ({shift.required_skill}) -> No assignment")

def print_shift_summary(employees: list[Employee]) -> None:
    print("\nShift count:")
    for employee in employees:
        print(f"{employee.name}: {len(employee.assigned_shifts)}")


def print_unassigned_shifts(shifts: list[Shift]) -> None:
    unassigned = [s for s in shifts if not s.is_fully_staffed]

    if not unassigned:
        print("\nAll shifts assigned")
        return

    print("\nUnassigned shifts:")
    for shift in unassigned:
        print(f"{shift.date} {shift.shift_type} ({shift.required_skill}) "
            f"[mangler {shift.missing_staff_count}/{shift.required_staff}]")