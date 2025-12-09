# src/models/drone/drone.py
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
        
        self.path_progress = 0.0
        self.current_waypoint_idx = 0
        
        self.pheromone_map = pheromone_map
        self.knowledge = {}  # store info about discovered survivors, obstacles, etc.
        
        self.total_distance_traveled = 0.0

    # =========================================
    # Task Assignment
    # =========================================
    def assign_target(self, target: Tuple[int,int], path: List[Tuple[int,int]]):
        """Assign new target + path to drone"""
        self.target = target
        self.path = path
        self.current_waypoint_idx = 0
        self.path_progress = 0.0
        
        # ถ้า path เริ่มที่ตำแหน่งปัจจุบัน ให้ข้าม waypoint แรก
        if self.path and self.path[0] == self.pos:
            self.current_waypoint_idx = 1
            
    # =========================================
    # Movement
    # =========================================
    def move_step(self):
        # Returns: current position
        if not self.path or self.current_waypoint_idx >= len(self.path):
            return self.pos
            
        # Increase progress by speed
        self.path_progress += self.speed
        
        # Follow along waypoints
        while self.path_progress >= 1.0 and self.current_waypoint_idx < len(self.path):
            self.path_progress -= 1.0
            
            # Move to the next waypoint
            old_pos = self.pos
            self.pos = self.path[self.current_waypoint_idx]
            self.current_waypoint_idx += 1
            
            # Calculate distance
            if old_pos != self.pos:
                dy = self.pos[0] - old_pos[0]
                dx = self.pos[1] - old_pos[1]
                distance = (dy**2 + dx**2) ** 0.5
                self.total_distance_traveled += distance
            
            # Update pheromone
            if self.pheromone_map is not None:
                self.update_knowledge(self.pos, amount=1.0)
                
        return self.pos

    # =========================================
    # Status Check
    # =========================================
    def reached_target(self) -> bool:
        return self.target is not None and self.pos == self.target
        
    def has_active_target(self) -> bool:
        return self.target is not None and not self.reached_target()
        
    def get_progress(self) -> float:
        # Calculate progress along the path to target (0.0 - 1.0)
        if not self.path or len(self.path) == 0:
            return 1.0
            
        total_waypoints = len(self.path)
        completed = self.current_waypoint_idx
        progress_in_current = min(self.path_progress, 1.0)
        
        return (completed + progress_in_current) / total_waypoints
        
    def estimated_time_to_target(self) -> float:
        # Estimate time to reach target based on remaining path and speed. (How many steps left)
        if not self.path or self.current_waypoint_idx >= len(self.path):
            return 0.0
            
        remaining_waypoints = len(self.path) - self.current_waypoint_idx
        remaining_in_current = 1.0 - self.path_progress
        
        total_remaining = remaining_waypoints + remaining_in_current
        return total_remaining / self.speed if self.speed > 0 else float('inf')

    # =========================================
    # Knowledge Management
    # =========================================
    def update_knowledge(self, pos, amount=1.0):
        if self.pheromone_map is not None:
            y, x = pos
            self.pheromone_map[y][x] += amount
            
    def share_knowledge(self, other_drone: "Drone"):
        for k, v in self.knowledge.items():
            if k not in other_drone.knowledge:
                other_drone.knowledge[k] = v
                
    def add_discovery(self, discovery_type: str, position: Tuple[int, int], data=None):
        key = f"{discovery_type}:{position}"
        self.knowledge[key] = {
            'type': discovery_type,
            'position': position,
            'data': data,
            'discovered_at': self.total_distance_traveled
        }
        
    # =========================================
    # Status Report
    # =========================================
    def get_status(self) -> dict:
        return {
            'id': self.drone_id,
            'pos': self.pos,
            'target': self.target,
            'speed': self.speed,
            'has_target': self.has_active_target(),
            'progress': self.get_progress() if self.has_active_target() else 1.0,
            'eta': self.estimated_time_to_target(),
            'distance_traveled': self.total_distance_traveled
        }
        
    def __repr__(self):
        return (f"Drone(id={self.drone_id}, pos={self.pos}, "
                f"target={self.target}, speed={self.speed:.2f})")