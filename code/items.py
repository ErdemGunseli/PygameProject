from characters import *
import pygame.transform
from strings import *


# TODO: DO NOT MODIFY UNNECESSARILY BEFORE FINISHING PROJECT - Maybe at the end:
#  Make some Optimisations

# TODO: DO NOT MODIFY UNNECESSARILY BEFORE FINISHING PROJECT - Maybe at the end:
#  Make some Optimisations Create
#  Potions with Different Effects
#  Put Properties Texts into strings.py


class Item(Tile):

    # Icon image name:
    ICON = "icon.png"


    def __init__(self, game, name, use_duration, image_path, size, owner=None, position=(0, 0)):
        self.image_path = image_path

        super().__init__(game, position=position, size=size)

        self.images = {}
        self.import_images()
        self.set_icon(self.images[self.ICON])

        # The name of the item:
        self.name = name

        # How long it takes to use item:
        self.in_use = False
        self.use_start_time = 0
        self.use_duration = use_duration

        # How much the image should be offset by to match the hand of the player:
        self.image_offsets = {UP: (0, 0), DOWN: (0, 0), LEFT: (0, 0), RIGHT: (0, 0)}
        # Values for this is set by the player, since if the player model was to change,
        # these values would also be different. So it is not wise to hard-code them.

        # If the item does not have an owner, it is on the ground:
        # The player can then be set as the owner:
        self.owner = None
        self.set_owner(owner)

    def set_owner(self, owner):
        if owner is None:

            # If item had a previous owner, place the item at the feet of the previous owner:
            if self.owner is not None:
                self.rect.midtop = self.owner.get_rect().midbottom
                self.collider.midtop = self.owner.get_rect().midbottom

            # Adding item into the level:
            self.level.add_tile(self, visible=True, depth=True, obstacle=False, dynamic=True, item=True)

        else:
            # If the owner is not none, removing the item from the level:
            self.level.remove_tile(self)

            # Getting correct image offsets for player:
            self.image_offsets = owner.get_item_offsets()

        self.owner = owner

        # Setting icon as image:
        self.image = self.images[self.ICON]


    def get_owner(self):
        return self.owner

    def import_images(self):
        # Base item class only has one image in its dictionary - children have more:
        final_path = self.image_path + "/" + self.ICON
        self.images = {self.ICON: resize_image(pygame.image.load(final_path).convert_alpha(), self.max_size)}

    def get_icon(self):
        return self.image

    def set_image_offsets(self, image_offsets):
        self.image_offsets = image_offsets

    def get_name(self):
        return self.name

    def get_use_duration(self):
        return self.use_duration

    def adjust_image(self):
        # Moving the image to the relevant side of the player and
        # adding an offset so that it matches the position of the hand:
        match self.owner.get_animation_status():
            case Player.UP_USE:
                self.collider.midbottom = self.owner.get_rect().midtop + self.image_offsets[UP]
            case Player.DOWN_USE:
                self.collider.midtop = self.owner.get_rect().midbottom + self.image_offsets[DOWN]
            case Player.LEFT_USE:
                self.collider.midright = self.owner.get_rect().midleft + self.image_offsets[LEFT]
            case Player.RIGHT_USE:
                self.collider.midleft = self.owner.get_rect().midright + self.image_offsets[RIGHT]
            case _: pass

        # Fixing rectangles:
        self.rect.center = self.collider.center
        self.rect.size = self.image.get_size()
        self.adjust_collider()

    def properties(self):
        return "Item"

    def use(self):
        if not self.in_use:
            self.in_use = True
            self.use_start_time = pygame.time.get_ticks()

    def is_in_use(self):
        return self.in_use

    def update_cooldown(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.use_start_time >= self.use_duration:
            self.in_use = False

    def draw(self, draw_offset):
        if self.owner is not None:
            # Need to adjust image every frame because direction could have changed:
            self.adjust_image()

        super().draw(draw_offset)

    def update(self):
        self.update_cooldown()


class Potion(Item):

    def __init__(self, game, name, health_boost, use_duration, image_path, size, owner=None, position=(0, 0)):
        super().__init__(game, name, use_duration, image_path, size, owner, position)

        self.health_boost = health_boost

        # Whether the item has been used
        self.consumed = False

    def use(self):
        super().use()
        self.owner.add_health(self.health_boost)
        # Setting consumed flag true so it is destroyed after it is used:
        self.consumed = True

    def properties(self):
        inventory = self.owner.get_inventory()
        stats = self.owner.get_stats()
        return "{}\nHealth Boost: {}\nUse Duration: {}s\nQuantity: {}".format(
            self.name,
            percentage_format(self.health_boost / stats[Character.FULL_HEALTH]),
            self.use_duration/1000,
            inventory[self])

    def update(self):
        super().update()
        if self.consumed and not self.in_use:
            # Only 1 item from inventory should be destroyed, so setting flag back to False:
            self.consumed = False
            self.owner.destroy_item(self)


class Weapon(Item):
    # Weapons can have images with different directions:
    UP = "up.png"
    DOWN = "down.png"
    LEFT = "left.png"
    RIGHT = "right.png"

    def __init__(self, game, name, damage,  use_duration, image_path, size, owner=None, position=(0, 0), ):
        super().__init__(game, name, use_duration, image_path, size, owner, position)
        self.damage = damage

        # How long it takes to use item.
        self.use_duration = use_duration

        self.import_images()

    def adjust_image(self):
        # A different image is shown depending on which way the player is facing:
        match self.owner.get_animation_status():
            case Player.UP_USE:
                self.collider.midbottom = self.owner.get_rect().midtop + self.image_offsets[UP]
                self.image = self.images[self.UP]

            case Player.DOWN_USE:
                self.collider.midtop = self.owner.get_rect().midbottom + self.image_offsets[DOWN]
                self.image = self.images[self.DOWN]

            case Player.LEFT_USE:
                self.collider.midright = self.owner.get_rect().midleft + self.image_offsets[LEFT]
                self.image = self.images[self.LEFT]
            case Player.RIGHT_USE:
                self.collider.midleft = self.owner.get_rect().midright + self.image_offsets[RIGHT]
                self.image = self.images[self.RIGHT]
            case _: pass

        # Fixing rectangles:
        self.rect.center = self.collider.center
        self.rect.size = self.image.get_size()
        self.adjust_collider()

    def import_images(self):
        # A dictionary of animation folder names and lists of images in the folders:

        self.images = {self.UP: [], self.DOWN: [], self.LEFT: [], self.RIGHT: [], self.ICON: []}

        for file_name in self.images.keys():
            final_path = self.image_path + "/" + file_name
            self.images[file_name] = resize_image(pygame.image.load(final_path).convert_alpha(), self.max_size)

    def get_icon(self):
        return self.images[self.ICON]

    def properties(self):
        stats = self.owner.get_stats()
        inventory = self.owner.get_inventory()
        return "{}\nDPS: {}\nImpact Duration: {}s\nQuantity: {}".format(
            self.name,
            round(self.damage * stats[Player.DAMAGE_MULTIPLIER], 2),
            self.use_duration/1000,
            inventory[self])

    def get_damage(self):
        return self.damage

    def check_hit(self):
        vulnerable_tiles = self.game.get_current_level().get_vulnerable_tiles().copy()

        # Weapon should not damage the owner:
        if self.owner in vulnerable_tiles: vulnerable_tiles.remove(self.owner)

        for tile in vulnerable_tiles:
            if self.collider.colliderect(tile.get_collider()):
                tile.receive_damage(self.damage * self.game.get_current_frame_time())

    def update(self):
        super().update()
        if self.in_use:
            self.check_hit()




