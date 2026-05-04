class Employee:
    def __init__(self, name, max_shifts, skills):
        self.name = name
        self.max_shifts = max_shifts
        self.skills = skills
        self.assigned_shifts = []

    def can_take_shift(self, shift):
        has_capacity = len(self.assigned_shifts) < self.max_shifts
        has_skill = shift.required_skill in self.skills

        return has_capacity and has_skill


class Shift:
    def __init__(self, date, shift_type, required_skill):
        self.date = date
        self.shift_type = shift_type
        self.required_skill = required_skill
        self.assigned_employee = None