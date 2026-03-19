from cambc import Direction, Position, Controller
from typing import List

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