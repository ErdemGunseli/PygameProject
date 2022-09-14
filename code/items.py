from player import *
import pygame.transform
from strings import *


# TODO: So far, the weapon class is very similar to how a generic item class would need to be.
#  Change name to item, then add special weapon attributes
class Weapon(Tile):
    # Weapon image file names:
    UP = "up.png"
    DOWN = "down.png"
    LEFT = "left.png"
    RIGHT = "right.png"
    ICON = "icon.png"

    def __init__(self, game, name, damage, cooldown, image_path, size):
        self.image_path = image_path

        super().__init__(game, size=size)

        self.player = self.level.get_player()

        self.name = name
        self.damage = damage

        # How long it takes to use item.
        self.cooldown = cooldown

        self.images = None
        self.image_offsets = None

        self.import_images()

    def import_images(self):
        # A dictionary of animation folder names and lists of images in the folders:

        self.images = {self.UP: [], self.DOWN: [], self.LEFT: [], self.RIGHT: [], self.ICON: []}

        for file_name in self.images.keys():
            final_path = self.image_path + "/" + file_name
            self.images[file_name] = Utils.resize_image(pygame.image.load(final_path).convert_alpha(), self.max_size)

    def get_icon(self):
        return self.images[self.ICON]

    def set_image_offsets(self, image_offsets):
        self.image_offsets = image_offsets

    def get_name(self):
        return self.name

    def get_cooldown(self):
        return self.cooldown

    def adjust_image(self, player):
        # Moving the image to the relevant side of the player and
        # adding an offset so that it matches the position of the hand:
        match player.get_animation_status():
            case Player.UP_ATTACK:
                self.collider.midbottom = player.get_rect().midtop + self.image_offsets[UP]
                self.image = self.images[self.UP]

            case Player.DOWN_ATTACK:
                self.collider.midtop = player.get_rect().midbottom + self.image_offsets[DOWN]
                self.image = self.images[self.DOWN]

            case Player.LEFT_ATTACK:
                self.collider.midright = player.get_rect().midleft + self.image_offsets[LEFT]
                self.image = self.images[self.LEFT]
            case Player.RIGHT_ATTACK:
                self.collider.midleft = player.get_rect().midright + self.image_offsets[RIGHT]
                self.image = self.images[self.RIGHT]
            case _: pass

        # Fixing rectangles:
        self.rect.center = self.collider.center
        self.rect.size = self.image.get_size()
        self.adjust_collider()

    def properties(self, player):
        player_stats = player.get_stats()
        player_inventory = player.get_inventory()
        return "{}\nDamage: {}\nCooldown: {}\nQuantity: {}".format(
            self.name,
            round(self.damage * player_stats[Player.MELEE_DAMAGE_MULTIPLIER], 2),
            round(self.cooldown * player_stats[Player.MELEE_COOLDOWN_MULTIPLIER], 2),
            player_inventory[self])

    def draw(self, draw_offset, player=None):
        self.adjust_image(player)
        super().draw(draw_offset)
