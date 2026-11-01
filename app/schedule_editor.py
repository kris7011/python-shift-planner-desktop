"""Manual changes to a generated schedule, validated by the same rules as the scheduler, with undo.

The editor changes the in-memory Shift and Employee objects only. It never writes to the CSV
files the schedule was loaded from.
"""

from dataclasses import dataclass, field
from datetime import date

from app.constants import ShiftType
from app.models import Employee, Shift

SHIFT_TYPE_ORDER = [ShiftType.DAY, ShiftType.EVENING, ShiftType.NIGHT]


class ScheduleEditError(ValueError):
    """Raised when a change would break a scheduling rule. `reasons` lists every broken rule."""

    def __init__(self, reasons: list[str]):
        super().__init__("; ".join(reasons))
        self.reasons = reasons


@dataclass
class _Placement:
    """Where an assignment sits in both lists, so undo can put it back in the same position."""

    shift: Shift
    employee: Employee
    shift_index: int
    employee_index: int


@dataclass
class ScheduleEdit:
    description: str
    removed: list[_Placement] = field(default_factory=list)
    added: list[_Placement] = field(default_factory=list)


_BLOCKER_TEXTS = {
    "at capacity": "har nået sit maksimale antal vagter",
    "already has shift same day": "har allerede en vagt samme dag",
    "rest time violation": "får for kort hviletid (nat eller aften før en vagt)",
    "shift is fully staffed": "vagten er fuldt bemandet",
    "already assigned to this shift": "er allerede på vagten",
    "not assigned to this shift": "er ikke på vagten",
}


def describe_blocker(blocker: str) -> str:
    """Danish text for a rule the change would break, as shown in the GUI."""
    if blocker.startswith("missing skill "):
        return f"mangler kompetencen {blocker.removeprefix('missing skill ')}"

    return _BLOCKER_TEXTS.get(blocker, blocker)


def describe_shift(shift: Shift) -> str:
    return f"{shift.date} {shift.shift_type.display_name} ({shift.required_skill})"


class ScheduleEditor:
    def __init__(self, employees: list[Employee], shifts: list[Shift]):
        self.employees = employees
        self.shifts = shifts
        self._undo_stack: list[ScheduleEdit] = []

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def history(self) -> list[str]:
        """Descriptions of the edits that can be undone, newest first."""
        return [edit.description for edit in reversed(self._undo_stack)]

    @property
    def edit_count(self) -> int:
        return len(self._undo_stack)

    def assignment_blockers(self, shift: Shift, employee: Employee) -> list[str]:
        """Every reason the employee cannot be added to the shift; empty when the change is allowed."""
        if employee in shift.assigned_employees:
            return ["already assigned to this shift"]

        blockers = []

        if shift.is_fully_staffed:
            blockers.append("shift is fully staffed")

        # The scheduler's own checks: capacity, skill, same day and rest time.
        blockers.extend(employee.get_shift_blockers(shift))

        return blockers

    def candidates(self, shift: Shift) -> list[tuple[Employee, list[str]]]:
        """All employees not on the shift, each with the reasons they cannot take it (if any)."""
        return [
            (employee, self.assignment_blockers(shift, employee))
            for employee in self.employees
            if employee not in shift.assigned_employees
        ]

    def assign(self, shift: Shift, employee: Employee) -> ScheduleEdit:
        blockers = self.assignment_blockers(shift, employee)

        if blockers:
            raise ScheduleEditError(blockers)

        edit = ScheduleEdit(description=f"Tilføjede {employee.name} til {describe_shift(shift)}")
        edit.added.append(self._add(shift, employee))
        self._undo_stack.append(edit)

        return edit

    def unassign(self, shift: Shift, employee: Employee) -> ScheduleEdit:
        if employee not in shift.assigned_employees:
            raise ScheduleEditError(["not assigned to this shift"])

        edit = ScheduleEdit(description=f"Fjernede {employee.name} fra {describe_shift(shift)}")
        edit.removed.append(self._remove(shift, employee))
        self._undo_stack.append(edit)

        return edit

    def replace(self, shift: Shift, current: Employee, replacement: Employee) -> ScheduleEdit:
        """Swaps one employee on a shift for another; the replacement is checked as if the current one had left."""
        if current not in shift.assigned_employees:
            raise ScheduleEditError(["not assigned to this shift"])

        removed = self._remove(shift, current)
        blockers = self.assignment_blockers(shift, replacement)

        if blockers:
            self._restore(removed)
            raise ScheduleEditError(blockers)

        edit = ScheduleEdit(
            description=f"Erstattede {current.name} med {replacement.name} på {describe_shift(shift)}",
            removed=[removed],
            added=[self._add(shift, replacement)],
        )
        self._undo_stack.append(edit)

        return edit

    def undo(self) -> ScheduleEdit | None:
        """Reverts the latest edit exactly, including the order of the assignment lists."""
        if not self._undo_stack:
            return None

        edit = self._undo_stack.pop()

        for placement in reversed(edit.added):
            placement.shift.assigned_employees.remove(placement.employee)
            placement.employee.assigned_shifts.remove(placement.shift)

        for placement in reversed(edit.removed):
            self._restore(placement)

        return edit

    def clear_history(self) -> None:
        """Called when a new schedule is generated: earlier edits belong to the old schedule."""
        self._undo_stack.clear()

    @staticmethod
    def _add(shift: Shift, employee: Employee) -> _Placement:
        placement = _Placement(
            shift=shift,
            employee=employee,
            shift_index=len(shift.assigned_employees),
            employee_index=len(employee.assigned_shifts),
        )
        shift.assigned_employees.append(employee)
        employee.assigned_shifts.append(shift)

        return placement

    @staticmethod
    def _remove(shift: Shift, employee: Employee) -> _Placement:
        placement = _Placement(
            shift=shift,
            employee=employee,
            shift_index=shift.assigned_employees.index(employee),
            employee_index=employee.assigned_shifts.index(shift),
        )
        shift.assigned_employees.pop(placement.shift_index)
        employee.assigned_shifts.pop(placement.employee_index)

        return placement

    @staticmethod
    def _restore(placement: _Placement) -> None:
        placement.shift.assigned_employees.insert(placement.shift_index, placement.employee)
        placement.employee.assigned_shifts.insert(placement.employee_index, placement.shift)


@dataclass
class CalendarCell:
    date: str
    shift_type: ShiftType
    shifts: list[Shift]

    @property
    def missing_staff(self) -> int:
        return sum(max(shift.missing_staff_count, 0) for shift in self.shifts)


def build_calendar(shifts: list[Shift]) -> tuple[list[str], list[ShiftType], dict[tuple[str, ShiftType], CalendarCell]]:
    """Groups shifts into a date × shift type grid for the calendar view.

    Returns the dates in order, the shift types in day order, and the cells that have shifts.
    """
    dates = sorted({shift.date for shift in shifts}, key=date.fromisoformat)
    cells: dict[tuple[str, ShiftType], CalendarCell] = {}

    for shift in shifts:
        key = (shift.date, shift.shift_type)
        cells.setdefault(key, CalendarCell(shift.date, shift.shift_type, [])).shifts.append(shift)

    for cell in cells.values():
        cell.shifts.sort(key=lambda shift: (shift.priority, shift.required_skill))

    return dates, SHIFT_TYPE_ORDER, cells
