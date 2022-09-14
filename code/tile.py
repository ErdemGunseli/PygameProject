import pygame
from utils import *
from colours import *


class Tile(pygame.sprite.Sprite):

    # The size attribute is the size of the tile relative to the default tile size.
    # The collider ratio is what ratio of the size of the object the collider should be.
    # For example, because the player should pass through the leaves of a tree,
    # the collider of the tree should be less than the size of its image, which includes its leaves.
    def __init__(self, game, position=(0, 0), size=(1, 1),
                 collider_ratio=(0.9, 0.9), image=None, protect_aspect_ratio=True):
        super().__init__()

        self.game = game
        self.level = game.get_current_level()
        self.tile_size = self.level.get_tile_size()

        # Whether the aspect ratio of the image should be respected when resizing it:
        self.protect_aspect_ratio = protect_aspect_ratio

        # What ratio of the image should be the collider:
        self.collider_ratio = collider_ratio

        # Setting the size in pixels:
        # The size of the rect can change with the image size, but max_size doesn't
        self.max_size = self.tile_to_pixel(size)

        if image is None:
            image = pygame.Surface(self.max_size)
        self.rect = pygame.rect.Rect(position, self.max_size)

        self.set_image(image)

        self.collider = pygame.rect.Rect
        self.collider_image = None
        self.adjust_collider()

        self.rect.center = self.collider.center

    def tile_to_pixel(self, size):
        return [dimension * self.tile_size for dimension in size]

    def set_image(self, image):
        if self.protect_aspect_ratio:
            # Resizing the tile whilst protecting the aspect ratio of the source image:
            self.image = Utils.resize_image(image, self.max_size)
        else:
            # Resizing the image without protecting the aspect ratio:
            self.image = pygame.transform.scale(image, self.max_size)

        self.rect.size = self.image.get_size()

    def adjust_collider(self):
        # The size of the collider should be different to the size of the image for a more realistic result.
        # Adjusting the size of the collider as required:
        self.collider = self.rect.copy().inflate([-(1 - self.collider_ratio[index]) * dimension
                                                  for index, dimension in enumerate(self.rect.size)])

        # The image of the collider (for debugging, testing etc.):
        self.collider_image = pygame.Surface([self.collider.width, self.collider.height])
        self.collider_image.set_alpha(128)
        self.collider_image.fill(RED)

    def draw(self, draw_offset):
        pygame.display.get_surface().blit(self.image, self.rect.topleft + draw_offset)
        # pygame.display.get_surface().blit(self.collider_image, self.collider.topleft + draw_offset)

    def get_collider(self):
        return self.collider
