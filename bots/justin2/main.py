import random
import sys

from cambc import Controller, Direction, EntityType, Environment, Position, Team
from pathfinder import DStarLite
from builder_bot import BuilderBot
from bot_state import *
from const import BUILDER_BOT_ACTION_RADIUS_SQUARED, BuildingState, ORTHOGONAL_DIRS
from utils import is_movable
import time

# non-centre directions
DIRECTIONS = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]

def is_in_bound(p:Position, ct:Controller):
    return p.x >= 0 and p.y >= 0 and p.x < ct.get_map_width() and p.y < ct.get_map_height()

class Player:
    def __init__(self):
        self.player = None
    def run(self, ct: Controller) -> None:
        if self.player == None: 
            etype = ct.get_entity_type()
            if etype == EntityType.CORE:
                self.player = Core()
            elif etype == EntityType.BUILDER_BOT:
                self.player = BuilderBot_()
        self.player.run(ct)
            
class Core:
    def __init__(self):
        self.num_spawned = 0
        self.spawn_direction : Direction = Direction.NORTHEAST
    def run(self, ct: Controller) -> None:
        # print(ct.get_current_round(), file=sys.stderr)
        # if ct.get_team() == Team.B:
        #     return
        # if ct.get_current_round() == 50:
        #     ct.resign()
        if self.num_spawned < 4:
            spawn_pos = ct.get_position().add(self.spawn_direction)
            if ct.can_spawn(spawn_pos):
                ct.spawn_builder(spawn_pos)
                self.num_spawned += 1
                self.spawn_direction = self.spawn_direction.rotate_right().rotate_right()

class BuilderBot_(BuilderBot):
    def __init__(self):
        super().__init__()

    def run(self, ct: Controller) -> None:
        t0 = time.perf_counter()
        super().run(ct)
        print(self.state)
        while True:
            match self.state:
                case Init():
                    direction = self.core_pos.direction_to(ct.get_position())
                    self.state = Explore(5, direction)
                    continue
                case Explore(turns_left, direction):
                    if self.explore(ct, direction):
                        self.state = Explore(turns_left - 1, direction)
                    else:
                        turns_left = 0 # end exploration early if we get blocked by something
                    if turns_left <= 0:
                        self.harvest_new_resource(ct)
                case MoveTo(path_finder, next_state):
                    if ct.get_position() == path_finder.s_goal:
                        self.state = next_state
                        continue
                    else:
                        self.move_to(ct, path_finder)
                case Patrol():
                    pass
                case Harvest(resource_pos):
                    if self.memory.grid[resource_pos.x][resource_pos.y].building and self.memory.grid[resource_pos.x][resource_pos.y].building.type == EntityType.HARVESTER:
                        self.harvest_new_resource(ct)
                    if ct.can_build_harvester(resource_pos):
                        # if ct.can_destroy(resource_pos):
                        #     ct.destroy(resource_pos)
                        ct.build_harvester(resource_pos)
                        self.state = BridgeConvey(
                            DStarLite(self.memory, self.get_suitable_bridge_pos(ct, resource_pos), self.get_closest_adj_pos(ct, self.core_pos), r2=9)
                        )
                case Convey(path_finder):
                    if ct.get_position().distance_squared(self.core_pos) <= 2:
                        self.harvest_new_resource(ct)
                    else:
                        self.convey2(ct, path_finder)
                case ConveyBuildConveyor(build_pos, next_state):
                    if ct.can_destroy(build_pos):
                        ct.destroy(build_pos)
                    if ct.can_build_conveyor(build_pos, build_pos.direction_to(ct.get_position())):
                        ct.build_conveyor(build_pos, build_pos.direction_to(ct.get_position()))
                        self.state = next_state
                case BridgeConvey(path_finder):
                    if path_finder.s_start.distance_squared(self.core_pos) <= 2:
                        self.harvest_new_resource(ct)
                    else:
                        self.bridge_convey(ct, path_finder)
            break

        t1 = time.perf_counter()
        print(f"Turn took {((t1-t0)*1000):.4f} ms")
                

