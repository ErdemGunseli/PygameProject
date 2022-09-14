from strings import *
from tile import Tile
from utils import *
from user_interface import Text


class Player(Tile):
    # Constants for player stat types:
    CURRENT_LEVEL_ID = 0
    FULL_HEALTH = 1
    CURRENT_HEALTH = 2
    SPEED_MULTIPLIER = 3  # Tiles per second
    MELEE_DAMAGE_MULTIPLIER = 4
    MELEE_COOLDOWN_MULTIPLIER = 5
    MAGIC_DAMAGE_MULTIPLIER = 6
    MAGIC_COOLDOWN_MULTIPLIER = 7
    INVULNERABILITY_DURATION = 8


    # Minimum and maximum values for starting player stats:
    MIN_HEALTH = 0.75
    MAX_HEALTH = 1.25
    MIN_SPEED = 0.75
    MAX_SPEED = 1.25
    MIN_MAGIC = 0.75
    MAX_MAGIC = 1.25
    MIN_ATTACK = 0.75
    MAX_ATTACK = 1.25

    # Where the animation files are located:
    ANIMATION_PATH = "../assets/images/player"

    # Animation folder names:
    UP_MOVE = "up_move"
    DOWN_MOVE = "down_move"
    LEFT_MOVE = "left_move"
    RIGHT_MOVE = "right_move"
    UP_IDLE = "up_idle"
    DOWN_IDLE = "down_idle"
    LEFT_IDLE = "left_idle"
    RIGHT_IDLE = "right_idle"
    UP_ATTACK = "up_attack"
    DOWN_ATTACK = "down_attack"
    LEFT_ATTACK = "left_attack"
    RIGHT_ATTACK = "right_attack"

    # Animation frame durations in ms:
    ANIMATION_FRAME_TIME = 150

    def __init__(self, game, position, stats, inventory):

        super().__init__(game, position, collider_ratio=(1, 1))
        self.database_helper = game.get_database_helper()

        # Player stats and inventory dictionaries:
        self.stats = stats
        self.inventory = inventory

        for item in inventory:
            # How much the image should be offset by, so that the item aligns with the player's hand:
            item.set_image_offsets({UP: pygame.Vector2(self.tile_to_pixel((-0.2, 0))),
                                   DOWN: pygame.Vector2(self.tile_to_pixel((-0.2, 0))),
                                   LEFT: pygame.Vector2(self.tile_to_pixel((0, 0.2))),
                                   RIGHT: pygame.Vector2(self.tile_to_pixel((0, 0.2)))})

        # Whether the player is using the item held:
        self.using_item = False
        self.item_use_start_time = 0
        # Whether the player is currently invulnerable
        # (the player is made invulnerable for a short period of time when taking damage):
        self.invulnerable = True
        self.invulnerability_start_time = 0
        self.item_selected = None
        self.item_use_cooldown = None
        self.set_item_held(list(self.inventory)[0])

        # Pygame provides vectors in 2D and 3D, and allows operations to be made using them:
        # This is the direction at which the player is moving:
        self.direction = pygame.math.Vector2()

        # For very high frame rates, the number of pixels the player should travel per frame is less than 1.
        # For this reason, storing this value and adding it to the distance each frame:
        self.displacement_deficit = [0, 0]

        # Speed in tiles per second:
        self.speed = 5

        self.animations = None
        self.animation_status = self.DOWN_IDLE
        self.animation_increment_time = 0
        self.current_animation_frame_index = 0
        self.import_animations()

        print("Player Stats: {}".format(self.stats))
        print("Player Inventory: {}".format(self.inventory))


    def import_animations(self):
        # A dictionary of animation folder names and lists of images in the folders:

        self.animations = {
            # Walking
            self.UP_MOVE: [], self.DOWN_MOVE: [], self.LEFT_MOVE: [], self.RIGHT_MOVE: [],
            # Stopping
            self.UP_IDLE: [], self.DOWN_IDLE: [], self.LEFT_IDLE: [], self.RIGHT_IDLE: [],
            # Attacking
            self.UP_ATTACK: [], self.DOWN_ATTACK: [], self.LEFT_ATTACK: [], self.RIGHT_ATTACK: []
        }

        for folder_name in self.animations.keys():
            final_path = self.ANIMATION_PATH + "/" + folder_name
            self.animations[folder_name] = [Utils.resize_image(image, self.max_size)
                                            for image in Utils.import_folder(final_path)]

    def handle_input(self):
        # Player cannot control character if using item:
        if self.using_item:
            self.direction.update(0, 0)
            return

        # Getting the keys that are being held down:
        keys_held = pygame.key.get_pressed()

        # Calculating the correct direction according to the keys held:
        if keys_held[pygame.K_a] and not keys_held[pygame.K_d]:
            self.direction.x = -1
            self.animation_status = self.LEFT_MOVE
        elif keys_held[pygame.K_d] and not keys_held[pygame.K_a]:
            self.direction.x = 1
            self.animation_status = self.RIGHT_MOVE
        else:
            self.direction.x = 0

        if keys_held[pygame.K_w] and not keys_held[pygame.K_s]:
            self.direction.y = -1
            self.animation_status = self.UP_MOVE
        elif keys_held[pygame.K_s] and not keys_held[pygame.K_w]:
            self.direction.y = 1
            self.animation_status = self.DOWN_MOVE

        else:
            self.direction.y = 0

        # Normalising the direction vector such that the speed of motion
        # is constant even if the player is moving diagonally:
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Attack and magic input should trigger once per key-press:
        # Attack input:
        if self.game.key_pressed(pygame.K_SPACE) and not self.using_item:
            self.use_item()
        self.set_idle_animation()

    def use_item(self):
        self.using_item = True
        self.item_use_start_time = pygame.time.get_ticks()
        self.set_attack_animation()

    def increment_item_selected(self):
        # Cannot swap item while using it:
        if self.using_item: return
        inventory_list = list(self.inventory)
        item_index = inventory_list.index(self.item_selected) + 1
        if item_index >= len(inventory_list):
            item_index = 0
        self.set_item_held(inventory_list[item_index])

    def set_attack_animation(self):
        match self.animation_status:
            case self.UP_MOVE | self.UP_IDLE:
                self.animation_status = self.UP_ATTACK
            case self.DOWN_MOVE | self.DOWN_IDLE:
                self.animation_status = self.DOWN_ATTACK
            case self.LEFT_MOVE | self.LEFT_IDLE:
                self.animation_status = self.LEFT_ATTACK
            case self.RIGHT_MOVE | self.RIGHT_IDLE:
                self.animation_status = self.RIGHT_ATTACK

    def set_idle_animation(self):
        if self.direction.magnitude() == 0 and not self.using_item:
            match self.animation_status:
                case self.UP_MOVE | self.UP_ATTACK:
                    self.animation_status = self.UP_IDLE
                case self.DOWN_MOVE | self.DOWN_ATTACK:
                    self.animation_status = self.DOWN_IDLE
                case self.LEFT_MOVE | self.LEFT_ATTACK:
                    self.animation_status = self.LEFT_IDLE
                case self.RIGHT_MOVE | self.RIGHT_ATTACK:
                    self.animation_status = self.RIGHT_IDLE

    def set_item_held(self, item):
        self.item_selected = item
        self.item_use_cooldown = self.item_selected.get_cooldown()

    def update_cooldown_timers(self):
        # The timers for when an action requires a cooldown.
        # Measuring the difference in ticks to calculate time.
        # Alternatively, it is possible to do it by counting frames and multiplying by frame time:

        current_time = pygame.time.get_ticks()

        if current_time - self.item_use_start_time >= self.item_use_cooldown:
            self.using_item = False

        if current_time - self.invulnerability_start_time >= self.stats[self.INVULNERABILITY_DURATION]:
            self.invulnerable = False

    def move_player(self, speed):
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

    def handle_collision(self, axis):
        # Retrieving the collision objects:
        obstacle_sprites = self.level.get_obstacle_tiles_in_frame()

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

    def update_animation(self):
        current_time = pygame.time.get_ticks()

        animation_frames = self.animations[self.animation_status]

        if current_time >= self.animation_increment_time + self.ANIMATION_FRAME_TIME:
            self.animation_increment_time = current_time
            if self.current_animation_frame_index < len(animation_frames) - 1:
                self.current_animation_frame_index += 1
            else:
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
        self.stats[self.CURRENT_HEALTH] = self.stats[self.FULL_HEALTH]
        self.level.set_done(True)
        self.game.show_death_screen()

    def get_rect(self):
        return self.rect

    def get_stats(self):
        return self.stats

    def set_stats(self, stats):
        self.stats = stats

    def get_inventory(self):
        return self.inventory

    def set_inventory(self, inventory):
        self.inventory = inventory

    def get_item_selected(self):
        return self.item_selected

    def draw(self, draw_offset):
        super().draw(draw_offset)
        if self.using_item:
            self.item_selected.draw(draw_offset, self)


    def update(self):
        self.handle_input()
        self.update_cooldown_timers()
        self.move_player(self.speed * self.stats[self.SPEED_MULTIPLIER])
        self.update_animation()
