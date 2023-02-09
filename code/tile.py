import pygame
from utils import resize_image
from colours import *


class Tile(pygame.sprite.Sprite):  # [TESTED & FINALISED]

    # The size attribute is the size of the tile relative to the default tile size.
    # The collider ratio is the ratio of the size of the object the collider should be.
    # This is used to create an overlap effect, and to also allow interactions
    # such as characters moving behind the leaves of a tree.
    def __init__(self, game, position=(0, 0), size=(1, 1),
                 collider_ratio=(0.9, 0.9), image=None, protect_aspect_ratio=True):
        super().__init__()

        # Attributes for game and level:
        self.game = game
        self.level = game.get_current_level()
        self.tile_size = self.level.get_tile_size()

        # What ratio of the image the collider should occupy - this allows objects to partially overlap each other:
        self.collider_ratio = collider_ratio

        # The size of the rectangle of the object can change with the image size, but the maximum size does not:
        self.max_size = self.tile_to_pixel(size)
        self.rect = pygame.rect.Rect(position, self.max_size)

        # Whether to maintain the aspect ratio of the image when resizing it:
        self.protect_aspect_ratio = protect_aspect_ratio
        # If there is no image, then the tile will be a blank rectangle:
        if image is None: image = pygame.Surface(self.max_size)
        # Setting the image and adjusting its size:
        self.set_image(image)

        # When the tile moves, the collider is moved first and is used to check for collisions.
        # Then, the rectangle is moved to match with the collider.
        # The rectangle is used to draw the player with the correct size and allow for the overlap effect.
        self.collider = pygame.rect.Rect
        # The collider has an image that is used for debugging:
        self.collider_image = None
        self.adjust_collider()

    def tile_to_pixel(self, size):
        # Converts a size in tiles to pixels:
        return [dimension * self.tile_size for dimension in size]

    def set_image(self, image):
        if self.protect_aspect_ratio:
            # Resizing the tile image whilst protecting the aspect ratio:
            self.image = resize_image(image, self.max_size)
        else:
            # Resizing the image without protecting the aspect ratio:
            self.image = pygame.transform.scale(image, self.max_size)

        # Calculating the new size of the rectangle:
        self.rect.size = self.image.get_size()
        # Adjusting the collider to adapt to this new image:
        self.adjust_collider()

    def adjust_collider(self):
        # The size of the collider should be different to the size of the image for a more realistic result:
        self.collider = self.rect.copy().inflate([-(1 - self.collider_ratio[index]) * dimension
                                                  for index, dimension in enumerate(self.rect.size)])

    def get_distance_to(self, point):
        # Returns the distance between the centre of the tile and a specified point:
        x, y = self.collider.center
        return ((x - point[0]) ** 2 + (y - point[1]) ** 2) ** 0.5

    def get_collider(self):
        return self.collider

    def get_rect(self):
        return self.rect

    def set_top_left(self, position):
        # Sets the top left of the tile to a specified position:
        # Useful for placing the tile onto the map, since the top left positions are provided in this case:
        self.rect.topleft = position
        self.collider.topleft = position

    def draw_collider(self, draw_offset):
        # The image of the collider (for debugging, testing etc.):
        self.collider_image = pygame.Surface(self.collider.size)
        # Making the collider 50% transparent:
        self.collider_image.set_alpha(128)
        self.collider_image.fill(RED)
        # Drawing the collider:
        pygame.display.get_surface().blit(self.collider_image, self.collider.topleft + draw_offset)

    def draw(self, draw_offset):
        pygame.display.get_surface().blit(self.image, self.rect.topleft + draw_offset)
        # Drawing the collider (for debugging, testing etc.):
        # self.draw_collider(draw_offset)
