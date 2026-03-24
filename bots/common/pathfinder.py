import time
from typing import List, Tuple
from data_structures.heappq import HeapPQ
from memory import Memory
from utils import is_movable, pos_within_r2
from data_structures.priority_queue import PriorityQueue
from const import TileState
from copy import deepcopy

from cambc import Direction, Environment, Position

import sys

class PathFinder:
    def __init__(self, memory: Memory, start: Position, goal: Position):
        pass

    def get_next_pos(self, start: Position) -> Position | None:
        """Returns the position of the next move to get from start to target, or None if no path exists."""
        pass

INT_MAX = 10**9

MAX_ITERS = 10

class DStarLite(PathFinder):
    def __init__(self, memory: Memory, start: Position, goal: Position, r2: int):
        super().__init__(memory, start, goal)
        self.s_start = start
        self.s_last = start
        self.s_goal = goal 
        self.memory = memory
        self.r2 = r2

        self.U = HeapPQ()
        self.k_m = 0
        self.w = len(self.memory.grid)
        self.h = len(self.memory.grid[0])
        self.g = [[INT_MAX for _ in range(self.h)] for _ in range(self.w)]
        self.rhs = [[INT_MAX for _ in range(self.h)] for _ in range(self.w)]
        self.rhs[goal.x][goal.y] = 0
        self.U.insert(self.calculate_key(goal), goal)
        self.interrupted = False
        self.iters = 0

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
            grid = self.memory.grid
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
            t0 = time.perf_counter()
            k_old, u = self.U.pop()
            k_new = self.calculate_key(u)
            if k_old < k_new:
                self.U.insert(k_new, u)
            elif self.g[u.x][u.y] > self.rhs[u.x][u.y]:
                self.g[u.x][u.y] = self.rhs[u.x][u.y]
                for s in self.succs(u):
                    self.update_vertex(s)
            else:
                self.g[u.x][u.y] = INT_MAX
                for s in self.succs(u) + [u]:
                    self.update_vertex(s)
            self.iters += 1
            print(f"One iteration of compute_shortest_path took {((time.perf_counter()-t0)*1000):.4f} ms")
            if self.iters >= MAX_ITERS:
                self.interrupted = True
                break

    # def replan_if_needed(self) -> None:
    #     self.iters = 0
    #     changed_vertices = self.memory.changed_tiles
    #     if changed_vertices:
    #         self.k_m += self.heuristic(self.s_last, self.s_start)
    #         self.s_last = self.s_start
    #         for u in changed_vertices:
    #             self.update_vertex(u)
    #         self.compute_shortest_path()

    def get_next_pos(self, start: Position) -> Position | None:
        """Returns the position of the next move to get from start to goal, or None if no path exists."""
        # print_grid(self.memory.grid)
        # print_g_or_rhs(self.g)
        # print_g_or_rhs(self.rhs)
        self.iters = 0
        if self.interrupted:
            self.interrupted = False
            self.compute_shortest_path() # continue computation
        if self.g[self.s_start.x][self.s_start.y] == INT_MAX:
            return None
        self.s_start = start
        changed_vertices = self.memory.changed_tiles
        if changed_vertices:
            self.k_m += self.heuristic(self.s_last, self.s_start)
            self.s_last = start
            for u in changed_vertices:
                self.update_vertex(u)
            self.compute_shortest_path()
            self.memory.reset_changed_tiles()
        if self.interrupted: # if interrupted during computation, skip turn
            return None
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


