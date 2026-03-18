from cambc import Position, Controller

def is_in_bound(p: Position, ct: Controller):
    return p.x >= 0 and p.y >= 0 and p.x < ct.get_map_width() and p.y < ct.get_map_height()