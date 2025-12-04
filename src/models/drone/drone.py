# drone/drone.py
from typing import List, Tuple, Optional

class Drone:
    def __init__(
        self,
        drone_id: int,
        start_pos: Tuple[int, int],
        speed: float = 1.0,
        drone_type: str = "search",
        pheromone_map=None
    ):
        self.drone_id = drone_id
        self.pos = start_pos
        self.speed = speed
        self.type = drone_type

        self.path: List[Tuple[int,int]] = []
        self.target: Optional[Tuple[int,int]] = None
        self.step_index: int = 0
        self.progress = 0.0

        self.pheromone_map = pheromone_map
        self.knowledge = {}  # store info about discovered survivors, obstacles, etc.

    # Assign new target + path
    def assign_target(self, target: Tuple[int,int], path: List[Tuple[int,int]]):
        self.target = target
        self.path = path
        self.step_index = 0
        self.progress = 0.0

    # Move drone one step along path (supports speed >1 or <1)
    def move_step(self):
        if self.path and self.step_index < len(self.path):
            self.progress += self.speed
            self.step_index = min(int(self.progress), len(self.path)-1)
            self.pos = self.path[self.step_index]
            # update pheromone at current position
            self.update_knowledge(self.pos, amount=1.0)
            return self.pos
        return self.pos

    # Check if drone reached target
    def reached_target(self) -> bool:
        return self.target is not None and self.pos == self.target

    # Update knowledge (pheromone / visited info)
    def update_knowledge(self, pos, amount=1.0):
        if self.pheromone_map is not None:
            y, x = pos
            self.pheromone_map[y][x] += amount

    # Share knowledge with another drone (simple merge)
    def share_knowledge(self, other_drone: "Drone"):
        for k, v in self.knowledge.items():
            if k not in other_drone.knowledge:
                other_drone.knowledge[k] = v
