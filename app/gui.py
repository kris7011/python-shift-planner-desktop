import tkinter as tk
from tkinter import scrolledtext, messagebox

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


def build_schedule_output() -> str:
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

    profiles_by_name = {
        profile.name: profile
        for profile in employee_profiles
    }

    lines = []

    lines.append("ASSIGNED SHIFTS")
    lines.append("=" * 50)

    for shift in assigned_shifts:
        if shift.assigned_employees:
            names = ", ".join(str(employee) for employee in shift.assigned_employees)
            lines.append(f"{shift} -> {names}")
        else:
            lines.append(f"{shift} -> No assignment")

    lines.append("")
    lines.append("UNASSIGNED SHIFTS")
    lines.append("=" * 50)

    unassigned = [shift for shift in assigned_shifts if not shift.is_fully_staffed]

    if not unassigned:
        lines.append("All shifts are fully staffed")
    else:
        for shift in unassigned:
            lines.append(
                f"{shift} [missing {shift.missing_staff_count}/{shift.required_staff}]"
            )

    lines.append("")
    lines.append("PERSONALIZED RISK REPORT")
    lines.append("=" * 50)

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


class ShiftPlannerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python Shift Planner")
        self.root.geometry("1000x700")

        title = tk.Label(
            root,
            text="Python Shift Planner",
            font=("Arial", 18, "bold"),
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            root,
            text="Prototype for shift planning, workload analysis and personalized risk reporting",
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

        self.output = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            font=("Consolas", 10),
        )
        self.output.pack(expand=True, fill="both", padx=10, pady=10)

    def run_scheduler(self) -> None:
        try:
            result = build_schedule_output()
            self.output.delete("1.0", tk.END)
            self.output.insert(tk.END, result)
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def clear_output(self) -> None:
        self.output.delete("1.0", tk.END)


def main() -> None:
    root = tk.Tk()
    app = ShiftPlannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()