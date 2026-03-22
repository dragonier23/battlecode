from cambc import Environment, Position, Controller
from typing import List

from const import TileState, PASSABLE

def pos_within_r2(w: int, h: int, pos: Position, r2: int) -> List[Position]: 
    """Returns a list of all positions within radius^2 r2 of the given position."""
    r = int(r2**0.5) + 1
    result = []
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            new_pos = Position(pos.x + dx, pos.y + dy)
            if 0 <= new_pos.x < w and 0 <= new_pos.y < h and pos.distance_squared(new_pos) <= r2:
                result.append(new_pos)
    return result

def is_in_bounds(p: Position, ct: Controller):
    return p.x >= 0 and p.y >= 0 and p.x < ct.get_map_width() and p.y < ct.get_map_height()

def is_movable(grid: List[List[TileState]], pos: Position) -> bool:
    w = len(grid)
    h = len(grid[0]) if w > 0 else 0
    if pos.x < 0 or pos.y < 0 or pos.x >= w or pos.y >= h:
        return False
    return (grid[pos.x][pos.y].env == None or grid[pos.x][pos.y].env == Environment.EMPTY) and \
        (grid[pos.x][pos.y].building.type if grid[pos.x][pos.y].building else None) in PASSABLE