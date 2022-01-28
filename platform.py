import pygame
from utils import *


class Platform (pygame.sprite.Sprite):
    def __init__(self, position, size):
        super().__init__()

        # Creating a square platform
        self.image = pygame.Surface((size, size))
        self.image.fill(TILECOLOUR)
        self.rect = self.image.get_rect(topleft = position)

    def update(self, xShift, yShift):
        # For shifting the level as the player moves
        self.rect.x += xShift
        self.rect.y += yShift
       