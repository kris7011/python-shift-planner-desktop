import pytest

from app.constants import ShiftType
from app.models import Employee, Shift
from app.schedule_editor import ScheduleEditError, ScheduleEditor, build_calendar, describe_blocker


def make_schedule():
    anna = Employee(name="Anna", max_shifts=2, skills=["CT"])
    kris = Employee(name="Kris", max_shifts=3, skills=["CT", "MR"])
    peter = Employee(name="Peter", max_shifts=3, skills=["MR"])

    monday_day = Shift(date="2026-05-11", shift_type=ShiftType.DAY, required_skill="CT", required_staff=2)
    monday_night = Shift(date="2026-05-11", shift_type=ShiftType.NIGHT, required_skill="MR")
    tuesday_day = Shift(date="2026-05-12", shift_type=ShiftType.DAY, required_skill="CT")

    editor = ScheduleEditor([anna, kris, peter], [monday_day, monday_night, tuesday_day])

    return editor, anna, kris, peter, monday_day, monday_night, tuesday_day


def snapshot(editor: ScheduleEditor):
    """The full assignment state, including list order, for exact comparisons."""
    return (
        [[employee.name for employee in shift.assigned_employees] for shift in editor.shifts],
        [[id(shift) for shift in employee.assigned_shifts] for employee in editor.employees],
    )


def test_assign_adds_the_employee_on_both_sides():
    editor, anna, _, _, monday_day, _, _ = make_schedule()

    edit = editor.assign(monday_day, anna)

    assert monday_day.assigned_employees == [anna]
    assert anna.assigned_shifts == [monday_day]
    assert edit.description == "Tilføjede Anna til 2026-05-11 Dag (CT)"
    assert editor.can_undo


@pytest.mark.parametrize(
    ("setup", "employee_name", "shift_index", "expected"),
    [
        ("none", "Peter", 0, "missing skill CT"),
        ("kris_monday_day", "Kris", 1, "already has shift same day"),
        ("kris_monday_night", "Kris", 2, "rest time violation"),
        ("anna_two_shifts", "Anna", 0, "at capacity"),
    ],
)
def test_assign_reuses_the_scheduler_rules(setup, employee_name, shift_index, expected):
    editor, anna, kris, peter, monday_day, monday_night, tuesday_day = make_schedule()
    extra_day = Shift(date="2026-05-13", shift_type=ShiftType.DAY, required_skill="CT")
    extra_day_2 = Shift(date="2026-05-14", shift_type=ShiftType.DAY, required_skill="CT")

    if setup == "kris_monday_day":
        editor.assign(monday_day, kris)
    elif setup == "kris_monday_night":
        editor.assign(monday_night, kris)
    elif setup == "anna_two_shifts":
        editor.assign(extra_day, anna)
        editor.assign(extra_day_2, anna)

    employee = {"Anna": anna, "Kris": kris, "Peter": peter}[employee_name]
    shift = [monday_day, monday_night, tuesday_day][shift_index]
    before = snapshot(editor)

    with pytest.raises(ScheduleEditError) as error:
        editor.assign(shift, employee)

    assert expected in error.value.reasons
    assert snapshot(editor) == before


def test_a_fully_staffed_shift_cannot_take_more_people():
    editor, anna, kris, peter, monday_day, monday_night, _ = make_schedule()
    editor.assign(monday_night, peter)

    with pytest.raises(ScheduleEditError) as error:
        editor.assign(monday_night, kris)

    assert error.value.reasons == ["shift is fully staffed"]


def test_assigning_the_same_employee_twice_is_refused():
    editor, anna, _, _, monday_day, _, _ = make_schedule()
    editor.assign(monday_day, anna)

    with pytest.raises(ScheduleEditError) as error:
        editor.assign(monday_day, anna)

    assert error.value.reasons == ["already assigned to this shift"]


def test_candidates_list_every_employee_not_on_the_shift_with_their_blockers():
    editor, anna, kris, peter, monday_day, _, _ = make_schedule()
    editor.assign(monday_day, anna)

    candidates = {employee.name: blockers for employee, blockers in editor.candidates(monday_day)}

    assert candidates == {"Kris": [], "Peter": ["missing skill CT"]}


def test_replace_checks_the_replacement_as_if_the_current_employee_had_left():
    editor, _, kris, peter, _, monday_night, _ = make_schedule()
    editor.assign(monday_night, peter)

    # The shift is full, but Kris may take Peter's place.
    edit = editor.replace(monday_night, peter, kris)

    assert monday_night.assigned_employees == [kris]
    assert peter.assigned_shifts == []
    assert edit.description == "Erstattede Peter med Kris på 2026-05-11 Nat (MR)"


def test_a_refused_replacement_leaves_the_schedule_unchanged():
    editor, anna, _, peter, _, monday_night, _ = make_schedule()
    editor.assign(monday_night, peter)
    before = snapshot(editor)

    with pytest.raises(ScheduleEditError) as error:
        editor.replace(monday_night, peter, anna)

    assert error.value.reasons == ["missing skill MR"]
    assert snapshot(editor) == before
    assert editor.edit_count == 1


def test_undo_reverts_edits_one_at_a_time_and_restores_list_order():
    editor, anna, kris, peter, monday_day, monday_night, tuesday_day = make_schedule()
    editor.assign(monday_day, anna)
    editor.assign(monday_day, kris)
    editor.assign(monday_night, peter)
    after_assignments = snapshot(editor)

    editor.unassign(monday_day, anna)
    editor.assign(tuesday_day, anna)

    assert editor.history == [
        "Tilføjede Anna til 2026-05-12 Dag (CT)",
        "Fjernede Anna fra 2026-05-11 Dag (CT)",
        "Tilføjede Peter til 2026-05-11 Nat (MR)",
        "Tilføjede Kris til 2026-05-11 Dag (CT)",
        "Tilføjede Anna til 2026-05-11 Dag (CT)",
    ]

    editor.undo()
    editor.undo()

    # Anna is back in front of Kris, exactly as before the removal.
    assert snapshot(editor) == after_assignments
    assert monday_day.assigned_employees == [anna, kris]

    while editor.can_undo:
        editor.undo()

    assert all(not shift.assigned_employees for shift in editor.shifts)
    assert all(not employee.assigned_shifts for employee in editor.employees)
    assert editor.undo() is None


def test_undoing_a_replacement_brings_back_the_original_employee():
    editor, _, kris, peter, _, monday_night, _ = make_schedule()
    editor.assign(monday_night, peter)
    before = snapshot(editor)

    editor.replace(monday_night, peter, kris)
    undone = editor.undo()

    assert undone.description.startswith("Erstattede Peter med Kris")
    assert snapshot(editor) == before


def test_unassigning_someone_not_on_the_shift_is_refused():
    editor, anna, _, _, monday_day, _, _ = make_schedule()

    with pytest.raises(ScheduleEditError):
        editor.unassign(monday_day, anna)

    assert not editor.can_undo


def test_clear_history_forgets_edits_without_changing_the_schedule():
    editor, anna, _, _, monday_day, _, _ = make_schedule()
    editor.assign(monday_day, anna)

    editor.clear_history()

    assert not editor.can_undo
    assert monday_day.assigned_employees == [anna]


def test_build_calendar_groups_shifts_by_date_and_type():
    _, anna, _, _, monday_day, monday_night, tuesday_day = make_schedule()
    second_monday_day = Shift(date="2026-05-11", shift_type="Day", required_skill="MR", priority=1)

    dates, shift_types, cells = build_calendar([tuesday_day, monday_night, monday_day, second_monday_day])

    assert dates == ["2026-05-11", "2026-05-12"]
    assert shift_types == [ShiftType.DAY, ShiftType.EVENING, ShiftType.NIGHT]
    assert cells[("2026-05-11", ShiftType.DAY)].shifts == [second_monday_day, monday_day]
    assert cells[("2026-05-11", ShiftType.DAY)].missing_staff == 3
    assert ("2026-05-12", ShiftType.EVENING) not in cells


@pytest.mark.parametrize(
    ("blocker", "text"),
    [
        ("missing skill CT", "mangler kompetencen CT"),
        ("rest time violation", "får for kort hviletid (nat eller aften før en vagt)"),
        ("shift is fully staffed", "vagten er fuldt bemandet"),
        ("something new", "something new"),
    ],
)
def test_blockers_are_described_in_danish(blocker, text):
    assert describe_blocker(blocker) == text
