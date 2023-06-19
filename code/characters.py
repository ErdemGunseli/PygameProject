import pygame.image
from tile import Tile
from user_interface import *


class Character(Tile):  # [TESTED & FINALISED]
    # Default speed of game characters in tiles per second:
    BASE_SPEED = 5

    # Constants for Stat Types:
    FULL_HEALTH = 0
    CURRENT_HEALTH = 1
    DAMAGE_MULTIPLIER = 2
    SPEED_MULTIPLIER = 3

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

    # Cooldown for damage sound in ms to prevent it from becoming too annoying:
    DAMAGED_SOUND_COOLDOWN = 2000

    def __init__(self, game, stats, inventory, animation_path, position=(0, 0)):
        super().__init__(game, position, collider_ratio=(1, 1))

        # Character stats and inventory dictionaries:
        self.stats = stats
        self.inventory = inventory

        # How much the location of items being used by the character
        # should be offset so that they match with the character's hand:
        self.item_offsets = {UP: pygame.Vector2(self.tile_to_pixel((-0.2, 0))),
                             DOWN: pygame.Vector2(self.tile_to_pixel((-0.2, 0))),
                             LEFT: pygame.Vector2(self.tile_to_pixel((0, 0.21))),
                             RIGHT: pygame.Vector2(self.tile_to_pixel((0, 0.21)))}

        # For each item in the inventory, setting the owner as the character:
        for item in self.inventory: item.set_owner(self)

        # The sound to be played when the character is damaged:
        self.damaged_sound = pygame.mixer.Sound(WEAPON_USE)
        self.damaged_sound_start_time = 0
        self.damaged_sound_can_be_played = True

        # The item that is held by the character:
        # The player cannot remove all items from their inventory,
        # so there is always an item to hold:
        self.item_held = list(self.inventory)[0]

        # The direction in which the character is moving:
        self.direction = pygame.math.Vector2()

        # For very high frame rates, the number of pixels the character should travel per frame is less than 1.
        # For this reason, storing this value and adding it to the distance each frame:
        self.displacement_deficit = [0, 0]

        # Animations:
        self.animations = None
        self.animation_path = animation_path
        self.animation_status = self.DOWN_IDLE
        self.animation_increment_time = 0
        self.current_animation_frame_index = 0
        self.import_animations()
        # How long each animation frame should take:
        self.animation_frame_time = 150 / self.stats[self.SPEED_MULTIPLIER]

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

        # Filling the dictionary:
        for folder_name in self.animations.keys():
            final_path = self.animation_path + "/" + folder_name
            # Max size inherited from parent:
            self.animations[folder_name] = [resize_image(image, self.max_size) for image in import_images(final_path)]

    def update_animation_status(self):
        # Setting the animation status according to the character's direction:
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
            # Converting the animation to the item use variant if the character is using an item:
            self.set_use_animation()
        elif self.direction.magnitude() == 0:
            # Converting the animation to the idle variant if the character is idling
            self.set_idle_animation()

    def get_animation_status(self):
        return self.animation_status

    def update_animation_frame(self):
        current_time = pygame.time.get_ticks()

        animation_frames = self.animations[self.animation_status]

        # If the current time is greater than the time the animation frame was last updated,
        # and the duration each animation frame should last, updating the animation frame:
        if current_time >= self.animation_increment_time + self.animation_frame_time:
            self.animation_increment_time = current_time
            self.current_animation_frame_index += 1

            if self.current_animation_frame_index >= len(animation_frames):
                self.current_animation_frame_index = 0

            self.image = animation_frames[self.current_animation_frame_index]
            # Adjusting the collider according to the size of the new animation frame:
            self.rect.size = self.image.get_size()
            self.adjust_collider()

    def set_use_animation(self):
        # Converting the animation status to using item:
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
        # Converting the animation status to idling:
        match self.animation_status:
            case self.UP_MOVE | self.UP_USE:
                self.animation_status = self.UP_IDLE
            case self.DOWN_MOVE | self.DOWN_USE:
                self.animation_status = self.DOWN_IDLE
            case self.LEFT_MOVE | self.LEFT_USE:
                self.animation_status = self.LEFT_IDLE
            case self.RIGHT_MOVE | self.RIGHT_USE:
                self.animation_status = self.RIGHT_IDLE

    def use_item(self):
        self.set_use_animation()
        self.item_held.use()

    def get_item_offsets(self):
        return self.item_offsets

    def get_item_by_name(self, name):
        # Identical instances with different positions are not the same object.
        # To determine whether an item is in the inventory, we need to compare names:
        for inventory_item in self.inventory:
            if name == inventory_item.get_name():
                return inventory_item

    def get_item_selected(self):
        return self.item_held

    def increment_item_selected(self):
        # Cannot swap item while using it:
        if self.item_held.is_in_use(): return

        inventory_list = list(self.inventory)
        item_index = inventory_list.index(self.item_held) + 1
        if item_index >= len(inventory_list):
            item_index = 0
        self.item_held = (inventory_list[item_index])

    def update_cooldown_timers(self):
        # The timers for when an action requires a cooldown.
        # Measuring the difference in ticks to calculate time.
        # Alternatively, it is possible to do it by counting frames and multiplying by frame time:

        current_time = pygame.time.get_ticks()

        # Character can only play damage sound after a cooldown:
        if current_time - self.damaged_sound_start_time >= self.DAMAGED_SOUND_COOLDOWN:
            self.damaged_sound_can_be_played = True

    def handle_collision(self, axis):
        # A flag that can be used to test if a collision has occurred:
        collision_detected = False

        # Retrieving the collision objects:
        obstacle_sprites = self.level.get_obstacle_tiles_in_frame().copy()

        # Cannot collide with itself:
        if self in obstacle_sprites: obstacle_sprites.remove(self)

        # x-axis:
        if axis == 0:
            for obstacle in obstacle_sprites:
                obstacle_collider = obstacle.get_collider()
                # Checking if the obstacle has collided with the character:
                if obstacle_collider.colliderect(self.collider):
                    collision_detected = True
                    # Using the character's direction to handle collision:
                    if self.direction.x > 0:
                        # The character is moving right, move the character to the left of the obstacle:
                        self.collider.right = obstacle_collider.left
                    else:
                        # The character is moving left, move the character to the right of the obstacle:
                        self.collider.left = obstacle_collider.right
        # y-axis:
        else:
            for obstacle in obstacle_sprites:
                obstacle_collider = obstacle.get_collider()
                # Checking if the obstacle has collided with the character:
                if obstacle_collider.colliderect(self.collider):
                    collision_detected = True
                    # Using the character's direction to handle collision:
                    if self.direction.y > 0:
                        # The character is moving down, move the character above of the obstacle:
                        self.collider.bottom = obstacle_collider.top
                    else:
                        # The character is moving up, move the character below the obstacle:
                        self.collider.top = obstacle_collider.bottom

        return collision_detected

    def add_health(self, health_value):
        # Increases the character's health by the specified amount, to not exceed the maximum health:
        self.stats[self.CURRENT_HEALTH] += health_value
        if self.stats[self.CURRENT_HEALTH] > self.stats[self.FULL_HEALTH]:
            self.stats[self.CURRENT_HEALTH] = self.stats[self.FULL_HEALTH]

    def receive_damage(self, damage_value):

        # Playing damage sound:
        if self.damaged_sound_can_be_played:
            self.damaged_sound_start_time = pygame.time.get_ticks()
            self.damaged_sound.set_volume(self.game.get_audio_volume())
            self.damaged_sound.play()
            self.damaged_sound_can_be_played = False

        # Reducing current health:
        self.stats[self.CURRENT_HEALTH] -= damage_value

        # If the player has died, starting the death sequence:
        if self.stats[self.CURRENT_HEALTH] <= 0:
            self.death_sequence()

    def death_sequence(self):
        # Needs to be implemented by each child.
        pass

    def get_rect(self):
        return self.rect

    def get_stats(self):
        return self.stats

    def set_stats(self, stats):
        self.stats = stats

    def get_inventory(self):
        return self.inventory

    def move(self, speed):
        # For high frame rates, the number of pixels the character moves per frame could be less than 1 pixel per frame.
        # For this reason, storing the distance that the character was unable to travel each frame,
        # and moving the character by that distance when it reaches 1:
        speed_per_frame = speed * self.level.get_tile_size() * self.game.get_current_frame_time()

        # How much the character needs to move this frame, including how much it couldn't move in the previous frames:
        displacement_required = [speed_per_frame * axis + self.displacement_deficit[index] for index, axis in
                                 enumerate(self.direction)]

        # How many pixels of displacement is possible:
        # The position of a character needs to be an integer, and this can be less than 1 if the frame rate is too high:
        displacement_possible = [int(axis) for axis in displacement_required]

        # The displacement that the character was unable to carry out (running total from all frames):
        self.displacement_deficit = [displacement_required[0] - displacement_possible[0],
                                     displacement_required[1] - displacement_possible[1]]

        # Moving the player with horizontal and vertical components separately,
        # so that we know which side the player is colliding on:
        self.collider.x += displacement_possible[0]
        self.handle_collision(0)

        self.collider.y += displacement_possible[1]
        self.handle_collision(1)

        # Centering the rectangle image of the player to where the collider has just been moved:
        self.rect.center = self.collider.center

    def update(self):
        self.update_cooldown_timers()
        self.update_animation_status()
        self.update_animation_frame()
        self.item_held.update()


class Player(Character):  # [TESTED & FINALISED]
    STEALTH_MULTIPLIER = 4
    CURRENT_LEVEL_ID = 5

    # Where the animation files are located:
    ANIMATION_PATH = "../assets/images/characters/player/knight"

    def __init__(self, game, stats, inventory, position=(0, 0)):
        super().__init__(game, stats, inventory, self.ANIMATION_PATH, position=position)

        # Sounds:
        self.damaged_sound = pygame.mixer.Sound(PLAYER_DAMAGED)
        self.item_pickup_sound = pygame.mixer.Sound(ITEM_PICKUP)

    def handle_input(self):
        # Player cannot move if an item is in use:
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
        # This means that the speed of the player is constant regardless of direction:
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Using item if space is pressed, using item:
        if self.game.key_pressed(pygame.K_SPACE):
            self.use_item()

    def handle_item_collision(self):
        # Checking collision with item tiles in frame, and adding them to the inventory if there is a collision:
        for item in self.level.get_item_tiles_in_frame():
            if item.get_collider().colliderect(self.collider):
                self.pick_up_item(item)

    def pick_up_item(self, item):
        # Removing the item from the ground and setting player as the owner:
        item.set_owner(self)

        # Playing sound:
        self.item_pickup_sound.set_volume(self.game.get_audio_volume())
        self.item_pickup_sound.play()

        # Determining if there is an identical item in the inventory:
        item_in_inventory = self.get_item_by_name(item.get_name())

        if item_in_inventory is not None:
            # If an identical item is already in the inventory, just increasing quantity:
            self.inventory[item_in_inventory] += 1
        else:
            # If an item is not in the inventory, adding it:
            self.inventory[item] = 1

    def destroy_item(self, item):
        # Cannot destroy the Knight's Sword or an item that is not in the inventory:
        if item not in self.inventory or self.item_held.get_name() == KNIGHT_SWORD: return

        if self.inventory[item] > 1:
            # If quantity is greater than 1, just reducing it:
            self.inventory[item] -= 1
        else:
            # Otherwise, deleting item from the inventory:
            del self.inventory[item]
            # Setting the item held as the Knight's Sword:
            self.item_held = self.get_item_by_name(KNIGHT_SWORD)

    def death_sequence(self):
        # Restoring health back to full:
        self.stats[self.CURRENT_HEALTH] = self.stats[self.FULL_HEALTH]
        # Restarting the same level:
        self.level.set_done(True)
        # Starting the death music and showing the death screen:
        self.game.set_music(DEATH_MUSIC)
        self.game.show_death_screen()

    def update(self):
        super().update()
        self.handle_input()
        self.handle_item_collision()
        self.move(self.BASE_SPEED * self.stats[self.SPEED_MULTIPLIER])


class Enemy(Character):  # [TESTED & FINALISED]
    # Additional Stats for Enemy:
    # Enemies don't have speed multipliers since their stats are constant:
    # The following are labels for the Stats dictionary, not the actual values:
    ALERT_RADIUS = 7
    RECOVERY_DURATION = 8

    def __init__(self, game, name, stats, inventory, animation_path, position=(0, 0)):
        super().__init__(game, stats, inventory, animation_path, position=position)

        # The name displayed above the enemy's head:
        self.name = name

        # The enemy has the player has an attribute for pathfinding, awareness radius, etc.
        self.player = self.level.get_player()
        self.tile_size = self.level.get_tile_size()

        # Multiplier for the minimum distance for the enemy to notice the player:
        self.alert_multiplier = self.player.get_stats()[Player.STEALTH_MULTIPLIER]

        # The attack range should be just where the item held can reach the player:
        self.attack_range = max(self.item_held.get_collider().size)
        # Enemies need to go into recovery for a period of time after they attack:
        self.in_recovery = True
        self.recovery_start_time = 0

        # Sound to be played upon taking damage:
        self.damaged_sound = pygame.mixer.Sound(ENEMY_DAMAGED)

        # Sound played by enemy upon death:
        self.death_sound = pygame.mixer.Sound(ENEMY_DEATH)

        # The health bar above the enemy's head:
        self.health_bar = ProgressBar(self.game, font_size=0.02,
                                      start_progress=self.stats[self.CURRENT_HEALTH] / self.stats[self.FULL_HEALTH],
                                      size=self.game.pixel_to_unit_point((self.tile_size, 0.2 * self.tile_size,)),
                                      padding=game.pixel_to_unit(0.1 * self.tile_size),
                                      margin=0.005,
                                      frame_thickness=game.pixel_to_unit(0.05 * self.tile_size))

        # The text object above the enemy's head, showing the enemy's name:
        self.name_tag = TextLine(self.game, self.name, font_size=0.02,
                                 above=self.health_bar, padding=0, margin=0, frame_condition=View.NEVER)

    def set_direction_towards(self, point):
        # Setting the direction of the enemy towards the specified point:
        direction = point[0] - self.collider.centerx, point[1] - self.collider.centery
        # Magnitude 0 vector cannot be normalised:
        if direction != (0, 0):
            self.direction = pygame.Vector2(direction).normalize()

    def update_cooldown_timers(self):
        super().update_cooldown_timers()
        # Also updating recovery cooldown:
        current_time = pygame.time.get_ticks()
        if current_time - self.recovery_start_time >= self.stats[self.RECOVERY_DURATION]:
            self.in_recovery = False

    def death_sequence(self):
        for item in self.inventory:
            # Obtaining the chance that the item gets dropped:
            drop_chance = Utils().get_drop_chance(self.name, item.get_name())
            if decision(drop_chance):
                # Setting the owner as None, so that the item appears on the ground:
                item.set_owner(None)

        # Playing death sound:
        self.death_sound.set_volume(self.game.get_audio_volume())
        self.death_sound.play()

        # Removing the enemy itself from the level:
        self.game.get_current_level().remove_tile(self)

    def use_item(self):
        # Enemy cannot use the item if it is currently in recovery:
        if self.in_recovery: return
        super().use_item()
        self.recovery_start_time = pygame.time.get_ticks()
        self.in_recovery = True

    def update_views(self):
        # Setting health bar progress according to enemy health:
        self.health_bar.set_progress(self.stats[self.CURRENT_HEALTH] / self.stats[self.FULL_HEALTH])

        # Obtaining draw offset from the level:
        offset = self.game.get_current_level().get_draw_offset()
        margin = self.health_bar.get_margin()
        # Manually placing the health bar on top of the enemy:
        self.health_bar.get_rect().midbottom = self.rect.midtop + pygame.Vector2(offset) - pygame.Vector2(0, margin)
        # Aligning the individual rectangles within the health bar:
        self.health_bar.align_rectangles()
        # Triggering for the health bar and all its relatives to calculate their positions:
        self.health_bar.calculate_position()

        # Updating the views:
        self.health_bar.update()
        self.name_tag.update()

    def ai(self):
        # Obtaining distance to player:
        distance = self.get_distance_to(self.player.get_rect().center)

        if not self.item_held.is_in_use():
            if distance * self.alert_multiplier < self.stats[self.ALERT_RADIUS] * self.level.get_tile_size():
                # If distance is less than the length of the weapon being held by the enemy, attacking the player:
                if distance < self.attack_range:
                    self.direction.update(0, 0)
                    self.use_item()
                else:
                    # Setting the direction of the enemy towards the player:
                    self.set_direction_towards(self.player.get_rect().center)
            else:
                # If the enemy is using an item, it cannot move:
                self.direction.update(0, 0)

    def update(self):
        super().update()
        self.ai()
        self.update_views()
        self.move(self.BASE_SPEED * self.stats[self.SPEED_MULTIPLIER])

