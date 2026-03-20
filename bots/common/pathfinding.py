from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from typing import Callable, Deque, Iterable

from cambc import Controller, Direction, Position

from memory import Memory
from const import TileState
from utils import is_in_bounds


class SearchInterface(ABC):

	@abstractmethod
	def search(
		self,
		ct: Controller,
		memory: Memory,
		start: Position,
		target: Position,
	) -> Deque[tuple[Position, Direction]] | None:
		"""Return the first move from start toward target, or None if no path exists."""


class BFS(SearchInterface):
	def __init__(self, directions: Iterable[Direction], traversable: Callable[[TileState], bool] | None = None):
		self.directions = directions	
		self.traverable = traversable

	def search(self, ct: Controller, memory: Memory, start: Position, target: list[Position]) -> Deque[tuple[Position, Direction]] | None:
		"""
        Return the shortest path from start to some set of target positions. 
		
        """
		q = deque([start])

        # marked is a dictionary mapping some node to the tuple containing its previous node, and the direction from that previous node moved to get to the key node
		marked: dict[Position, tuple[Position, Direction]] = {start: (None, None)}

		while q: 
			c = q.popleft()
			if c in target:
				res = deque([(c, None)])
				while c != start: 
					res.appendleft(marked[c])
					c = marked[c][0]
				return res                 

			for d in self.directions:
				neighbour = c.add(d)
                
				if neighbour not in marked and is_in_bounds(neighbour, ct): 
					tile = memory.grid[neighbour.x][neighbour.y]
					if self.traverable(tile):
						marked[neighbour] = (c, d)
						q.append(neighbour)
