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
        print(f"{employee}: {employee.assigned_shift_count}")

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
        
def print_employee_details(employees: list[Employee]) -> None:
    print("\nEmployee details:")
    
    for employee in employees:
        skills = ", ".join(employee.skills)
        assigned_shifts = employee.assigned_shift_count
        max_shifts = employee.max_shifts
        print(f"{employee} - skills: {skills} - shifts: {assigned_shifts}/{max_shifts}")
        
def print_employees_at_capacity(employees: list[Employee]) -> None:
    at_capacity = [e for e in employees if e.is_at_capacity]
    
    if not at_capacity:
        print("\nNo employees at capacity")
        return
    
    print("\nEmployees at capacity:")
    for employee in at_capacity:
        assigned = employee.assigned_shift_count
        max_shifts = employee.max_shifts
        print(f"{employee} - {assigned}/{max_shifts}")

def print_overloaded_employees(employees: list[Employee], threshold: float = 0.8) -> None:
    # Filter employees with a workload_ratio of 0.8 (80%) or above
    overloaded_employees = [e for e in employees if e.workload_ratio >= threshold]
    
    if not overloaded_employees:
        print("\nNo high workload employees")
        return
    
    print("\nHigh workload employees:")
    for employee in overloaded_employees:
        assigned = employee.assigned_shift_count
        max_shifts = employee.max_shifts
        # Calculate percentage (e.g. 0.75 -> 75%)
        percentage = int(employee.workload_ratio * 100)
        
        print(f"{employee} - {assigned}/{max_shifts} ({percentage}%)")

def print_workload_score_report(employees: list[Employee]) -> None:
    print("\nWorkload Score Report:")
    
    # Sort by highest load
    sorted_employees = sorted(employees, key=lambda e: e.total_workload_score, reverse=True)
    
    for e in sorted_employees:
        print(f"{e} - Score: {e.total_workload_score} (Shifts: {e.assigned_shift_count})")