from __future__ import annotations

import random

from mazegen.cell import Cell, NORTH, EAST, SOUTH, WEST, OPPOSITE, DELTA


class Maze:
    def __init__(
        self,
        width: int,
        height: int,
        entry_coords: tuple[int, int],
        exit_coords: tuple[int, int],
        output_filename: str,
        is_perfect_maze: bool,
        seed: int | str | None = None,
    ) -> None:
        if width < 3 or height < 3:
            raise ValueError("Maze must be at least 3x3 to stay structurally valid.")
        if entry_coords == exit_coords:
            raise ValueError("Entry and exit must be different cells.")
        for coords in (entry_coords, exit_coords):
            x, y = coords
            if not (0 <= x < width and 0 <= y < height):
                raise ValueError(f"Coordinates {coords} are outside the maze bounds.")
        if not self._is_on_border(entry_coords, width, height):
            raise ValueError("ENTRY must be on the external border of the maze.")
        if not self._is_on_border(exit_coords, width, height):
            raise ValueError("EXIT must be on the external border of the maze.")

        self.width = width
        self.height = height
        self.entry_coords = entry_coords
        self.exit_coords = exit_coords
        self.output_filename = output_filename
        self.is_perfect_maze = is_perfect_maze
        self.seed = seed

        self.rng = random.Random(seed)

        self.grid: list[list[Cell]] = [
            [Cell(x, y) for y in range(height)] for x in range(width)
        ]

    @staticmethod
    def _is_on_border(coords: tuple[int, int], width: int, height: int) -> bool:
        x, y = coords
        return x in (0, width - 1) or y in (0, height - 1)

    def cell(self, x: int, y: int) -> Cell:
        return self.grid[x][y]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def neighbor_coords(self, x: int, y: int, direction: str) -> tuple[int, int]:
        dx, dy = DELTA[direction]
        return x + dx, y + dy

    @staticmethod
    def _direction_between(a: tuple[int, int], b: tuple[int, int]) -> str:
        ax, ay = a
        bx, by = b
        delta = (bx - ax, by - ay)
        for direction, d in DELTA.items():
            if d == delta:
                return direction
        raise ValueError(f"{a} and {b} are not adjacent cells.")

    _GLYPH_4 = [
        [1, 0, 0, 1, 0],
        [1, 0, 0, 1, 0],
        [1, 0, 0, 1, 0],
        [1, 1, 1, 1, 1],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 1, 0],
    ]
    _GLYPH_2 = [
        [1, 1, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1],
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1],
    ]

    def _stamp_42_pattern(self) -> None:
        glyph_h = len(self._GLYPH_4)
        glyph_w = len(self._GLYPH_4[0])
        total_w = glyph_w * 2 + 1

        if self.width < total_w + 2 or self.height < glyph_h + 2:
            return

        start_x = (self.width - total_w) // 2
        start_y = (self.height - glyph_h) // 2

        for glyph, x_offset in ((self._GLYPH_4, 0), (self._GLYPH_2, glyph_w + 1)):
            for row_idx, row in enumerate(glyph):
                for col_idx, bit in enumerate(row):
                    if not bit:
                        continue
                    x, y = start_x + x_offset + col_idx, start_y + row_idx
                    if not self.in_bounds(x, y):
                        continue
                    if (x, y) in (self.entry_coords, self.exit_coords):
                        continue
                    cell = self.cell(x, y)
                    cell.is_stamped = True
                    cell.walls = {NORTH: True, EAST: True, SOUTH: True, WEST: True}

    def _edge_open(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        direction = self._direction_between((x1, y1), (x2, y2))
        return not self.cell(x1, y1).has_wall(direction)

    def _would_create_large_open_area(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        min_x, min_y = min(x1, x2), min(y1, y2)
        for top_x in range(min_x - 2, min_x + 1):
            for top_y in range(min_y - 2, min_y + 1):
                if self._block_would_be_fully_open(top_x, top_y, (x1, y1), (x2, y2)):
                    return True
        return False

    def _block_would_be_fully_open(
        self, top_x: int, top_y: int, pending_a: tuple[int, int], pending_b: tuple[int, int]
    ) -> bool:
        cells = [(top_x + dx, top_y + dy) for dy in range(3) for dx in range(3)]
        if not all(self.in_bounds(x, y) for x, y in cells):
            return False
        if any(self.cell(x, y).is_stamped for x, y in cells):
            return False

        def open_between(a: tuple[int, int], b: tuple[int, int]) -> bool:
            if (a, b) in ((pending_a, pending_b), (pending_b, pending_a)):
                return True
            return self._edge_open(*a, *b)

        for dy in range(3):
            for dx in range(2):
                a, b = (top_x + dx, top_y + dy), (top_x + dx + 1, top_y + dy)
                if not open_between(a, b):
                    return False
        for dy in range(2):
            for dx in range(3):
                a, b = (top_x + dx, top_y + dy), (top_x + dx, top_y + dy + 1)
                if not open_between(a, b):
                    return False
        return True

    def _carve(self, x1: int, y1: int, x2: int, y2: int) -> None:
        direction = self._direction_between((x1, y1), (x2, y2))
        self.cell(x1, y1).remove_wall(direction)
        self.cell(x2, y2).remove_wall(OPPOSITE[direction])

    def _usable_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        result = []
        for direction in (NORTH, EAST, SOUTH, WEST):
            nx, ny = self.neighbor_coords(x, y, direction)
            if self.in_bounds(nx, ny) and not self.cell(nx, ny).is_stamped:
                result.append((nx, ny))
        return result

    def _generate_spanning_tree(self) -> None:
        start = self.entry_coords
        if self.cell(*start).is_stamped:
            start = self._first_free_cell()

        stack = [start]
        self.cell(*start).visited = True

        while stack:
            x, y = stack[-1]
            candidates = [
                (nx, ny)
                for nx, ny in self._usable_neighbors(x, y)
                if not self.cell(nx, ny).visited
                and not self._would_create_large_open_area(x, y, nx, ny)
            ]
            if not candidates:
                stack.pop()
                continue
            nx, ny = self.rng.choice(candidates)
            self._carve(x, y, nx, ny)
            self.cell(nx, ny).visited = True
            stack.append((nx, ny))

    def _first_free_cell(self) -> tuple[int, int]:
        for x in range(self.width):
            for y in range(self.height):
                if not self.cell(x, y).is_stamped:
                    return (x, y)
        raise RuntimeError("No free cell available to start generation.")

    def _apply_border(self) -> None:
        for x in range(self.width):
            for y in range(self.height):
                cell = self.cell(x, y)
                if y == 0:
                    cell.add_wall(NORTH)
                if y == self.height - 1:
                    cell.add_wall(SOUTH)
                if x == 0:
                    cell.add_wall(WEST)
                if x == self.width - 1:
                    cell.add_wall(EAST)

    def _all_internal_edges(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        edges = []
        for x in range(self.width):
            for y in range(self.height):
                if self.cell(x, y).is_stamped:
                    continue
                for direction in (EAST, SOUTH):
                    nx, ny = self.neighbor_coords(x, y, direction)
                    if self.in_bounds(nx, ny) and not self.cell(nx, ny).is_stamped:
                        edges.append(((x, y), (nx, ny)))
        return edges

    def _open_corners_and_centre(self) -> None:
        targets = [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
            (self.width // 2, self.height // 2),
        ]
        for (x, y) in targets:
            if self.cell(x, y).is_stamped:
                continue
            if self.cell(x, y).wall_count() == 4:
                neighbors = self._usable_neighbors(x, y)
                self.rng.shuffle(neighbors)
                for nx, ny in neighbors:
                    if not self._would_create_large_open_area(x, y, nx, ny):
                        self._carve(x, y, nx, ny)
                        break

    def _add_loops(self, loop_count: int) -> None:
        edges = self._all_internal_edges()
        self.rng.shuffle(edges)
        added = 0
        for (x1, y1), (x2, y2) in edges:
            if added >= loop_count:
                break
            if self._edge_open(x1, y1, x2, y2):
                continue
            if self._would_create_large_open_area(x1, y1, x2, y2):
                continue
            self._carve(x1, y1, x2, y2)
            added += 1

    def _reduce_dead_ends(self, max_passes: int = 2) -> None:
        for _ in range(max_passes):
            dead_ends = [
                (x, y)
                for x in range(self.width)
                for y in range(self.height)
                if self.cell(x, y).is_dead_end()
            ]
            self.rng.shuffle(dead_ends)
            for (x, y) in dead_ends:
                candidates = [
                    (nx, ny)
                    for nx, ny in self._usable_neighbors(x, y)
                    if not self._edge_open(x, y, nx, ny)
                    and not self._would_create_large_open_area(x, y, nx, ny)
                ]
                if candidates:
                    nx, ny = self.rng.choice(candidates)
                    self._carve(x, y, nx, ny)

    def generate(self) -> None:
        self._stamp_42_pattern()
        self._generate_spanning_tree()

        if not self.is_perfect_maze:
            self._open_corners_and_centre()
            loop_target = max(2, (self.width * self.height) // 25)
            self._add_loops(loop_target)
            self._reduce_dead_ends()

        self._apply_border()

    def render_ascii(self, color_logo: bool = False) -> str:
        red = "\033[31m"
        reset = "\033[0m"

        def color_token(token: str, should_color: bool) -> str:
            return red + token + reset if color_logo and should_color else token

        lines = []
        for y in range(self.height):
            top = ""
            side = ""
            for x in range(self.width):
                cell = self.cell(x, y)
                above_stamped = y > 0 and self.cell(x, y - 1).is_stamped
                left_stamped = x > 0 and self.cell(x - 1, y).is_stamped
                corner_stamped = cell.is_stamped or above_stamped or left_stamped
                if x > 0:
                    corner_stamped = corner_stamped or self.cell(x - 1, y - 1 if y > 0 else y).is_stamped
                top += color_token("+", corner_stamped)
                top += color_token("--" if cell.has_wall(NORTH) else "  ", cell.is_stamped or above_stamped)

                marker = "S" if (x, y) == self.entry_coords else "E" if (x, y) == self.exit_coords else " "
                side += color_token(
                    ("|" if cell.has_wall(WEST) else " ") + marker + " ",
                    cell.is_stamped or left_stamped,
                )
            last_above_stamped = y > 0 and self.cell(self.width - 1, y - 1).is_stamped
            lines.append(top + color_token("+", self.cell(self.width - 1, y).is_stamped or last_above_stamped))
            last_cell = self.cell(self.width - 1, y)
            east_wall = color_token(
                "|" if last_cell.has_wall(EAST) else " ",
                last_cell.is_stamped,
            )
            lines.append(side + east_wall)
        bottom = "".join(
            color_token("+", self.cell(x, self.height - 1).is_stamped or (x > 0 and self.cell(x - 1, self.height - 1).is_stamped))
            + color_token("--" if self.cell(x, self.height - 1).has_wall(SOUTH) else "  ", self.cell(x, self.height - 1).is_stamped)
            for x in range(self.width)
        )
        lines.append(bottom + color_token("+", self.cell(self.width - 1, self.height - 1).is_stamped))
        return "\n".join(lines)

    def _cell_hex_code(self, x: int, y: int) -> str:
        cell = self.cell(x, y)
        value = 0
        if cell.has_wall(NORTH):
            value |= 1 << 0
        if cell.has_wall(EAST):
            value |= 1 << 1
        if cell.has_wall(SOUTH):
            value |= 1 << 2
        if cell.has_wall(WEST):
            value |= 1 << 3
        return format(value, "X")

    def write_to_file(self) -> None:
        rows = [
            "".join(self._cell_hex_code(x, y) for x in range(self.width))
            for y in range(self.height)
        ]

        entry_line = f"{self.entry_coords[0]}, {self.entry_coords[1]}"
        exit_line = f"{self.exit_coords[0]}, {self.exit_coords[1]}"

        content = "\n".join(rows)
        content += "\n\n"
        content += f"{entry_line}\n"
        content += f"{exit_line}\n"

        with open(self.output_filename, "w") as file_obj:
            file_obj.write(content)