# main.py
import numpy as np
from src.models.ai.a_star import AStar
from src.models.map.map_visualizer import MapVisualizer
from src.models.map.map import Map, CellType
from src.models.drone.drone import Drone

# -------------------------------
# Map test case
# -------------------------------
grid = np.zeros((10, 10), dtype=int)

# Obstacles (impassable)
grid[3, 1:9] = CellType.OBSTACLE

# Danger zone (walkable, higher cost)
grid[4, 1:9] = CellType.DANGER

# Survivors
survivors = [(8, 2), (8, 5), (8, 8)]
for y, x in survivors:
    grid[y, x] = CellType.SURVIVOR

# Drones
drone_positions = [(0, 2), (0, 7)]
drone_objs = []
for i, pos in enumerate(drone_positions):
    drone_objs.append(Drone(drone_id=i, start_pos=pos, speed=1.0))

# Create Map instance
world = Map(grid)
world.cost_normal = 1
world.cost_danger = 2  # Danger cost

print("Map grid (0=N,1=O,2=D,3=S,4=DR):")
print(world.grid)

# -------------------------------
# A* pathfinding for all drones → all survivors
# -------------------------------
astar = AStar(world, allow_diagonal=True)

# Simple round-robin assignment: each survivor gets a drone
for i, survivor in enumerate(survivors):
    drone = drone_objs[i % len(drone_objs)]
    result = astar.find_path(drone.pos, survivor)
    if result:
        path, cost = result
        drone.assign_target(survivor, path)
        print(f"Drone {drone.drone_id} -> Survivor {survivor}: length={len(path)}, cost={cost}")
    else:
        print(f"No path from Drone {drone.drone_id} -> Survivor {survivor}")

# -------------------------------
# Visualize + Animate
# -------------------------------
vis = MapVisualizer(world, drones=drone_objs)
vis.animate_drones()
