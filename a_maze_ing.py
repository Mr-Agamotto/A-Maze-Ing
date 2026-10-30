import os
from typing import Any
import sys
import ops

from mazegen.maze import Maze


def parser(content: str) -> dict[str, Any]:
    config_dict: dict[str, Any] = {}
    lines = content.split('\n')

    for line_number, line in enumerate(lines, start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Configuration error on line {line_number}: expected KEY=VALUE.")
        key, value = (part.strip() for part in line.split("=", 1))
        key = key.upper()
        if not key:
            raise ValueError(f"Configuration error on line {line_number}: missing key.")
        if key in config_dict:
            raise ValueError(f"Configuration error on line {line_number}: duplicate key '{key}'.")

        if key in ("WIDTH", "HEIGHT"):
            try:
                config_dict[key] = int(value)
            except ValueError as error:
                raise ValueError(f"Configuration error: '{key}' must be a valid integer, but got '{value}'") from error
        elif key in ("ENTRY", "EXIT"):
            coordinates = value.split(",")
            if len(coordinates) != 2:
                raise ValueError(f"Configuration error: '{key}' must be two coordinates in x,y format.")
            try:
                config_dict[key] = tuple(int(coordinate.strip()) for coordinate in coordinates)
            except ValueError as error:
                raise ValueError(f"Configuration error: '{key}' must contain two valid integers.") from error
        elif key == "PERFECT":
            if value.lower() not in ("true", "false"):
                raise ValueError("Configuration error: 'PERFECT' must be True or False.")
            config_dict[key] = value.lower() == "true"
        elif key == "SEED":
            config_dict[key] = value or None
        else:
            config_dict[key] = value

    required_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT", "OUTPUT_FILE"]
    for key in required_keys:
        if key not in config_dict:
            raise ValueError(f"Configuration error: Missing required field '{key}' in config file.")
    if config_dict["WIDTH"] * config_dict["HEIGHT"] > 50000:
        raise ValueError("Configuration error: maze cannot exceed 50000 cells.")
    if not config_dict["OUTPUT_FILE"]:
        raise ValueError("Configuration error: 'OUTPUT_FILE' cannot be empty.")

    return config_dict


def input_checker(argv: list[str]) -> str:
    if len(argv) != 2:
        raise ValueError("Invalid format! correct format: python3 a_maze_ing.py <config_filename>")

    return argv[1]


def build_maze(config_dict: dict[str, Any]) -> Maze:
    return Maze(
        width=config_dict["WIDTH"],
        height=config_dict["HEIGHT"],
        entry_coords=tuple(config_dict["ENTRY"]),
        exit_coords=tuple(config_dict["EXIT"]),
        output_filename=config_dict.get("OUTPUT_FILE", "maze_output.txt"),
        is_perfect_maze=config_dict.get("PERFECT", False),
        seed=config_dict.get("SEED"),
    )


def main() -> int:
    try:
        filename = input_checker(sys.argv)
        with open(filename, "r", encoding="utf-8") as config_file_obj:
            config_dict = parser(config_file_obj.read())

        maze = build_maze(config_dict)
        maze.generate()
        display_needed = True
        show_path = False
        wall_color_index = 0

        while True:
            if display_needed:
                os.system("clear")
                if maze.logo_notice:
                    print(maze.logo_notice)
                print(f"seed used: {maze.seed!r}")
                print(maze.render_ascii(color_logo=True, show_path=show_path, wall_color_index=wall_color_index))
                maze.write_to_file()
                display_needed = False

            choice = ops.menu()
            if choice == "1":
                maze = build_maze(config_dict)
                maze.generate()
                show_path = False
                display_needed = True
            elif choice == "2":
                show_path = not show_path
                display_needed = True
            elif choice == "3":
                wall_color_index = (wall_color_index + 1) % 3
                display_needed = True
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please select 1-4.")
                input("Press Enter to continue...")
    except (ValueError, OSError, UnicodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except EOFError:
        print("\nInput closed. Exiting.")
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
