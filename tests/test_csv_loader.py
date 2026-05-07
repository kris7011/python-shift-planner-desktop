import pytest
from app.csv_loader import parse_int


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