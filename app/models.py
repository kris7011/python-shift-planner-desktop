class Employee:
    def __init__(self, name, max_shifts):
        self.name = name
        self.max_shifts = max_shifts
        self.assigned_shifts = []

    def can_take_shift(self):
        return len(self.assigned_shifts) < self.max_shifts


class Shift:
    def __init__(self, date, required_role):
        self.date = date
        self.required_role = required_role
        self.assigned_employee = None