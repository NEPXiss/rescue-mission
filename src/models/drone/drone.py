# drone/drone.py
from typing import List, Tuple, Optional

class Drone:
    def __init__(
        self,
        drone_id: int,
        start_pos: Tuple[int, int],
        speed: float = 1.0,
        drone_type: str = "search",
        knowledge: Optional[dict] = None
    ):
        """
        drone_id: unique identifier
        start_pos: (y, x) initial position
        speed: relative speed (1.0 = normal, >1 faster, <1 slower)
        drone_type: search/rescue/cargo etc.
        knowledge: dict to store information about map / pheromones / survivors
        """
        self.drone_id = drone_id
        self.pos = start_pos
        self.speed = speed
        self.type = drone_type
        self.knowledge = knowledge or {}  # store pheromone map / visited info / discovered survivors

        self.path: List[Tuple[int,int]] = []  # planned path
        self.target: Optional[Tuple[int,int]] = None  # current target (survivor)
        self.step_index: int = 0  # index for current position along path

    # ---------------------------
    # Assign new target + path
    # ---------------------------
    def assign_target(self, target: Tuple[int,int], path: List[Tuple[int,int]]):
        self.target = target
        self.path = path
        self.step_index = 0

    # ---------------------------
    # Move drone one step along path
    # ---------------------------
    def move_step(self):
        if self.path and self.step_index < len(self.path):
            self.pos = self.path[self.step_index]
            self.step_index += 1
            return self.pos
        return self.pos  # stay at last position if path done

    # ---------------------------
    # Check if drone reached target
    # ---------------------------
    def reached_target(self) -> bool:
        return self.target is not None and self.pos == self.target

    # ---------------------------
    # Update knowledge (pheromone / visited info)
    # ---------------------------
    def update_knowledge(self, key, value):
        self.knowledge[key] = value

    # ---------------------------
    # Share knowledge with another drone (simple merge)
    # ---------------------------
    def share_knowledge(self, other_drone: "Drone"):
        for k, v in self.knowledge.items():
            if k not in other_drone.knowledge:
                other_drone.knowledge[k] = v
