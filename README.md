# Python Shift Planner Desktop

Desktop-based shift planning and workload analysis system built in Python.

The project focuses on:

- Intelligent shift assignment
- Workload balancing
- Employee well-being analysis
- Personalized workload scoring
- Risk detection
- Transparent assignment explanations
- GUI-based schedule analysis

The system is inspired by real-world healthcare scheduling challenges in 24/7 departments.

---

## Features

### Shift Planning

- Assign employees to shifts based on:
  - Skills
  - Capacity
  - Rest time rules
  - Shift conflicts
  - Personalized workload tolerance

### Workload & Risk Analysis

- Workload score calculation
- Personalized workload scoring
- Employee risk analysis
- Heavy shift detection
- Capacity warnings
- Unassigned shift tracking

### GUI Application

- Desktop GUI built with Tkinter
- CSV file selection
- Interactive tables
- Shift explanation viewer
- Report export to `.txt`

### Assignment Transparency

The system explains WHY employees were assigned:

- Required skill match
- Preferred shift match
- Personalized workload score
- Eligibility reasoning

---

# Screenshots

## Main GUI

_Add screenshot here later_

---

## Technologies

- Python 3.12
- Tkinter
- Pytest
- CSV-based data import

---

## Project Structure

```text
python-shift-planner-desktop/
│
├── app/
│   ├── gui.py
│   ├── main.py
│   ├── scheduler.py
│   ├── models.py
│   ├── reporting.py
│   ├── csv_loader.py
│   ├── personalized_workload.py
│   ├── assignment_explanation.py
│   └── constants.py
│
├── data/
│   ├── employees.csv
│   ├── shifts.csv
│   └── employee_profiles.csv
│
├── tests/
│
├── requirements.txt
├── pytest.ini
└── README.md
```

---

# Installation

Clone repository:

```bash
git clone https://github.com/kris7011/python-shift-planner-desktop.git
```

Navigate to project:

```bash
cd python-shift-planner-desktop
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Run Application

Run GUI:

```bash
py -m app.gui
```

Run tests:

```bash
pytest
```

---

# CSV Data Format

## employees.csv

```csv
name,max_shifts,skills
Kris,4,CT;MR
Anna,4,CT
Peter,4,MR
```

## shifts.csv

```csv
date,shift_type,required_skill,required_staff,priority,workload_score
2026-05-05,Day,CT,2,2,1
2026-05-05,Evening,MR,1,2,2
```

## employee_profiles.csv

```csv
employee_id,name,night_tolerance,weekend_tolerance,late_tolerance,max_weekly_load,preferred_shift
1,Anna,0.4,0.6,0.8,35,DAY
```

---

# Current Capabilities

- Multi-staff shift assignment
- Risk scoring
- Personalized workload analysis
- Rest-time validation
- GUI reporting
- Report export
- Interactive explanations

---

# Planned Features

- SQLite database
- Drag-and-drop scheduling
- Calendar view
- Fairness optimization
- AI-assisted scheduling
- What-if simulations
- PDF export
- Employee preference management
- Real-world agreement rules

---

# Testing

Project includes automated unit tests using Pytest.

Current coverage includes:

- Employee rules
- Shift rules
- CSV loading
- Personalized workload scoring
- Scheduler behavior

---

# Purpose

This project was created as part of a larger initiative exploring:

- Workforce planning
- Employee well-being
- Scheduling optimization
- Healthcare operations
- Explainable scheduling systems

---

# Status

Active development.

The project is continuously evolving with new scheduling logic, GUI improvements, and workload analysis features.
