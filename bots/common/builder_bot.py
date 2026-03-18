from cambc import Controller, Environment, Position, EntityType, Direction
from collections import deque
from typing import List
from const import TileState, BuildingState, DirectedBuildings

class BuilderBot:
    def __init__(self):
        self.initialised = False

    def init(self, ct: Controller) -> None:
        """Intended to be called when the bot first spawns and run is called."""
        self.w = ct.get_map_width()
        self.h = ct.get_map_height()
        self.tile_env : List[List[Environment | None]] = [[None for _ in range(self.h)] for _ in range(self.w)]
        self.grid : List[List[TileState | None]] = [[None for _ in range(self.h)] for _ in range(self.w)]

        self.core_id = [ent for ent in ct.get_nearby_entities(2) if ct.get_entity_type(ent) == EntityType.CORE][0]
        self.core_pos = ct.get_position(self.core_id)

    def update_state(self, ct: Controller) -> None:
        """Intended to be called at the start of every turn to update the bot's state."""
        pos = ct.get_position()
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                x, y = pos.x + dx, pos.y + dy
                if 0 <= x < self.w and 0 <= y < self.h:
                    self.tile_env[x][y] = ct.get_tile_environment(Position(x, y))

        for pos in ct.get_nearby_tiles(): 
            x, y = pos.x, pos.y

            tile_env = ct.get_tile_env(pos)
            if self.grid[x][y] is None:
                match tile_env:
                    case Environment.WALL:
                        self.grid[x][y] = TileState(Environment.WALL)
                    case Environment.ORE_AXIONITE | Environment.ORE_TITANIUM | Environment.EMPTY:
                        self.grid[x][y] = TileState(tile_env)
                    case Environment.EMPTY: 
                        self.grid[x][y] = TileState(Environment.EMPTY)

            entity_id = ct.get_tile_building_id(pos)
            if entity_id:
                self.grid[x][y].team = ct.get_team(entity_id)
                entity_type = ct.get_entity_type(entity_id)
                direction = ct.get_direction(entity_id) if entity_type.name in DirectedBuildings.__members__ else None
                bot = True if ct.get_tile_builder_bot_id(pos) else False
                self.grid[x][y].building = BuildingState(entity_type, direction, bot)

    def run(self, ct: Controller) -> None:
        if not self.initialised:
            self.init(ct)
        self.update_state(ct)

    def get_direction(self, goal):
        pass

    def conveyor_path(self, ct: Controller, pos: Position) -> List[Position] | None:
        """
        Return the shortest path from pos to any tile around the 3x3 core.
        Currently just a BFS search, preferably do something slightly more efficient
        """

        q = deque([pos])
        marked = {pos: None}

        while q: 
            c = q.popleft()
            if c.x in range(self.core_pos.x - 2, self.core_pos.x + 3) and c.y in range(self.core_pos.y - 2, self.core_pos.y + 3): 
                res = deque([c])
                while c != pos: 
                    res.appendleft(marked[c])
                    c = marked[c]
                return res                 

            for d in Direction:
                neighbour = c.add(d)
                if neighbour not in marked: 
                    tile = self.grid[neighbour.x][neighbour.y]
                    if tile.env == Environment.EMPTY and tile.building in [None, EntityType.ARMOURED_CONVEYOR, EntityType.BUILDER_BOT, EntityType.CONVEYOR, EntityType.ROAD, EntityType.SPLITTER, EntityType.BRIDGE]: 
                        marked[neighbour] = c
                        q.append(neighbour)