from characters import *
import pygame.transform
from strings import *
from assets import *


class Item(Tile):  # [TESTED & FINALISED]
    # Icon image file name:
    ICON = "icon.png"

    def __init__(self, game, name, use_duration, image_path, size, use_sound_path=None, owner=None, position=(0, 0)):

        super().__init__(game, position=position, size=size)

        # The name of the item:
        self.name = name

        # How long it takes to use item:
        self.in_use = False
        self.use_start_time = 0
        self.use_duration = use_duration

        # Sound effects for using item:
        self.use_sound = pygame.mixer.Sound(use_sound_path)

        # The path to the folder containing the images:
        self.image_path = image_path
        # A dictionary of labels and image surfaces:
        self.images = {}
        # Filling image dictionary:
        self.import_images()
        self.set_image(self.images[self.ICON])

        # How much the image should be offset by to match the hand of the player:
        # Values for this is set by the player, since if the player model was to change,
        # these values would also be different. So it is not wise to hard-code them:
        self.image_offsets = {UP: (0, 0), DOWN: (0, 0), LEFT: (0, 0), RIGHT: (0, 0)}

        # If the item does not have an owner, it is on the ground:
        # If an item is in collision with the player, it's owner can be set to the player:
        self.owner = None
        self.set_owner(owner)

    def set_owner(self, owner):
        # Cannot be in use when owner changes:
        self.in_use = False

        if owner is None:

            # If item had a previous owner, placing the item at the feet of the previous owner:
            if self.owner is not None:
                self.rect.midtop = self.owner.get_rect().midbottom
                self.collider.midtop = self.owner.get_rect().midbottom

            # Adding the item into the level, since it no longer has an owner:
            self.level.add_tile(self, visible=True, depth=True, obstacle=False, dynamic=True, item=True)

        else:
            # If an owner has been set, removing the item from the level:
            self.level.remove_tile(self)

            # Getting correct image offsets from owner:
            self.image_offsets = owner.get_item_offsets()

        self.owner = owner

        # Setting icon as image:
        self.image = self.images[self.ICON]

    def get_owner(self):
        return self.owner

    def import_images(self):
        # Base item class only has one image in its dictionary - children have more:
        final_path = path.format(self.image_path, self.ICON)
        self.images = {self.ICON: resize_image(pygame.image.load(final_path).convert_alpha(), self.max_size)}

    def adjust_image(self):
        # Moving the image to the relevant side of the character and
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

    def get_icon(self):
        return self.image

    def get_name(self):
        return self.name

    def use(self):
        if not self.in_use:
            # Playing use sound:
            self.use_sound.set_volume(self.game.get_audio_volume())
            self.use_sound.play()
            self.in_use = True
            self.use_start_time = pygame.time.get_ticks()

    def is_in_use(self):
        return self.in_use

    def update_cooldown(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.use_start_time >= self.use_duration:
            self.in_use = False

    def properties(self):
        # Overriden by children:
        return "Item"

    def draw(self, draw_offset):
        if self.owner is not None:
            # Adjusting the image of the item to match the hand of the owner:
            # Needs to be done each frame since the direction may have changed:
            self.adjust_image()

        super().draw(draw_offset)

    def update(self):
        # Drawing the item if it is in use:
        if self.in_use:
            self.draw(self.level.get_draw_offset())
        self.update_cooldown()


class Potion(Item):  # [TESTED & FINALISED]

    def __init__(self, game, name, health_boost, use_duration, image_path, size, owner=None, position=(0, 0)):
        super().__init__(game, name, use_duration, image_path, size,
                         use_sound_path=POTION_USE, owner=owner, position=position)

        # The increase in health of the owner when the potion is consumed:
        self.health_boost = health_boost

        # Whether the item has been used
        self.consumed = False

    def use(self):
        super().use()
        # Increasing the health of the owner by the boost amount:
        self.owner.add_health(self.health_boost)
        # Setting a flag to indicate that the item has been consumed,
        # so that it is destroyed after the use is finished:
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


class Weapon(Item):  # [TESTED & FINALISED]
    # Weapons can have images with different directions:
    UP = "up.png"
    DOWN = "down.png"
    LEFT = "left.png"
    RIGHT = "right.png"

    def __init__(self, game, name, damage,  use_duration, image_path, size, owner=None, position=(0, 0)):
        super().__init__(game, name, use_duration, image_path, size,
                         use_sound_path=WEAPON_USE, owner=owner, position=position)

        # The damage to be dealt per second to any vulnerable sprite when impacted:
        self.damage = damage

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
        self.images = {self.UP: [], self.DOWN: [], self.LEFT: [], self.RIGHT: [], self.ICON: []}

        # Filling the image dictionary with images for each direction and the icon:
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

        # Can only deal damage if owned by a character:
        if self.owner is None: return

        # Obtaining vulnerable tiles in frame from the level:
        vulnerable_tiles = self.game.get_current_level().get_vulnerable_tiles_in_frame().copy()

        # Weapon should not damage the owner:
        if self.owner in vulnerable_tiles: vulnerable_tiles.remove(self.owner)

        for tile in vulnerable_tiles:
            if self.collider.colliderect(tile.get_collider()):
                output_damage = self.damage * self.game.get_current_frame_time() * self.owner.get_stats()[Character.DAMAGE_MULTIPLIER]

                # If the owner is a player, we need to include its damage multiplier:
                if isinstance(self.owner, Player): output_damage *= self.owner.get_stats()[Player.DAMAGE_MULTIPLIER]

                # Applying damage to vulnerable tile:
                tile.receive_damage(output_damage)

    def update(self):
        super().update()
        if self.in_use:
            self.check_hit()

