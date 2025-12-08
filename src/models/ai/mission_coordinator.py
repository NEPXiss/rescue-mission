# src/models/ai/mission_coordinator.py
import math
from typing import List, Tuple, Dict, Set, Optional
from src.models.drone.drone import Drone
from src.models.map.map import Map
from src.models.ai.a_star import AStar

Coord = Tuple[int, int]

class MissionCoordinator:
    # Dynamic Task Assignment for Drone Rescue Mission
    # Use A* for pathfinding and greedy assignment strategy
    # Re-plan when new survivors are discovered
    
    def __init__(
        self,
        world: Map,
        spawn_point: Coord,
        detection_radius: int = 2,
        drone_spawn_delay: int = 5,
        allow_diagonal: bool = True
    ):
        self.world = world
        self.spawn_point = spawn_point
        self.detection_radius = detection_radius
        self.drone_spawn_delay = drone_spawn_delay
        
        # A* pathfinder
        self.astar = AStar(world, allow_diagonal=allow_diagonal)
        
        # Tracking
        self.drones: List[Drone] = []
        self.known_survivors: Set[Coord] = set()
        self.rescued_survivors: Set[Coord] = set()
        self.discovered_survivors: Set[Coord] = set()
        
        # Assignments: drone_id -> target_survivor
        self.assignments: Dict[int, Coord] = {}
        
        # Time management
        self.current_time = 0
        self.next_spawn_time = 0
        self.drone_id_counter = 0
        
    # =========================================
    # Initialize Mission
    # =========================================
    def initialize_mission(self, initial_survivors: List[Coord]):
        self.known_survivors = set(initial_survivors)
        print(f"Mission initialized with {len(initial_survivors)} known survivors")
        
    # =========================================
    # Spawn Drone
    # =========================================
    def spawn_drone(self, speed: float = 1.0):
        # Spwan Drone at spawn_point
        drone = Drone(
            drone_id=self.drone_id_counter,
            start_pos=self.spawn_point,
            speed=speed,
            pheromone_map=self.world.pheromone
        )
        self.drones.append(drone)
        self.drone_id_counter += 1
        return drone
        
    # =========================================
    # Task Assignment
    # =========================================
    def assign_tasks(self):
        # Allocate available drones to unassigned survivors by greedy method
        # Calculate cost of each drone-survivor pair
        # Assign drones to survivors with lowest cost first

        # Find all survivors that need rescue (not assigned and not rescued)
        available_survivors = (
            self.known_survivors | self.discovered_survivors
        ) - self.rescued_survivors
        
        # Find all suitable drones that is available (No target or target already rescued)
        available_drones = [
            d for d in self.drones 
            if d.target is None or d.target in self.rescued_survivors
        ]
        
        if not available_survivors or not available_drones:
            return
            
        # Calculate cost matrix
        assignments = []
        for drone in available_drones:
            best_survivor = None
            best_cost = float('inf')
            best_path = None
            
            for survivor in available_survivors:
                # Skip if survivor if assigned
                if survivor in self.assignments.values():
                    continue
                    
                # Find path and cost with A*
                result = self.astar.find_path(drone.pos, survivor)
                if result is None:
                    continue
                    
                path, path_cost = result
                # Cost = path_cost / speed (estimated time)
                time_cost = path_cost / drone.speed
                
                if time_cost < best_cost:
                    best_cost = time_cost
                    best_survivor = survivor
                    best_path = path
                    
            # Assign best survivor to drone
            if best_survivor is not None:
                drone.assign_target(best_survivor, best_path)
                self.assignments[drone.drone_id] = best_survivor
                assignments.append((drone.drone_id, best_survivor, best_cost))
                
        return assignments
        
    # =========================================
    # Re-planning
    # =========================================
    def replan_if_needed(self):
        # Replan if there are unassigned survivors (newly discovered) or idle drones
        # Check if there's unassigned survivor.
        unassigned = (
            self.known_survivors | self.discovered_survivors
        ) - self.rescued_survivors - set(self.assignments.values())
        
        if unassigned:
            # If there's unassigned survivor
            # Consider re-assign drones with high cost targets.
            self.reassign_drones()
            
    def reassign_drones(self):
        # Find unassigned survivors
        unassigned = (
            self.known_survivors | self.discovered_survivors
        ) - self.rescued_survivors - set(self.assignments.values())
        
        if not unassigned:
            return
            
        # Consider re-assign each drone
        for drone in self.drones:
            if drone.target is None or drone.reached_target():
                continue
                
            current_target = drone.target
            current_result = self.astar.find_path(drone.pos, current_target)
            if current_result is None:
                continue
            current_cost = current_result[1] / drone.speed
            
            # Find better cost survivor
            for new_survivor in unassigned:
                new_result = self.astar.find_path(drone.pos, new_survivor)
                if new_result is None:
                    continue
                new_cost = new_result[1] / drone.speed
                
                # Re-assign if new cost under threshold (threshold 50%)
                if new_cost < current_cost * 0.5:
                    print(f"Re-assigning Drone {drone.drone_id}: {current_target} -> {new_survivor}")
                    # Cancel previous assignment
                    del self.assignments[drone.drone_id]
                    # Assign new target
                    drone.assign_target(new_survivor, new_result[0])
                    self.assignments[drone.drone_id] = new_survivor
                    unassigned.remove(new_survivor)
                    break
                    
    # =========================================
    # Detection
    # =========================================
    def check_detection(self, drone: Drone):
        dy, dx = drone.pos
        discovered = []
        
        for y in range(max(0, dy - self.detection_radius), 
                       min(self.world.height, dy + self.detection_radius + 1)):
            for x in range(max(0, dx - self.detection_radius),
                          min(self.world.width, dx + self.detection_radius + 1)):
                dist = math.sqrt((y - dy)**2 + (x - dx)**2)
                if dist > self.detection_radius:
                    continue
                    
                pos = (y, x)
                # Found new survivor
                if (pos not in self.known_survivors and 
                    pos not in self.discovered_survivors and
                    pos not in self.rescued_survivors):
                    from src.constants import CellType
                    if self.world.grid[y][x] == CellType.SURVIVOR:
                        discovered.append(pos)
                        self.discovered_survivors.add(pos)
                        
        return discovered
        
    def check_rescue(self, drone: Drone):
        if drone.target and drone.pos == drone.target:
            self.rescued_survivors.add(drone.target)
            if drone.drone_id in self.assignments:
                del self.assignments[drone.drone_id]
            drone.target = None
            drone.path = []
            return True
        return False
        
    # =========================================
    # Simulation Step
    # =========================================
    def step(self, spawn_new_drone: bool = True, new_drone_speed: float = 1.0):
        step_log = {
            'time': self.current_time,
            'spawned': False,
            'moved': [],
            'discovered': [],
            'rescued': [],
            'assigned': []
        }
        
        # Spawn new drone
        if spawn_new_drone and self.current_time >= self.next_spawn_time:
            drone = self.spawn_drone(speed=new_drone_speed)
            self.next_spawn_time = self.current_time + self.drone_spawn_delay
            step_log['spawned'] = drone.drone_id
            
        # Move all drones
        for drone in self.drones:
            old_pos = drone.pos
            new_pos = drone.move_step()
            if old_pos != new_pos:
                step_log['moved'].append((drone.drone_id, old_pos, new_pos))
                
            # Detection check
            discovered = self.check_detection(drone)
            if discovered:
                step_log['discovered'].extend(discovered)
                
            # Rescue check
            if self.check_rescue(drone):
                step_log['rescued'].append((drone.drone_id, drone.pos))
                
        # Re-plan if new survivors discovered
        if step_log['discovered']:
            self.replan_if_needed()
            
        # Assign tasks to available drones
        assignments = self.assign_tasks()
        if assignments:
            step_log['assigned'] = assignments
            
        self.current_time += 1
        return step_log
        
    # =========================================
    # Status
    # =========================================
    def get_status(self):
        total_known = len(self.known_survivors | self.discovered_survivors)
        return {
            'time': self.current_time,
            'drones_deployed': len(self.drones),
            'known_survivors': len(self.known_survivors),
            'discovered_survivors': len(self.discovered_survivors),
            'rescued_survivors': len(self.rescued_survivors),
            'total_survivors': total_known,
            'remaining_survivors': total_known - len(self.rescued_survivors),
            'active_assignments': len(self.assignments)
        }
        
    def is_mission_complete(self):
        total_known = self.known_survivors | self.discovered_survivors
        return len(self.rescued_survivors) >= len(total_known)