from src.models.drone.drone import Drone
from src.models.map.map_generator import MapGenerator
from src.models.ai.a_star import AStar

# Generate small map
gen = MapGenerator(width=10, height=10, obstacle_prob=0.1, danger_prob=0.2, seed=42)
world = gen.generate(survivors=2, drones=2)

drones_pos = world.list_drones()
survivors_pos = world.list_survivors()

# Drone objects
drones = []
for i, pos in enumerate(drones_pos):
    # speed => 0.5–2.0
    drone = Drone(drone_id=i, start_pos=pos, speed=1.0 + i*0.5, drone_type="search")
    drones.append(drone)

# A* pathfinding
astar = AStar(world)
for drone, target in zip(drones, survivors_pos):
    path, cost = astar.find_path(drone.pos, target)
    drone.assign_target(target, path)
    print(f"Drone {drone.drone_id} path to {target}: {path}")
