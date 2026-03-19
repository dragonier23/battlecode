from cambc import Controller, Environment, Position, EntityType, Direction
from collections import deque
from typing import List, Deque
from bot_state import BotState, Idle
from const import TileState, BuildingState, DirectedBuildings, BuilderState, Passable, Pathable, Quadrant, Target
from utils import pos_within_r2, is_in_bounds

class BuilderBot:
    def __init__(self):
        self.initialised = False
        self.state : BotState = Idle()

    def init(self, ct: Controller) -> None:
        """Intended to be called when the bot first spawns and run is called."""
        self.initialised = True
        self.w = ct.get_map_width()
        self.h = ct.get_map_height()
        self.grid : List[List[TileState]] = [[TileState() for _ in range(self.h)] for _ in range(self.w)]

        self.core_id = [ent for ent in ct.get_nearby_entities(2) if ct.get_entity_type(ent) == EntityType.CORE][0]
        self.core_pos = ct.get_position(self.core_id)
        # self.core_quad = Quadrant[self.core_pos.x % (self.w // 3)][self.core_pos.y % (self.h // 3)]
        # self.opp_core_pos = Position(self.w - self.core_pos.x, self.h - self.core_pos.y)

    def update_state(self, ct: Controller) -> None:
        """Intended to be called at the start of every turn to update the bot's state."""
        pos = ct.get_position()

        for pos in ct.get_nearby_tiles(): 
            if not is_in_bounds(pos, ct):
                continue
            x, y = pos.x, pos.y

            tile_env = ct.get_tile_env(pos)
            if self.grid[x][y].env is None:
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

    def build_road_and_move(self, ct: Controller, direction: Direction) -> bool:
        """Move in given direction. If necessary, builds a road first. Returns True if successful."""
        pos = ct.get_position().add(direction)
        if ct.can_build_road(pos):
            ct.build_road(pos)
        if ct.can_move(direction):
            ct.move(direction)
            return True
        return False

    def get_closest_resource(self, ct: Controller) -> Position | None:
        """Returns the position of the closest ore or axionite, or None if there are no known resources."""
        pos = ct.get_position()
        closest_resource = None
        closest_distance = float('inf')

        for x in range(self.w):
            for y in range(self.h):
                tile = self.grid[x][y]
                if tile.env in [Environment.ORE_AXIONITE, Environment.ORE_TITANIUM]:
                    print("Found resource at", x, y)
                    distance = pos.distance_squared(Position(x, y))
                    if distance < closest_distance:
                        closest_resource = Position(x, y)
                        closest_distance = distance

        return closest_resource

    def get_direction(self, goal: Position, ct: Controller) -> Direction:
        """Returns next direction to move to get from current position to goal, using a simple local strategy."""
        adjacent = [p for p in pos_within_r2(self.w, self.h, ct.get_position(), 2) if p != ct.get_position() and ct.get_tile_env(p) != Environment.WALL]
        adjacent.sort(key=lambda p: p.distance_squared(goal))
        return ct.get_position().direction_to(adjacent[0]) if adjacent else Direction.CENTRE

    def search(self, ct: Controller, target: Position) -> None: 
        for d in Direction:
            n = ct.get_position().add(d)
            if not is_in_bounds(n, ct): continue

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
                if is_in_bounds(neighbour, ct) and neighbour not in marked: 
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
            tile = self.grid[p.x][p.y]
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
                
                if neighbour not in marked and is_in_bounds(neighbour, ct): 
                    tile = self.grid[neighbour.x][neighbour.y]
                    if tile.env == Environment.EMPTY and tile.building.type in Pathable: 
                        marked[neighbour] = (c, d)
                        q.append(neighbour)