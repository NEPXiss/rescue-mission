from src.models.map.map_generator import MapGenerator
from src.models.ai.a_star import AStar
from src.models.map.map_visualizer import MapVisualizer

# generate map
gen = MapGenerator(width=20, height=20, obstacle_prob=0.15, danger_prob=0.10, seed=42)
world = gen.generate(survivors=3, drones=2)

# find path for each drone to first survivor (demo)
drones = world.list_drones()
survivors = world.list_survivors()

astar = AStar(world, allow_diagonal=True)
paths = []
for drone, survivor in zip(drones, survivors):
    result = astar.find_path(drone, survivor)
    if result:
        path, cost = result
        print(f"Drone {drone} -> Survivor {survivor} path length={len(path)}, cost={cost}")
        paths.append(path)
    else:
        paths.append([])

# visualize
vis = MapVisualizer(world, paths=paths)
vis.animate_drones(paths)
