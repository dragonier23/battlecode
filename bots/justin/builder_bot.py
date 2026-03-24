import sys
from typing import List, Deque

from cambc import Controller, Environment, Position, EntityType, Direction

from bot_state import *
from pathfinder import DStarLite
from const import BuilderState, PASSABLE, BuildingState, Quadrant, ORTHOGONAL_DIRS
from utils import is_movable, pos_within_r2, is_in_bounds
from memory import Memory
from pathfinding import BFS
import random

class BuilderBot:
    def __init__(self):
        self.initialised = False
        self.state : BotState = Init()

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

        self.target = Position(6, 1) # self.opp_core_pos # [Position(0, 0), Position(0, self.h), Position(self.w, 0), Position(self.w, self.h), Position(self.w // 2, 0), Position(self.w // 2, self.h // 2), Position(0, self.h // 2), Position(self.w, self.h // 2), Position(self.w // 2, self.h)][self.i]# target
        self.conveyor_path: Deque[tuple[Position, Direction]] | None = None
        self.initialised = True

        self.search_strategy = BFS(Direction, lambda tile: tile.env != Environment.WALL and (tile.building == None or tile.building.type in PASSABLE))
        self.conveyor_strategy = BFS([Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST], lambda tile: (tile.env == None and (tile.team == None or tile.team == ct.get_team()) and tile.building == None and tile.bot == False) or (tile.building.type == EntityType.CORE and tile.team == ct.get_team())) 

    def run(self, ct: Controller) -> None:
        if not self.initialised:
            self.init(ct)
        self.memory.update(ct)

    def explore(self, ct: Controller, direction: Direction) -> bool:
        directions = [direction, direction, direction.rotate_left(), direction.rotate_right()]
        random.shuffle(directions)
        for d in directions:
            if is_movable(self.memory.grid, ct.get_position().add(d)) and self.move_may_build_road(ct, d):
                return True
        return False
    
    def harvest_new_resource(self, ct: Controller) -> None:
        resource_pos = self.memory.get_closest_resource(ct)
        if resource_pos is not None:
            resource_ortho_pos = min([resource_pos.add(d) for d in ORTHOGONAL_DIRS if is_movable(self.memory.grid, resource_pos.add(d))], key=lambda p: p.distance_squared(self.core_pos), default=None)
            if resource_ortho_pos is not None:
                self.state = MoveTo(DStarLite(self.memory, ct.get_position(), resource_ortho_pos, r2=2), Harvest(resource_pos))
            else:
                self.state = Explore(5, random.choice(ORTHOGONAL_DIRS))
        else:
            self.state = Explore(5, random.choice(ORTHOGONAL_DIRS))

    def move_may_build_road(self, ct: Controller, direction: Direction) -> bool:
        """Move in given direction. If necessary, builds a road first. Returns True if successful."""
        pos = ct.get_position().add(direction)
        if ct.can_build_road(pos):
            ct.build_road(pos)
        if ct.can_move(direction):
            ct.move(direction)
            return True
        return False

    def get_closest_adj_pos(self, ct: Controller, pos: Position) -> Position:
        """Returns the closest square in a 3x3 area centred at pos to the bot's current position."""
        return min([p for p in pos_within_r2(self.w, self.h, pos, 2) if is_movable(self.memory.grid, p)], key=lambda p: ct.get_position().distance_squared(p))

    def move_random(self, ct: Controller) -> None:
        """Move in a random direction to prevent softlocks."""
        positions = [p for p in pos_within_r2(self.w, self.h, ct.get_position(), 2) if is_movable(self.memory.grid, p) and p != ct.get_position()]
        if positions:
            self.move_may_build_road(ct, ct.get_position().direction_to(random.choice(positions)))

    def move_to(self, ct: Controller, path_finder: PathFinder) -> None:
        next_pos = path_finder.get_next_pos(ct.get_position())
        print(f'next_pos: {next_pos}')
        if next_pos:
            direction = ct.get_position().direction_to(next_pos)
            if not self.move_may_build_road(ct, direction):
                self.move_random(ct)
        else: 
            self.move_random(ct)

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

    def build_conveyor(self, ct: Controller, build_pos: Position, direction: Direction):
        """Build a conveyor in the given position and direction, destroying any existing building if necessary. Returns True if successful."""
        if self.memory.is_directional_building(ct, build_pos, EntityType.CONVEYOR, direction):
            return True
        if ct.can_destroy(build_pos):
            ct.destroy(build_pos)
        if ct.can_build_conveyor(build_pos, direction):
            ct.build_conveyor(build_pos, direction)
            return True
        return False

    def convey2(self, ct: Controller, path_finder: PathFinder):
        """Convey written by Justin"""
        next_pos = path_finder.get_next_pos(ct.get_position())
        print(next_pos)
        if next_pos:
            prev_pos = ct.get_position()
            direction = prev_pos.direction_to(next_pos)
            if self.move_may_build_road(ct, direction):
                if self.memory.grid[prev_pos.x][prev_pos.y].building != BuildingState(EntityType.CONVEYOR, direction):
                    if ct.can_destroy(prev_pos):
                        ct.destroy(prev_pos)
                    if ct.can_build_conveyor(prev_pos, direction):
                        ct.build_conveyor(prev_pos, direction)
                    else:
                        self.state = ConveyBuildConveyor(prev_pos, self.state)
                else:
                    self.harvest_new_resource(ct)
        
    def get_suitable_bridge_pos(self, ct: Controller, resource_pos: Position) -> Position | None:
        """Returns a position adjacent to resource_pos that would be suitable for building a bridge, or None if no such position exists."""
        for d in ORTHOGONAL_DIRS:
            pos = resource_pos.add(d)
            if self.memory.grid[pos.x][pos.y].env == Environment.EMPTY:
                return pos
        return None

    def bridge_convey(self, ct: Controller, path_finder: PathFinder):
        """Convey via bridges"""
        cur_pos = ct.get_position()
        next_pos = path_finder.get_next_pos(cur_pos)
        if next_pos:
            if self.memory.grid[cur_pos.x][cur_pos.y].building and self.memory.grid[cur_pos.x][cur_pos.y].building.type == EntityType.BRIDGE:
                self.state = MoveTo(
                    DStarLite(self.memory, ct.get_position(), next_pos, r2=2),
                    next_state=self.state
                )
                return
            if ct.can_destroy(cur_pos):
                ct.destroy(cur_pos)
            if ct.can_build_bridge(cur_pos, next_pos):
                ct.build_bridge(cur_pos, next_pos)
                # Move close to next pos, repeat
                self.state = MoveTo(
                    DStarLite(self.memory, ct.get_position(), next_pos, r2=2),
                    next_state=self.state
                )

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
