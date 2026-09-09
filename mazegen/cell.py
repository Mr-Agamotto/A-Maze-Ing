from dataclasses import dataclass, field

NORTH, EAST, SOUTH, WEST = "N", "E", "S", "W"

OPPOSITE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
DELTA = {NORTH: (0, -1), SOUTH: (0, 1), EAST: (1, 0), WEST: (-1, 0)}


@dataclass
class Cell:
    x: int
    y: int
    walls: dict[str, bool] = field(
        default_factory=lambda: {NORTH: True, EAST: True, SOUTH: True, WEST: True}
    )
    visited: bool = False
    is_stamped: bool = False

    def has_wall(self, direction: str) -> bool:
        return self.walls[direction]

    def remove_wall(self, direction: str) -> None:
        self.walls[direction] = False

    def add_wall(self, direction: str) -> None:
        self.walls[direction] = True

    def wall_count(self) -> int:
        return sum(self.walls.values())

    def is_fully_closed(self) -> bool:
        return all(self.walls.values())

    def is_dead_end(self) -> bool:
        return not self.is_stamped and self.wall_count() == 3