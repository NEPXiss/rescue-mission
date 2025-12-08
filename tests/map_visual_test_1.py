# main.py
import numpy as np
from src.models.ai.a_star import AStar
from src.models.map.map_visualizer import MapVisualizer
from src.models.map.map import Map
from src.constants import CellType

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
drones = [(0, 2), (0, 7)]
for y, x in drones:
    grid[y, x] = CellType.DRONE

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
paths = []

# Simple round-robin assignment: each survivor gets a drone
for i, survivor in enumerate(survivors):
    drone = drones[i % len(drones)]
    result = astar.find_path(drone, survivor)
    if result:
        path, cost = result
        print(f"Drone {drone} -> Survivor {survivor}: length={len(path)}, cost={cost}")
        paths.append(path)
    else:
        print(f"No path from Drone {drone} -> Survivor {survivor}")
        paths.append([])

# -------------------------------
# Visualize + Animate
# -------------------------------
vis = MapVisualizer(world, paths=paths)
vis.animate_drones(paths)
