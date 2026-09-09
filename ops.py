import os

def menu():
    print("=== A-Maze-ing ===")
    print("1. Re-generate a new maze")
    print("2. Show / Hide all the shortest path")
   print("3. Rotate the wall colours")
    print("4. Quit")
    option = input("Choice? (1-4): ")
    if option == "1":
      os.system("clear")
      os.system("python3 a_maze_ing.py config.txt")
    if option == "4":
        os.system("clear")
