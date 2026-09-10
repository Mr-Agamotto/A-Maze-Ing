import os


def menu() -> str:
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show / Hide the shortest path")
    print("3. Rotate the wall colours")
    print("4. Quit")
    return input("Choice? (1-4): ").strip()
