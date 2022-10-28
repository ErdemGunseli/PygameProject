import pygame.display
from pytmx import *
from items import *
from tile import Tile
from utils import *
from colours import *


# TODO: DO NOT MODIFY UNNECESSARILY BEFORE FINISHING PROJECT - Maybe at the end:
#  Make some Optimisations
#  Create variable minimum tile count 10-30
#  Order Layers & Draw in order for Improved Depth Effect


class Level:  # [DONE]
    # Layer Names:
    GROUND = "Ground"
    RIVER = "River"
    ROAD = "Road"
    PEBBLES = "Pebbles"
    PLANTS = "Plants"
    TREES = "Trees"
    ROCKS = "Rocks"
    BUILDINGS = "Buildings"
    QUEST_BOARD = "Quest Board"
    BARRIERS = "Barriers"
    COLLIDERS = "Colliders"

    # The resolution of the tile images:
    TILE_RESOLUTION = 256

    def __init__(self, game, level_id, min_tile_count=15):
        # Player & Quest Board will be set when the map is created:
        self.player = None
        self.quest_board = None
        self.quest_board_views = None
        self.txt_info = None
        self.btn_next_level = None
        self.btn_restart_level = None
        self.txt_error = None
        self.game = game
        self.database_helper = game.get_database_helper()

        # Whether the level is done:
        self.done = False

        self.display = pygame.display.get_surface()
        # Calculating the pixel size of each tile according to how many should fit on-screen:
        self.tile_size = min(self.display.get_rect().width, self.display.get_rect().height) // min_tile_count
        # Setting the scale factor for the correct conversion of the position of objects:
        self.scale_factor = self.TILE_RESOLUTION / self.tile_size
        self.display_center = self.display.get_rect().center

        # Importing map data:
        self.map_set_up = False
        self.level_id = level_id
        # self.path = self.database_helper.get_map_path(level_id) # TODO: REMOVE
        self.path = Utils().get_level_path(self.level_id)
        self.tmx_data = load_pygame(self.path)

        # The size of the level excluding the world border:
        self.level_size = ((self.tmx_data.width - 2) * self.tile_size, (self.tmx_data.height - 2) * self.tile_size)

        # Background colour for map:
        # self.background_colour = self.database_helper.get_background_colour(self.level_id) # TODO: REMOVE
        self.background_colour = Utils().get_level_colour(self.level_id)

        # Draw offset amount such that the player is always centred:
        self.draw_offset = pygame.math.Vector2()

        # Groups determining how the sprites should be categorised.
        # Groups are not mutually exclusive:
        self.all_tiles = pygame.sprite.Group()  # All the sprites in the level.
        self.flat_tiles = pygame.sprite.Group()  # Sprites with no depth effect - items in the background.
        self.depth_tiles = pygame.sprite.Group()  # Sprites with depth effect - 3D items to be represented in 2D.
        self.dynamic_tiles = pygame.sprite.Group()  # Sprites that should be updated.
        self.obstacle_tiles = pygame.sprite.Group()  # Sprites that have collision.
        self.item_tiles = pygame.sprite.Group()  # Sprites that are items on the ground.
        self.hostile_tiles = pygame.sprite.Group()  # Sprites that are hostile to the player.
        self.vulnerable_tiles = pygame.sprite.Group()  # Sprites that have health.

        # Groups for tiles in frame (re-calculated each frame):
        self.depth_tiles_in_frame = pygame.sprite.Group()  # Depth sprites that are on-screen.
        self.flat_tiles_in_frame = pygame.sprite.Group()  # Flat sprites that are on-screen.
        self.obstacle_tiles_in_frame = pygame.sprite.Group()  # Obstacle sprites that are on-screen.
        self.item_tiles_in_frame = pygame.sprite.Group()  # Item sprites that are on-screen.

        # The map set up is triggered externally by the game class.

    def get_id(self):
        return self.level_id

    def set_up_map(self):
        if self.map_set_up: return
        self.map_set_up = True

        # Setting up layers:
        self.set_up_layer(self.RIVER, visible=True, depth=False, obstacle=False)
        self.set_up_layer(self.ROAD, visible=True, depth=False, obstacle=False)
        self.set_up_layer(self.PEBBLES, collider_ratio=(0.5, 0.5), visible=True, depth=True, obstacle=True)
        self.set_up_layer(self.PLANTS, visible=True, depth=True, obstacle=False)
        self.set_up_layer(self.TREES, collider_ratio=(0.6, 0.4), visible=True, depth=True, obstacle=True)
        self.set_up_layer(self.ROCKS, collider_ratio=(0.7, 0.7), visible=True, depth=True, obstacle=True)
        # Because buildings can have different shapes, they have custom colliders:
        self.set_up_layer(self.BUILDINGS, visible=True, depth=True, obstacle=False)
        self.set_up_layer(self.QUEST_BOARD, visible=True, depth=True, obstacle=False)

        # Setting up Items:
        for item_name in ITEM_NAMES:
            print(item_name)
            self.set_up_layer(item_name, visible=True, depth=True, obstacle=False, dynamic=True, item=True)

        # Setting up Characters:
        self.set_up_layer(PLAYER, visible=True, depth=True, obstacle=False, dynamic=True, vulnerable=True)
        for enemy_name in ENEMY_NAMES:
            self.set_up_layer(enemy_name, visible=True, depth=True, obstacle=False, dynamic=True, vulnerable=True,
                              hostile=True)
        # Barriers and colliders are invisible, but have collision:
        self.set_up_layer(self.BARRIERS, collider_ratio=(1, 1), visible=False, obstacle=True)
        self.set_up_layer(self.COLLIDERS, collider_ratio=(1, 1), visible=False, obstacle=True)


    def set_up_layer(self, layer_name, collider_ratio=(0.9, 0.9), visible=True, depth=True, obstacle=True,
                     dynamic=False, item=False, hostile=False, vulnerable=False):
        # If a rotated or flipped object/tile is used,
        # pytmx is supposed to adjust the image automatically and return the correct surface.
        # However, this does not work for me, and I can't figure out why.
        # For this reason, not using rotated or flipped objects/tiles,
        # creating a duplicate flipped/rotated image is absolutely necessary.

        # Validating layer name:
        # Not creating the layer if it has been set as invisible in Tiled - useful for debugging:
        if layer_name not in [layer.name for layer in self.tmx_data.visible_layers]: return

        # Returns a TiledTileLayer or TiledObjectGroup instance.
        # TiledTileLayer.tiles() returns the position and surface of each tile in the layer.
        # TiledObjectGroup returns the position, size and surface of each object in the layer.
        layer = self.tmx_data.get_layer_by_name(layer_name)

        # If object layer:
        if isinstance(layer, TiledObjectGroup):
            for map_object in layer:
                if map_object.image is not None:
                    tile = Tile(self.game, (map_object.x / self.scale_factor, map_object.y / self.scale_factor),
                                size=(
                                    map_object.width / self.TILE_RESOLUTION, map_object.height / self.TILE_RESOLUTION),
                                # The aspect ratio of objects should not be protected:
                                collider_ratio=collider_ratio, image=map_object.image, protect_aspect_ratio=False)

                    if layer_name == self.QUEST_BOARD:
                        self.quest_board = tile
                        self.set_up_quest_board_views()
                    # Adding to correct groups:
                    self.add_tile(tile, visible, depth, obstacle, dynamic, item, hostile, vulnerable)

        # If tile layer:
        elif isinstance(layer, TiledTileLayer):
            for x, y, surface in layer.tiles():
                if surface is not None:
                    # Converting the position of the tile to pixels:
                    tile_position = (x * self.tile_size, y * self.tile_size)

                    # For special tiles such as the player or enemies, the relevant class is instantiated:
                    if layer_name == PLAYER:
                        self.player = self.database_helper.get_player()
                        tile = self.player
                        tile.set_top_left(tile_position)
                    elif layer_name in ENEMY_NAMES:
                        tile = Utils().get_enemy(self.game, layer_name)
                        # Setting the position of the player using its collider:
                        tile.set_top_left(tile_position)
                    elif layer_name in ITEM_NAMES:
                        tile = Utils().get_item(self.game, layer_name)
                        tile.set_top_left(tile_position)
                    else:
                        # Other objects:
                        tile = Tile(self.game, tile_position, collider_ratio=collider_ratio, image=surface,
                                    # The aspect ratio of tiles should be protected:
                                    protect_aspect_ratio=True)

                    # Adding to correct groups:
                    self.add_tile(tile, visible, depth, obstacle, dynamic, item, hostile, vulnerable)

    def add_tile(self, tile, visible=True, depth=True, obstacle=True, dynamic=False, item=False, hostile=False,
                 vulnerable=False):
        if visible:
            if depth: self.depth_tiles.add(tile)
            else: self.flat_tiles.add(tile)
        if obstacle: self.obstacle_tiles.add(tile)
        if dynamic: self.dynamic_tiles.add(tile)
        if item: self.item_tiles.add(tile)
        if hostile: self.hostile_tiles.add(tile)
        if vulnerable: self.vulnerable_tiles.add(tile)
        self.all_tiles.add(tile)

    def remove_tile(self, tile):
        self.all_tiles.remove(tile)
        self.flat_tiles.remove(tile)
        self.depth_tiles.remove(tile)
        self.dynamic_tiles.remove(tile)
        self.obstacle_tiles.remove(tile)
        self.item_tiles.remove(tile)
        self.hostile_tiles.remove(tile)
        self.vulnerable_tiles.remove(tile)

        # Groups for tiles in frame (re-calculated each frame):
        self.depth_tiles_in_frame.remove(tile)
        self.flat_tiles_in_frame.remove(tile)
        self.obstacle_tiles_in_frame.remove(tile)
        self.item_tiles_in_frame.remove(tile)

    def draw_map(self):
        # Calculating how far the player is from the centre of the screen,
        # and determining correct offset such that the player is back at the centre:
        self.draw_offset.x = self.display_center[0] - self.player.get_rect().centerx
        self.draw_offset.y = self.display_center[1] - self.player.get_rect().centery

        # Checking which sprites are on-screen, as we only need to be concerned with those:
        self.depth_tiles_in_frame = self.get_tiles_in_frame(self.depth_tiles, self.player)
        self.obstacle_tiles_in_frame = self.get_tiles_in_frame(self.obstacle_tiles, self.player)
        self.flat_tiles_in_frame = self.get_tiles_in_frame(self.flat_tiles, self.player)
        self.item_tiles_in_frame = self.get_tiles_in_frame(self.item_tiles, self.player)

        # First drawing sprites without depth effect since these are at the background:
        for tile in self.flat_tiles_in_frame:
            tile.draw(self.draw_offset)

        # Sorting sprites with depth effect in ascending order of y-position:
        for tile in sorted(self.depth_tiles_in_frame, key=lambda sprite_in_list: sprite_in_list.rect.centery):
            tile.draw(self.draw_offset)

    def get_tiles_in_frame(self, group, character):
        sprites_in_frame = pygame.sprite.Group()
        screen_rect = self.game.get_rect().copy()
        screen_rect.center = character.get_rect().center

        for sprite in group:
            if pygame.Rect.colliderect(sprite.rect, screen_rect):
                sprites_in_frame.add(sprite)
        return sprites_in_frame

    def get_size(self):
        # Returns the level size, excluding the world borders:
        return self.level_size

    def get_background_colour(self):
        return self.background_colour

    def get_id(self):
        return self.level_id

    def get_player(self):
        return self.player

    def get_obstacle_tiles_in_frame(self):
        return self.obstacle_tiles_in_frame

    def get_obstacle_tiles(self):
        return self.obstacle_tiles

    def get_item_tiles_in_frame(self):
        return self.item_tiles_in_frame

    def get_vulnerable_tiles(self):
        return self.vulnerable_tiles

    def get_all_tiles(self):
        return self.all_tiles

    def get_tile_size(self):
        return self.tile_size

    def get_tmx_data(self):
        return self.tmx_data

    def get_tile_size(self):
        return self.tile_size

    def get_scale_factor(self):
        return self.scale_factor

    def get_draw_offset(self):
        return self.draw_offset

    def is_done(self):
        return self.done

    def set_done(self, value):
        self.done = value

    def draw_hostile_indicators(self):
        # Calculating points of intersection between display lines
        # and lines between player and hostile sprites to draw indicators:
        rect = self.display.get_rect()
        rect.center = self.player.get_rect().center
        top = (rect.topleft, rect.topright)
        right = (rect.topright, rect.bottomright)
        bottom = (rect.bottomright, rect.bottomleft)
        left = (rect.bottomleft, rect.topleft)
        display_lines = [top, right, bottom, left]
        for hostile in self.hostile_tiles:
            player_to_hostile = (self.player.get_collider().center, hostile.get_collider().center)
            if self.player.get_distance_to(hostile.get_collider().center) < \
                    Utils.SHOW_INDICATOR_RADIUS * self.tile_size * self.player.get_stats()[Player.STEALTH_MULTIPLIER]:
                for line in display_lines:
                    intersection = get_segment_intersection(player_to_hostile, line)
                    if intersection is not None:
                        self.draw_indicator(intersection + self.draw_offset, RED)

    def draw_quest_board_indicator(self):
        # Calculating points of intersection between display lines
        # and lines between player and hostile sprites to draw indicators:
        rect = self.display.get_rect()
        rect.center = self.player.get_rect().center
        top = (rect.topleft, rect.topright)
        right = (rect.topright, rect.bottomright)
        bottom = (rect.bottomright, rect.bottomleft)
        left = (rect.bottomleft, rect.topleft)
        display_lines = [top, right, bottom, left]

        player_to_board = (self.player.get_collider().center, self.quest_board.get_collider().center)
        for line in display_lines:
            intersection = get_segment_intersection(player_to_board, line)
            if intersection is not None:
                self.draw_indicator(intersection + self.draw_offset, GREEN)

    def set_up_quest_board_views(self):
        self.quest_board_views = []

        self.txt_info = Text(self.game, font_size=0.02, above=self.btn_next_level, margin=0.01,
                             text_alignment=Text.CENTRE, frame_thickness=0, text_colour=WHITE)
        self.quest_board_views.append(self.txt_info)

        self.btn_restart_level = Button(self.game, text_string=RESTART_LEVEL, to_left_of=self.txt_info,
                                        font_size=0.02, margin=0.01, frame_condition=View.ALWAYS, frame_thickness=0,
                                        text_colour=WHITE, text_hover_colour=WHITE)
        self.quest_board_views.append(self.btn_restart_level, )

        self.btn_next_level = Button(self.game, text_string=NEXT_LEVEL, to_right_of=self.txt_info, font_size=0.02,
                                     margin=0.01, frame_condition=View.ALWAYS, frame_thickness=0, text_colour=WHITE,
                                     text_hover_colour=WHITE)
        self.quest_board_views.append(self.btn_next_level)

        self.txt_error = TextLine(self.game, text_string=NEXT_LEVEL_ERROR, above=self.txt_info, font_size=0.02,
                                  margin=0.01, visible=False, text_colour=WHITE, frame_colour=RED, frame_thickness=0,
                                  frame_condition=View.ALWAYS)
        self.quest_board_views.append(self.txt_error)

    def update_quest_board_data(self):
        self.txt_info.get_rect().midbottom = self.quest_board.get_rect().midtop + pygame.Vector2(
            self.draw_offset) - pygame.Vector2(0, self.txt_info.get_margin())

        self.txt_info.calculate_position()

        self.txt_info.set_text(QUEST_BOARD_TEXT.format(len(self.item_tiles), len(self.hostile_tiles)))
        self.txt_info.get_text_lines()[0].set_font_size(0.04)

        if len(self.hostile_tiles) == 0:
            self.btn_next_level.set_text_colour(GREEN)
        else:
            self.btn_next_level.set_text_colour(RED)

        if self.btn_restart_level.clicked():
            self.set_done(True)
        elif self.btn_next_level.clicked():
            if len(self.hostile_tiles) == 0:
                self.set_done(True)
            else:
                self.txt_error.set_visibility(True)
        elif self.txt_error.clicked():
            self.txt_error.set_visibility(False)

        for view in self.quest_board_views: view.update()

    def draw_indicator(self, point, colour):
        pygame.draw.circle(self.display, colour, point, Utils.INDICATOR_RADIUS * self.tile_size)

    def update(self):
        self.draw_map()
        self.dynamic_tiles.update()
        self.draw_hostile_indicators()
        if self.quest_board is not None:
            self.draw_quest_board_indicator()
            self.update_quest_board_data()

        # print(self.item_tiles)