"""
COMP 8085 - Assignment 1 Example Template

Run:
    python assignment2-template.py

Please rename this template (i.e., at least take out the name "template" when you submit the file).

A good web site you can use to make tiles is at: https://www.pixilart.com/draw?ref=home-page

The images can easily be converted into text files.

"""

import sys
import pygame
from collections import deque
import heapq

########################################################################################################
## GLOBALS (Sssshhh, don't tell the Java programmers about this ;)
########################################################################################################

# Change this to your liking for how big you want this window on the screen
TILE_SIZE = 32

# We want the animation to be updated every one-tenth of a second (so 10 FPS). You can adjust this but if you make
# it too fast, you'll mist the visual representation of how the algorithms work
ANIMATION_DELAY_MS = 500

# These are the colors we define for the board
COLORS = {
    "#": (60, 100, 240),      # wall / boundary
    ".": (245, 245, 245),     # empty
    "E": (220, 40, 40),       # enemy
    "P": (40, 180, 80),       # health / power-up
    "G": (255, 230, 40),      # goal / treasure
    "S": (150, 95, 55),       # start / player
    "*": (120, 200, 255),     # visited
    "@": (255, 160, 40),      # final path
}

########################################################################################################
## DATA MODEL FUNCTION DECLARATIONS
########################################################################################################

def load_map(filename):
    grid = []

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.rstrip("\n")
            if line:
                grid.append(list(line))

    start = None
    goal = None

    # This is a bit of an error-check: make sure we have a start _and_ a finish/goal!
    for row_index, row in enumerate(grid):
        for col_index, value in enumerate(row):
            if value == "S":
                start = (row_index, col_index)
            elif value == "G":
                goal = (row_index, col_index)

    if start is None:
        raise ValueError("Map does not contain a start tile: S")

    if goal is None:
        raise ValueError("Map does not contain a goal tile: G")

    return grid, start, goal


def get_valid_moves(grid, position):
    row, col = position

    possible_moves = [
        (row - 1, col),  # up
        (row + 1, col),  # down
        (row, col - 1),  # left
        (row, col + 1),  # right
    ]

    valid_neighbors = []

    for next_row, next_col in possible_moves:
        if next_row < 0 or next_row >= len(grid):
            continue

        if next_col < 0 or next_col >= len(grid[0]):
            continue

        if grid[next_row][next_col] == "#":
            continue

        valid_neighbors.append((next_row, next_col))

    return valid_neighbors

########################################################################################################
## VISUALIZATION FUNCTION DECLARATIONS
########################################################################################################

def reconstruct_path(came_from, start, goal):
    if goal not in came_from:
        return []

    current = goal
    path = []

    while current != start:
        path.append(current)
        current = came_from[current]

    path.append(start)
    path.reverse()

    return path


def draw_map(screen, grid, player_position=None, visited=None, path=None):
    visited = visited or set()
    path = path or set()

    for row_index, row in enumerate(grid):
        for col_index, value in enumerate(row):
            position = (row_index, col_index)

            if position in path:
                color = COLORS["@"]
            elif position in visited and value not in ("S", "G"):
                color = COLORS["*"]
            else:
                color = COLORS.get(value, COLORS["."])

            rect = pygame.Rect(
                col_index * TILE_SIZE,
                row_index * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (210, 210, 210), rect, 1)

    if player_position:
        row, col = player_position

        rect = pygame.Rect(
            col * TILE_SIZE,
            row * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE
        )

        pygame.draw.rect(screen, COLORS["S"], rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)

########################################################################################################
## SEARCH ALGORITHM FUNCTION DECLARATIONS
########################################################################################################

## Breadth-First Search - as an example
def bfs(grid, start, goal):
    frontier = deque([start])
    visited = {start}
    came_from = {}

    animation_steps = []

    while frontier:
        current = frontier.popleft()

        animation_steps.append({
            "position": current,
            "visited": set(visited),
            "path": set()
        })

        if current == goal:
            break

        for neighbor in get_valid_moves(grid, current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                frontier.append(neighbor)

    path = reconstruct_path(came_from, start, goal)

    for position in path:
        animation_steps.append({
            "position": position,
            "visited": set(visited),
            "path": set(path)
        })

    # Print path length and number of explored states:
    print(f"Path length: {len(path)}")
    print(f"Explored states: {len(visited)}")

    return animation_steps

## Depth-First Search
def dfs(grid, start, goal):
    frontier = deque([start])
    visited = {start}
    came_from = {}

    animation_steps = []

    while frontier:
        current = frontier.pop()

        animation_steps.append({
            "position": current,
            "visited": set(visited),
            "path": set()
        })

        if current == goal:
            break

        # Could reverse()
        for neighbor in get_valid_moves(grid, current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                frontier.append(neighbor)

    path = reconstruct_path(came_from, start, goal)

    for position in path:
        animation_steps.append({
            "position": position,
            "visited": set(visited),
            "path": set(path)
        })

    # Print path length and number of explored states:
    print(f"Path length: {len(path)}")
    print(f"Explored states: {len(visited)}")

    return animation_steps

## Greedy Best-First Search
def greedy_search(grid, start, goal):
    frontier = []
    visited = {start}
    came_from = {}
    animation_steps = []

    heapq.heappush(frontier, (heuristic(start, goal), start))

    while frontier:
        _, current = heapq.heappop(frontier)
        
        animation_steps.append({
            "position": current,
            "visited": set(visited),
            "path": set()
        })

        if current == goal:
            break

        for neighbor in get_valid_moves(grid, current):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current

                priority = heuristic(neighbor, goal)
                heapq.heappush(frontier, (priority, neighbor))

    path = reconstruct_path(came_from, start, goal)

    for position in path:
        animation_steps.append({
            "position": position,
            "visited": set(visited),
            "path": set(path)
        })

    # Print path length and number of explored states:
    print(f"Path length: {len(path)}")
    print(f"Explored states: {len(visited)}")

    return animation_steps

## A-Star Search
def astar_search(grid, start, goal):
    frontier = []
    visited = set()
    came_from = {}
    g_score = {start: 0}
    animation_steps = []

    start_priority = heuristic(start, goal)
    heapq.heappush(frontier, (start_priority, 0, start))

    while frontier:
        _, current_cost, current = heapq.heappop(frontier)

        if current_cost != g_score[current]:
            continue

        if current in visited:
            continue

        visited.add(current)

        animation_steps.append({
            "position": current,
            "visited": set(visited),
            "path": set()
        })

        if current == goal:
            break

        for neighbor in get_valid_moves(grid, current):
            possible_g = g_score[current] + 1

            if possible_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = possible_g

                priority = possible_g + heuristic(neighbor, goal)
                heapq.heappush(frontier, (priority, possible_g, neighbor))

    path = reconstruct_path(came_from, start, goal)

    for position in path:
        animation_steps.append({
            "position": position,
            "visited": set(visited),
            "path": set(path)
        })
    
    # Print path length and number of explored states:
    print(f"Path length: {len(path)}")
    print(f"Explored states: {len(visited)}")

    return animation_steps

########################################################################################################
## HELPER FUNCTION DECLARATIONS
########################################################################################################

def choose_search_algorithm(name, grid, start, goal):
    # You can change this to a switch/match statement where you choose which function you want to call
    # ... or not. It's not really important for the assignment and learning outcomes.
    if name == "bfs":
        return bfs(grid, start, goal)
    elif name == "dfs":
        return dfs(grid, start, goal)
    elif name == "greedy":
        return greedy_search(grid, start, goal)
    elif name == "astar":
        return astar_search(grid, start, goal)

    raise ValueError(f"Unknown search algorithm: {name}")

# Helper used to find heuristic
def heuristic(current, goal):
    current_row, current_coll = current
    goal_row, goal_coll = goal

    heuristic_val = abs(goal_row - current_row) + abs(goal_coll - current_coll)

    return heuristic_val

########################################################################################################
## AND ..... RUN
########################################################################################################


def main():
    health = 100
    score = 0

    if len(sys.argv) < 2:
        print("Usage: python assignment2-template.py dungeon_map_1.txt")
        sys.exit(1)

    map_filename = sys.argv[1]
    algorithms = ("bfs", "dfs", "greedy", "astar")

    grid, start, goal = load_map(map_filename)

    # Let the user also select the algorihm to use
    while True:
        algorithm = input("Choose algorithm (bfs, dfs, greedy, astar): ").strip().lower()

        if algorithm in algorithms:
            break

        print("Invalid algorithm choice, please choose from: bfs, dfs, greedy, or astar.\n")
    
    animation_steps = choose_search_algorithm(algorithm, grid, start, goal)    

    # Some info to the user to let them know what keys to press
    print(f"Loaded map: {len(grid)} rows x {len(grid[0])} columns")
    print(f"Start: {start}")
    print(f"Goal: {goal}")
    print("Press 's' to start animation.")
    print("Press 'p' to pause animation.")
    print("Close the window to quit.")

    pygame.init()

    rows = len(grid)
    cols = len(grid[0])

    screen = pygame.display.set_mode(
        (cols * TILE_SIZE, rows * TILE_SIZE)
    )

    pygame.display.set_caption("COMP 8085 - Search Visualization")

    clock = pygame.time.Clock()

    current_step_index = 0
    is_running = False
    last_step_time = 0

    player_position = start
    visited = set()
    path = set()

    running = True

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    is_running = True

                elif event.key == pygame.K_p:
                    is_running = False

        # This is a rather crude way of updating, but for our purposes, it'll do - we don't need frame-precision
        if is_running and current_step_index < len(animation_steps):
            if current_time - last_step_time >= ANIMATION_DELAY_MS:
                step = animation_steps[current_step_index]

                player_position = step["position"]
                visited = step["visited"]
                path = step["path"]

                row, col = player_position
                tile = grid[row][col]

                if tile == "E":
                    health -= 25
                    print(f"Enemy encountered at ({row}, {col})")
                    print(f"Health: {health}")

                elif tile == "P":
                    health += 20
                    print(f"Health power-up collected at ({row}, {col})")
                    print(f"Health: {health}")

                elif tile == "G":
                    score += 100
                    print(f"Treasure reached! Score: {score}")

                current_step_index += 1
                last_step_time = current_time

        screen.fill((255, 255, 255))
        draw_map(screen, grid, player_position, visited, path)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
