from __future__ import annotations
from typing import List
from cambc import Direction, Position
from dataclasses import dataclass
from pathfinder import PathFinder

@dataclass(frozen=True)
class Init:
    tag = "init"

@dataclass(frozen=True)
class Explore:
    tag = "explore"
    turns_left : int = 5
    direction : Direction = Direction.CENTRE

@dataclass(frozen=True)
class MoveTo:
    """Moving to or near a specific position. Once reached, will transition to next_state."""
    tag = "move_to"
    path_finder : PathFinder
    next_state : BotState

@dataclass(frozen=True)
class Patrol:
    tag = "patrol"

@dataclass(frozen=True)
class Harvest:
    tag = "harvest"
    resource_pos : Position
    
@dataclass(frozen=True)
class Convey:
    tag = "convey"
    path_finder : PathFinder | None

@dataclass(frozen=True)
class ConveyBuildConveyor:
    tag = "convey2"
    build_pos : Position
    next_state : BotState

@dataclass(frozen=True)
class BridgeConvey:
    tag = "bridge_convey"
    path_finder : PathFinder | None

@dataclass(frozen=True)
class BridgeConveyBuildBridge:
    tag = "bridge_convey_build_bridge"
    build_pos : Position
    next_state : BotState

BotState = Init | Explore | MoveTo | Patrol | Convey | Harvest | ConveyBuildConveyor | BridgeConvey | BridgeConveyBuildBridge