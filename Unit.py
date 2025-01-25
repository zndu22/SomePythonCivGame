import pygame
from constants import *

class Unit:
    position = [0, 0]
    moveDist = 2
    validTiles = [grassColor]
    image = unit
    movedThisTurn = False
    team = 0 # 0 is player's team
    maxHealth = 10
    health = maxHealth
    attack = 2

    def __init__(self, position, team = 0):
        self.position = position
        self.team = team
        colorImage = self.image.copy()
        colorImage.fill(teamColors[team], special_flags=pygame.BLEND_ADD)
        self.image = colorImage
        mask = pygame.mask.from_surface(self.image)
        outline = mask.convolve(pygame.mask.Mask((3, 3), fill=True)).to_surface(setcolor=(0, 0, 0), unsetcolor=self.image.get_colorkey())
        outline.blit(self.image, (1, 1))
        self.image = outline

    def __str__(self):
        return f"{str(self.position)}, {self.team}"

    def __repr__(self):
        return f"{str(self.position)}, {self.team}"

    def is_path_valid(self, target_pos, img):
        x0, y0 = self.position
        x1, y1 = target_pos
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while (x0, y0) != (x1, y1):
            if img.getpixel((x0, y0)) not in self.validTiles:
                return False
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return img.getpixel((x1, y1)) in self.validTiles and not self.movedThisTurn

class Ship(Unit):
    moveDist = 3
    validTiles = [waterColor]
    image = ship
    maxHealth = 20
    health = maxHealth
    carrying_units = []


    def __init__(self, position, team = 0):
        super().__init__(position, team)
        self.moveDist = 3

    def __str__(self):
        return f"Ship at {str(self.position)}"

    def __repr__(self):
        return f"Ship at {str(self.position)}"

    def is_path_valid(self, target_pos, img):
        return super().is_path_valid(target_pos, img)

    def load_unit(self, unit):
        if isinstance(unit, Unit):
            self.carrying_units.append(unit)
            unit.position = self.position  # Update unit's position to ship's position

    def unload_unit(self, unit):
        if unit in self.carrying_units:
            self.carrying_units.remove(unit)
            # Optionally, update unit's position to ship's position or a new position

    def get_carried_units(self):
        return self.carrying_units
