import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

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


def load_schedule_data(
    employees_path: str,
    shifts_path: str,
    profiles_path: str,
):
    employees = load_employees_from_csv(employees_path)
    shifts = load_shifts_from_csv(shifts_path)
    employee_profiles = load_employee_profiles_from_csv(profiles_path)

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
    lines = ["TILDELTE VAGTER", "=" * 50]

    for shift in shifts:
        if shift.assigned_employees:
            names = ", ".join(str(employee) for employee in shift.assigned_employees)
            lines.append(f"{shift} -> {names}")
        else:
            lines.append(f"{shift} -> No assignment")

    return "\n".join(lines)


def build_unassigned_output(shifts) -> str:
    lines = ["UBESATTE VAGTER", "=" * 50]
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
        self.root.title("Vagtplanlægning")
        self.root.geometry("1150x800")

        self.employees_path = tk.StringVar(value=EMPLOYEES_CSV_PATH)
        self.shifts_path = tk.StringVar(value=SHIFTS_CSV_PATH)
        self.profiles_path = tk.StringVar(value=EMPLOYEE_PROFILES_CSV_PATH)
        
        self.current_shifts = []
        self.current_profiles = []

        title = tk.Label(
            root,
            text="Vagtplanlægning",
            font=("Arial", 18, "bold"),
        )
        title.pack(pady=10)

        subtitle = tk.Label(
            root,
            text="Planlægning, belastningsanalyse og personlig risikovurdering",
            font=("Arial", 10),
        )
        subtitle.pack(pady=5)

        self.create_file_picker_section(root)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        run_button = tk.Button(
            button_frame,
            text="Kør vagtplan",
            command=self.run_scheduler,
            width=20,
        )
        run_button.pack(side=tk.LEFT, padx=5)

        clear_button = tk.Button(
            button_frame,
            text="Ryd",
            command=self.clear_output,
            width=20,
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        export_button = tk.Button(
            button_frame,
            text="Eksportér rapport",
            command=self.export_report,
            width=20,
        )
        export_button.pack(side=tk.LEFT, padx=5)

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=True, fill="both", padx=10, pady=10)

        self.assigned_table = self.create_table_tab(
            "Tildelte vagter",
            ["Dato", "Vagt", "Kompetence", "Tildelt", "Prioritet", "Score"],
        )
        self.assigned_table.bind("<<TreeviewSelect>>", self.show_selected_shift_explanation)
        
        self.unassigned_table = self.create_table_tab(
            "Ubesatte vagter",
            ["Dato", "Vagt", "Kompetence", "Mangler", "Prioritet", "Score"],
        )
        self.risk_table = self.create_table_tab(
            "Risikorapport",
            ["Medarbejder", "Risiko", "Gennemsnit", "Vagter"],
        )
        self.explanation_output = self.create_tab("Forklaringer")

    def create_file_picker_section(self, root: tk.Tk) -> None:
        file_frame = tk.LabelFrame(root, text="CSV files", padx=10, pady=10)
        file_frame.pack(fill="x", padx=10, pady=10)

        self.create_file_picker_row(
            file_frame,
            row=0,
            label="Medarbejdere CSV:",
            variable=self.employees_path,
        )

        self.create_file_picker_row(
            file_frame,
            row=1,
            label="Vagter CSV:",
            variable=self.shifts_path,
        )

        self.create_file_picker_row(
            file_frame,
            row=2,
            label="Profiler CSV:",
            variable=self.profiles_path,
        )

    def create_file_picker_row(
        self,
        parent,
        row: int,
        label: str,
        variable: tk.StringVar,
    ) -> None:
        tk.Label(parent, text=label, width=15, anchor="w").grid(
            row=row,
            column=0,
            padx=5,
            pady=4,
            sticky="w",
        )

        entry = tk.Entry(parent, textvariable=variable)
        entry.grid(
            row=row,
            column=1,
            padx=5,
            pady=4,
            sticky="ew",
        )

        browse_button = tk.Button(
            parent,
            text="Browse",
            command=lambda: self.browse_file(variable),
            width=12,
        )
        browse_button.grid(
            row=row,
            column=2,
            padx=5,
            pady=4,
        )

        parent.columnconfigure(1, weight=1)

    def browse_file(self, variable: tk.StringVar) -> None:
        selected_file = filedialog.askopenfilename(
            title="Vælg CSV-fil",
            filetypes=[("CSV-filer", "*.csv"), ("All files", "*.*")],
        )

        if selected_file:
            variable.set(selected_file)

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
            employees, shifts, employee_profiles = load_schedule_data(
                employees_path=self.employees_path.get(),
                shifts_path=self.shifts_path.get(),
                profiles_path=self.profiles_path.get(),
            )

            self.current_shifts = shifts
            self.current_profiles = employee_profiles

            self.populate_assigned_table(shifts)
            self.populate_unassigned_table(shifts)
            self.populate_risk_table(employees, employee_profiles)
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
        self.current_shifts = []
        self.current_profiles = []

        self.assigned_table.delete(*self.assigned_table.get_children())
        self.unassigned_table.delete(*self.unassigned_table.get_children())
        self.risk_table.delete(*self.risk_table.get_children())

        self.explanation_output.delete("1.0", tk.END)
    
    def create_table_tab(self, title: str, columns: list[str]):
        frame = ttk.Frame(self.tabs)
        self.tabs.add(frame, text=title)

        tree = ttk.Treeview(frame, columns=columns, show="headings")

        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, width=140, anchor="w")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, expand=True, fill="both", padx=(10, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill="y", padx=(0, 10), pady=10)

        return tree
    
    def populate_assigned_table(self, shifts) -> None:
        self.assigned_table.delete(*self.assigned_table.get_children())

        for index, shift in enumerate(shifts):
            assigned = (
                ", ".join(str(employee) for employee in shift.assigned_employees)
                if shift.assigned_employees
                else "Ingen tildeling"
            )

            self.assigned_table.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    shift.date,
                    shift.shift_type.display_name,
                    shift.required_skill,
                    assigned,
                    shift.priority,
                    shift.workload_score,
                ),
            )
    
    def populate_unassigned_table(self, shifts) -> None:
        self.unassigned_table.delete(*self.unassigned_table.get_children())

        unassigned = [
            shift for shift in shifts
            if not shift.is_fully_staffed
        ]

        for shift in unassigned:
            self.unassigned_table.insert(
                "",
                tk.END,
                values=(
                    shift.date,
                    shift.shift_type.display_name,
                    shift.required_skill,
                    f"{shift.missing_staff_count}/{shift.required_staff}",
                    shift.priority,
                    shift.workload_score,
                ),
            )
            
    def populate_risk_table(self, employees, employee_profiles) -> None:
        self.risk_table.delete(*self.risk_table.get_children())

        profiles_by_name = {
            profile.name: profile
            for profile in employee_profiles
        }

        for employee in employees:
            profile = profiles_by_name.get(str(employee))

            if profile is None:
                risk = "Ukendt"
                average_score = 0
            else:
                total_score = sum(
                    calculate_personalized_workload_score(shift, profile)
                    for shift in employee.assigned_shifts
                )

                shift_count = len(employee.assigned_shifts)

                average_score = (
                    total_score / shift_count
                    if shift_count > 0
                    else 0
                )

                if average_score >= AVERAGE_SCORE_LIMIT:
                    risk = "Høj"
                elif average_score >= AVERAGE_SCORE_LIMIT * 0.75:
                    risk = "Middel"
                else:
                    risk = "Lav"

            self.risk_table.insert(
                "",
                tk.END,
                values=(
                    employee.name,
                    risk,
                    f"{average_score:.1f}",
                    employee.assigned_shift_count,
                ),
            )
            
    def show_selected_shift_explanation(self, event=None) -> None:
        selected = self.assigned_table.selection()

        if not selected:
            return

        selected_index = int(selected[0])

        if selected_index >= len(self.current_shifts):
            return

        shift = self.current_shifts[selected_index]

        profiles_by_name = {
            profile.name: profile
            for profile in self.current_profiles
        }

        lines = []
        lines.append("FORKLARING AF VALGT VAGT")
        lines.append("=" * 50)
        lines.append("")
        lines.append(str(shift))

        if not shift.assigned_employees:
            lines.append("Ingen tildeling")
            self.set_output(self.explanation_output, "\n".join(lines))
            return

        for employee in shift.assigned_employees:
            profile = profiles_by_name.get(str(employee))

            lines.append("")
            lines.append(f"Tildelt til: {employee}")
            lines.append(f"Krævet kompetence: {shift.required_skill}")
            lines.append(f"Medarbejderkompetencer: {', '.join(employee.skills)}")

            if profile is None:
                lines.append("Ingen medarbejderprofil fundet")
                continue

            personalized_score = calculate_personalized_workload_score(
                shift,
                profile,
            )

            lines.append(f"Foretrukken vagttype: {profile.preferred_shift.display_name}")
            lines.append(f"Personlig belastningsscore: {personalized_score:.1f}")

            if shift.shift_type == profile.preferred_shift:
                lines.append("Begrundelse: vagten matcher medarbejderens foretrukne vagttype")
            else:
                lines.append("Begrundelse: medarbejderen var kvalificeret og havde en passende belastningsscore")

        self.set_output(self.explanation_output, "\n".join(lines))
        
    def export_report(self) -> None:
        if not self.current_shifts:
            messagebox.showinfo("Ingen data", "Kør vagtplanen før du eksporterer en rapport.")
            return

        selected_file = filedialog.asksaveasfilename(
            title="Gem rapport",
            defaultextension=".txt",
            filetypes=[("Tekstfiler", "*.txt"), ("Alle filer", "*.*")],
        )

        if not selected_file:
            return

        report_parts = [
            build_assigned_output(self.current_shifts),
            build_unassigned_output(self.current_shifts),
            self.build_current_risk_report_text(),
            build_explanation_output(self.current_shifts, self.current_profiles),
        ]

        with open(selected_file, "w", encoding="utf-8") as file:
            file.write("\n\n".join(report_parts))

        messagebox.showinfo("Export complete", f"Report saved to:\n{selected_file}")
        
    def build_current_risk_report_text(self) -> str:
        lines = ["PERSONALIZED RISK REPORT", "=" * 50]

        for item in self.risk_table.get_children():
            employee, risk, average, shifts = self.risk_table.item(item, "values")
            lines.append(
                f"{employee}: {risk} "
                f"(personalized average={average}, shifts={shifts})"
            )

        return "\n".join(lines)


def main() -> None:
    root = tk.Tk()
    ShiftPlannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()