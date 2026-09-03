from typing import tuple
import random

class Maze:
    def __init__(
                 self,
                 width: int,
                 height: int,
                 entry_coords: tuple[int],
                 exit_coords: tuple[int],
                 output_filename: str,
                 is_perfect_maze: bool
                 ) -> None:
        self.width = width
        self.height = height
        self.entry_coords = entry_coords
        self.exit_coords = exit_coords
        self.output_filename = output_filename
        self.is_perfect_maze = is_perfect_maze








random.seed("hello")