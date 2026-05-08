## Features

* Assigns employees to shifts based on:

  * Required skills
  * Maximum number of shifts per employee
  * No double shifts on the same day
  * Rest time rules
  * Shift priority
  * Workload balancing
  * Personalized employee workload profiles

* Supports:

  * Multiple employees per shift
  * Shift workload scoring
  * Personalized workload calculations
  * Personalized risk reporting
  * Assignment explanation reporting
  * CSV-based configuration
  * Pytest-based unit testing

## Project Structure

```text
python-shift-planner-desktop/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── scheduler.py
│   ├── reporting.py
│   ├── csv_loader.py
│   ├── personalized_workload.py
│   └── assignment_explanation.py
│
├── data/
│   ├── employees.csv
│   ├── shifts.csv
│   └── employee_profiles.csv
│
├── tests/
│   ├── test_csv_loader.py
│   ├── test_employee.py
│   ├── test_scheduler.py
│   ├── test_shift.py
│   └── test_personalized_workload.py
│
├── README.md
├── requirements.txt
└── pytest.ini
```

## How to Run

Run tests:

```powershell
pytest
```

Run the application:

```powershell
py -m app.main
```

## Personalized Employee Profiles

The system supports personalized workload calculations using employee profiles.

Example profile settings:

* Night shift tolerance
* Evening shift tolerance
* Weekly workload tolerance
* Preferred shift type

This allows the system to calculate workload differently per employee.

## Reports

The system generates reports for:

* Assigned shifts
* Unassigned shifts
* Critical unassigned shifts
* Employee workload
* Employee risk levels
* Personalized workload analysis
* Personalized risk analysis
* Assignment explanation reporting

## Assignment Explanation

The scheduler can explain why an employee was assigned to a shift.

Example:

* Required skill match
* Personalized workload score
* Preferred shift match
* Eligibility based on scheduling rules

## Current Status

Current version includes:

* Rule-based scheduling
* Personalized workload analysis
* Explainable assignment reporting
* Unit-tested scheduling logic

The project is currently a prototype and learning project focused on intelligent and explainable shift planning.
