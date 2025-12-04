from ...constants.dronestate import DroneState

class Drone:
    def __init__(self, id, start_x, start_y, state: DroneState = DroneState.IDLE):
        self.id = id
        self.start_x = start_x
        self.start_y = start_y
        self.current_x = start_x
        self.current_y = start_y
        self.state = state
        self.trace = [(start_x, start_y)]
    