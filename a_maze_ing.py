from typing import Any





def parser(content: str) -> dict[str, Any]:
    lines: list[str]
    key_and_value: list[str]

    config_dict: dict[str, Any] = {}

    lines = content.split('\n')

    for line in lines:
        key_and_value = line.split("=")
        key = key_and_value[0]
        value = key_and_value[1]
        if key in ("WIDTH", "HEIGHT"):
            config_dict[key] = int(value)
        elif key in ("ENTRY", "EXIT"):
            config_dict[key] = tuple(int(coordinate) for coordinate in value.split(","))
        elif key == "PERFECT":
            config_dict[key] = value == "True"
        else:
            config_dict[key] = value

    return config_dict





def main() -> None:
    with open("config.txt", "r") as config_file_obj:
        configs = config_file_obj.read()
        config_dict = parser(configs)
        

if __name__ == "__main__":
    main()