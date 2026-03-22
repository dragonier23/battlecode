from typing import List, Tuple
from utils import is_movable, pos_within_r2
from data_structures.priority_queue import PriorityQueue
from const import TileState
from copy import deepcopy

from cambc import Direction, Environment, Position

import sys

class PathFinder:
    def __init__(self, grid: List[List[TileState]], start: Position, goal: Position):
        pass

    def get_next_pos(self, start: Position, grid: List[List[TileState]]) -> Position | None:
        """Returns the position of the next move to get from start to target, or None if no path exists."""
        pass

INT_MAX = 10**9

VISION_EDGE_MIN_R2 = 13 # 3^2 + 2^2
VISION_EDGE_MAX_R2 = 20 # 4^2 + 2^2

class DStarLite(PathFinder):
    def __init__(self, grid: List[List[TileState]], start: Position, goal: Position, r2: int):
        super().__init__(grid, start, goal)
        self.s_start = start
        self.s_last = start
        self.s_goal = goal 
        self.grid = deepcopy(grid)
        self.r2 = r2

        self.U = PriorityQueue()
        self.k_m = 0
        self.w = len(grid)
        self.h = len(grid[0])
        self.g = [[INT_MAX for _ in range(self.h)] for _ in range(self.w)]
        self.rhs = [[INT_MAX for _ in range(self.h)] for _ in range(self.w)]
        self.rhs[goal.x][goal.y] = 0
        self.U.insert(self.calculate_key(goal), goal)

        self.compute_shortest_path()

    def __repr__(self) -> str:
        return f"DStarLite(s_start={self.s_start}, s_goal={self.s_goal}, r2={self.r2}, k_m={self.k_m})"

    def heuristic(self, a: Position, b: Position) -> int:
        """Returns the heuristic estimate of the cost to get from a to b."""
        return (a.distance_squared(b) / self.r2 + 10**-6) ** .5

    def calculate_key(self, s: Position) -> tuple[int, int]:
        k1 = min(self.g[s.x][s.y], self.rhs[s.x][s.y]) + self.heuristic(self.s_start, s) + self.k_m
        k2 = min(self.g[s.x][s.y], self.rhs[s.x][s.y])
        return (k1, k2)
    
    def c(self, u: Position, v: Position, grid: List[List[TileState]] | None = None) -> int:
        """Returns the cost of moving from u to v. Assumes u and v are adjacent."""
        if grid is None:
            grid = self.grid
        if not is_movable(grid, u) or not is_movable(grid, v):
            return INT_MAX
        else:
            return 1
    
    def succs(self, u: Position) -> List[Position]:
        return [p for p in pos_within_r2(self.w, self.h, u, self.r2) if p != u]

    def update_vertex(self, u: Position) -> None:
        if u != self.s_goal:
            self.rhs[u.x][u.y] = min([self.c(u, s) + self.g[s.x][s.y] for s in self.succs(u)])
        if self.U.is_member(u):
            self.U.remove(u)
        if self.g[u.x][u.y] != self.rhs[u.x][u.y]:
            self.U.insert(self.calculate_key(u), u)

    def compute_shortest_path(self) -> None:
        while self.U.top_key() < self.calculate_key(self.s_start) or self.rhs[self.s_start.x][self.s_start.y] != self.g[self.s_start.x][self.s_start.y]:
            k_old, u = self.U.pop()
            if k_old < self.calculate_key(u):
                self.U.insert(self.calculate_key(u), u)
            elif self.g[u.x][u.y] > self.rhs[u.x][u.y]:
                self.g[u.x][u.y] = self.rhs[u.x][u.y]
                for s in self.succs(u):
                    self.update_vertex(s)
            else:
                self.g[u.x][u.y] = INT_MAX
                for s in self.succs(u) + [u]:
                    self.update_vertex(s)

    def edge_vertices(self, u: Position) -> List[Position]:
        """Returns the vertices at the ends of the vision radius from u."""
        vertices = []
        for v in pos_within_r2(self.w, self.h, u, VISION_EDGE_MAX_R2):
            # if v.distance_squared(u) >= VISION_EDGE_MIN_R2:
            vertices.append(v)
        return vertices

    def get_next_pos(self, start: Position, grid: List[List[TileState]]) -> Position | None:
        """Returns the position of the next move to get from start to goal, or None if no path exists."""
        # print_grid(grid)
        # print_g_or_rhs(self.g)
        # print_g_or_rhs(self.rhs)
        if self.g[self.s_start.x][self.s_start.y] == INT_MAX:
            return None
        self.s_start = start
        changed_vertices = [n for n in self.edge_vertices(self.s_start) if self.grid[n.x][n.y].env != grid[n.x][n.y].env] # ! only considered env changes, not building changes, which affects is_movable
        if changed_vertices:
            # print("Vertices changed:", changed_vertices, file=sys.stderr)
            self.k_m += self.heuristic(self.s_last, self.s_start)
            self.s_last = start
            for u in self.edge_vertices(self.s_start):
                self.update_vertex(u)
                self.grid[u.x][u.y] = grid[u.x][u.y]
            self.compute_shortest_path()
        self.s_start = min([su for su in self.succs(self.s_start)], key=lambda p: self.c(self.s_start, p) + self.g[p.x][p.y])
        return self.s_start
    
########################################
# Unit tests and debugging tools below #
########################################

def print_grid(grid: List[List[TileState]]) -> None:
    for y in range(len(grid[0])):
        for x in range(len(grid)):
            tile = grid[x][y]
            if not is_movable(grid, Position(x, y)):
                print("#", end="", file=sys.stderr)
            else:
                print(".", end="", file=sys.stderr)
        print(file=sys.stderr)

def print_g_or_rhs(arr: List[List[int]]) -> None:
    for y in range(len(arr[0])):
        for x in range(len(arr)):
            if arr[x][y] >= INT_MAX:
                print("X", end="", file=sys.stderr)
            else:
                print(arr[x][y], end="", file=sys.stderr)
        print(file=sys.stderr)

def test():
    grid_str = """........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
.....................#..................
..................#.....................
.........######.........................
........#......##.......................
................##......................
.................#......................
..................#.....................
........................................
..................##....................
...................#....................
...................#....................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................
........................................"""
    n = len(grid_str.splitlines()[0])
    m = len(grid_str.splitlines())
    grid = [[TileState(Environment.EMPTY) for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            if grid_str.splitlines()[j][i] == "#":
                grid[i][j].env = Environment.WALL
    p0 = Position(18, 19)
    pe = Position(11, 25)
    pf = DStarLite(grid, p0, pe, r2=9)
    for i in range(20):
        if i == 5:
            grid[18][26].env = Environment.WALL
        print(p0)
        if p0 == pe:
            break
        p0 = pf.get_next_pos(p0, grid)

if __name__ == "__main__":
    test()
    # from const import BuildingState, TileState, EntityType
    # grid = [[TileState(Environment.EMPTY) for _ in range(5)] for _ in range(5)]
    # grid_see = [[TileState(Environment.EMPTY) for _ in range(5)] for _ in range(5)]
    # grid[1][2].env = Environment.WALL
    # grid[1][3].env = Environment.WALL
    # grid[2][1].env = Environment.WALL
    # grid[3][1].env = Environment.WALL

    # pf = DStarLite(grid_see, Position(0, 0), Position(2, 2), r2=1)
    # p0 = Position(0, 0)
    # for i in range(10):
    #     if i == 2:
    #         grid_see = grid
    #     if p0 == Position(2, 2):
    #         break
    #     nm = pf.get_next_move(p0, grid_see)
    #     print(nm)
    #     if nm is None:
    #         break
    #     p0 = p0.add(nm)
    #     print(p0)


