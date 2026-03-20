from typing import List, Deque

from cambc import Controller, Environment, Position, EntityType, Direction

from bot_state import BotState, Idle
from const import BuilderState, Passable, Quadrant
from utils import pos_within_r2, is_in_bounds
from memory import Memory
from pathfinding import BFS

class BuilderBot:
    def __init__(self):
        self.initialised = False
        self.state : BotState = Idle()

    def init(self, ct: Controller) -> None:
        """Intended to be called when the bot first spawns and run is called."""
        self.initialised = True
        self.w = ct.get_map_width()
        self.h = ct.get_map_height()
        self.memory = Memory(self.w, self.h)

        self.core_id = [ent for ent in ct.get_nearby_entities(2) if ct.get_entity_type(ent) == EntityType.CORE][0]
        self.core_pos = ct.get_position(self.core_id)
        self.core_quad = Quadrant[self.core_pos.x // (self.w // 3)][self.core_pos.y // (self.h // 3)]
        self.opp_core_pos = Position(self.w - self.core_pos.x, self.h - self.core_pos.y)

        self.state = BuilderState.SEARCHING
        self.target = Position(6, 1) # self.opp_core_pos # [Position(0, 0), Position(0, self.h), Position(self.w, 0), Position(self.w, self.h), Position(self.w // 2, 0), Position(self.w // 2, self.h // 2), Position(0, self.h // 2), Position(self.w, self.h // 2), Position(self.w // 2, self.h)][self.i]# target
        self.conveyor_path: Deque[tuple[Position, Direction]] | None = None
        self.initialised = True

        self.search_strategy = BFS(Direction, lambda tile: tile.env != Environment.WALL and (tile.building == None or tile.building.type in Passable))
        self.conveyor_strategy = BFS([Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST], lambda tile: (tile.env == None and (tile.team == None or tile.team == ct.get_team()) and tile.building == None and tile.bot == False) or (tile.building.type == EntityType.CORE and tile.team == ct.get_team())) 

    def run(self, ct: Controller) -> None:
        if not self.initialised:
            self.init(ct)
        self.memory.update(ct)

        match self.state: 
            case BuilderState.SEARCHING: 
                self.search(ct, self.target)
            case BuilderState.CONVEY: 
                self.convey(ct, ct.get_position())


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
        for d in [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]:
            n = ct.get_position().add(d)
            if not is_in_bounds(n, ct): continue

            tile = self.memory.grid[n.x][n.y]
            if (tile.env in [Environment.ORE_AXIONITE, Environment.ORE_TITANIUM]) and ct.can_build_harvester(n):
                ct.build_harvester(n)
                self.state = BuilderState.CONVEY
                return
        path = self.search_strategy.search(ct, self.memory, ct.get_position(), target)
        dest, dir = path[1][0], path[0][1]
        if ct.can_build_road(dest):
            ct.build_road(dest)
        if ct.can_move(dir):
            ct.move(dir)

    def convey(self, ct: Controller, pos: Position): 
        self.update_conveyor_path(ct, pos)
        if len(self.conveyor_path) == 0: 
            self.state = BuilderState.SEARCHING
            return 

        print(self.conveyor_path)
        currPos, nextDirection = self.conveyor_path.popleft()
        print(currPos, nextDirection) 
        if ct.can_move(nextDirection): 
            ct.move(nextDirection)
            if ct.can_destroy(currPos):
                ct.destroy(currPos)
            if ct.can_build_conveyor(currPos, nextDirection): 
                ct.build_conveyor(currPos, nextDirection)
        else: 
            # if ct.can_build_road(currPos): 
            ct.build_road(currPos.add(nextDirection))
            self.conveyor_path.appendleft((currPos, nextDirection))
            

    def update_conveyor_path(self, ct: Controller, pos: Position) -> None: 
        '''
        Given controller, position of the bot, and curr position, update converyor path to contain the shortest path from the curr position to the core for conveyor pathing
        '''
        if self.conveyor_path and self.check_path(self.conveyor_path): 
            return 
        self.conveyor_path = self.conveyor_strategy.search(ct, self.memory, pos, [Position(x, y) for x in range(self.core_pos.x - 1, self.core_pos.x + 2) for y in range(self.core_pos.y - 1, self.core_pos.y + 2)])

    def check_path(self, curr: List[tuple[Position, Direction]]) -> bool: 
        for p, _ in curr: 
            tile = self.memory.grid[p.x][p.y]
            if self.conveyor_strategy.traverable(tile):
                return False 
        return True
