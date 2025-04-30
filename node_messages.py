from enum import Enum


class Messages(str, Enum):
    HELLO = "HELLO"
    BSHELLO = "BS-HELLO"
    DEVHELLO = "DEV-HELLO"
    SCHED = "SCHED"
    DATA = "DATA"
