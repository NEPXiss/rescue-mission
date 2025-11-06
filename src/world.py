from math import inf

class Terrain:
    NORMAL = 0
    OBSTACLE = 1
    DANGER = 2


class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Terrain.NORMAL for _ in range(width)] for _ in range(height)]
        self.survivors = []
        self.drones = []
        self.terrain_costs = {
            Terrain.NORMAL: 1,
            Terrain.OBSTACLE: inf,
            Terrain.DANGER: 4
        }

    def is_walkable(self, x, y):
        if x < 0 or x >= self.width or \
           y < 0 or y >= self.height:
            return False
        # TODO
        return self.grid[y][x] != Terrain.OBSTACLE

    def get_terrain_cost(self, x, y):
        if not self.is_walkable(x, y):
            return inf
        # TODO
        return self.terrain_costs[self.grid[y][x]]

    def add_obstacles(self, positions):
        for x, y in positions:
            # TODO
            if 0 <= x < self.width and 0 <= y < self.height:
                # TODO
                self.grid[y][x] = Terrain.OBSTACLE

    def add_danger_zones(self, positions):
        for x, y in positions:
            # TODO
            if 0 <= x < self.width and 0 <= y < self.height:
                # TODO
                self.grid[y][x] = Terrain.DANGER

    def add_survivors(self, positions):
        self.survivors = [
            {"id": i, "x": x, "y": y, "rescued": False}
            for i, (x, y) in enumerate(positions)
        ]

    def add_drones(self, positions):
        self.drones = [
            {
                "id": i,
                "startX": x,
                "startY": y,
                "x": x,
                "y": y,
                "target": None,
                "path": [],
                "state": "IDLE",
                "totalDistance": 0
            }
            for i, (x, y) in enumerate(positions)
        ]
