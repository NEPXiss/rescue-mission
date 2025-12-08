from enum import Enum

class DroneState:
    IDLE = 0
    TRAVELING = 1
    AT_TARGET = 2
    RETURNING = 3
    SEARCHING = 4