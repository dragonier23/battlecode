from enum import Enum

class BuilderState(Enum): 
    __slot__ = ()

    SEARCHING = "search"    
    CONVEY = "convey"
    