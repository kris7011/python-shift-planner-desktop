# Python Shift Planner (Desktop)

A simple Python-based shift planning system that assigns employees to shifts based on rules such as skills, availability, rest time, and workload.

## Features

* Assigns employees to shifts based on:

  * Required skills
  * Maximum number of shifts per employee
  * No double shifts on the same day
  * Rest time rules (e.g. no Evening → Day, no Night → next day)

* Supports:

  * Multiple employees per shift
  * Shift priorities (e.g. critical shifts)
  * Workload scoring per shift
  * CSV-based configuration (employees and shifts)

## Project Structure

```
python-shift-planner-desktop/
│
├── app/
│   ├── main.py          # Entry point
│   ├── models.py        # Employee and Shift classes
│   ├── scheduler.py     # Shift assignment logic
│   ├── reporting.py     # Output/reporting
│   └── csv_loader.py    # Load data from CSV
│
├── data/
│   ├── employees.csv
│   └── shifts.csv
│
├── README.md
└── requirements.txt
```

## How to Run

1. Make sure Python is installed
2. Navigate to the project folder:

```
cd python-shift-planner-desktop
```

3. Run the program:

```
python app/main.py
```

## CSV Format

### employees.csv

```
name,max_shifts,skills
Kris,4,CT;MR
Anna,4,CT
Peter,4,MR
Maria,3,CT;UL
Jonas,3,MR;UL
```

### shifts.csv

```
date,shift_type,required_skill,required_staff,priority,workload_score
2026-05-05,Day,CT,2,2,1
2026-05-05,Evening,MR,1,2,2
2026-05-06,Day,CT,2,2,1
2026-05-06,Evening,MR,1,2,2
2026-05-07,Day,CT,1,2,1
2026-05-07,Evening,UL,1,3,2
2026-05-08,Night,MR,1,1,3
2026-05-09,Day,MR,1,2,1
2026-05-09,Day,UL,1,1,1
2026-05-10,Day,CT,2,2,1
2026-05-10,Evening,MR,1,2,2
2026-05-11,Day,UL,1,3,1
```

## Output

The system prints:

* Assigned shifts
* Shift count per employee
* Unassigned shifts
* Critical unassigned shifts
* Employee details
* Employees at capacity
* High workload employees
* Workload score report

## Purpose

This project is a foundation for a more advanced shift planning system.

The goal is to support:

* Better planning decisions
* Employee well-being (workload balancing)
* Detection of overload situations
* Future simulation ("what-if" scenarios)

## Next Steps

* Add GUI (desktop application)
* Add database (SQLite)
* Improve scheduling algorithm (fairness + optimization)
* Add individual employee profiles
* Add rules based on real-world agreements (e.g. Danish working rules)

---

Built as a learning project and stepping stone towards a real-world scheduling system.
