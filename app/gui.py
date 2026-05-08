import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from app.config import (
    WORKLOAD_RATIO_LIMIT,
    AVERAGE_SCORE_LIMIT,
    HIGH_RISK_FLAG_COUNT,
    EMPLOYEES_CSV_PATH,
    SHIFTS_CSV_PATH,
    EMPLOYEE_PROFILES_CSV_PATH,
)
from app.csv_loader import (
    load_employees_from_csv,
    load_shifts_from_csv,
    load_employee_profiles_from_csv,
)
from app.scheduler import assign_shifts
from app.personalized_workload import calculate_personalized_workload_score


def load_schedule_data():
    employees = load_employees_from_csv(EMPLOYEES_CSV_PATH)
    shifts = load_shifts_from_csv(SHIFTS_CSV_PATH)
    employee_profiles = load_employee_profiles_from_csv(EMPLOYEE_PROFILES_CSV_PATH)

    assigned_shifts = assign_shifts(
        employees,
        shifts,
        employee_profiles=employee_profiles,
        workload_ratio_threshold=WORKLOAD_RATIO_LIMIT,
        average_score_threshold=AVERAGE_SCORE_LIMIT,
        high_risk_flag_count=HIGH_RISK_FLAG_COUNT,
    )

    return employees, assigned_shifts, employee_profiles


def build_assigned_output(shifts) -> str:
    lines = ["ASSIGNED SHIFTS", "=" * 50]

    for shift in shifts:
        if shift.assigned_employees:
            names = ", ".join(str(employee) for employee in shift.assigned_employees)
            lines.append(f"{shift} -> {names}")
        else:
            lines.append(f"{shift} -> No assignment")

    return "\n".join(lines)


def build_unassigned_output(shifts) -> str:
    lines = ["UNASSIGNED SHIFTS", "=" * 50]
    unassigned = [shift for shift in shifts if not shift.is_fully_staffed]

    if not unassigned:
        lines.append("All shifts are fully staffed")
        return "\n".join(lines)

    for shift in unassigned:
        lines.append(f"{shift} [missing {shift.missing_staff_count}/{shift.required_staff}]")

    return "\n".join(lines)


def build_risk_output(employees, employee_profiles) -> str:
    lines = ["PERSONALIZED RISK REPORT", "=" * 50]

    profiles_by_name = {
        profile.name: profile
        for profile in employee_profiles
    }

    for employee in employees:
        profile = profiles_by_name.get(str(employee))

        if profile is None:
            lines.append(f"{employee}: No profile found")
            continue

        total_score = sum(
            calculate_personalized_workload_score(shift, profile)
            for shift in employee.assigned_shifts
        )

        shift_count = len(employee.assigned_shifts)
        average_score = total_score / shift_count if shift_count > 0 else 0

        if average_score >= AVERAGE_SCORE_LIMIT:
            risk = "HIGH"
        elif average_score >= AVERAGE_SCORE_LIMIT * 0.75:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        lines.append(
            f"{employee}: {risk} "
            f"(personalized average={average_score:.1f}, shifts={shift_count})"
        )

    return "\n".join(lines)


def build_explanation_output(shifts, employee_profiles) -> str:
    lines = ["ASSIGNMENT EXPLANATIONS", "=" * 50]

    profiles_by_name = {
        profile.name: profile
        for profile in employee_profiles
    }

    for shift in shifts:
        lines.append("")
        lines.append(str(shift))

        if not shift.assigned_employees:
            lines.append("  No assignment")
            continue

        for employee in shift.assigned_employees:
            profile = profiles_by_name.get(str(employee))

            lines.append(f"  Assigned to: {employee}")
            lines.append(f"  Required skill: {shift.required_skill}")
            lines.append(f"  Employee skills: {', '.join(employee.skills)}")

            if profile is None:
                lines.append("  No employee profile found")
                continue

            personalized_score = calculate_personalized_workload_score(shift, profile)

            lines.append(f"  Preferred shift: {profile.preferred_shift.value}")
            lines.append(f"  Personalized score: {personalized_score:.1f}")

            if shift.shift_type == profile.preferred_shift:
                lines.append("  Reason: shift matches employee preference")
            else:
                lines.append("  Reason: employee was eligible and had a suitable score")

    return "\n".join(lines)


class ShiftPlannerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python Shift Planner")
        self.root.geometry("1100x750")

        title = tk.Label(
            root,
            text="Python Shift Planner",
            font=("Arial", 18, "bold"),
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            root,
            text="Shift planning, workload analysis and personalized risk reporting",
            font=("Arial", 10),
        )
        subtitle.pack(pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        run_button = tk.Button(
            button_frame,
            text="Run Scheduler",
            command=self.run_scheduler,
            width=20,
        )
        run_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_output,
            width=20,
        )
        clear_button.pack(side=tk.LEFT, padx=5)

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=True, fill="both", padx=10, pady=10)

        self.assigned_output = self.create_tab("Assigned Shifts")
        self.unassigned_output = self.create_tab("Unassigned")
        self.risk_output = self.create_tab("Risk Report")
        self.explanation_output = self.create_tab("Explanations")

    def create_tab(self, title: str):
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text=title)

        output = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
        )
        output.pack(expand=True, fill="both", padx=10, pady=10)

        return output

    def run_scheduler(self) -> None:
        try:
            employees, shifts, employee_profiles = load_schedule_data()

            self.set_output(self.assigned_output, build_assigned_output(shifts))
            self.set_output(self.unassigned_output, build_unassigned_output(shifts))
            self.set_output(self.risk_output, build_risk_output(employees, employee_profiles))
            self.set_output(
                self.explanation_output,
                build_explanation_output(shifts, employee_profiles),
            )

        except Exception as error:
            messagebox.showerror("Error", str(error))

    def set_output(self, output, text: str) -> None:
        output.delete("1.0", tk.END)
        output.insert(tk.END, text)

    def clear_output(self) -> None:
        for output in [
            self.assigned_output,
            self.unassigned_output,
            self.risk_output,
            self.explanation_output,
        ]:
            output.delete("1.0", tk.END)


def main() -> None:
    root = tk.Tk()
    ShiftPlannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()