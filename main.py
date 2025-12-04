# main.py
import numpy as np
import random
from src.models.map.map_generator import MapGenerator
from src.models.drone.drone import Drone
from src.models.map.map_visualizer import MapVisualizer
from src.models.ai.swarm_intelligence import SwarmIntelligence
import pygame

# -----------------------------
# 1. Generate random map
# -----------------------------
WIDTH, HEIGHT = 20, 20
OBSTACLE_PROB = 0.15
DANGER_PROB = 0.2
NUM_DRONES = 3
NUM_SURVIVORS = 4

valid_map = False
while not valid_map:
    map_gen = MapGenerator(width=WIDTH, height=HEIGHT, obstacle_prob=OBSTACLE_PROB, danger_prob=DANGER_PROB)
    world = map_gen.generate()
    
    # simple check: enough free cells for survivors
    free_cells = list(zip(*np.where(world.grid != 1)))  # not obstacle
    if len(free_cells) >= NUM_SURVIVORS + NUM_DRONES:
        valid_map = True

# -----------------------------
# 2. Initialize drones
# -----------------------------
drone_starts = random.sample(free_cells, NUM_DRONES)
drones = []
for i, start in enumerate(drone_starts):
    speed = random.uniform(0.5, 2.0)  # different speeds
    drone = Drone(drone_id=i, start_pos=start, speed=speed)
    drones.append(drone)

# -----------------------------
# 3. Initialize survivors
# -----------------------------
remaining_cells = [c for c in free_cells if c not in drone_starts]
survivors = random.sample(remaining_cells, NUM_SURVIVORS)
for y,x in survivors:
    world.grid[y][x] = 3  # mark survivor

# -----------------------------
# 4. Assign targets via SwarmIntelligence
# -----------------------------
swarm = SwarmIntelligence(world, drones, survivors)
swarm.assign_targets()

# -----------------------------
# 5. Visualizer
# -----------------------------
visualizer = MapVisualizer(world, drones)

running = True
while running:
    for event in pygame.event.get():  # <-- ใช้ pygame.event.get() ถูกต้อง
        if event.type == pygame.QUIT:
            running = False

    # step all drones
    swarm.step_drones()
    swarm.share_knowledge()

    # draw current frame
    visualizer.draw()
    visualizer.clock.tick(5)  # FPS

    # stop when all drones reached targets
    if all(d.reached_target() for d in drones):
        running = False

print("Mission complete!")
# pygame.quit()
