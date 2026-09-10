import os
os.system("clear")
from typing import Any
import sys
import ops

from mazegen.maze import Maze


def parser(content: str) -> dict[str, Any]:
    config_dict: dict[str, Any] = {}
    lines = content.split('\n')

    for line in lines:
        if not line.strip():
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        key = key.upper()

        if key in ("WIDTH", "HEIGHT"):
            try:
                config_dict[key] = int(value)
            except ValueError as error:
                raise ValueError(f"Configuration error: '{key}' must be a valid integer, but got '{value}'") from error
        elif key in ("ENTRY", "EXIT"):
            config_dict[key] = tuple(int(coordinate) for coordinate in value.split(","))
        elif key == "PERFECT":
            config_dict[key] = value.lower() == "true"
        elif key == "SEED":
            config_dict[key] = value or None
        else:
            config_dict[key] = value

    required_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT", "OUTPUT_FILE"]
    for key in required_keys:
        if key not in config_dict:
            raise ValueError(f"Configuration error: Missing required field '{key}' in config file.")

    return config_dict


def input_checker(argv: list[str]) -> str:
    if len(argv) != 2:
        raise ValueError("Invalid format! correct format: python3 a_maze_ing.py <config_filename>")

    filename: str = argv[1]
    try:
        with open(filename, "r"):
            pass
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Configuration file not found: {filename}") from error
    except PermissionError as error:
        raise PermissionError(f"Permission denied: {filename}") from error

    return filename


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


def main() -> None:
    filename: str

    try:
        if len(sys.argv) != 2:
            raise ValueError("Invalid format! correct format: python3 a_maze_ing.py <config_filename>")
        filename = input_checker(sys.argv)
    except (ValueError, FileNotFoundError, PermissionError) as error:
        print(error, file=sys.stderr)
        return

    with open(filename, "r") as config_file_obj:
        config_dict = parser(config_file_obj.read())

    maze = build_maze(config_dict)
    maze.generate()
    display_needed = True
    show_path = False

    while True:
        if display_needed:
            os.system("clear")
            print(f"seed used: {maze.seed!r}")
            print(maze.render_ascii(color_logo=True, show_path=show_path))
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
            display_needed = True
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please select 1-4.")
            try:
                input("Press Enter to continue...")
            except EOFError:
                pass
            display_needed = True

if __name__ == "__main__":
    main()
