"""The editable calendar tab: a date × shift type grid and a panel for changing one shift."""

import tkinter as tk
from collections.abc import Callable
from datetime import date
from tkinter import ttk

from app.models import Shift
from app.schedule_editor import ScheduleEditError, ScheduleEditor, build_calendar, describe_blocker, describe_shift

WEEKDAYS = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]

STAFFED_COLOUR = "#d1fae5"
MISSING_COLOUR = "#fee2e2"
SELECTED_COLOUR = "#bfdbfe"
OK_TEXT_COLOUR = "#065f46"
ERROR_TEXT_COLOUR = "#991b1b"


class CalendarView(ttk.Frame):
    def __init__(self, parent, on_change: Callable[[], None]):
        super().__init__(parent)
        self.on_change = on_change
        self.editor: ScheduleEditor | None = None
        self.selected_shift: Shift | None = None
        self.shift_buttons: dict[int, tk.Button] = {}
        self.candidate_employees = []

        # The panel is packed first so it keeps its width; the calendar gets the rest and scrolls.
        self._create_edit_panel()
        self._create_scrollable_grid_area()
        tk.Label(self.grid_area, text="Kør vagtplanen for at se kalenderen.").pack(pady=20)

    def _create_scrollable_grid_area(self) -> None:
        container = tk.Frame(self)
        container.pack(side=tk.LEFT, fill="both", expand=True, padx=(10, 4), pady=6)

        history = tk.LabelFrame(container, text="Ændringer (nyeste først) – fortryd med Ctrl+Z", padx=6, pady=4)
        history.pack(side=tk.BOTTOM, fill="x", pady=(6, 0))
        self.history_list = tk.Listbox(history, height=3)
        self.history_list.pack(fill="x")

        canvas = tk.Canvas(container, highlightthickness=0)
        horizontal = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        vertical = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(xscrollcommand=horizontal.set, yscrollcommand=vertical.set)

        horizontal.pack(side=tk.BOTTOM, fill="x")
        vertical.pack(side=tk.RIGHT, fill="y")
        canvas.pack(side=tk.LEFT, fill="both", expand=True)

        self.grid_area = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.grid_area, anchor="nw")
        self.grid_area.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )

    def _create_edit_panel(self) -> None:
        panel = tk.LabelFrame(self, text="Redigér vagt", padx=8, pady=6)
        panel.pack(side=tk.RIGHT, fill="y", padx=(4, 10), pady=6)

        self.shift_label = tk.Label(panel, text="Vælg en vagt i kalenderen.", font=("Arial", 10, "bold"),
                                    wraplength=250, justify="left")
        self.shift_label.pack(anchor="w")

        # Directly under the heading so the result of a change is always visible.
        self.message = tk.Label(panel, text="", wraplength=250, justify="left")
        self.message.pack(anchor="w", pady=(6, 0))

        tk.Label(panel, text="På vagten:").pack(anchor="w", pady=(8, 0))
        self.assigned_list = tk.Listbox(panel, height=2, exportselection=False)
        self.assigned_list.pack(fill="x")

        self.remove_button = tk.Button(panel, text="Fjern valgte", command=self.remove_selected, state=tk.DISABLED)
        self.remove_button.pack(anchor="w", pady=4)

        tk.Label(panel, text="Medarbejder:").pack(anchor="w", pady=(10, 0))
        self.candidate_box = ttk.Combobox(panel, state="readonly", width=34)
        self.candidate_box.pack(fill="x")

        buttons = tk.Frame(panel)
        buttons.pack(anchor="w", pady=4)
        self.add_button = tk.Button(buttons, text="Tilføj", command=self.add_selected, state=tk.DISABLED)
        self.add_button.pack(side=tk.LEFT)
        self.replace_button = tk.Button(buttons, text="Erstat valgte", command=self.replace_selected,
                                        state=tk.DISABLED)
        self.replace_button.pack(side=tk.LEFT, padx=6)


    def load(self, editor: ScheduleEditor) -> None:
        self.editor = editor
        self.selected_shift = None
        self.show_message("")
        self.refresh()

    def clear(self) -> None:
        self.editor = None
        self.selected_shift = None
        self.show_message("")
        self.refresh()

    def refresh(self) -> None:
        self._draw_grid()
        self._update_panel()

    def _draw_grid(self) -> None:
        for child in self.grid_area.winfo_children():
            child.destroy()

        self.shift_buttons = {}

        if self.editor is None or not self.editor.shifts:
            tk.Label(self.grid_area, text="Kør vagtplanen for at se kalenderen.").pack(pady=20)
            return

        dates, shift_types, cells = build_calendar(self.editor.shifts)
        table = tk.Frame(self.grid_area)
        table.pack(anchor="nw")

        for column, day in enumerate(dates, start=1):
            weekday = WEEKDAYS[date.fromisoformat(day).weekday()]
            tk.Label(table, text=f"{weekday}\n{day}", font=("Arial", 9, "bold")).grid(row=0, column=column, padx=2)

        for row, shift_type in enumerate(shift_types, start=1):
            tk.Label(table, text=shift_type.display_name, font=("Arial", 9, "bold")).grid(row=row, column=0, sticky="e",
                                                                                            padx=4)

            for column, day in enumerate(dates, start=1):
                cell_frame = tk.Frame(table, bd=1, relief="solid", width=130, height=70)
                cell_frame.grid(row=row, column=column, padx=2, pady=2, sticky="nsew")
                cell = cells.get((day, shift_type))

                if cell is None:
                    tk.Label(cell_frame, text="–", fg="#9ca3af", width=12).pack(pady=8)
                    continue

                for shift in cell.shifts:
                    self._add_shift_button(cell_frame, shift)

    def _add_shift_button(self, parent: tk.Frame, shift: Shift) -> None:
        names = ", ".join(employee.name for employee in shift.assigned_employees) or "Ingen"
        staffing = f"{len(shift.assigned_employees)}/{shift.required_staff}"

        button = tk.Button(
            parent,
            text=f"{shift.required_skill} {staffing}\n{names}",
            width=12,
            wraplength=100,
            justify="center",
            relief="flat",
            bg=self._colour(shift),
            command=lambda: self.select_shift(shift),
        )
        button.pack(fill="x", padx=2, pady=2)
        self.shift_buttons[id(shift)] = button

    def _colour(self, shift: Shift) -> str:
        if shift is self.selected_shift:
            return SELECTED_COLOUR

        return STAFFED_COLOUR if shift.is_fully_staffed else MISSING_COLOUR

    def select_shift(self, shift: Shift) -> None:
        self.selected_shift = shift
        self.show_message("")

        for button_shift in self.editor.shifts:
            button = self.shift_buttons.get(id(button_shift))
            if button is not None:
                button.configure(bg=self._colour(button_shift))

        self._update_panel()

    def _update_panel(self) -> None:
        self.assigned_list.delete(0, tk.END)
        self.history_list.delete(0, tk.END)
        self.candidate_box.set("")

        if self.editor is not None:
            for description in self.editor.history:
                self.history_list.insert(tk.END, description)

        shift = self.selected_shift

        if self.editor is None or shift is None:
            self.shift_label.configure(text="Vælg en vagt i kalenderen.")
            self.candidate_box.configure(values=[])
            for button in (self.remove_button, self.add_button, self.replace_button):
                button.configure(state=tk.DISABLED)
            return

        self.shift_label.configure(
            text=f"{describe_shift(shift)}\nBemanding {len(shift.assigned_employees)}/{shift.required_staff}, "
                 f"prioritet {shift.priority}"
        )

        for employee in shift.assigned_employees:
            self.assigned_list.insert(tk.END, employee.name)

        candidates = self.editor.candidates(shift)
        self.candidate_employees = [employee for employee, _ in candidates]
        self.candidate_box.configure(
            values=[
                employee.name if not blockers
                else f"{employee.name} – {', '.join(describe_blocker(blocker) for blocker in blockers)}"
                for employee, blockers in candidates
            ]
        )

        has_people = bool(shift.assigned_employees)
        self.remove_button.configure(state=tk.NORMAL if has_people else tk.DISABLED)
        self.replace_button.configure(state=tk.NORMAL if has_people and candidates else tk.DISABLED)
        self.add_button.configure(state=tk.NORMAL if candidates else tk.DISABLED)

    def _chosen_candidate(self):
        index = self.candidate_box.current()

        if index < 0:
            self.show_message("Vælg en medarbejder først.", error=True)
            return None

        return self.candidate_employees[index]

    def _chosen_assigned(self):
        selection = self.assigned_list.curselection()

        if not selection:
            self.show_message("Vælg en medarbejder på vagten først.", error=True)
            return None

        return self.selected_shift.assigned_employees[selection[0]]

    def add_selected(self) -> None:
        employee = self._chosen_candidate()

        if employee is not None:
            self._apply(lambda: self.editor.assign(self.selected_shift, employee), employee.name)

    def remove_selected(self) -> None:
        employee = self._chosen_assigned()

        if employee is not None:
            self._apply(lambda: self.editor.unassign(self.selected_shift, employee), employee.name)

    def replace_selected(self) -> None:
        current = self._chosen_assigned()
        replacement = self._chosen_candidate() if current is not None else None

        if current is not None and replacement is not None:
            self._apply(lambda: self.editor.replace(self.selected_shift, current, replacement), replacement.name)

    def undo(self) -> None:
        if self.editor is None:
            return

        edit = self.editor.undo()

        if edit is None:
            self.show_message("Der er intet at fortryde.", error=True)
            return

        self.refresh()
        self.show_message(f"Fortrudt: {edit.description}")
        self.on_change()

    def _apply(self, change: Callable, employee_name: str) -> None:
        try:
            edit = change()
        except ScheduleEditError as error:
            reasons = ", ".join(describe_blocker(reason) for reason in error.reasons)
            self.show_message(f"Ikke tilladt for {employee_name}: {reasons}.", error=True)
            return

        self.refresh()
        self.show_message(edit.description)
        self.on_change()

    def show_message(self, text: str, error: bool = False) -> None:
        self.message.configure(text=text, fg=ERROR_TEXT_COLOUR if error else OK_TEXT_COLOUR)
