import pygame
from utils import resize_image
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

        # What ratio of the image the collider should occupy - this allows objects to partially overlap each other:
        self.collider_ratio = collider_ratio

        # The size of the rect can change with the image size, but max_size doesn't:
        self.max_size = self.tile_to_pixel(size)
        self.rect = pygame.rect.Rect(position, self.max_size)

        # Whether the aspect ratio of the image should be respected when resizing it:
        self.protect_aspect_ratio = protect_aspect_ratio
        if image is None: image = pygame.Surface(self.max_size)
        # Setting the image and adjusting its size:
        self.set_icon(image)

        # The collider is moved and used to check for collisions.
        # The rectangle is used to draw the player with the correct size.
        self.collider = pygame.rect.Rect
        # The collider has an image for debugging:
        self.collider_image = None
        self.adjust_collider()

    def tile_to_pixel(self, size):
        # Converts a size in tiles to pixels:
        return [dimension * self.tile_size for dimension in size]

    def set_icon(self, image):
        if self.protect_aspect_ratio:
            # Resizing the tile whilst protecting the aspect ratio of the source image:
            self.image = resize_image(image, self.max_size)
        else:
            # Resizing the image without protecting the aspect ratio:
            self.image = pygame.transform.scale(image, self.max_size)

        self.rect.size = self.image.get_size()


    def adjust_collider(self):
        # The size of the collider should be different to the size of the image for a more realistic result:
        self.collider = self.rect.copy().inflate([-(1 - self.collider_ratio[index]) * dimension
                                                  for index, dimension in enumerate(self.rect.size)])

    def get_distance_to(self, point):
        x, y = self.collider.center
        return ((x - point[0]) ** 2 + (y - point[1]) ** 2) ** 0.5

    def get_collider(self):
        return self.collider

    def get_rect(self):
        return self.rect

    def set_top_left(self, position):
        self.rect.topleft = position
        self.collider.topleft = position

    def draw(self, draw_offset):
        pygame.display.get_surface().blit(self.image, self.rect.topleft + draw_offset)
        # self.draw_collider(draw_offset)

    def draw_collider(self, draw_offset):
        # The image of the collider (for debugging, testing etc.):
        self.collider_image = pygame.Surface([self.collider.width, self.collider.height])
        self.collider_image.set_alpha(128)
        self.collider_image.fill(RED)
        pygame.display.get_surface().blit(self.collider_image, self.collider.topleft + draw_offset)
