from __future__ import annotations
from typing import List
from cambc import Direction, Position
from dataclasses import dataclass

@dataclass(frozen=True)
class Idle:
    tag = "idle"

@dataclass(frozen=True)
class Wander:
    tag = "wander"
    turns_left : int = 5
    direction : Direction = Direction.CENTRE

@dataclass(frozen=True)
class MoveTo:
    """Moving to or near a specific position. Once reached, will transition to next_state."""
    tag = "move_to"
    position : Position
    r2 : int = 0 # radius to be within of the position
    next_state : BotState = Idle()

@dataclass(frozen=True)
class Patrol:
    tag = "patrol"

@dataclass(frozen=True)
class Convey:
    tag = "convey"
    path : List[Position] | None = None


BotState = Idle | Wander | MoveTo | Patrol | Convey