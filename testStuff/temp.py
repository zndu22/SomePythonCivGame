import pygame
from queue import PriorityQueue
# I got a bad feeling this file is going to become very not temporary

def points_within_distance(currPos, distance):
    points = []
    for x in range(-distance, distance + 1):
        for y in range(-distance, distance + 1):
            if abs(x) + abs(y) <= distance:  # Use Manhattan distance instead of Euclidean
                points.append((currPos[0] + x, currPos[1] + y))
    return points

def addTuples(a, b):
    return tuple(max(min(255, a + b), 0) for a, b in zip(a, b))

def Render_Text(window, what, color, where):
    font = pygame.font.Font('graphics/Roboto-Italic-VariableFont_wdth,wght.ttf', 12)
    text = font.render(what, 1, pygame.Color(color), (0, 0, 0))
    window.blit(text, where)

def lerp(start, end, t):
    return start + t * (end - start)

def a_star_pathfinding(start, goal, img, unit):
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: abs(start[0] - goal[0]) + abs(start[1] - goal[1])}

    iteration_count = 0

    while not open_set.empty():
        iteration_count += 1
        if iteration_count > 10000:  # Arbitrary limit to prevent infinite loops
            print(f"A* failed: Too many iterations from {start} to {goal}")
            return None

        _, current = open_set.get()

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        neighbors = points_within_distance(current, 1)  # Get adjacent tiles
        for neighbor in neighbors:
            if not (0 <= neighbor[0] < img.width and 0 <= neighbor[1] < img.height):
                continue
            if not unit.isTileValid(img, neighbor):  # Check if the tile is valid
                continue

            tentative_g_score = g_score[current] + 1
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + abs(neighbor[0] - goal[0]) + abs(neighbor[1] - goal[1])
                open_set.put((f_score[neighbor], neighbor))

    return None  # No path found

def distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5