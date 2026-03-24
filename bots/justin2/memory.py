from cambc import Controller, Direction, EntityType, Environment, Position
from typing import List
from const import TileState, BuildingState, DirectedBuildings
from utils import is_in_bounds, is_movable

class Memory: 
    def __init__(self, w: int, h: int): 
        self.w = w
        self.h = h
        self.grid : List[List[TileState]] = [[TileState() for _ in range(self.h)] for _ in range(self.w)]
        self.titanium_pos : List[Position] = []
        self.axionite_pos : List[Position] = []
        self.changed_tiles : set[Position] = set()

    def get_closest_resource(self, ct: Controller) -> Position | None:
        positions = self.titanium_pos
        positions.sort(key=lambda p: ct.get_position().distance_squared(p), reverse=True)
        while positions and self.is_building(ct, positions[-1], EntityType.HARVESTER):
            positions.pop()
        return positions[-1] if positions else None
    
    def is_building(self, ct: Controller, pos: Position, building: EntityType) -> bool:
        return is_in_bounds(pos, ct) and self.grid[pos.x][pos.y].building is not None and self.grid[pos.x][pos.y].building.type == building
    
    def is_directional_building(self, ct: Controller, pos: Position, building: EntityType, direction: Direction) -> bool:
        return is_in_bounds(pos, ct) and self.grid[pos.x][pos.y].building is not None and self.grid[pos.x][pos.y].building.type == building and self.grid[pos.x][pos.y].building.direction == direction

    def reset_changed_tiles(self) -> None:
        self.changed_tiles = set()

    def update(self, ct: Controller) -> None:
        """Intended to be called at the start of every turn to update the bot's memory."""
        pos = ct.get_position()
        for pos in ct.get_nearby_tiles(): 
            x, y = pos.x, pos.y
            prev_movable = is_movable(self.grid, pos)

            tile_env = ct.get_tile_env(pos)
            if self.grid[x][y].env is None:
                self.grid[x][y] = TileState(tile_env)
                if tile_env == Environment.ORE_TITANIUM:
                    self.titanium_pos.append(pos)
                elif tile_env == Environment.ORE_AXIONITE:
                    self.axionite_pos.append(pos)

            entity_id = ct.get_tile_building_id(pos)
            if entity_id:
                self.grid[x][y].team = ct.get_team(entity_id)
                entity_type = ct.get_entity_type(entity_id)
                direction = ct.get_direction(entity_id) if entity_type.name in DirectedBuildings.__members__ else None
                self.grid[x][y].bot =  True if ct.get_tile_builder_bot_id(pos) else False
                self.grid[x][y].building = BuildingState(entity_type, direction)

            if prev_movable != is_movable(self.grid, pos):
                self.changed_tiles.add(pos)