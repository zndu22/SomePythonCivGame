import pygame

worldWidth = 50
worldHeight = 50

grass = pygame.image.load("graphics/gras.png")
water = pygame.image.load("graphics/watr.png")
mountain = pygame.image.load("graphics/mountain.png")
unit = pygame.image.load("graphics/unit.png")
ship = pygame.image.load("graphics/ship.png")
cursor = pygame.image.load("graphics/cursor.png")
cursorPressed = pygame.image.load("graphics/cursorPressed.png")
blueSquareThing = pygame.image.load("graphics/moveMarker.png")
turnButton = pygame.image.load("graphics/turn.png")
exclamationMark = pygame.image.load("graphics/exclamashonMark.png")
redSquareThing = pygame.image.load("graphics/attackMarker.png")

white = (255, 255, 255)
black = (0, 0, 0)

grassColor = (0, 255, 0)
waterColor = (0, 0, 255)
mountainColor = (180, 180, 180)
teamColors = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255), (200, 0, 200), (0, 252, 126), (164, 252, 0), (252, 172, 0)]