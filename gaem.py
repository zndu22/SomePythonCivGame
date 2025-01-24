from PIL import Image
import opensimplex
import pygame
from Unit import Unit, Ship
from constants import *
import random
from testStuff.temp import points_within_distance

# ------- setup ---------
pygame.init()
opensimplex.random_seed()
pygame.mouse.set_visible(False)
running = True
selected = -1 # -1 means nothing's selected
leftMouseDown = False
rightMouseDown = False
cursorPosSS = [0, 0] # [0] is x and [1] is y
cursorPos = [0, 0] # same ^
camPos = [0, 0] # in pixel space
units = []

selectedTeam = 0 # ! temporary variable, replace with GUI eventually, please

# ------ worldgen --------
img = Image.new("RGB", (60,60), (0,0,255))
for y in range(img.height):
    for x in range(img.width):
        height = int((opensimplex.noise2(x/20, y/20) + 
                      opensimplex.noise2(x/5,y/5) + 
                      opensimplex.noise2(x/3,y/3)) * 255)
        if height > 245:
            img.putpixel((x, y), mountainColor)
        elif height > 1:
            img.putpixel((x, y), grassColor)
        else:
            img.putpixel((x, y), waterColor)

# ------- game -----------
screen = pygame.display.set_mode((800, 500))

print(str(units))

while running:
    pygame.display.set_caption(f"{str(cursorPos)} , {selected}, {str(units)}, {camPos}, {selectedTeam}")
    screen.fill((0, 0, 0))

    # draw the map
    for y in range(img.height):
        for x in range(img.width):
            # TODO: add a border system
            # * have a texture with colors for each team
            # if img.getpixel((x, y)) == grassColor:
            #     if (img.getpixel((min(x+1, img.width-1), y)) == waterColor 
            #     or img.getpixel((x, min(y+1, img.height-1))) == waterColor
            #     or img.getpixel((max(x-1, 0), y)) == waterColor 
            #     or img.getpixel((x, max(y-1, 0))) == waterColor 
            #     or img.getpixel((min(x+1, img.width-1), min(y+1, img.height-1))) == waterColor
            #     or img.getpixel((max(x-1, 0), max(y-1, 0))) == waterColor):
            #         pygame.draw.rect(screen, (255, 255, 255), (camPos[0] + x*20-1, camPos[1] + y*20-1, 22, 22))

            if img.getpixel((x, y)) == grassColor:
                screen.blit(grass, (camPos[0] + x*20+1, camPos[1] + y*20+1))
            elif img.getpixel((x, y)) == mountainColor:
                screen.blit(mountain, (camPos[0] + x*20+1, camPos[1] + y*20+1))
            else:
                screen.blit(water, (camPos[0] + x*20+1, camPos[1] + y*20+1))

            if (selected >= 0 and abs(units[selected].position[0] - x) <= units[selected].moveDist 
                              and abs(units[selected].position[1] - y) <= units[selected].moveDist
                              and units[selected].is_path_valid([x, y], img)):
                if any(u.position == [x, y] for u in units):
                    target_unit = next((u for u in units if u.position == [x, y]), None)
                    if target_unit and units[selected].team != target_unit.team:
                        screen.blit(redSquareThing, (camPos[0] + x*20+1, camPos[1] + y*20+1))
                    continue
                screen.blit(blueSquareThing, (camPos[0] + x*20+1, camPos[1] + y*20+1))
    
    # draw the units
    for i in units:
        screen.blit(i.image, (camPos[0] + i.position[0]*20+1, camPos[1] + i.position[1]*20+1))
        if cursorPos == i.position and i.health < i.maxHealth:
            pygame.draw.rect(screen, "black", (camPos[0] + i.position[0]*20+4, camPos[1] + i.position[1]*20+7, 12, 8))
            pygame.draw.rect(screen, "red", (camPos[0] + i.position[0]*20+5, camPos[1] + i.position[1]*20+8, 10, 6))
            pygame.draw.rect(screen, "green", (camPos[0] + i.position[0]*20+5, camPos[1] + i.position[1]*20+8, 10 * (i.health/i.maxHealth), 6))
        if not i.movedThisTurn and i.team == 0:
            screen.blit(exclamationMark, (camPos[0] + i.position[0]*20+1, camPos[1] + i.position[1]*20+1))
    
    # update input variables
    cursorPosSS = [int(pygame.mouse.get_pos()[0]/20), int(pygame.mouse.get_pos()[1]/20)]
    cursorPos = [cursorPosSS[0] - int((camPos[0])//20), cursorPosSS[1] - int((camPos[1])//20)]
    leftMouseDown = pygame.mouse.get_pressed()[0]
    rightMouseDown = pygame.mouse.get_pressed()[2]

    # handle input
    if leftMouseDown:
        for i, u in enumerate(units):
            if cursorPos == u.position and u.movedThisTurn == False and u.team == 0:
                selected = i
    if rightMouseDown and selected >= 0:
        if (abs(units[selected].position[0] - cursorPos[0]) <= units[selected].moveDist 
            and abs(units[selected].position[1] - cursorPos[1]) <= units[selected].moveDist 
            and units[selected].is_path_valid(cursorPos, img)):
            if any(u.position == cursorPos for u in units):
                target_unit = next((u for u in units if u.position == cursorPos), None)
                if target_unit and units[selected].team != target_unit.team:
                    target_unit.health -= units[selected].attack
                    if target_unit.health <= 0:
                        selected -= 1 if selected > units.index(target_unit) else 0
                        units.remove(target_unit)
            else:
                units[selected].position = cursorPos
            units[selected].movedThisTurn = True
            selected = -1
    
    # move the camera
    pressed = pygame.key.get_pressed()
    moveSpeed = 5 if pressed[pygame.K_LSHIFT] else 1
    if pressed[pygame.K_w] and camPos[1] < 0:
       camPos[1] += moveSpeed
    if pressed[pygame.K_s] and camPos[1] > -(img.height * 20)+500:
       camPos[1] -= moveSpeed
    if pressed[pygame.K_a] and camPos[0] < 0:
       camPos[0] += moveSpeed
    if pressed[pygame.K_d] and camPos[0] > -(img.width * 20)+800:
       camPos[0] -= moveSpeed
    
    screen.blit(turnButton, (screen.get_width()-39, screen.get_height()-39))

    if cursorPosSS[0] > (screen.get_width()-41)/20 and cursorPosSS[1] > (screen.get_height()-41)/20:
        screen.blit(cursorPressed if leftMouseDown or rightMouseDown else cursor, 
                    (cursorPosSS[0]*20+1, cursorPosSS[1]*20+1))
    else:
        screen.blit(cursorPressed if leftMouseDown or rightMouseDown else cursor, 
                    (camPos[0]%20 + cursorPosSS[0]*20+1, camPos[1]%20 + cursorPosSS[1]*20+1))
    pygame.display.update()
    
    def newTurn():
        if event.button == 1:
                    for i in units:
                        # ! very temporary enemy AI, please replace with something better, eventually, please
                        if i.team != 0:
                            possible_moves = points_within_distance(i.position, i.moveDist)
                            random.shuffle(possible_moves)
                            for move in possible_moves:
                                if (0 <= move[0] < img.width and 0 <= move[1] < img.height and
                                    img.getpixel(move) in i.validTiles
                                    and not list(move) == i.position): # I don't actually know if this line does anything important
                                    if any(unit.position == list(move) for unit in units):
                                        target_unit = next((unit for unit in units if unit.position == list(move)), None)
                                        if target_unit and i.team != target_unit.team:
                                            target_unit.health -= i.attack
                                            if target_unit.health <= 0:
                                                units.remove(target_unit)
                                    else:
                                        i.position = list(move)
                                    i.movedThisTurn = True
                                    break
                        else:
                            i.movedThisTurn = False if i.team == 0 else True

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if cursorPosSS[0] > (screen.get_width()-61)/20 and cursorPosSS[1] > (screen.get_height()-61)/20: 
                newTurn()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
            if event.key == pygame.K_1:
                selectedTeam = 0
            if event.key == pygame.K_2:
                selectedTeam = 1
            if event.key == pygame.K_3:
                selectedTeam = 2
            if event.key == pygame.K_4:
                selectedTeam = 3
            if event.key == pygame.K_5:
                selectedTeam = 4
            if event.key == pygame.K_6:
                selectedTeam = 5
            if event.key == pygame.K_7:
                selectedTeam = 6
            if event.key == pygame.K_8:
                selectedTeam = 7
            if event.key == pygame.K_z:
                units.append(Unit([cursorPos[0], cursorPos[1]], selectedTeam))
            if event.key == pygame.K_x:
                units.append(Ship([cursorPos[0], cursorPos[1]], selectedTeam))
            if event.key == pygame.K_c:
                itarget_unit = next((unit for unit in units if unit.position == cursorPos), None)
                if itarget_unit:
                    selected = -1
                    units.remove(itarget_unit)
            if event.key == pygame.K_v:
                img.putpixel(cursorPos, grassColor)
            if event.key == pygame.K_b:
                img.putpixel(cursorPos, waterColor)
            if event.key == pygame.K_n:
                img.putpixel(cursorPos, mountainColor)