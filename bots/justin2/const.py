from enum import Enum
from cambc import Environment, EntityType, Team, Direction

BUILDER_BOT_ACTION_RADIUS_SQUARED = 2

ORTHOGONAL_DIRS = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]

PATHABLE = [None, EntityType.ARMOURED_CONVEYOR, EntityType.BUILDER_BOT, EntityType.CONVEYOR, EntityType.ROAD, EntityType.SPLITTER, EntityType.BRIDGE]
PASSABLE = [None, EntityType.ARMOURED_CONVEYOR, EntityType.CONVEYOR, EntityType.ROAD, EntityType.CORE, EntityType.BRIDGE] # Should also be able to path through an allied core, but avoided for simplicity now o (allowed now)

Quadrant = { 
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

Target = { 
    Direction.NORTHWEST: Direction.SOUTHEAST, 
    Direction.NORTHEAST: Direction.SOUTHWEST, 
    Direction.NORTH: Direction.SOUTH, 
    Direction.WEST: Direction.EAST, 
    Direction.EAST: Direction.WEST, 
    Direction.SOUTHWEST: Direction.NORTHEAST, 
    Direction.SOUTH: Direction.NORTH, 
    Direction.SOUTHEAST: Direction.NORTHWEST, 
}

class DirectedBuildings(Enum): 
    __slot__ = () 

    GUNNER = "gunner"
    SENTINEL = "sentinel"
    BREACH = "breach"
    LAUNCHER = "launcher"
    CONVEYOR = "conveyor"
    SPLITTER = "splitter"
    ARMOURED_CONVEYOR = "armoured_conveyor"

class BuilderState(Enum): 
    __slot__ = ()

    SEARCHING = "search"    
    CONVEY = "convey"

class BuildingState: 
    def __init__(self, type: EntityType, direction: Direction): 
        self.type = type 
        self.direction = direction

class MarkerState: 
    def __init__(self, message): 
        self.message = message

class TileState: 
    '''
    Records the state of a particular tile: 
    Team: the team the tile belongs to 
    Environment: Empty, Wall, Ore type
    Building: Contains the object type and the direction it is facing. 
    '''
    def __init__(self, 
                 env: Environment | None = None,
                 team: Team | None = None,
                 building: BuildingState | None = None,
                 marker: MarkerState | None = None,
                 bot: bool = False): 
        self.team = team 
        self.env = env
        self.building = building
        self.marker = marker
        self.bot = bot