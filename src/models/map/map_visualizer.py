import pygame
from typing import List
from src.models.drone.drone import Drone
import math

TILE = 30  # pixel size of each grid cell
FPS = 5

# Colors: RGB
COLORS = {
    0: (220, 220, 220),  # NORMAL
    1: (50, 50, 50),     # OBSTACLE
    2: (255, 165, 0),    # DANGER
    3: (255, 0, 0),      # SURVIVOR
}

PATH_COLORS = [
    (0, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (255, 255, 0),
    (0, 128, 255),
    (128, 0, 255)
]

class MapVisualizer:
    def __init__(self, world, drones: List[Drone]=None):
        self.world = world
        self.drones = drones or []

        self.height, self.width = world.height, world.width
        pygame.init()
        self.screen = pygame.display.set_mode((self.width*TILE, self.height*TILE))
        pygame.display.set_caption("Rescue Drone Mission Visualizer")
        self.clock = pygame.time.Clock()

        # initialize progress for each drone
        for drone in self.drones:
            drone.progress = 0.0  # float index along path

    def draw_grid(self):
        for y in range(self.height):
            for x in range(self.width):
                cell_value = self.world.grid[y][x]
                color = COLORS.get(cell_value, (255, 255, 255))
                pygame.draw.rect(self.screen, color, (x*TILE, y*TILE, TILE, TILE))
                pygame.draw.rect(self.screen, (180,180,180), (x*TILE, y*TILE, TILE, TILE), 1)

    def draw_paths(self):
        for idx, drone in enumerate(self.drones):
            color = PATH_COLORS[idx % len(PATH_COLORS)]
            if not drone.path:
                continue
            for i in range(len(drone.path)-1):
                y1, x1 = drone.path[i]
                y2, x2 = drone.path[i+1]
                start_pos = (x1*TILE + TILE//2, y1*TILE + TILE//2)
                end_pos = (x2*TILE + TILE//2, y2*TILE + TILE//2)
                pygame.draw.line(self.screen, color, start_pos, end_pos, 4)

    def draw_drones(self):
        for idx, drone in enumerate(self.drones):
            color = PATH_COLORS[idx % len(PATH_COLORS)]
            y, x = drone.pos
            pygame.draw.circle(self.screen, color, (x*TILE + TILE//2, y*TILE + TILE//2), TILE//3)

    def draw(self):
        self.screen.fill((255,255,255))
        self.draw_grid()
        self.draw_paths()
        self.draw_drones()
        pygame.display.flip()

    def animate_drones(self):
        """
        Animate all drones along their paths, using Drone.speed
        speed = cells per frame (or scaled)
        """
        max_len = max(len(drone.path) for drone in self.drones if drone.path)
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Update drones
            for drone in self.drones:
                if not drone.path:
                    continue
                # advance progress by speed
                drone.progress += drone.speed  # can scale if too fast
                idx = min(int(math.floor(drone.progress)), len(drone.path)-1)
                drone.pos = drone.path[idx]

            # draw frame
            self.draw()
            self.clock.tick(FPS)

            # stop if all drones reached end
            if all(drone.progress >= len(drone.path)-1 for drone in self.drones if drone.path):
                running = False
