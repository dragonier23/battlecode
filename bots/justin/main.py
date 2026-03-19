import random

from cambc import Controller, Direction, EntityType, Environment, Position
from builder_bot import BuilderBot
from bot_state import *

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
        if self.num_spawned < 4:
            # if we haven't spawned 4 builder bots yet, try to spawn one on a random tile
            spawn_pos = ct.get_position().add(self.spawn_direction)
            if ct.can_spawn(spawn_pos):
                ct.spawn_builder(spawn_pos)
                self.num_spawned += 1
                self.spawn_direction = self.spawn_direction.rotate_right().rotate_right()

class BuilderBot_(BuilderBot):
    def __init__(self):
        super().__init__()

    def run(self, ct: Controller) -> None:
        super().run(ct)
        print(self.state)
        match self.state:
            case Idle():
                direction = self.core_pos.direction_to(ct.get_position())
                self.state = Wander(10, direction)
                self.run(ct) # immediately transition to wandering
            case Wander(turns_left, direction):
                if self.build_road_and_move(ct, direction):
                    self.state = Wander(turns_left-1, direction)
                else:
                    self.state = Wander(turns_left-1, random.choice(DIRECTIONS))
                if turns_left <= 0:
                    resource_pos = self.get_closest_resource(ct)
                    if resource_pos is not None:
                        self.state = MoveTo(resource_pos, 2, Convey(None))
                    else:
                        self.state = Wander(10, random.choice(DIRECTIONS))
            case MoveTo(position, r2, next_state):
                if ct.get_position().distance_squared(position) <= r2:
                    self.state = next_state
                else:
                    direction = self.get_direction(position, ct)
                    if not self.build_road_and_move(ct, direction):
                        random_direction = random.choice(DIRECTIONS)
                        if ct.can_move(random_direction):
                            ct.move(random_direction)
            case Patrol():
                pass
            case Convey(path):
                pass

                # if path is None:
                #     path = self.gen_conveyor_path(ct, ct.get_position())
                # if path is not None and len(path) > 0:
                #     next_pos = path[0]
                #     if ct.can_move(ct.get_position().direction_to(next_pos)):
                #         ct.move(ct.get_position().direction_to(next_pos))
                #         path.pop(0)
                #     else:
                #         path = None
                #         random_direction = random.choice(DIRECTIONS)
                #         if ct.can_move(random_direction):
                #             ct.move(random_direction)
