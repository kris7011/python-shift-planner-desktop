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
    def total_workload_score(self) -> int:
        return sum(shift.workload_score for shift in self.assigned_shifts)
    
    @property
    def average_workload_score(self) -> float:
        if self.assigned_shift_count == 0:
            return 0.0
        return self.total_workload_score / self.assigned_shift_count

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
    
    def get_risk_flags(self, workload_ratio_threshold: float, average_score_threshold: float) -> list[str]:
        flags = []
        
        if self.is_at_capacity:
            flags.append("AT CAPACITY")
            
        if self.workload_ratio >= workload_ratio_threshold:
            percentage = int(self.workload_ratio * 100)
            flags.append(f"HIGH RATIO ({percentage}%)")
            
        if self.average_workload_score >= average_score_threshold:
            flags.append(f"HEAVY SHIFTS ({self.average_workload_score:.1f})")
            
        return flags
    
    def get_risk_level(
        self,
        workload_ratio_threshold: float,
        average_score_threshold: float,
        high_risk_flag_count: int,
    ) -> str:
        num_flags = len(self.get_risk_flags(workload_ratio_threshold, average_score_threshold))

        if num_flags >= high_risk_flag_count:
            return "HIGH"
        elif num_flags == 1:
            return "MEDIUM"
        else:
            return "LOW"
    
class Shift:
    def __init__(self, date, shift_type, required_skill, required_staff=1, priority=2, workload_score=1):
        self.date = date
        self.shift_type = shift_type
        self.required_skill = required_skill
        self.required_staff = required_staff
        self.priority = priority
        self.workload_score = workload_score
        self.assigned_employees = []

    def __str__(self) -> str:
        return f"{self.date} {self.shift_type} ({self.required_skill}) [P{self.priority}] [Score {self.workload_score}]"

    @property
    def is_fully_staffed(self):
        return len(self.assigned_employees) >= self.required_staff
    
    @property
    def missing_staff_count(self):
        return self.required_staff - len(self.assigned_employees)