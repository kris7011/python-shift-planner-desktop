# Python Shift Planner Desktop — project walkthrough

A developer-level guide to the system and, in depth, to the editable calendar, undo and PDF export. It describes only what exists in the repository.

## 1. System overview

```text
CSV files (data/) ──► csv_loader ──► Employee / Shift / EmployeeProfile (models.py)
                                         │
                                         ▼
                                  scheduler.assign_shifts      rule-based assignment
                                         │
                     ┌───────────────────┼───────────────────────┐
                     ▼                   ▼                       ▼
            gui.ShiftPlannerApp   schedule_editor           pdf_export
            (Tkinter tabs)        (manual changes, undo)    (ReportLab)
                     │
                     └─ calendar_view.CalendarView (Kalender tab)
```

The scheduler's rules live on `Employee`: `can_take_shift` and `get_shift_blockers` check capacity, required skill, one shift per day, and rest time (no shift the day after a night; no day shift the morning after an evening).

## 2. Editable calendar, undo and PDF export

### Problem

A generated schedule is a starting point. Planners need to correct it by hand without breaking the rules the scheduler respects, take back a mistake, and hand the result out as a document.

### `app/schedule_editor.py` (no Tk, fully tested)

- `ScheduleEditor(employees, shifts)` changes the same objects the GUI displays.
- `assignment_blockers(shift, employee)` = "already assigned", "shift is fully staffed", plus `employee.get_shift_blockers(shift)`. **The scheduler's rules are reused, not copied**, so a rule change applies to both automatic and manual planning.
- `assign`, `unassign`, `replace` raise `ScheduleEditError(reasons)` and change nothing when a rule would break. `replace` removes the current employee first, checks the replacement against that state, and restores the original if the check fails.
- **Undo (command pattern):** each edit records `_Placement`s: the shift, the employee and their positions in both lists. `undo()` removes what was added and re-inserts what was removed at the original positions, so the state, including list order, is exactly as before. A test compares full snapshots of both sides of every assignment.
- `build_calendar(shifts)` groups shifts into a date × shift type grid.
- `describe_blocker` turns rule codes into Danish text for the GUI.

### `app/calendar_view.py` (Tk)

- The edit panel is packed before the grid, so it keeps its width; the grid sits in a scrollable canvas.
- Cells show skill, staffing (`1/2`) and names; green = fully staffed, red = missing staff, blue = selected.
- The employee list shows every candidate, with the reasons for those who cannot take the shift, so the planner sees *why* before trying.
- After each change the view calls back into `ShiftPlannerApp.refresh_after_edit`, which refreshes the other tabs and the undo button.

### `app/pdf_export.py`

- ReportLab (BSD licence) builds an A4 landscape document: period, print time, number of manual changes, all shifts (rows missing staff highlighted) and an employee table.
- **File safety:** the name must end in `.pdf`; an existing file is refused unless `overwrite=True`; the PDF is written to a temporary file in the same folder and moved into place with `os.replace`, so a failure leaves any existing file untouched and no temporary file behind. The GUI passes `overwrite=True` only after the native save dialog (`confirmoverwrite=True`) has asked the user.
- Names are escaped before going into ReportLab paragraphs, which interpret markup.

### Input files are never written

Edits change objects in memory only. "Kør vagtplan" rebuilds from the CSV files and asks for confirmation when there are manual changes, so work is not lost silently. A test hashes the three CSV files before and after editing and exporting.

## 3. Testing

| File | What it proves |
| --- | --- |
| `tests/test_schedule_editor.py` (19) | assignments go through the scheduler's rules (skill, capacity, same day, rest time), full shifts, duplicates, candidates with reasons, replace semantics, refused changes leave the state unchanged, undo order and completeness, calendar grouping, Danish rule text |
| `tests/test_pdf_export.py` (5) | PDF content (period, change count, names), no overwrite without permission, existing file kept and no temp file left when the build fails, `.pdf` required, CSV inputs unchanged |
| existing tests (48) | scheduler, models, CSV loading, personalised workload |

Total: **72 passed** locally (Python 3.12). CI runs Python 3.12 and 3.13 on Ubuntu. The tests do not import Tkinter, so they need no display.

Not automated: the Tk widgets. They contain no rules; they call the tested editor.

## 4. Desktop demonstration (1 November 2026, Windows 11, Python 3.12, Tk 8.6)

The real application window was opened and driven by a script (`invoke()` on the real buttons, which runs the same code as a click). Only the modal save dialog and message boxes were replaced. Screenshots are of the actual window:

1. "Kør vagtplan": 12 shifts; Monday 2026-05-11 Day UL is unstaffed (1 row in "Ubesatte vagter").
2. Adding Jonas to it was refused: "Ikke tilladt for Jonas: har nået sit maksimale antal vagter, får for kort hviletid (nat eller aften før en vagt)."
3. Replacing Jonas with Peter on Sunday evening succeeded; then Jonas could take Monday's shift. "Ubesatte vagter" became empty, and the history showed both changes.
4. "Eksportér PDF" (dialog options included `confirmoverwrite: True`) wrote a 2-page PDF: "12 vagter, 12 fuldt bemandede … Manuelle ændringer: 2."
5. "Fortryd" reverted the last change; Monday was unstaffed again.
6. The SHA-256 of all three CSV files was unchanged.

The demo also found two layout problems in the first version, both fixed: the edit panel could be pushed out of the window at the default width, and the change history was cut off.

## 5. Limitations

- An edited schedule cannot be saved for later (only exported as PDF).
- Undo has no redo.
- The calendar is a grid, not drag-and-drop.
- The GUI is not DPI-aware on Windows; at high display scaling it is scaled by Windows.

## 6. Ownership and AI assistance

Implemented with AI assistance (Claude Code). The owner defined the requirements (editable calendar, undo, PDF export, reuse of validation, no overwriting of user files) and reviews and merges.

## 7. Interview preparation

**Non-technical:** After the plan is generated you can click any shift, swap or add people, and the program stops changes that break the rest and skill rules, telling you why. You can undo, and print the plan as a PDF.

**Developer:** `ScheduleEditor` reuses `Employee.get_shift_blockers`, records each change as a command with list positions, and undo replays it backwards. The Tk view only calls the editor and redraws.

**Senior:** Rules have a single source of truth shared by automatic and manual planning. State changes are reversible and atomic (a refused replace restores itself). File output is atomic and never overwrites without consent. The GUI is a thin layer, so the logic is tested without a display.

**Questions and answers**

1. *Why the command pattern instead of saving a copy of the whole schedule for undo?* Each edit touches one or two assignments; recording them is small and exact, and it keeps object identity (the GUI holds references to the same objects).
2. *Why check the replacement after removing the current employee?* Otherwise a full shift or the current person's own shift would block every replacement.
3. *How do you avoid overwriting a user's file?* The function refuses existing files unless told otherwise; the GUI only says so after the OS dialog asked; the write goes through a temporary file and an atomic rename.
4. *Why ReportLab?* Mature, BSD-licensed, pure Python with wheels, and good table layout. It is the only new runtime dependency.
5. *What is not tested and why is that acceptable?* The Tk widgets. They hold no rules; the editor they call is tested, and the window was demonstrated on Windows.

**Hands-on exercise:** Add redo: keep a second stack, push to it in `undo()`, clear it on every new edit, add `redo()` with tests, and bind Ctrl+Y in the GUI.
