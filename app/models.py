import datetime

class Employee:
    def __init__(self, name, max_shifts, skills):
        self.name = name
        self.max_shifts = max_shifts
        self.skills = skills
        self.assigned_shifts = []
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def assigned_shift_count(self):
        return len(self.assigned_shifts)
    
    @property
    def is_at_capacity(self):
        return self.assigned_shift_count >= self.max_shifts

    def can_take_shift(self, shift):
        has_capacity = self.has_capacity()
        has_skill = self.has_required_skill(shift)
        has_no_shift_same_day = self.has_no_shift_same_day(shift)
        has_rest_time = self.has_required_rest_time(shift)

        return has_capacity and has_skill and has_no_shift_same_day and has_rest_time
    
    def has_capacity(self):
        return len(self.assigned_shifts) < self.max_shifts
    
    def has_required_skill(self, shift):
        return shift.required_skill in self.skills
    
    def has_no_shift_same_day(self, shift):
        return all(
            assigned_shift.date != shift.date
            for assigned_shift in self.assigned_shifts
        )

    def has_required_rest_time(self, shift):
        for assigned_shift in self.assigned_shifts:
            existing_date = datetime.datetime.strptime(assigned_shift.date, "%Y-%m-%d")
            new_date = datetime.datetime.strptime(shift.date, "%Y-%m-%d")

            is_next_day = new_date == existing_date + datetime.timedelta(days=1)
            is_evening_to_day = assigned_shift.shift_type == "Evening" and shift.shift_type == "Day"
            is_night_before = assigned_shift.shift_type == "Night"

            if is_next_day and (is_evening_to_day or is_night_before):
                return False

        return True
    
class Shift:
    def __init__(self, date, shift_type, required_skill, required_staff=1, priority=2):
        self.date = date
        self.shift_type = shift_type
        self.required_skill = required_skill
        self.required_staff = required_staff
        self.priority = priority
        self.assigned_employees = []
    
    def __str__(self) -> str:
        return f"{self.date} {self.shift_type} ({self.required_skill}) [P{self.priority}]"

    @property
    def is_fully_staffed(self):
        return len(self.assigned_employees) >= self.required_staff
    
    @property
    def missing_staff_count(self):
        return self.required_staff - len(self.assigned_employees)