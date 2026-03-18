from cambc import Controller, Environment, Position, EntityType, Direction
from collections import deque
from typing import List, Deque
from const import TileState, BuildingState, DirectedBuildings, BuilderState, Passable, Pathable, Quadrant, Target
from utils import is_in_bound

class BuilderBot:
    def __init__(self):
        self.initialised = False

    def init(self, ct: Controller, target: Position) -> None:
        """Intended to be called when the bot first spawns and run is called."""
        self.w = ct.get_map_width()
        self.h = ct.get_map_height()
        self.tile_env : List[List[Environment | None]] = [[None for _ in range(self.h)] for _ in range(self.w)]
        self.grid : List[List[TileState | None]] = [[None for _ in range(self.h)] for _ in range(self.w)]

        self.core_id = [ent for ent in ct.get_nearby_entities(2) if ct.get_entity_type(ent) == EntityType.CORE][0]
        self.core_pos = ct.get_position(self.core_id)
        self.core_quad = Quadrant[self.core_pos.x % (self.w // 3)][self.core_pos.y % (self.h // 3)]
        self.opp_core_pos = Position(self.w - self.core_pos.x, self.h - self.core_pos.y)

        self.state = BuilderState.SEARCHING
        self.target = target
        self.convey_path: Deque[tuple[Position, Direction]] | None = None
        

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

    def run(self, ct: Controller, target: Position) -> None:
        if not self.initialised:
            self.init(ct, target)
        self.update_state(ct)

        match self.state: 
            case BuilderState.SEARCHING: 
                self.search(ct, self.target)
            case BuilderState.CONVEY: 
                self.convey(ct)

    def get_direction(self, goal):
        pass

    def search(self, ct: Controller, target: Position) -> None: 
        for d in Direction:
            n = ct.get_position().add(d)
            if not is_in_bound(n, ct): continue

            tile = self.grid[n.x][n.y]
            if (tile.env in [Environment.ORE_AXIONITE, Environment.ORE_TITANIUM]) and ct.can_build_harvester(n):
                ct.build_harvester(n)
                self.state = BuilderState.CONVEY
                return
        
        dest, dir = self.step(ct, target)
        if ct.can_build_road(dest):
            ct.build_road(dest)
        if ct.can_move(dir):
            ct.move(dir)

    def step(self, ct: Controller, target: Position) -> tuple[Position, Direction]: 
        '''
        Given our existing view of the map, figure out how to step towards the target position 
        '''
        pos = ct.get_position()
        q = deque([pos])

        # marked is a dictionary mapping some node to the tuple containing its previous node, and the direction from that previous node moved to get to the key node
        marked: dict[Position, tuple[Position, Direction]] = {pos: (None, None)}

        while q: 
            c = q.popleft()
            if c == target: 
                prev, d = marked[c]
                while prev != pos: 
                    c = prev
                return (prev, d)                 

            for d in Direction:
                neighbour = c.add(d)
                if is_in_bound(neighbour, ct) and neighbour not in marked: 
                    tile = self.grid[neighbour.x][neighbour.y]
                    if tile.env == Environment.EMPTY and tile.building.type in Passable: 
                        marked[neighbour] = (c, d)
                        q.append(neighbour)

    def convey(self, ct: Controller, pos: Position): 
        self.update_converyor_path(ct, pos)
        if len(self.converyor_path) == 0: 
            self.state = BuilderState.SEARCHING
            return 

        currPos, nextDirection = self.converyor_path.popleft()
        if ct.can_move(nextDirection): 
            ct.move(nextDirection)
            if ct.can_destroy(currPos):
                ct.destroy(currPos)
            if ct.can_build_conveyor(currPos): 
                ct.build_conveyor(currPos)
            

    def update_converyor_path(self, ct: Controller, pos: Position) -> None: 
        '''
        Given controller, position of the bot, and curr position, update converyor path to contain the shortest path from the curr position to the core for conveyor pathing
        '''
        if self.converyor_path and self.check_path(self.converyor_path): 
            return 
        self.converyor_path = self.gen_conveyor_path(ct, pos)

    def check_path(self, curr: List[Position]) -> bool: 
        for p in curr: 
            tile = self.gird[p.x][p.y]
            if tile.building.type not in Pathable: 
                return False 
        return True

    def gen_conveyor_path(self, ct: Controller, pos: Position) -> Deque[tuple[Position, Direction]]:
        """
        Return the shortest path from pos to any tile around the 3x3 core.
        Currently just a BFS search, preferably do something slightly more efficient
        Curr: List[Position] the currently computed path from the last conveyer built to the core.  
        """
        q = deque([pos])

        # marked is a dictionary mapping some node to the tuple containing its previous node, and the direction from that previous node moved to get to the key node
        marked: dict[Position, tuple[Position, Direction]] = {pos: (None, None)}

        while q: 
            c = q.popleft()
            if c.x in range(self.core_pos.x - 2, self.core_pos.x + 3) and c.y in range(self.core_pos.y - 2, self.core_pos.y + 3): 
                res = deque([(c, None)])
                while c != pos: 
                    res.appendleft(marked[c])
                    c = marked[c][0]
                return res                 

            for d in Direction:
                neighbour = c.add(d)
                if is_in_bound(neighbour, ct) and neighbour not in marked: 
                    tile = self.grid[neighbour.x][neighbour.y]
                    if tile.env == Environment.EMPTY and tile.building.type in Pathable: 
                        marked[neighbour] = (c, d)
                        q.append(neighbour)