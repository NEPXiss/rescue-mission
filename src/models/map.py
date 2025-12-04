from math import inf
import random

from ..constants import Terrain, DroneState
from .human import Survivor
from .drone import Drone

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Terrain.NORMAL for _ in range(width)] for _ in range(height)]
        self.survivors: list[Survivor] = []
        self.drones: list[Drone] = []
        self.terrain_costs = {
            Terrain.NORMAL: 1,
            Terrain.OBSTACLE: inf,
            Terrain.DANGER: 4
        }

    ### Initialization/Grid Setup ###
    def randomize(self, obstacle_prob=0.15, danger_prob=0.1, seed=None):

        # TODO: If possible, make sure that this function always initialize a "rescuable" mission.

        if seed is not None:
            random.seed(seed)
        for y in range(self.height):
            for x in range(self.width):
                r = random.random()
                if r < obstacle_prob:
                    self.grid[y][x] = Terrain.OBSTACLE
                elif r < obstacle_prob + danger_prob:
                    self.grid[y][x] = Terrain.DANGER
                else:
                    self.grid[y][x] = Terrain.NORMAL
    
    def add_obstacles(self, positions):
        for x, y in positions:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = Terrain.OBSTACLE

    def add_danger_zones(self, positions):
        for x, y in positions:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.grid[y][x] = Terrain.DANGER

    def decay_danger(self, decay_rate=0.1):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == Terrain.DANGER and random.random() < decay_rate:
                    self.grid[y][x] = Terrain.NORMAL

    ### Terrian & Walkability ###
    def is_walkable(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.grid[y][x] != Terrain.OBSTACLE

    def get_terrain_cost(self, x, y):
        if not self.is_walkable(x, y):
            return inf
        return self.terrain_costs[self.grid[y][x]]

    def get_neighbors(self, x, y):
        moves = [(0,1), (0,-1), (1,0), (-1,0)]
        neighbors = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                cost = self.get_terrain_cost(nx, ny)
                neighbors.append(((nx, ny), cost))
        return neighbors

    ### Survivors/Drones Related Utilities ###

    def add_survivors(self, positions):
        self.survivors.extend([
            Survivor(
                id = i, 
                x = x, 
                y = y
            )
            for i, (x, y) in enumerate(positions)
        ])

    def add_drones(self, positions):
        self.drones.extend([
            Drone(
                id = i, 
                start_x = x,
                start_y = y,
                state = DroneState.IDLE
            )
            for i, (x, y) in enumerate(positions)
        ])
    
    def get_survivor_positions(self):
        return [(s.x, s.y) for s in self.survivors if not s.rescued]

    def get_drone_positions(self):
        return [(d.current_x, d.current_y) for d in self.drones]

    ### Visualization ###
    def display(self):
        symbols = {
            Terrain.NORMAL: ".",
            Terrain.OBSTACLE: "█",
            Terrain.DANGER: "~"
        }
        grid_copy = [[symbols[self.grid[y][x]] for x in range(self.width)] for y in range(self.height)]
        for s in self.survivors:
            grid_copy[s.y][s.x] = "S"
        for d in self.drones:
            grid_copy[d.current_y][d.current_x] = "D"
        print("\n".join("".join(row) for row in grid_copy))

    def __repr__(self):
        return f"<Map {self.width}x{self.height} | {len(self.survivors)} survivors, {len(self.drones)} drones>"


# For test
if __name__ == "__main__":
    world = Map(20,20)
    world.randomize(obstacle_prob=0.1, danger_prob=0.2, seed=42)
    world.add_survivors([(2, 3), (7, 8), (5, 1)])
    world.add_drones([(0, 0), (9, 9)])

    print(world)
    world.display()

    x, y = 2, 3
    print(f"\nNeighbors of ({x}, {y}):")
    for (nx, ny), cost in world.get_neighbors(x, y):
        print(f"  -> ({nx}, {ny}) cost={cost}")
    
    # decay test
    print("\nAfter danger decay:")
    world.decay_danger(decay_rate=0.5)
    world.display()