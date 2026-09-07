from typing import Any
import sys


def parser(content: str) -> dict[str, Any]:
    config_dict: dict[str, Any] = {}
    lines = content.split('\n')

    for line in lines:
        if not line.strip():
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if key in ("WIDTH", "HEIGHT"):
            config_dict[key] = int(value)
        elif key in ("ENTRY", "EXIT"):
            config_dict[key] = tuple(int(coordinate) for coordinate in value.split(","))
        elif key == "PERFECT":
            config_dict[key] = value == "True"
        else:
            config_dict[key] = value

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
    



def main() -> None:
    filename: str

    try:
        filename = input_checker(sys.argv)
    except (ValueError, FileNotFoundError, PermissionError) as error:
        print(error, file=sys.stderr)
        return
    with open(filename, "r") as config_file_obj:
        configs = config_file_obj.read()
        config_dict = parser(configs)
        print(config_dict)
        

if __name__ == "__main__":
    main()