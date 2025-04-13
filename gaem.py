from PIL import Image, ImageDraw
import opensimplex
import pygame
from Unit import Unit, Ship
from constants import *
import random
from testStuff.temp import *

# ------- setup ---------
pygame.init()
pygame.mouse.set_visible(False)
running = True
clock = pygame.time.Clock()
selected = -1 # -1 means nothing's selected
leftMouseDown = False
rightMouseDown = False
cursorPosSS = [0, 0] # [0] is x and [1] is y
cursorPos = [0, 0] # same ^^
cursorPosDown = [0, 0] # in SS
cursorPosDelta = [0, 0] # also in SS
camPos = [0, 0] # in pixel space
units = []
turnNum = 0
showMinimap = False

selectedTeam = 0 # ! temporary variable, replace with GUI eventually, please

# ------ worldgen --------
img = Image.new("RGB", (worldWidth,worldHeight), (0,0,255))
imgclr = ImageDraw.Draw(img)
borders = Image.new("RGB", (worldWidth,worldHeight), (0,0,0))
bordersclr = ImageDraw.Draw(borders)
def genWorld():
    imgclr.rectangle([(0,0),img.size], fill = (0,0,255))
    bordersclr.rectangle([(0,0),borders.size], fill = (0,0,0) )
    opensimplex.random_seed()
    for y in range(img.height):
        for x in range(img.width):
            height = int((opensimplex.noise2(x/20, y/20) + 
                          opensimplex.noise2(x/5,y/5) + 
                          opensimplex.noise2(x/3,y/3) + 1) * 255 / 2)
            height = lerp(height, (-0.1*((x-(worldWidth/2))**2)+(-0.2*(y-(worldHeight/2))**2)+245), 0.2)
            if height > 250:
                img.putpixel((x, y), mountainColor)
                borders.putpixel((x, y), (128, 128, 128))
            elif height > 100:
                img.putpixel((x, y), grassColor)
                borders.putpixel((x, y), (255, 255, 255))
            else:
                img.putpixel((x, y), waterColor)
                borders.putpixel((x, y), black)
                
            # img.putpixel((x, y), grassColor)
            # borders.putpixel((x, y), (255, 255, 255))
genWorld()

# ------- game -----------
screen = pygame.display.set_mode((800, 500), pygame.HWACCEL | pygame.RESIZABLE)
terrainTexture = pygame.Surface((worldWidth * 20, worldHeight * 20))
worldTexture = pygame.Surface((worldWidth * 20, worldHeight * 20))

# a way to get new units in the game
def addNewUnit(): # ! another very temporary thing, replace with actual gameplay eventually, pretty please
    global turnNum
    if turnNum % 10 == 0 and len(units) < 1000:
        for i, v in enumerate(teamColors):
            t = []
            for x in range(borders.width):
                for y in range(borders.height):
                    if borders.getpixel((x, y)) == v:
                        t.append([x, y])
            random.shuffle(t)
            try:
                # for x in range(len(t)//10):
                units.append(Unit(t[0], i))
            except IndexError:
                continue

def findClosestEnemy(ai_unit):
    enemies = [u for u in units if u.team != ai_unit.team]
    if not enemies:
        return None
    return min(enemies, key=lambda e: abs(ai_unit.position[0] - e.position[0]) + abs(ai_unit.position[1] - e.position[1]))

def findClosestEnemyFromPos(team, position):
    enemies = [u for u in units if u.team != team]
    if not enemies:
        return None
    return min(enemies, key=lambda e: abs(position[0] - e.position[0]) + abs(position[1] - e.position[1]))

def newTurn():
    global turnNum
    addNewUnit() 
    for i in units:
        # very temporary enemy AI, please replace with something better, eventually, please
        # I'm working on it 'lil bro
        # unfortunately, it's become not very temporary
        closestUnit = findClosestEnemy(i)
        if i.team != 0:
            possible_moves = points_within_distance(i.position, i.moveDist)
            random.shuffle(possible_moves)
            for j, v in enumerate(possible_moves):
                try:
                    try:
                        if (distance(i.position, closestUnit.position) > distance(v, closestUnit.position) 
                            and img.getpixel(possible_moves[0]) == grassColor):
                            possible_moves.insert(0, possible_moves.pop(j))
                        
                        # path = a_star_pathfinding(tuple(i.position), tuple(closestUnit.position), img, i)
                        # if path is None or len(path) <= 1:
                        #     print(f"No valid path for unit at {i.position} to {closestUnit.position}")
                        #     continue
                        # possible_moves.insert(0, list(path[1]))
                    except AttributeError:
                        pass
                    if borders.getpixel(v) != teamColors[i.team] and img.getpixel(v) == grassColor and distance(i.position, closestUnit.position) > 5:
                        possible_moves.insert(0, possible_moves.pop(j))
                except IndexError:
                    continue
            for move in possible_moves:
                if (0 <= move[0] < img.width and 0 <= move[1] < img.height
                    and i.isTileValid(img, move)
                    and not list(move) == i.position):
                    # and i.is_path_valid(list(move), img)): I don't know why this doesn't work
                    if any(unit.position == list(move) for unit in units):
                        target_unit = next((unit for unit in units if unit.position == list(move)), None)
                        if target_unit and i.team != target_unit.team:
                            target_unit.health -= i.attack
                            if target_unit.health <= 0:
                                units.remove(target_unit)
                    else:
                        i.move(list(move), img)
                        if borders.getpixel(move) == white or borders.getpixel(move) in teamColors:
                            borders.putpixel((move), teamColors[i.team])
                    i.movedThisTurn = True
                    break
        else:
            i.movedThisTurn = False if i.team == 0 else True
    turnNum += 1
    updateWorldTexture()

# some smarter AI stuff, doesn't work yet

# def newTurn():
#     global turnNum
#     addNewUnit()
#     for ai_unit in units:
#         if ai_unit.team != 0:  # AI-controlled unit
#             target = findClosestEnemy(ai_unit)
#             if target:
#                 path = a_star_pathfinding(ai_unit.position, target.position, img)
#                 if path and len(path) > 1:  # Move one step along the path
#                     ai_unit.position = path[1]
#                     ai_unit.movedThisTurn = True
#     turnNum += 1
#     updateWorldTexture()

def updateTerrainTexture():
    terrainTexture.fill((0, 0, 0))

    # draw the map
    for y in range(img.height):
        for x in range(img.width):
            if img.getpixel((x, y)) == grassColor:
                terrainTexture.blit(grass, (x*20+1, y*20+1))
            elif img.getpixel((x, y)) == mountainColor:
                terrainTexture.blit(mountain, (x*20+1, y*20+1))
            else:
                terrainTexture.blit(water, (x*20+1, y*20+1))
updateTerrainTexture()

# god himself came to me in a dream and gave me this optimization~
def updateWorldTexture():
    worldTexture.fill((0, 0, 0))
    worldTexture.blit(terrainTexture, (0,0))
    # draw the map
    for y in range(img.height):
        for x in range(img.width):
            # this block of code is in my nightmares
            c = borders.getpixel((x, y))
            if c in teamColors:
                if x > 0 and borders.getpixel((x - 1, y)) != c:
                    pygame.draw.rect(worldTexture, black, (x*20+1, y*20+1, 1, 18))
                    pygame.draw.rect(worldTexture, addTuples(c, (25, 25, 25)), (x*20, y*20, 1, 20))
                    # pygame.draw.rect(screen, black, (camPos[0] + x*20-1, camPos[1] + y*20, 1, 20))
                if x < borders.width - 1 and borders.getpixel((x + 1, y)) != c:
                    pygame.draw.rect(worldTexture, black, (x*20+18, y*20+1, 1, 18))
                    pygame.draw.rect(worldTexture, addTuples(c, (25, 25, 25)), (x*20+19, y*20, 1, 20))
                    # pygame.draw.rect(screen, black, (camPos[0] + x*20+20, camPos[1] + y*20, 1, 20))
                if y > 0 and borders.getpixel((x, y - 1)) != c:
                    pygame.draw.rect(worldTexture, black, (x*20+1, y*20+1, 18, 1))
                    pygame.draw.rect(worldTexture, addTuples(c, (25, 25, 25)), (x*20, y*20, 20, 1))
                    # pygame.draw.rect(screen, black, (camPos[0] + x*20, camPos[1] + y*20-1, 20, 1))
                if y < borders.height - 1 and borders.getpixel((x, y + 1)) != c:
                    pygame.draw.rect(worldTexture, black, (x*20+1, y*20+18, 18, 1))
                    pygame.draw.rect(worldTexture, addTuples(c, (25, 25, 25)) , (x*20, y*20+19, 20, 1))
                    # pygame.draw.rect(screen, black, (camPos[0] + x*20, camPos[1] + y*20+20, 20, 1))
            if (selected >= 0 and abs(units[selected].position[0] - x) <= units[selected].moveDist 
                              and abs(units[selected].position[1] - y) <= units[selected].moveDist
                              and units[selected].is_path_valid([x, y], img)):
                if any(u.position == [x, y] for u in units):
                    target_unit = next((u for u in units if u.position == [x, y]), None)
                    if target_unit and units[selected].team != target_unit.team:
                        worldTexture.blit(redSquareThing, (x*20+1, y*20+1))
                    continue
                worldTexture.blit(blueSquareThing, (x*20+1, y*20+1))
    
updateWorldTexture()

while running:
    visible_x_start = -camPos[0] // 20
    visible_y_start = -camPos[1] // 20
    visible_x_end = visible_x_start + screen.get_width() // 20
    visible_y_end = visible_y_start + screen.get_height() // 20

    screen.blit(worldTexture, (camPos[0], camPos[1]))
    # draw the units
    for i in units:
        if visible_x_start <= i.position[0] <= visible_x_end and visible_y_start <= i.position[1] <= visible_y_end:
                screen.blit(i.image, (camPos[0] + i.position[0]*20+1, camPos[1] + i.position[1]*20+1))        
        
        if cursorPos == i.position and i.health < i.maxHealth:
            pygame.draw.rect(screen, "black", (camPos[0] + i.position[0]*20+4, camPos[1] + i.position[1]*20+7, 12, 8))
            pygame.draw.rect(screen, "red", (camPos[0] + i.position[0]*20+5, camPos[1] + i.position[1]*20+8, 10, 6))
            pygame.draw.rect(screen, "green", (camPos[0] + i.position[0]*20+5, camPos[1] + i.position[1]*20+8, 10 * (i.health/i.maxHealth), 6))
        if not i.movedThisTurn and i.team == 0:
            screen.blit(exclamationMark, (camPos[0] + i.position[0]*20+1, camPos[1] + i.position[1]*20+1))

    pygame.display.set_caption(f"{turnNum}, {str(cursorPos)}, {selectedTeam} , {selected}, {str([camPos[0]//20, camPos[1]//20])}, {str(units)}")

    # * draw UI past here
    # this is an abomoination, I'm sorry to anyone who has the misfortunate of reading this
    if showMinimap:
        screen.blit(pygame.transform.scale(pygame.image.fromstring(borders.tobytes(), borders.size, borders.mode).convert(), (borders.width*2,borders.height*2)), (screen.get_width()-borders.width*2, 0))
        pygame.draw.rect(screen, (255, 255, 0), ((-camPos[0]//10 +  screen.get_width()-borders.width*2, -camPos[1]//10), (80, 50)), 2)
    Render_Text(screen, str(int(clock.get_fps())), (255,255,255), (0,0))
    
    # update input variables
    cursorPosSS = [int(pygame.mouse.get_pos()[0]/20), int(pygame.mouse.get_pos()[1]/20)]
    cursorPos = [cursorPosSS[0] - int((camPos[0])//20), cursorPosSS[1] - int((camPos[1])//20)]
    leftMouseDown = pygame.mouse.get_pressed()[0]
    rightMouseDown = pygame.mouse.get_pressed()[2]

    # handle input
    if pygame.key.get_pressed()[pygame.K_LALT]:
        newTurn()
    
    # if leftMouseDown:
    #     if selected == 0:
    #         for i, u in enumerate(units):
    #             if cursorPos == u.position and u.movedThisTurn == False and u.carried == False and u.team == 0:
    #                 selected = i
    #     if isinstance(units[selected], ship):
    
    if leftMouseDown:
        cursorPosDelta = [cursorPosDown[0] - cursorPosSS[0], cursorPosDown[1] - cursorPosSS[1]]
        camPos[0] += cursorPosDelta[0]
        camPos[1] += cursorPosDelta[1]

    if rightMouseDown and selected >= 0:
        
        if (abs(units[selected].position[0] - cursorPos[0]) <= units[selected].moveDist 
            and abs(units[selected].position[1] - cursorPos[1]) <= units[selected].moveDist
            and units[selected].position != cursorPos
            and units[selected].is_path_valid(cursorPos, img)):
            if any(u.position == cursorPos for u in units):
                target_unit = next((u for u in units if u.position == cursorPos), None)
                if target_unit and units[selected].team != target_unit.team:
                    target_unit.health -= units[selected].attack
                    if target_unit.health <= 0:
                        selected -= 1 if selected > units.index(target_unit) else 0
                        units.remove(target_unit)
                elif target_unit.team == units[selected].team:
                    target_unit.health += 2
                # elif isinstance(target_unit, Ship):
                #     target_unit.load_unit(units[selected])
                #     units[selected].carried = True
            else:
                units[selected].move(cursorPos, img)
                if borders.getpixel(cursorPos) == white or borders.getpixel(cursorPos) in teamColors:
                    borders.putpixel(cursorPos, teamColors[units[selected].team])
            try:
                units[selected].movedThisTurn = True
            except:
                pass
        selected = -1
        updateWorldTexture()

    # move the camera
    pressed = pygame.key.get_pressed()
    moveSpeed = 5 if pressed[pygame.K_LSHIFT] else 1
    if pressed[pygame.K_w]:
       camPos[1] += moveSpeed
    if pressed[pygame.K_s]:
       camPos[1] -= moveSpeed
    if pressed[pygame.K_a]:
       camPos[0] += moveSpeed
    if pressed[pygame.K_d]:
       camPos[0] -= moveSpeed
    
    camPos[0] = max(min(camPos[0], 0), -(img.width * 20) + 800)
    camPos[1] = max(min(camPos[1], 0), -(img.height * 20) + 500)
    
    screen.blit(turnButton, (screen.get_width()-39, screen.get_height()-39))

    if cursorPosSS[0] > (screen.get_width()-41)/20 and cursorPosSS[1] > (screen.get_height()-41)/20:
        screen.blit(cursorPressed if leftMouseDown or rightMouseDown else cursor, 
                    (cursorPosSS[0]*20+1, cursorPosSS[1]*20+1))
    else:
        screen.blit(cursorPressed if leftMouseDown or rightMouseDown else cursor, 
                    (camPos[0]%20 + cursorPosSS[0]*20+1, camPos[1]%20 + cursorPosSS[1]*20+1))
    pygame.display.update()

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if cursorPosSS[0] > (screen.get_width()-61)/20 and cursorPosSS[1] > (screen.get_height()-61)/20: 
                newTurn()
            # 1 - left click
            # 2 - middle click
            # 3 - right click
            # 4 - scroll up
            # 5 - scroll down
            if event.button == 1:
                cursorPosDown = cursorPosSS
                for i, u in enumerate(units):
                    if cursorPos == u.position and u.movedThisTurn == False and u.carried == False and u.team == 0:
                        selected = i
                        updateWorldTexture()
                try: 
                    if isinstance(units[selected], Ship):
                        selected = units.index(units[selected].carrying_units[0])
                except: pass
        
        # brace yourself, the code below gets pretty ugly
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
            if event.key == pygame.K_SPACE:
                newTurn()
            if event.key == pygame.K_m:
                showMinimap = not showMinimap
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
            if event.key == pygame.K_9:
                selectedTeam = 8
            if event.key == pygame.K_0:
                selectedTeam = 9 
            if event.key == pygame.K_z:
                units.append(Unit(cursorPos, selectedTeam))
            if event.key == pygame.K_x:
                units.append(Ship([cursorPos[0], cursorPos[1]], selectedTeam))
            if event.key == pygame.K_c:
                itarget_unit = next((unit for unit in units if unit.position == cursorPos), None)
                if itarget_unit:
                    selected = -1
                    units.remove(itarget_unit)
            if event.key == pygame.K_v:
                img.putpixel(cursorPos, grassColor)
                borders.putpixel(cursorPos, white)
                updateTerrainTexture()
            if event.key == pygame.K_b:
                img.putpixel(cursorPos, waterColor)
                borders.putpixel(cursorPos, black)
                updateTerrainTexture()
            if event.key == pygame.K_n:
                img.putpixel(cursorPos, mountainColor)
                borders.putpixel(cursorPos, (180, 180, 180))
                updateTerrainTexture()
            if event.key == pygame.K_r:
                genWorld()
                updateTerrainTexture()
            if event.key == pygame.K_t:
                for i in units:
                    del i
                units = []
    clock.tick()