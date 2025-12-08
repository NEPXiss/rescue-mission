# ai/a_star.py
import heapq
import math
from typing import List, Tuple, Optional, Dict
from src.models.map.map import Map
from src.constants import CellType

Coord = Tuple[int, int]

class AStar:
    def __init__(self, world: Map, allow_diagonal: bool = False):
        self.world = world
        self.allow_diagonal = allow_diagonal

        # neighbor deltas
        self._orthogonal = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self._diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    def heuristic(self, a: Coord, b: Coord) -> float:
        # Heuristic: Manhattan for 4-way, Euclidean for 8-way
        (y1, x1), (y2, x2) = a, b
        dy = abs(y1 - y2)
        dx = abs(x1 - x2)
        if self.allow_diagonal:
            return math.hypot(dy, dx)
        else:
            return dy + dx

    def neighbors(self, node: Coord) -> List[Tuple[Coord, float]]:
        # Return list of (neighbor_coord, move_cost_multiplier)
        # move_cost_multiplier is 1 for orthogonal, sqrt(2) for diagonal
        y, x = node
        res = []

        # orthogonal neighbors
        for dy, dx in self._orthogonal:
            ny, nx = y + dy, x + dx
            if not self.world.in_bounds(ny, nx):
                continue
            if not self.world.is_walkable(ny, nx):
                continue
            res.append(((ny, nx), 1.0))

        # diagonal neighbors (optional)
        if self.allow_diagonal:
            for dy, dx in self._diagonals:
                ny, nx = y + dy, x + dx
                if not self.world.in_bounds(ny, nx):
                    continue
                if not self.world.is_walkable(ny, nx):
                    continue
                # Optional: disallow cutting corners (if either adjacent orthogonal is obstacle)
                # check the two adjacent orthogonal cells
                adj1 = (y + dy, x)
                adj2 = (y, x + dx)
                if (self.world.in_bounds(*adj1) and self.world.in_bounds(*adj2)
                    and (self.world.grid[adj1[0]][adj1[1]] == CellType.OBSTACLE
                         or self.world.grid[adj2[0]][adj2[1]] == CellType.OBSTACLE)):
                    # skip diagonal that cuts through corner between obstacles
                    continue
                res.append(((ny, nx), math.sqrt(2)))

        return res

    def reconstruct_path(self, came_from: Dict[Coord, Coord], current: Coord) -> List[Coord]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def find_path(self, start: Coord, goal: Coord) -> Optional[Tuple[List[Coord], float]]:
        """
        Run A* from start to goal.
        Returns: (path_list, total_cost) or None if unreachable
        """
        # basic checks
        if not self.world.in_bounds(*start) or not self.world.in_bounds(*goal):
            return None
        if not self.world.is_walkable(*start) or not self.world.is_walkable(*goal):
            return None

        open_set = []
        # heap elements: (f_score, g_score, node)
        g_score = {start: 0.0}
        f_score = {start: self.heuristic(start, goal)}
        heapq.heappush(open_set, (f_score[start], g_score[start], start))

        came_from: Dict[Coord, Coord] = {}

        closed = set()

        while open_set:
            current_f, current_g, current = heapq.heappop(open_set)

            if current in closed:
                continue
            # goal check
            if current == goal:
                path = self.reconstruct_path(came_from, current)
                total_cost = g_score[current]
                return path, total_cost

            closed.add(current)

            for neighbor, move_multiplier in self.neighbors(current):
                if neighbor in closed:
                    continue

                # movement cost: use neighbor cell cost (terrain), scaled by move multiplier
                # optionally average current & neighbor cost:
                # cost = ((self.world.get_cost(*current) + self.world.get_cost(*neighbor)) / 2.0) * move_multiplier
                cost = self.world.get_cost(*neighbor) * move_multiplier

                tentative_g = g_score[current] + cost

                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor, goal)
                    f_score[neighbor] = f
                    heapq.heappush(open_set, (f, tentative_g, neighbor))

        # no path found
        return None


# -------------------------
# Quick test / example
# -------------------------
if __name__ == "__main__":
    # small smoke test if run directly
    from src.models.map.map_generator import MapGenerator

    gen = MapGenerator(width=20, height=20, obstacle_prob=0.18, danger_prob=0.10, seed=42)
    world = gen.generate(survivors=3, drones=2)

    print("Map grid (0=N,1=O,2=D,3=S,4=DR):")
    world.print_map()

    drones = world.list_drones()
    survivors = world.list_survivors()
    print("Drones:", drones)
    print("Survivors:", survivors)

    if not drones or not survivors:
        print("Need at least one drone and one survivor to test pathfinding.")
    else:
        start = drones[0]
        goal = survivors[0]
        astar = AStar(world, allow_diagonal=True)
        result = astar.find_path(start, goal)
        if result is None:
            print("No path found from", start, "to", goal)
        else:
            path, cost = result
            print("Path from", start, "to", goal, "len=", len(path), "cost=", cost)
            print(path)
