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
from const import BuilderState

# non-centre directions
DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]

QUANDRANT = { 
    0: { 
        0: Direction.NORTHWEST,
        1: Direction.NORTH,
        2: Direction.NORTHEAST, 
    },
    1: { 
        0: Direction.WEST,
        1: Direction.CENTRE,
        2: Direction.EAST, 
    },
    2: { 
        0: Direction.SOUTHWEST,
        1: Direction.SOUTH,
        2: Direction.SOUTHEAST, 
    }
}

TARGET = { 
    Direction.NORTHWEST: Direction.SOUTHEAST, 
    Direction.NORTHEAST: Direction.SOUTHWEST, 
    Direction.NORTH: Direction.SOUTH, 
    Direction.WEST: Direction.EAST, 
    Direction.EAST: Direction.WEST, 
    Direction.SOUTHWEST: Direction.NORTHEAST, 
    Direction.SOUTH: Direction.NORTH, 
    Direction.SOUTHEAST: Direction.NORTHWEST, 
}

class Player:
    def __init__(self):
        self.num_spawned = 0 # number of builder bots spawned so far (core)

    def run(self, ct: Controller) -> None:
        etype = ct.get_entity_type()
        if etype == EntityType.CORE:
            if self.num_spawned < 5:
                # if we haven't spawned 3 builder bots yet, try to spawn one on a random tile
                spawn_pos = ct.get_position().add(random.choice(DIRECTIONS))
                if ct.can_spawn(spawn_pos):
                    ct.spawn_builder(spawn_pos)
                    self.num_spawned += 1
                    
        elif etype == EntityType.BUILDER_BOT:
            # if we are adjacent to an ore tile, build a harvester on it
            for d in Direction:
                check_pos = ct.get_position().add(d)
                if ct.can_build_harvester(check_pos):
                    ct.build_harvester(check_pos)
                    break
            
            # move in a random direction
            move_dir = random.choice(DIRECTIONS)
            move_pos = ct.get_position().add(move_dir)
            # we need to place a conveyor or road to stand on, before we can move onto a tile
            if ct.can_build_road(move_pos):
                ct.build_road(move_pos)
            if ct.can_move(move_dir):
                ct.move(move_dir)

            # place a marker on an adjacent tile with the current round number
            marker_pos = ct.get_position().add(random.choice(DIRECTIONS))
            if ct.can_place_marker(marker_pos):
                ct.place_marker(marker_pos, ct.get_current_round())


class Builder: 
    def __init__(self, ct: Controller): 
        self.core = [ct.get_position(id) for id in ct.get_nearby_buildings(1) if ct.get_entity_type(id) == EntityType.CORE][0]
        self.stage = BuilderState.SEARCHING

        self.height = ct.get_map_height
        self.width = ct.get_map_width
        self.core_quad = QUANDRANT[self.core.x % (self.width // 3)][self.core.y % (self.height // 3)]
        self.target = TARGET[self.core_quad]

        self.direction = Direction.NORTH

        self.grid = [dict() ]


    def run(self, ct: Controller): 
        markers = self.read_markers()


    def 


    def read_markers(self, ct: Controller): 
        return [(ct.get_marker_value(id), ct.get_position(id)) for id in ct.get_nearby_entities() if ct.get_entity_type(id) == EntityType.MARKER]
        

    