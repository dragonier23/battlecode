from enum import Enum
from cambc import Environment, EntityType, Team, Direction

class DirectedBuildings(Enum): 
    __slot__ = () 

    GUNNER = "gunner"
    SENTINEL = "sentinel"
    BREACH = "breach"
    LAUNCHER = "launcher"
    CONVEYOR = "conveyor"
    SPLITTER = "splitter"
    ARMOURED_CONVEYOR = "armoured_conveyor"
    BRIDGE = "bridge"

class BuilderState(Enum): 
    __slot__ = ()

    SEARCHING = "search"    
    CONVEY = "convey"

class BuildingState: 
    def __init__(self, type: EntityType, direction: Direction, bot: bool = False): 
        self.type = type 
        self.direction = direction
        self.bot = bot

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
    def __init__(self, env: Environment, team: Team = None, building: BuildingState = None, marker: MarkerState = None): 
        self.team = team 
        self.env = env
        self.building = building
        self.marker = marker