# I got a bad feeling this file is going to become very not temporary

def points_within_distance(currPos, distance):
    points = []
    for x in range(-distance, distance + 1):
        for y in range(-distance, distance + 1):
            if x**2 + y**2 <= distance**2:
                points.append((currPos[0] + x, currPos[1] + y))
    return points