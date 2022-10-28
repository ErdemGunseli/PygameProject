import pygame.image
from tile import Tile
from utils import *
from user_interface import *

# TODO: DO NOT MODIFY UNNECESSARILY BEFORE FINISHING PROJECT - Maybe at the end:
#  Make some Optimisations
#  Fix Animation Glitch when Drinking Last Potion
#  Fix Animation Glitch of Enemy Health Bar
#  Choose Player Avatar


class Character(Tile):
    # Constants for Stat Types::
    FULL_HEALTH = 0
    CURRENT_HEALTH = 1

    INVULNERABILITY_DURATION = 2

    # Animation folder names:
    UP_MOVE = "up_move"
    DOWN_MOVE = "down_move"
    LEFT_MOVE = "left_move"
    RIGHT_MOVE = "right_move"

    UP_IDLE = "up_idle"
    DOWN_IDLE = "down_idle"
    LEFT_IDLE = "left_idle"
    RIGHT_IDLE = "right_idle"

    UP_USE = "up_use"
    DOWN_USE = "down_use"
    LEFT_USE = "left_use"
    RIGHT_USE = "right_use"

    # Animation frame durations in ms:
    ANIMATION_FRAME_TIME = 150

    def __init__(self, game, stats, inventory, animation_path, position=(0, 0)):
        super().__init__(game, position, collider_ratio=(1, 1))
        self.database_helper = game.get_database_helper()

        # Player stats and inventory dictionaries:
        self.stats = stats
        self.inventory = inventory

        # How much the location of items being used by the player
        # should be offset so that they match with the player's hand:
        self.item_offsets = {UP: pygame.Vector2(self.tile_to_pixel((-0.2, 0))),
                             DOWN: pygame.Vector2(self.tile_to_pixel((-0.2, 0))),
                             LEFT: pygame.Vector2(self.tile_to_pixel((0, 0.21))),
                             RIGHT: pygame.Vector2(self.tile_to_pixel((0, 0.21)))}
        # Setting owner as player:
        for item in self.inventory: item.set_owner(self)

        # Whether the player is currently invulnerable
        # (the player is made invulnerable for a short period of time after taking damage):
        self.invulnerable = True
        self.invulnerability_start_time = 0

        self.item_held = list(self.inventory)[0]

        # The direction in which the player is moving:
        self.direction = pygame.math.Vector2()

        # For very high frame rates, the number of pixels the player should travel per frame is less than 1.
        # For this reason, storing this value and adding it to the distance each frame:
        self.displacement_deficit = [0, 0]

        self.animations = None
        self.animation_path = animation_path
        self.animation_status = self.DOWN_IDLE
        self.animation_increment_time = 0
        self.current_animation_frame_index = 0
        self.import_animations()

    def get_item_offsets(self):
        return self.item_offsets

    def import_animations(self):
        # A dictionary of animation folder names and lists of images in the folders:

        self.animations = {
            # Walking
            self.UP_MOVE: [], self.DOWN_MOVE: [], self.LEFT_MOVE: [], self.RIGHT_MOVE: [],
            # Stopping
            self.UP_IDLE: [], self.DOWN_IDLE: [], self.LEFT_IDLE: [], self.RIGHT_IDLE: [],
            # Attacking
            self.UP_USE: [], self.DOWN_USE: [], self.LEFT_USE: [], self.RIGHT_USE: []
        }

        for folder_name in self.animations.keys():
            final_path = self.animation_path + "/" + folder_name
            # Max size inherited from parent:
            self.animations[folder_name] = [resize_image(image, self.max_size) for image in import_images(final_path)]

    def use_item(self):
        self.set_use_animation()
        self.item_held.use()

    def increment_item_selected(self):
        # Cannot swap item while using it:
        if self.item_held.is_in_use(): return
        inventory_list = list(self.inventory)
        item_index = inventory_list.index(self.item_held) + 1
        if item_index >= len(inventory_list):
            item_index = 0
        self.item_held = (inventory_list[item_index])

    def set_use_animation(self):
        match self.animation_status:
            case self.UP_MOVE | self.UP_IDLE:
                self.animation_status = self.UP_USE
            case self.DOWN_MOVE | self.DOWN_IDLE:
                self.animation_status = self.DOWN_USE
            case self.LEFT_MOVE | self.LEFT_IDLE:
                self.animation_status = self.LEFT_USE
            case self.RIGHT_MOVE | self.RIGHT_IDLE:
                self.animation_status = self.RIGHT_USE

    def set_idle_animation(self):
        match self.animation_status:
            case self.UP_MOVE | self.UP_USE:
                self.animation_status = self.UP_IDLE
            case self.DOWN_MOVE | self.DOWN_USE:
                self.animation_status = self.DOWN_IDLE
            case self.LEFT_MOVE | self.LEFT_USE:
                self.animation_status = self.LEFT_IDLE
            case self.RIGHT_MOVE | self.RIGHT_USE:
                self.animation_status = self.RIGHT_IDLE

    def update_cooldown_timers(self):
        # The timers for when an action requires a cooldown.
        # Measuring the difference in ticks to calculate time.
        # Alternatively, it is possible to do it by counting frames and multiplying by frame time:

        current_time = pygame.time.get_ticks()

        # Characters have invulnerability for a short time after taking damage:
        if current_time - self.invulnerability_start_time >= self.stats[self.INVULNERABILITY_DURATION]:
            self.invulnerable = False

    def handle_collision(self, axis):
        # Retrieving the collision objects:
        obstacle_sprites = self.level.get_obstacle_tiles_in_frame().copy()

        # Cannot collide with itself:
        if self in obstacle_sprites: obstacle_sprites.remove(self)

        # x-axis:
        if axis == 0:
            for obstacle in obstacle_sprites:
                obstacle_collider = obstacle.get_collider()
                # Checking if the obstacle has collided with the player:
                if obstacle_collider.colliderect(self.collider):
                    # Using the player's direction to stop collision:
                    if self.direction.x > 0:
                        # The player is moving right, move the player to the left of the obstacle:
                        self.collider.right = obstacle_collider.left
                    else:
                        # The player is moving left, move the player to the right of the obstacle:
                        self.collider.left = obstacle_collider.right
        # y-axis:
        else:
            for obstacle in obstacle_sprites:
                obstacle_collider = obstacle.get_collider()
                # Checking if the obstacle has collided with the player:
                if obstacle_collider.colliderect(self.collider):
                    # Using the player's direction to stop collision:
                    if self.direction.y > 0:
                        # The player is moving down, move the player above of the obstacle:
                        self.collider.bottom = obstacle_collider.top
                    else:
                        # The player is moving up, move the player below the obstacle:
                        self.collider.top = obstacle_collider.bottom

    def update_animation_status(self):
        # Setting the animation status according to the direction:

        if abs(self.direction.x) > abs(self.direction.y):
            if self.direction.x > 0:
                self.animation_status = self.RIGHT_MOVE
            elif self.direction.x < 0:
                self.animation_status = self.LEFT_MOVE
        else:
            if self.direction.y > 0:
                self.animation_status = self.DOWN_MOVE
            elif self.direction.y < 0:
                self.animation_status = self.UP_MOVE

        if self.item_held.is_in_use():
            self.set_use_animation()
        else:
            if self.direction.magnitude() == 0:
                self.set_idle_animation()

    def update_animation_frame(self):
        current_time = pygame.time.get_ticks()

        animation_frames = self.animations[self.animation_status]

        if current_time >= self.animation_increment_time + self.ANIMATION_FRAME_TIME:
            self.animation_increment_time = current_time

            self.current_animation_frame_index += 1

            if self.current_animation_frame_index >= len(animation_frames):
                self.current_animation_frame_index = 0
            self.image = animation_frames[self.current_animation_frame_index]
            self.rect.size = self.image.get_size()
            self.adjust_collider()

    def get_animation_status(self):
        return self.animation_status

    @staticmethod
    def deal_damage(recipient, damage_value):
        recipient.receive_damage(damage_value)

    def receive_damage(self, damage_value):
        if self.invulnerable: return
        self.invulnerable = True
        self.invulnerability_start_time = pygame.time.get_ticks()

        self.stats[self.CURRENT_HEALTH] -= damage_value

        if self.stats[self.CURRENT_HEALTH] <= 0:
            self.death_sequence()

    def death_sequence(self):
        return None

    def add_health(self, health_value):
        self.stats[self.CURRENT_HEALTH] += health_value
        if self.stats[self.CURRENT_HEALTH] > self.stats[self.FULL_HEALTH]:
            self.stats[self.CURRENT_HEALTH] = self.stats[self.FULL_HEALTH]

    def get_rect(self):
        return self.rect

    def get_stats(self):
        return self.stats

    def set_stats(self, stats):
        self.stats = stats

    def get_inventory(self):
        return self.inventory

    def get_item_selected(self):
        return self.item_held

    def get_item_by_name(self, name):
        # Identical instances with different positions are not the same object.
        # To determine whether an item is in the inventory, we need to compare names:
        for inventory_item in self.inventory:
            if name == inventory_item.get_name():
                return inventory_item

    def move(self, speed):
        # In this implementation, the player is moved as usual, and if there is a collision, the player is moved to the
        # appropriate side of the obstacle, which is determined using the player's direction of motion:

        # For high frame rates, the number of pixels the player moves per frame could be less than 1 pixel per frame.
        # For this reason, storing the distance that the player should have travelled, and moving the player by that
        # distance when it reaches 1:

        speed_per_frame = speed * self.level.get_tile_size() * self.game.get_current_frame_time()

        # How much the player needs to move this frame,
        # taking into account how much it couldn't move in the previous frames:
        displacement_required = [speed_per_frame * axis + self.displacement_deficit[index] for index, axis in
                                 enumerate(self.direction)]

        # How much motion is possible.
        # The number of pixels moved per frame must be an integer,
        # and this can be less than 1 if the frame rate is high:
        displacement_possible = [int(axis) for axis in displacement_required]

        self.displacement_deficit = [displacement_required[0] - displacement_possible[0],
                                     displacement_required[1] - displacement_possible[1]]

        self.collider.x += displacement_possible[0]
        self.handle_collision(0)

        self.collider.y += displacement_possible[1]
        self.handle_collision(1)

        # Centering the rectangle of the player to where the collider has just been moved:
        self.rect.center = self.collider.center

    def draw(self, draw_offset):
        super().draw(draw_offset)
        if self.item_held.is_in_use():
            self.item_held.draw(draw_offset)

    def update(self):
        self.update_cooldown_timers()
        self.update_animation_frame()


class Player(Character):
    # Additional Stats for Player:
    CURRENT_LEVEL_ID = 3
    SPEED_MULTIPLIER = 4
    DAMAGE_MULTIPLIER = 5
    STEALTH_MULTIPLIER = 6

    # Where the animation files are located:
    ANIMATION_PATH = "../assets/images/characters/player/knight"

    # Default speed of the player in tiles per second:
    BASE_SPEED = 5

    def __init__(self, game, stats, inventory, position=(0, 0)):
        super().__init__(game, stats, inventory, self.ANIMATION_PATH, position=position)

    def handle_input(self):
        # Player cannot control character if using item:
        if self.item_held.is_in_use():
            self.direction.update(0, 0)
            return

        # Getting the keys that are being held down:
        keys_held = pygame.key.get_pressed()

        # Calculating the correct direction according to the keys held:
        # X-Direction:
        if keys_held[pygame.K_a] and not keys_held[pygame.K_d]:
            self.direction.x = -1
        elif keys_held[pygame.K_d] and not keys_held[pygame.K_a]:
            self.direction.x = 1
        else:
            self.direction.x = 0

        # Y-Direction:
        if keys_held[pygame.K_w] and not keys_held[pygame.K_s]:
            self.direction.y = -1
        elif keys_held[pygame.K_s] and not keys_held[pygame.K_w]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        # Normalising direction vector (adjusting so that the magnitude is 1):
        # This means that the speed of the player is constant even when moving diagonally:
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Using item if space is pressed:
        if self.game.key_pressed(pygame.K_SPACE):
            self.use_item()

    def handle_item_collision(self):
        for item in self.level.get_item_tiles_in_frame():
            if item.get_collider().colliderect(self.collider):
                self.pick_up_item(item)

    def death_sequence(self):
        self.stats[self.CURRENT_HEALTH] = self.stats[self.FULL_HEALTH]
        self.level.set_done(True)
        self.game.show_death_screen()

    def pick_up_item(self, item):
        # Removing the item from the ground:
        item.set_owner(self)

        # Finding if there is an identical item in the inventory:
        item_in_inventory = self.get_item_by_name(item.get_name())

        if item_in_inventory is not None:
            # The item is already in the inventory, so just increase quantity:
            self.inventory[item_in_inventory] += 1
        else:
            # The item is not in the inventory, so add it:
            self.inventory[item] = 1

        # Update inventory in database:
        self.database_helper.update_player_inventory(self.inventory)

    def destroy_item(self, item):
        # Cannot destroy the Knight's Sword or if the item is not in the inventory:
        if item not in self.inventory or self.item_held.get_name() == KNIGHT_SWORD: return

        if self.inventory[item] > 1:
            self.inventory[item] -= 1
        else:
            del self.inventory[item]
            # Setting the item held as the Knight's Sword:
            self.item_held = self.get_item_by_name(KNIGHT_SWORD)
        # Updating database
        self.database_helper.update_player_inventory(self.inventory)

    def update(self):
        self.handle_input()
        self.handle_item_collision()
        self.update_cooldown_timers()
        self.move(self.BASE_SPEED * self.stats[self.SPEED_MULTIPLIER])
        self.update_animation_status()
        self.update_animation_frame()
        self.item_held.update()


class Enemy(Character):
    # Additional Stats for Enemy:
    # Enemies don't have speed multipliers since their stats is not variable:
    # The following are labels for the Stats dictionary, not the actual values:
    SPEED = 7
    ALERT_RADIUS = 8
    RECOVERY_DURATION = 9

    # NOTE: It is too demanding to calculate collision for every enemy every frame.
    #       So, enemies will only have collision once they are visible on-screen.

    def __init__(self, game, name, stats, inventory, animation_path, position=(0, 0)):
        super().__init__(game, stats, inventory, animation_path, position=position)

        self.name = name

        self.player = self.game.get_current_level().get_player()
        self.tile_size = self.level.get_tile_size()

        # Multiplier for the minimum distance for enemy to notice player:
        self.alert_multiplier = (1 / self.player.get_stats()[Player.STEALTH_MULTIPLIER])

        # The attack range should be just where the item held can reach:
        self.attack_range = max(self.item_held.get_collider().size)

        # Enemies need to go into recovery for a period of time after they attack,
        # so that they are not overpowered:
        self.in_recovery = True
        self.recovery_start_time = 0

        self.health_bar = ProgressBar(self.game, font_size=0.02,
                                      bar_size=self.game.pixel_to_unit_point((self.tile_size, 0.2 * self.tile_size,)),
                                      padding=game.pixel_to_unit(0.1 * self.tile_size),
                                      margin=0.005,
                                      frame_thickness=game.pixel_to_unit(0.05 * self.tile_size))

        self.name_text = TextLine(self.game, self.name, font_size=0.02,
                                  above=self.health_bar, padding=0, margin=0, frame_condition=View.NEVER)

    def set_direction_towards(self, point):
        # Set the direction towards a point
        value = point[0] - self.collider.centerx, point[1] - self.collider.centery
        if value != (0, 0):
            self.direction = pygame.Vector2(value).normalize()

    def death_sequence(self):
        # Remove from all lists within the level.
        # Iterate through inventory items and set owner as None
        # (so that inventory items are dropped onto the ground).
        for item in self.inventory:
            drop_chance = Utils().get_drop_chance(self.game, self.name, item.get_name())
            if decision(drop_chance):
                item.set_owner(None)

        self.game.get_current_level().remove_tile(self)

    def use_item(self):
        if self.in_recovery: return
        super().use_item()
        self.recovery_start_time = pygame.time.get_ticks()
        self.in_recovery = True

    def update_cooldown_timers(self):
        super().update_cooldown_timers()

        current_time = pygame.time.get_ticks()
        if current_time - self.recovery_start_time >= self.stats[self.RECOVERY_DURATION]:
            self.in_recovery = False

    def update_views(self):
        self.health_bar.set_progress(self.stats[self.CURRENT_HEALTH] / self.stats[self.FULL_HEALTH])
        offset = self.game.get_current_level().get_draw_offset()
        margin = self.health_bar.get_margin()
        self.health_bar.get_rect().midbottom = self.rect.midtop + pygame.Vector2(offset) - pygame.Vector2(0, margin)
        self.health_bar.update()
        self.health_bar.calculate_position()
        self.name_text.update()

    def update(self):
        distance = self.get_distance_to(self.player.get_rect().center)

        if not self.item_held.is_in_use():
            if distance * self.alert_multiplier < self.stats[self.ALERT_RADIUS] * self.level.get_tile_size():
                if distance < self.attack_range:
                    self.direction.update(0, 0)
                    self.use_item()
                else:
                    self.set_direction_towards(self.player.get_rect().center)
            else:
                self.direction.update(0, 0)


        self.update_views()
        self.update_cooldown_timers()
        self.move(self.stats[self.SPEED])
        self.update_animation_status()
        self.update_animation_frame()
        self.item_held.update()
