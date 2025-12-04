import pygame
import numpy as np
from typing import List, Tuple

TILE = 30  # pizel size of each grid cell
FPS = 5

# Colors: RGB
COLORS = {
    0: (220, 220, 220),  # NORMAL
    1: (50, 50, 50),     # OBSTACLE
    2: (255, 165, 0),    # DANGER
    3: (255, 0, 0),      # SURVIVOR
    4: (0, 0, 255),      # DRONE
}

PATH_COLOR = (0, 255, 0)  # Green for paths


class MapVisualizer:
    def __init__(self, world, paths: List[List[Tuple[int,int]]]=None):
        """
        world: instance of Map
        paths: list of paths (list of coords) to show for each drone
        """
        self.world = world
        self.paths = paths or []

        self.height, self.width = world.height, world.width
        pygame.init()
        self.screen = pygame.display.set_mode((self.width*TILE, self.height*TILE))
        pygame.display.set_caption("Rescue Drone Mission Visualizer")
        self.clock = pygame.time.Clock()

    def draw_grid(self):
        for y in range(self.height):
            for x in range(self.width):
                cell_value = self.world.grid[y][x]
                color = COLORS.get(cell_value, (255, 255, 255))
                pygame.draw.rect(self.screen, color, (x*TILE, y*TILE, TILE, TILE))
                # grid line
                pygame.draw.rect(self.screen, (180, 180, 180), (x*TILE, y*TILE, TILE, TILE), 1)

    def draw_paths(self):
        for path in self.paths:
            if not path:
                continue
            for i in range(len(path)-1):
                y1, x1 = path[i]
                y2, x2 = path[i+1]
                start_pos = (x1*TILE + TILE//2, y1*TILE + TILE//2)
                end_pos = (x2*TILE + TILE//2, y2*TILE + TILE//2)
                pygame.draw.line(self.screen, PATH_COLOR, start_pos, end_pos, 4)

    def draw(self):
        self.screen.fill((255,255,255))
        self.draw_grid()
        self.draw_paths()
        pygame.display.flip()

    def animate_drones(self, drone_paths: List[List[Tuple[int,int]]]):
        """
        Animate drones along their path step by step
        """
        max_steps = max(len(p) for p in drone_paths)
        drone_positions = [p[0] for p in drone_paths]  # initial positions

        running = True
        step = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # draw map
            self.draw_grid()

            # draw paths
            self.draw_paths()

            # draw drones at current step
            for i, path in enumerate(drone_paths):
                if step < len(path):
                    y, x = path[step]
                else:
                    y, x = path[-1]  # stop at last cell
                pygame.draw.circle(self.screen, (0,0,255), (x*TILE+TILE//2, y*TILE+TILE//2), TILE//3)

            pygame.display.flip()
            self.clock.tick(FPS)
            step += 1
            if step > max_steps:
                step = max_steps  # stop at end
