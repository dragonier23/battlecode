from enum import Enum
from cambc import Environment, EntityType, Team, Direction

class BuilderState(Enum): 
    __slot__ = ()

    SEARCHING = "search"    
    CONVEY = "convey"

class BuildingState: 
    def __init__(self, type: EntityType, direction: Direction): 
        self.type = type 
        self.direction = direction
class TileState: 
    '''
    record the state of a particular tile: 
    Should record the type Environment state - Empty, Wall, Ore type
    if it is empty, it could contain something - what entity is in it, or is it empty
    we want to also record if it is friendly or not 
    we want to record if it is a weapon, some stats
    we want to record if its a converyer, the direction 
    '''
    def __init__(self, team: Team, env: Environment , building: BuildingState): 
        self.team = team 
        self.env = env