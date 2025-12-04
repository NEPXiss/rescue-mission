# swarm_intelligence.py
from typing import List, Tuple
from src.models.ai.a_star import AStar
from src.models.drone.drone import Drone

class SwarmIntelligence:
    def __init__(self, world, drones: List[Drone], survivors: List[Tuple[int,int]], alpha: float = 1.0, beta: float = 2.0):
        """
        world: Map object
        drones: list of Drone objects
        survivors: list of (y,x) survivor positions
        alpha, beta: parameters for pheromone / heuristic weighting (future extension)
        """
        self.world = world
        self.drones = drones
        self.survivors = survivors
        self.alpha = alpha
        self.beta = beta
        self.astar = AStar(world)

    def assign_targets(self):
        """
        Assign best reachable target to each drone
        Safe against A* returning None
        """
        for drone in self.drones:
            best_path = None
            best_cost = float('inf')
            best_target = None

            for target in self.survivors:
                y, x = target
                if self.world.grid[y][x] == 1:
                    continue  # skip obstacles
                result = self.astar.find_path(drone.pos, target)
                if result is None:
                    continue  # path not found, skip
                path, cost = result
                if cost < best_cost:
                    best_cost = cost
                    best_path = path
                    best_target = target

            if best_path:
                drone.assign_target(best_target, best_path)
                print(f"Drone {drone.drone_id} assigned target {best_target}, path len={len(best_path)}, cost={best_cost:.2f}")
            else:
                print(f"Drone {drone.drone_id} has no reachable target")

    def step_drones(self):
        """
        Move all drones one step along their path, update pheromone
        """
        for drone in self.drones:
            if drone.path and not drone.reached_target():
                drone.move_step()
                # Update pheromone / visited map
                drone.update_knowledge(drone.pos)

    # -----------------------------
    # Future extension hooks
    # -----------------------------
    def share_knowledge(self):
        """
        Share knowledge (pheromone / visited map) between all drones
        """
        for i, drone in enumerate(self.drones):
            for j, other in enumerate(self.drones):
                if i != j:
                    drone.share_knowledge(other)

    def reassign_dynamic(self):
        """
        Re-evaluate target assignment dynamically (e.g., survivors move)
        """
        # For future implementation
        self.assign_targets()
