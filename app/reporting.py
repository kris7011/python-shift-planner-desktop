from app.constants import RiskLevel
from app.models import Employee, Shift
from app.personalized_workload import calculate_personalized_workload_score

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
        print(f"{shift} [missing {shift.missing_staff_count}/{shift.required_staff}]")

def print_critical_unassigned_shifts(shifts: list[Shift]) -> None:
    critical = [s for s in shifts if s.priority == 1 and not s.is_fully_staffed]

    if not critical:
        print("\nNo critical unassigned shifts")
        return

    print("\nCritical unassigned shifts:")
    for shift in critical:
        print(f"{shift} [missing {shift.missing_staff_count}/{shift.required_staff}]")
        
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
    
    sorted_employees = sorted(employees, key=lambda e: e.total_workload_score, reverse=True)
    
    for employee in sorted_employees:
        print(f"{employee} - Score: {employee.total_workload_score} (Shifts: {employee.assigned_shift_count})")
        
def print_average_workload_score(employees: list[Employee]) -> None:
    print("\nAverage workload score:")
    for employee in employees:
        print(f"{employee} - {employee.total_workload_score} / {employee.assigned_shift_count} = {employee.average_workload_score:.1f}")
        
def print_average_workload_ranking(employees: list[Employee]) -> None:
    print("\nAverage workload ranking:")
    
    # Sort employees by their average_workload_score property
    # reverse=True ensures that the highest score comes first
    sorted_employees = sorted(
        employees, 
        key=lambda e: e.average_workload_score, 
        reverse=True
    )
    
    for employee in sorted_employees:
        print(f"{employee} - {employee.average_workload_score:.1f}")
        
def print_risk_report(
    employees: list[Employee],
    workload_ratio_threshold: float = 0.75,
    average_score_threshold: float = 2.0,
    high_risk_flag_count: int = 2,
) -> None:
    print("\n" + "="*50)
    print(f"{'EMPLOYEE RISK REPORT':^50}")
    print("="*50)
    
    for employee in employees:
        flags = employee.get_risk_flags(workload_ratio_threshold, average_score_threshold)
        level = employee.get_risk_level(
            workload_ratio_threshold,
            average_score_threshold,
            high_risk_flag_count,
        )
        
        flags_str = f"[ {' | '.join(flags)} ]" if flags else ""
        print(f"{str(employee):10} -> {level.value:6} {flags_str}")
    
    print("="*50)
    
def print_unassigned_report(shifts: list[Shift], employees: list[Employee], detailed: bool = False) -> None:
    unassigned = [s for s in shifts if not s.is_fully_staffed]
    
    if not unassigned:
        print("\nAll shifts are fully staffed!")
        return

    title = "DETAILED UNASSIGNED REASONS" if detailed else "UNASSIGNED SHIFTS"
    print("\n" + "="*50)
    print(f"{title:^50}")
    print("="*50)

    for shift in unassigned:
        print(f"\n{shift}")
        
        if not detailed:
            can_anyone = any(e.can_take_shift(shift) for e in employees)
            reason = "Potential candidates exist" if can_anyone else "No eligible employees found"
            print(f"Status: {reason}")
        else:
            print("Reasons per employee:")
            for e in employees:
                if e.can_take_shift(shift):
                    print(f"  {str(e):15} -> could have taken it")
                else:
                    blockers = e.get_shift_blockers(shift)
                    print(f"  {str(e):15} -> {', '.join(blockers)}")
            
    print("\n" + "="*50)
    
def print_personalized_workload_report(employees, employee_profiles):
    print("\nPERSONALIZED WORKLOAD REPORT")
    print("-" * 40)

    profiles_by_name = {
        profile.name: profile
        for profile in employee_profiles
    }

    for employee in employees:
        profile = profiles_by_name.get(employee.name)

        if profile is None:
            print(f"{str(employee)}: No profile found")
            continue

        total_score = sum(
            calculate_personalized_workload_score(shift, profile)
            for shift in employee.assigned_shifts
        )

        shift_count = len(employee.assigned_shifts)
        average_score = total_score / shift_count if shift_count > 0 else 0

        print(
            f"{str(employee)}: "
            f"personalized total={total_score:.1f}, "
            f"average={average_score:.1f}"
        )
        
def print_personalized_risk_report(
    employees,
    employee_profiles,
    average_score_threshold: float = 2.0,
) -> None:
    print("\nPERSONALIZED RISK REPORT")
    print("-" * 40)

    profiles_by_name = {
        profile.name: profile
        for profile in employee_profiles
    }

    for employee in employees:
        profile = profiles_by_name.get(employee.name)

        if profile is None:
            print(f"{str(employee)}: No profile found")
            continue

        total_score = sum(
            calculate_personalized_workload_score(shift, profile)
            for shift in employee.assigned_shifts
        )

        shift_count = len(employee.assigned_shifts)
        average_score = total_score / shift_count if shift_count > 0 else 0

        if average_score >= average_score_threshold:
            risk = RiskLevel.HIGH
        elif average_score >= average_score_threshold * 0.75:
            risk = RiskLevel.MEDIUM
        else:
            risk = RiskLevel.LOW

        print(
            f"{str(employee)}: "
            f"{risk.value} "
            f"(personalized average={average_score:.1f})"
        )
        
def print_assignment_explanation_report(shifts, employee_profiles) -> None:
    print("\nASSIGNMENT EXPLANATION REPORT")
    print("-" * 40)

    profiles_by_name = {
        profile.name: profile
        for profile in employee_profiles
    }

    for shift in shifts:
        print(f"\n{shift}")

        if not shift.assigned_employees:
            print("  No assignment")
            continue

        for employee in shift.assigned_employees:
            profile = profiles_by_name.get(str(employee))

            print(f"  Assigned to: {employee}")
            print(f"  Required skill: {shift.required_skill}")
            print(f"  Employee skills: {', '.join(employee.skills)}")

            if profile is None:
                print("  No employee profile found")
                continue

            personalized_score = calculate_personalized_workload_score(
                shift,
                profile,
            )

            print(f"  Preferred shift: {profile.preferred_shift.value}")
            print(f"  Personalized score: {personalized_score:.1f}")

            if shift.shift_type == profile.preferred_shift:
                print("  Reason: shift matches employee preference")
            else:
                print("  Reason: employee was eligible and had a suitable score")