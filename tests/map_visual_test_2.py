# test_maps.py
import numpy as np
import random
from src.models.ai.a_star import AStar
from src.models.map.map_visualizer import MapVisualizer
from src.models.map.map import Map, CellType
from src.models.drone.drone import Drone

# -------------------------------
# Helper function: generate random map with obstacles + danger
# -------------------------------
def generate_random_map(width=20, height=20, obstacle_prob=0.15, danger_prob=0.25, num_drones=3, num_survivors=5, seed=None):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    grid = np.zeros((height, width), dtype=int)

    # Obstacles / Danger
    for y in range(height):
        for x in range(width):
            if random.random() < obstacle_prob:
                grid[y, x] = CellType.OBSTACLE
            elif random.random() < danger_prob:
                grid[y, x] = CellType.DANGER

    # Survivors
    survivors = []
    while len(survivors) < num_survivors:
        y, x = random.randint(0, height-1), random.randint(0, width-1)
        if grid[y, x] == CellType.NORMAL:
            grid[y, x] = CellType.SURVIVOR
            survivors.append((y, x))

    # Drones
    drone_objs = []
    while len(drone_objs) < num_drones:
        y, x = random.randint(0, height-1), random.randint(0, width-1)
        if grid[y, x] == CellType.NORMAL:
            grid[y, x] = CellType.DRONE
            drone_id = len(drone_objs)
            speed = random.uniform(0.5, 2.0)  # random speed for demo
            drone_objs.append(Drone(drone_id=drone_id, start_pos=(y, x), speed=speed))

    world = Map(grid)
    world.cost_normal = 1
    world.cost_danger = 3  # higher cost
    return world, drone_objs, survivors


# -------------------------------
# Test case 1: random map with many danger zones
# -------------------------------
def test_random_danger_map():
    print("\n=== Test 1: Random map with many Danger zones ===")
    world, drones, survivors = generate_random_map(width=20, height=20, obstacle_prob=0.1, danger_prob=0.3, num_drones=3, num_survivors=5, seed=42)

    print("Drones:", [(d.pos, d.speed) for d in drones])
    print("Survivors:", survivors)
    print("Map grid:")
    print(world.grid)

    # A* pathfinding round-robin assignment
    astar = AStar(world, allow_diagonal=True)
    for i, survivor in enumerate(survivors):
        drone = drones[i % len(drones)]
        result = astar.find_path(drone.pos, survivor)
        if result:
            path, cost = result
            drone.assign_target(survivor, path)
            print(f"Drone {drone.drone_id} -> Survivor {survivor}: len={len(path)}, cost={cost:.2f}")
        else:
            print(f"No path from Drone {drone.drone_id} -> Survivor {survivor}")

    # Visualize
    vis = MapVisualizer(world, drones=drones)
    vis.animate_drones()


# -------------------------------
# Test case 2: more drones than survivors
# -------------------------------
def test_more_drones_than_survivors():
    print("\n=== Test 2: More drones than survivors ===")
    world, drones, survivors = generate_random_map(width=15, height=15, obstacle_prob=0.1, danger_prob=0.2, num_drones=5, num_survivors=3, seed=24)

    print("Drones:", [(d.pos, d.speed) for d in drones])
    print("Survivors:", survivors)
    print("Map grid:")
    print(world.grid)

    # Assign survivor to nearest drone (round-robin demo)
    astar = AStar(world, allow_diagonal=True)
    for i, survivor in enumerate(survivors):
        drone = drones[i % len(drones)]
        result = astar.find_path(drone.pos, survivor)
        if result:
            path, cost = result
            drone.assign_target(survivor, path)
            print(f"Drone {drone.drone_id} -> Survivor {survivor}: len={len(path)}, cost={cost:.2f}")
        else:
            print(f"No path from Drone {drone.drone_id} -> Survivor {survivor}")

    # Visualize
    vis = MapVisualizer(world, drones=drones)
    vis.animate_drones()


# -------------------------------
# Main: run tests
# -------------------------------
if __name__ == "__main__":
    test_random_danger_map()
    test_more_drones_than_survivors()
