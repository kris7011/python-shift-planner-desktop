from enum import Enum


class ShiftType(Enum):
    DAY = "Day"
    EVENING = "Evening"
    NIGHT = "Night"

    @property
    def display_name(self) -> str:
        names = {
            ShiftType.DAY: "Dag",
            ShiftType.EVENING: "Aften",
            ShiftType.NIGHT: "Nat",
        }

        return names[self]


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

    @property
    def display_name(self) -> str:
        names = {
            RiskLevel.LOW: "Lav",
            RiskLevel.MEDIUM: "Middel",
            RiskLevel.HIGH: "Høj",
        }

        return names[self]