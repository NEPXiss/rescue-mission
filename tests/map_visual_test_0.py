# tests/map_visual_test_1.py
from src.models.map.map_generator import MapGenerator
from src.models.ai.a_star import AStar
from src.models.map.map_visualizer import MapVisualizer
from src.models.drone.drone import Drone

# -----------------------------
# Generate map
# -----------------------------
gen = MapGenerator(width=20, height=20, obstacle_prob=0.15, danger_prob=0.10, seed=42)
world = gen.generate(survivors=3, drones=2)

# -----------------------------
# Initialize drones
# -----------------------------
drones = world.list_drones()  # assume returns list of (y,x)
drone_objs = []
for i, pos in enumerate(drones):
    drone_objs.append(Drone(drone_id=i, start_pos=pos, speed=1.0))

# -----------------------------
# Get survivors
# -----------------------------
survivors = world.list_survivors()

# -----------------------------
# Find paths with A*
# -----------------------------
astar = AStar(world, allow_diagonal=True)

for drone in drone_objs:
    # assign first available survivor for demo
    if survivors:
        target = survivors.pop(0)
        result = astar.find_path(drone.pos, target)
        if result:
            path, cost = result
            drone.assign_target(target, path)
            print(f"Drone {drone.drone_id} assigned target {target}, path len={len(path)}, cost={cost}")
        else:
            print(f"Drone {drone.drone_id} cannot reach target {target}")

# -----------------------------
# Visualize
# -----------------------------
vis = MapVisualizer(world, drones=drone_objs)
vis.animate_drones()
