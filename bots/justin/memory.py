from cambc import Controller
from typing import List
from const import TileState, BuildingState, DirectedBuildings
from utils import is_in_bounds

class Memory: 
    def __init__(self, w: int, h: int): 
        self.w = w
        self.h = h
        self.grid : List[List[TileState]] = [[TileState() for _ in range(self.h)] for _ in range(self.w)]
        
    def update(self, ct: Controller) -> None:
        """Intended to be called at the start of every turn to update the bot's state."""
        pos = ct.get_position()

        for pos in ct.get_nearby_tiles(): 
            if not is_in_bounds(pos, ct):
                continue
            x, y = pos.x, pos.y

            tile_env = ct.get_tile_env(pos)
            if self.grid[x][y].env is None:
                self.grid[x][y] = TileState(tile_env)

            entity_id = ct.get_tile_building_id(pos)
            if entity_id:
                self.grid[x][y].team = ct.get_team(entity_id)
                entity_type = ct.get_entity_type(entity_id)
                direction = ct.get_direction(entity_id) if entity_type.name in DirectedBuildings.__members__ else None
                self.grid[x][y].bot =  True if ct.get_tile_builder_bot_id(pos) else False
                self.grid[x][y].building = BuildingState(entity_type, direction)