"""Starter bot - a simple example to demonstrate usage of the Controller API.

Each unit gets its own Player instance; the engine calls run() once per round.
Use Controller.get_entity_type() to branch on what kind of unit you are.

This bot:
  - Core: spawns up to 3 builder bots on random adjacent tiles
  - Builder bot: builds a harvester on any adjacent ore tile, then moves in a
    random direction (laying a road first so the tile is passable), and places
    a marker recording the current round number
"""

import random

from cambc import Controller, Direction, EntityType, Environment, Position

# non-centre directions
DIRECTIONS = [Direction.NORTH, Direction.EAST, Direction.WEST, Direction.SOUTH]

class Player:
    def __init__(self):
        self.player = None
    def run(self, ct: Controller) -> None:
        if self.player == None: 
            etype = ct.get_entity_type()
            if etype == EntityType.CORE:
                self.player = Core()
            elif etype == EntityType.BUILDER_BOT:
                self.player = BuilderBot()
        self.player.run(ct)
            
class Core:
    def __init__(self):
        self.num_spawned = 0
    def run(self, ct: Controller) -> None:
        if self.num_spawned < 5:
            # if we haven't spawned 3 builder bots yet, try to spawn one on a random tile
            spawn_pos = ct.get_position().add(random.choice(DIRECTIONS))
            if ct.can_spawn(spawn_pos):
                ct.spawn_builder(spawn_pos)
                self.num_spawned += 1

class BuilderBot:
    def __init__(self):
        self.path = []
        self.state = 0
    def run(self, ct: Controller) -> None:
        if self.state == 0:
            if self.path == []:
                self.path.append(ct.get_position())
            for d in DIRECTIONS:
                check_pos = ct.get_position().add(d)
                if ct.can_build_harvester(check_pos):
                    ct.build_harvester(check_pos)
                    self.state = 1
                    break
            

            move_dir = DIRECTIONS
            move_pos = [ct.get_position().add(d) for d in move_dir]
            move_pos_no_overlap = [x for x in move_pos if x not in self.path]
            dest: Position = None
            if len(move_pos_no_overlap) > 0: 
                # there is some move to new square
                dest = random.choice(move_pos_no_overlap)

            else:
                dest = random.choice(move_pos)
                self.path = self.path[0: self.path.index(dest)]
            
            dir: Direction = None
            dir = ct.get_position().direction_to(dest)
            
            if ct.can_build_road(dest):
                ct.build_road(dest)
            if ct.can_move(dir):
                ct.move(dir)
                self.path.append(dest)

        elif self.state == 1:
            self.path.pop()
            # build bridge
            dir = ct.get_position().direction_to(self.path[-1])
            ct.destroy(ct.get_position())
            ct.build_bridge(ct.get_position(), self.path[-1])
            ct.move(dir)
            self.state = 2

        elif self.state == 2:
            self.path.pop()
            if len(self.path) == 0: 
                self.state = 3
                return
            dir = ct.get_position().direction_to(self.path[-1])
            if ct.can_destroy(ct.get_position()):
                ct.destroy(ct.get_position())
            ct.build_conveyor(ct.get_position(), dir)
            ct.move(dir)
            
        elif self.state == 3:
            #finish
            pass

