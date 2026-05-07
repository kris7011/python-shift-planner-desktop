from enum import Enum

class ShiftType(Enum):
    DAY = "Day"
    EVENING = "Evening"
    NIGHT = "Night"

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
