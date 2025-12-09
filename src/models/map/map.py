# map.py
import numpy as np
from src.constants import CellType

class Map:
    def __init__(self, grid: np.ndarray):
        self.grid = grid
        self.height, self.width = grid.shape

        # Cost settings
        self.cost_normal = 1
        self.cost_danger = 5

        self.pheromone = np.zeros((self.height, self.width), dtype=float)

    # --------------------------
    # Basic checks
    # --------------------------
    def in_bounds(self, y, x):
        return 0 <= y < self.height and 0 <= x < self.width

    def is_walkable(self, y, x):
        if not self.in_bounds(y, x):
            return False

        cell = self.grid[y][x]
        return cell != CellType.OBSTACLE  # obstacle = impossible

    def get_cost(self, y, x):
        """Return movement cost for A*"""
        cell = self.grid[y][x]

        if cell == CellType.NORMAL:
            return self.cost_normal
        elif cell == CellType.DANGER:
            return self.cost_danger
        elif cell in (CellType.SURVIVOR, CellType.DRONE):
            return self.cost_normal
        else:
            return 999999  # not walkable (shouldn't be used)
    
    def deposit_pheromone(self, pos, amount=1.0):
        y, x = pos
        self.pheromone[y][x] += amount

    def decay_pheromone(self, decay_rate=0.05):
        self.pheromone *= (1.0 - decay_rate)

    # --------------------------
    # Query helpers
    # --------------------------
    def list_survivors(self):
        return [(y, x)
                for y in range(self.height)
                for x in range(self.width)
                if self.grid[y][x] == CellType.SURVIVOR]

    def list_drones(self):
        return [(y, x)
                for y in range(self.height)
                for x in range(self.width)
                if self.grid[y][x] == CellType.DRONE]

    def print_map(self):
        print(self.grid)
