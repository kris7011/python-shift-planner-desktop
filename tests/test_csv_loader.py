import pytest
from unittest.mock import patch, mock_open
from app.constants import ShiftType
from app.csv_loader import parse_int, parse_float, load_shifts_from_csv, load_employees_from_csv, load_employee_profiles_from_csv

def test_parse_int_returns_default_for_empty_value():
    result = parse_int("", default=1, field_name="required_staff")
    assert result == 1

def test_parse_int_returns_default_for_none():
    result = parse_int(None, default=2, field_name="priority")
    assert result == 2

def test_parse_int_converts_valid_number():
    result = parse_int("3", default=1, field_name="workload_score")
    assert result == 3

def test_parse_int_raises_for_invalid_number():
    with pytest.raises(ValueError):
        parse_int("abc", default=1, field_name="required_staff")

def test_load_shifts_from_csv_integration():
    # Simulate the content of a shifts.csv file
    csv_content = (
        "date,shift_type,required_skill,required_staff,priority,workload_score\n"
        "2026-05-01,Day,Nurse,2,1,3"
    )
    
    # Mock the open function to return our csv_content instead of reading from disk
    with patch("builtins.open", mock_open(read_data=csv_content)):
        shifts = load_shifts_from_csv("dummy_path.csv")
        
        assert len(shifts) == 1
        assert shifts[0].date == "2026-05-01"
        assert shifts[0].required_skill == "Nurse"
        assert shifts[0].required_staff == 2

def test_load_employees_from_csv_integration():
    # Simulate the content of an employees.csv file
    csv_content = (
        "name,max_shifts,skills\n"
        "Henrik,5,Assistant;Nurse"
    )
    
    with patch("builtins.open", mock_open(read_data=csv_content)):
        employees = load_employees_from_csv("dummy_path.csv")
        
        assert len(employees) == 1
        assert employees[0].name == "Henrik"
        assert employees[0].max_shifts == 5
        assert "Nurse" in employees[0].skills

def test_load_shifts_raises_error_on_invalid_data():
    # Test that the loader catches invalid numeric data in the CSV
    csv_content = (
        "date,shift_type,required_skill,required_staff,priority,workload_score\n"
        "2026-05-01,Day,Nurse,NOT_A_NUMBER,1,3"
    )
    
    with patch("builtins.open", mock_open(read_data=csv_content)):
        with pytest.raises(ValueError) as exception_info:
            load_shifts_from_csv("dummy_path.csv")
        
        assert "required_staff" in str(exception_info.value)
        
def test_load_employees_raises_error_when_name_missing():
    # CSV row with an empty name field
    csv_content = "name,max_shifts,skills\n,5,Assistant"
    
    with patch("builtins.open", mock_open(read_data=csv_content)):
        with pytest.raises(ValueError) as exc_info:
            load_employees_from_csv("dummy.csv")
        assert "name" in str(exc_info.value).lower()

def test_load_employees_raises_error_when_skills_missing():
    # CSV row with an empty skills field
    csv_content = "name,max_shifts,skills\nHenrik,5,"
    
    with patch("builtins.open", mock_open(read_data=csv_content)):
        with pytest.raises(ValueError) as exc_info:
            load_employees_from_csv("dummy.csv")
        assert "skills" in str(exc_info.value).lower()

def test_load_employees_raises_error_when_max_shifts_invalid():
    # CSV row with non-numeric value in max_shifts
    csv_content = "name,max_shifts,skills\nHenrik,FIVE,Assistant"
    
    with patch("builtins.open", mock_open(read_data=csv_content)):
        with pytest.raises(ValueError) as exc_info:
            load_employees_from_csv("dummy.csv")
        assert "max_shifts" in str(exc_info.value)
        assert "number" in str(exc_info.value).lower()

def test_parse_float_returns_default_for_empty_value():
    result = parse_float("", default=0.5, field_name="night_tolerance")
    assert result == 0.5


def test_parse_float_converts_valid_number():
    result = parse_float("0.8", default=0.5, field_name="late_tolerance")
    assert result == 0.8


def test_parse_float_raises_for_invalid_number():
    with pytest.raises(ValueError):
        parse_float("abc", default=0.5, field_name="night_tolerance")


def test_load_employee_profiles_from_csv_integration():
    csv_content = (
        "employee_id,name,night_tolerance,weekend_tolerance,late_tolerance,max_weekly_load,preferred_shift\n"
        "1,Anna,0.4,0.6,0.8,35,DAY\n"
        "2,Peter,0.9,0.7,0.5,40,NIGHT"
    )

    with patch("builtins.open", mock_open(read_data=csv_content)):
        profiles = load_employee_profiles_from_csv("dummy_path.csv")

        assert len(profiles) == 2
        assert profiles[0].employee_id == "1"
        assert profiles[0].name == "Anna"
        assert profiles[0].night_tolerance == 0.4
        assert profiles[0].preferred_shift == ShiftType.DAY
        assert profiles[1].preferred_shift == ShiftType.NIGHT
        
def test_load_employee_profiles_raises_error_when_name_missing():
    csv_content = (
        "employee_id,name,night_tolerance,weekend_tolerance,late_tolerance,max_weekly_load,preferred_shift\n"
        "1,,0.4,0.6,0.8,35,DAY"
    )

    with patch("builtins.open", mock_open(read_data=csv_content)):
        with pytest.raises(ValueError) as exc_info:
            load_employee_profiles_from_csv("dummy.csv")

        assert "name" in str(exc_info.value).lower()