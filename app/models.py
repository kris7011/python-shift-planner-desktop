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
    
    @property
    def workload_ratio(self):
        if self.max_shifts == 0:
            return 0

        return self.assigned_shift_count / self.max_shifts
    
    @property
    def total_workload_score(self):
        scores = {"Night": 3, "Evening": 2, "Day": 1}
        # Sum points for all assigned shifts (default 1 if type does not exist)
        return sum(scores.get(shift.shift_type, 1) for shift in self.assigned_shifts)

    def can_take_shift(self, shift):
        return (
            not self.is_at_capacity
            and self.has_required_skill(shift)
            and self.has_no_shift_same_day(shift)
            and self.has_required_rest_time(shift)
        )
    
    def has_capacity(self):
        return not self.is_at_capacity
    
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