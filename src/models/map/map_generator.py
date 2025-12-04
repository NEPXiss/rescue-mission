import numpy as np
import random
from .map import Map, CellType

class MapGenerator:
    def __init__(self, width=20, height=20,
                 obstacle_prob=0.15, danger_prob=0.10,
                 seed=None):
        self.width = width
        self.height = height
        self.obstacle_prob = obstacle_prob
        self.danger_prob = danger_prob

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    # ------------------------------------------------------
    # Main generator
    # ------------------------------------------------------
    def generate(self, survivors=5, drones=3):
        grid = np.zeros((self.height, self.width), dtype=int)

        # 1. Place obstacle + danger
        for y in range(self.height):
            for x in range(self.width):
                r = random.random()
                if r < self.obstacle_prob:
                    grid[y][x] = CellType.OBSTACLE
                elif r < self.obstacle_prob + self.danger_prob:
                    grid[y][x] = CellType.DANGER

        # 2. Place survivors
        for _ in range(survivors):
            y, x = self._find_free_cell(grid)
            grid[y][x] = CellType.SURVIVOR

        # 3. Place drones
        for _ in range(drones):
            y, x = self._find_free_cell(grid)
            grid[y][x] = CellType.DRONE

        return Map(grid)

    # ------------------------------------------------------
    # Internal helper to locate free cells
    # ------------------------------------------------------
    def _find_free_cell(self, grid):
        while True:
            y = random.randint(0, self.height - 1)
            x = random.randint(0, self.width - 1)
            if grid[y][x] == CellType.NORMAL:
                return y, x
