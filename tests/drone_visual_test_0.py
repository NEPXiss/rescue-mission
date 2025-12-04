# test_maps_large.py
import random
from src.models.map.map_generator import MapGenerator
from src.models.ai.a_star import AStar
from src.models.drone.drone import Drone
from src.models.map.map_visualizer import MapVisualizer

def generate_large_random_map(width=25, height=25, obstacle_prob=0.15, danger_prob=0.25,
                              num_drones=5, num_survivors=6, seed=None):
    if seed is not None:
        random.seed(seed)

    gen = MapGenerator(width=width, height=height, obstacle_prob=obstacle_prob, danger_prob=danger_prob, seed=seed)
    world = gen.generate(survivors=num_survivors, drones=num_drones)

    drones_pos = world.list_drones()
    survivors_pos = world.list_survivors()

    # Create Drone objects with different speed
    drones = []
    for i, pos in enumerate(drones_pos):
        speed = round(random.uniform(5, 20.0), 2)
        drone = Drone(drone_id=i, start_pos=pos, speed=speed, drone_type="search")
        drones.append(drone)

    return world, drones, survivors_pos

# -------------------------------
# Test function
# -------------------------------
def test_large_random_map():
    print("=== Test: Large Random Map ===")
    world, drones, survivors = generate_large_random_map(width=25, height=25, num_drones=5, num_survivors=6, seed=123)
    print("Drones (pos, speed):", [(d.pos, d.speed) for d in drones])
    print("Survivors:", survivors)

    # A* pathfinding
    astar = AStar(world, allow_diagonal=True)
    for i, survivor in enumerate(survivors):
        # Assign to drones round-robin
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
# Run test
# -------------------------------
if __name__ == "__main__":
    test_large_random_map()
