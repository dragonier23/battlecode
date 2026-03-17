from cambc import Controller, Environment, Position, EntityType
from typing import List

class BuilderBot:
    def __init__(self):
        self.initialised = False

    def init(self, ct: Controller) -> None:
        """Intended to be called when the bot first spawns and run is called."""
        self.w = ct.get_map_width()
        self.h = ct.get_map_height()
        self.tile_env : List[List[Environment | None]] = [[None for _ in range(self.h)] for _ in range(self.w)]

        self.core_id = [ent for ent in ct.get_nearby_entities(2) if ct.get_entity_type(ent) == EntityType.CORE][0]
        self.core_pos = ct.get_position(self.core_id)

    def update_state(self, ct: Controller) -> None:
        """Intended to be called at the start of every turn to update the bot's state."""
        pos = ct.get_position()
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                x, y = pos.x + dx, pos.y + dy
                if 0 <= x < self.w and 0 <= y < self.h:
                    self.tile_env[x][y] = ct.get_tile_environment(Position(x, y))

    def run(self, ct: Controller) -> None:
        if not self.initialised:
            self.init(ct)
        self.update_state(ct)

    def get_direction(self, goal):
        pass

