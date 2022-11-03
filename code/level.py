import pygame.display
from pytmx import *
from items import *
from tile import *
from utils import *
from colours import *


class Level:  # [TESTED & FINALISED]
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

    def __init__(self, game, level_id):
        # Attributes for game and database:
        self.game = game
        self.database_helper = game.get_database_helper()

        # Whether the level is done:
        self.done = False

        # Player attribute will be set when the level is created:
        self.player = None
        # Quest Board attributes will be set when the level is created:
        self.quest_board = None
        self.quest_board_views = None
        self.txt_info = None
        self.btn_next_level = None
        self.btn_restart_level = None
        self.txt_level_name = None
        self.txt_error = None

        # Setting up display:
        self.display = pygame.display.get_surface()
        self.display_rect = self.display.get_rect()
        # Calculating the pixel size of each tile according to how many should fit on-screen:
        min_tile_count = Utils().LEVELS[level_id][Utils.MIN_TILE_COUNT]
        self.tile_size = min(self.display_rect.width, self.display_rect.height) // min_tile_count
        # Setting the scale factor for the correct conversion of the position of objects:
        self.scale_factor = self.TILE_RESOLUTION / self.tile_size

        # The 4 line segments (represented as groups of 2 points) that make up the display:
        # Used for drawing indicators where lines connecting items of interest and the screen lines intersect:
        self.display_lines = []

        # Importing map data:
        self.map_set_up = False
        self.id = level_id
        # Obtaining a list of item/object positions and surfaces by layer using pytmx:
        self.tmx_data = load_pygame(Utils().get_level_path(self.id))

        # Background colour of the map:
        self.background_colour = Utils().get_level_colour(self.id)

        # Draw offset amount for the simulated camera:
        self.draw_offset = pygame.math.Vector2()

        # Groups determining how the sprites should be categorised.
        # Groups are not mutually exclusive:
        self.all_tiles = pygame.sprite.Group()  # All the sprites in the level.
        self.flat_tiles = pygame.sprite.Group()  # Sprites with no depth effect - flat items in the background.
        self.depth_tiles = pygame.sprite.Group()  # Sprites with depth effect - 3D items to be represented in 2D.
        self.dynamic_tiles = pygame.sprite.Group()  # Sprites that should be updated if they are on-screen.
        self.obstacle_tiles = pygame.sprite.Group()  # Sprites that have collision.
        self.item_tiles = pygame.sprite.Group()  # Sprites that are items on the ground.
        self.hostile_tiles = pygame.sprite.Group()  # Sprites that are hostile to the player.
        self.vulnerable_tiles = pygame.sprite.Group()  # Sprites that have health.

        # Groups for tiles in frame (re-calculated each frame):
        self.flat_tiles_in_frame = pygame.sprite.Group()  # Flat sprites that are on-screen.
        self.depth_tiles_in_frame = pygame.sprite.Group()  # Depth sprites that are on-screen.
        self.dynamic_tiles_in_frame = pygame.sprite.Group()  # Dynamic sprites that are on-screen
        self.obstacle_tiles_in_frame = pygame.sprite.Group()  # Obstacle sprites that are on-screen.
        self.item_tiles_in_frame = pygame.sprite.Group()  # Item sprites that are on-screen.

    def get_id(self):
        return self.id

    def set_up_map(self):
        if self.map_set_up: return
        self.map_set_up = True

        # Setting up individual layers, describing how the sprites from the layers should be grouped:
        self.set_up_layer(self.RIVER, visible=True, depth=False, obstacle=False)
        self.set_up_layer(self.ROAD, visible=True, depth=False, obstacle=False)
        self.set_up_layer(self.PEBBLES, collider_ratio=(0.5, 0.5), visible=True, depth=True, obstacle=True)
        self.set_up_layer(self.PLANTS, visible=True, depth=True, obstacle=False)
        self.set_up_layer(self.TREES, collider_ratio=(0.6, 0.4), visible=True, depth=True, obstacle=True)
        self.set_up_layer(self.ROCKS, collider_ratio=(0.7, 0.7), visible=True, depth=True, obstacle=True)

        # Because buildings can have different shapes, they have custom colliders, they themselves are not obstacles:
        self.set_up_layer(self.BUILDINGS, visible=True, depth=True, obstacle=False)
        self.set_up_layer(self.QUEST_BOARD, visible=True, depth=True, obstacle=False)

        # Item layers have the same name as the items themselves.
        # Since all items need to be handled identically, iterating over each layer:
        for item_name in ITEM_NAMES:
            self.set_up_layer(item_name, visible=True, depth=True, obstacle=False, dynamic=True, item=True)

        self.set_up_layer(PLAYER, visible=True, depth=True, obstacle=False, dynamic=True, vulnerable=True)

        # Enemy layers have the same name as the enemies themselves.
        # Since all enemies need to be handled identically, iterating over each layer:
        for enemy_name in ENEMY_NAMES:
            self.set_up_layer(enemy_name, visible=True, depth=True, obstacle=False, dynamic=True, vulnerable=True,
                              hostile=True)

        # Barriers and colliders are invisible, but have collision:
        # Barriers are 1x1 tiles that can be placed easily to block certain areas.
        # Colliders can be any size and can be used to block very precise parts of the map.
        self.set_up_layer(self.BARRIERS, collider_ratio=(1, 1), visible=False, obstacle=True)
        self.set_up_layer(self.COLLIDERS, collider_ratio=(1, 1), visible=False, obstacle=True)

    def add_tile(self, tile, visible=True, depth=True, obstacle=True, dynamic=False, item=False, hostile=False,
                 vulnerable=False):
        # Adding tile into relevant groups:
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
        # Removing tile from all groups:
        self.all_tiles.remove(tile)
        self.flat_tiles.remove(tile)
        self.depth_tiles.remove(tile)
        self.dynamic_tiles.remove(tile)
        self.obstacle_tiles.remove(tile)
        self.item_tiles.remove(tile)
        self.hostile_tiles.remove(tile)
        self.vulnerable_tiles.remove(tile)
        # No need to remove from in_frame groups, since these are re-calculated each frame.

    def set_up_layer(self, layer_name, collider_ratio=(0.9, 0.9), visible=True, depth=True, obstacle=True,
                     dynamic=False, item=False, hostile=False, vulnerable=False):
        # If a rotated or flipped map_object/tile is used,
        # pytmx is supposed to adjust the image automatically and return the correct surface.
        # However, this does not work for me, and I cannot figure out why.
        # For this reason, not using rotated or flipped objects/tiles,
        # creating a duplicate flipped/rotated image if absolutely necessary.

        # Validating layer name:
        # Not creating the layer if it has been set as invisible in Tiled - useful for debugging:
        if layer_name not in [layer.name for layer in self.tmx_data.visible_layers]: return

        # Returns a TiledTileLayer or TiledObjectGroup instance.
        # TiledTileLayer.tiles() returns the position and surface of each tile in the layer.
        # TiledObjectGroup returns the position, size and surface of each map_object in the layer.
        layer = self.tmx_data.get_layer_by_name(layer_name)

        # If map_object layer:
        if isinstance(layer, TiledObjectGroup):
            for map_object in layer:
                if map_object.image is not None:
                    tile = Tile(self.game,
                                position=(map_object.x / self.scale_factor, map_object.y / self.scale_factor),
                                size=(map_object.width / self.TILE_RESOLUTION,
                                      map_object.height / self.TILE_RESOLUTION),
                                # The aspect ratio of objects should not be protected:
                                collider_ratio=collider_ratio, image=map_object.image,
                                # Objects images can be stretched for more variety:
                                protect_aspect_ratio=False)

                    # Checking for special objects:
                    if layer_name == self.QUEST_BOARD:
                        self.quest_board = tile
                        self.set_up_quest_board_views()

                    # Adding map object to correct groups:
                    self.add_tile(tile, visible=visible, depth=depth, obstacle=obstacle, dynamic=dynamic, item=item,
                                  hostile=hostile, vulnerable=vulnerable)

        # If tile layer:
        elif isinstance(layer, TiledTileLayer):
            for x, y, surface in layer.tiles():
                if surface is not None:
                    # Converting the position of the tile to pixels:
                    tile_position = (x * self.tile_size, y * self.tile_size)

                    # Checking for special tiles for which the relevant object must be instantiated:
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
                        # Other tiles:
                        tile = Tile(self.game, position=tile_position, collider_ratio=collider_ratio, image=surface,
                                    # The aspect ratio of tiles should be protected:
                                    protect_aspect_ratio=True)

                    # Adding tile to correct groups:
                    self.add_tile(tile, visible=visible, depth=depth, obstacle=obstacle, dynamic=dynamic, item=item,
                                  hostile=hostile, vulnerable=vulnerable)

    def get_tiles_in_frame(self, group):
        tiles_in_frame = pygame.sprite.Group()

        for sprite in group:
            # Checking collision with screen rectangle and rectangle of the sprite's image:
            if pygame.Rect.colliderect(sprite.rect, self.display_rect):
                tiles_in_frame.add(sprite)

        return tiles_in_frame

    def calculate_tiles_in_frame(self):
        # Checking which sprites are on-screen, as we only need to be concerned with those:
        self.flat_tiles_in_frame = self.get_tiles_in_frame(self.flat_tiles)
        self.depth_tiles_in_frame = self.get_tiles_in_frame(self.depth_tiles)

        # The following is used to only update tiles if they are on-screen:
        self.dynamic_tiles_in_frame = self.get_tiles_in_frame(self.dynamic_tiles)

        # The following are used for collision by the player & enemies:
        self.obstacle_tiles_in_frame = self.get_tiles_in_frame(self.obstacle_tiles)
        self.item_tiles_in_frame = self.get_tiles_in_frame(self.item_tiles)

    def draw_map(self):
        # Calculating how far the player is from the centre of the screen,
        # and determining correct offset such that the player is back at the centre:
        self.draw_offset.x = self.display.get_rect().centerx - self.player.get_rect().centerx
        self.draw_offset.y = self.display.get_rect().centery - self.player.get_rect().centery

        # First drawing sprites without depth effect since these are at the background:
        for tile in self.flat_tiles_in_frame:
            tile.draw(self.draw_offset)

        # Sorting sprites with depth effect in ascending order of y-position:
        for tile in sorted(self.depth_tiles_in_frame, key=lambda sprite_in_list: sprite_in_list.rect.centery):
            tile.draw(self.draw_offset)

    def get_player(self):
        return self.player

    def get_obstacle_tiles_in_frame(self):
        return self.obstacle_tiles_in_frame

    def get_item_tiles_in_frame(self):
        return self.item_tiles_in_frame

    def get_vulnerable_tiles(self):
        return self.vulnerable_tiles

    def get_tile_size(self):
        return self.tile_size

    def get_draw_offset(self):
        return self.draw_offset

    def is_done(self):
        return self.done

    def set_done(self, value):
        self.done = value

    def calculate_display_lines(self):
        # The 4 line segments (represented as groups of 2 points) that make up the display:
        # Used for drawing indicators where lines connecting items of interest and the screen lines intersect:
        self.display_rect.center = self.player.get_rect().center
        top = (self.display_rect.topleft, self.display_rect.topright)
        right = (self.display_rect.topright, self.display_rect.bottomright)
        bottom = (self.display_rect.bottomright, self.display_rect.bottomleft)
        left = (self.display_rect.bottomleft, self.display_rect.topleft)
        self.display_lines = [top, right, bottom, left]

    def draw_hostile_indicators(self):
        for hostile in self.hostile_tiles:
            hostile_center = hostile.get_collider().center
            # Obtaining the centres of the player and hostile character, which represents the line segment between them:
            player_to_hostile = (self.player.get_collider().center, hostile_center)

            # The minimum distance between the hostile and player for the indicator to show up:
            # This takes into account the player's stealth value - higher the stealth,
            # the greater the distance from which the indicator can be seen:
            min_distance = \
                Utils.INDICATOR_DISTANCE * self.tile_size * self.player.get_stats()[Player.STEALTH_MULTIPLIER]

            if self.player.get_distance_to(hostile_center) < min_distance:
                # Iterating over each display line segment (the 4 lines that make up the display):
                for line in self.display_lines:
                    # Determining if and where the display line segment and the
                    # line segment connecting the player and hostile intersects:
                    intersection = get_segment_intersection(player_to_hostile, line)
                    if intersection is not None:
                        # If there is an intersection, drawing a red indicator:
                        self.draw_indicator(intersection + self.draw_offset, RED)

    def draw_quest_board_indicator(self):
        # Obtaining the centres of the player and quest board, which represents the line segment between them:
        player_to_board = (self.player.get_collider().center, self.quest_board.get_collider().center)

        # Iterating over each display line segment (the 4 lines that make up the display):
        for line in self.display_lines:
            # Determining if and where the display line segment and the
            # line segment connecting the player and quest board intersects:
            intersection = get_segment_intersection(player_to_board, line)
            if intersection is not None:
                # If there is an intersection, drawing a green indicator:
                self.draw_indicator(intersection + self.draw_offset, GREEN)

    def draw_indicator(self, point, colour):
        pygame.draw.circle(self.display, colour, point, Utils.INDICATOR_RADIUS * self.tile_size)

    def set_up_quest_board_views(self):
        self.quest_board_views = []

        # Quest Board Information Text:
        self.txt_info = Text(self.game, font_size=0.02, above=self.btn_next_level, margin=0.01,
                             text_alignment=Text.CENTRE, frame_thickness=0, text_colour=WHITE)
        self.quest_board_views.append(self.txt_info)

        # Restart Level Button:
        self.btn_restart_level = Button(self.game, text=RESTART_LEVEL, to_left_of=self.txt_info,
                                        font_size=0.02, margin=0.01, frame_condition=View.ALWAYS, frame_thickness=0,
                                        text_colour=WHITE, text_hover_colour=WHITE)
        self.quest_board_views.append(self.btn_restart_level, )

        # Next Level Button:
        self.btn_next_level = Button(self.game, text=NEXT_LEVEL, to_right_of=self.txt_info, font_size=0.02,
                                     margin=0.01, frame_condition=View.ALWAYS, frame_thickness=0, text_colour=WHITE,
                                     text_hover_colour=WHITE)
        self.quest_board_views.append(self.btn_next_level)

        # Level Name Text:
        self.txt_level_name = TextLine(self.game, text=Utils().LEVELS[self.id][Utils.NAME], font_size=0.04,
                                       above=self.txt_info, margin=0, padding=0.015, frame_condition=View.ALWAYS,
                                       frame_thickness=0, text_colour=WHITE)
        self.quest_board_views.append(self.txt_level_name)

        # Error Text:
        self.txt_error = TextLine(self.game, text=NEXT_LEVEL_ERROR, above=self.txt_level_name, font_size=0.02,
                                  margin=0.01, visible=False, text_colour=WHITE, frame_colour=RED, frame_thickness=0,
                                  frame_condition=View.ALWAYS)
        self.quest_board_views.append(self.txt_error)

    def update_quest_board_views(self):
        # Manually placing the info text on top of the quest board:
        self.txt_info.get_rect().midbottom = self.quest_board.get_rect().midtop + pygame.Vector2(
            self.draw_offset) - pygame.Vector2(0, self.txt_info.get_margin())

        # Updating the text of the quest board info text:
        self.txt_info.set_text(QUEST_BOARD_TEXT.format(len(self.item_tiles), len(self.hostile_tiles)))
        # Setting the first line of the info text to have a higher font size than the rest:
        self.txt_info.get_text_lines()[0].set_font_size(0.04)

        # If all hostiles are dead, showing button in green:
        if len(self.hostile_tiles) == 0:
            self.btn_next_level.set_text_colour(GREEN)
        # Otherwise, showing button in red:
        else:
            self.btn_next_level.set_text_colour(RED)

        if self.btn_restart_level.clicked():
            # Restarting the level:
            self.set_done(True)
        elif self.btn_next_level.clicked():
            # Increasing the level id and starting the level
            if len(self.hostile_tiles) == 0:
                # Increasing the level id:
                self.game.update_level_id(self.id + 1)
                self.set_done(True)
            else:
                self.txt_error.set_visibility(True)
        elif self.txt_error.clicked():
            # If the error message is clicked, hiding it:
            self.txt_error.set_visibility(False)

        for view in self.quest_board_views: view.update()

    def update(self):
        # Centering the camera on the player and calculating the points representing the
        # 4 line segments that make up the display (used for many features):
        self.calculate_display_lines()
        self.draw_map()
        # Calculating which tiles are in the frame and need to be processed further:
        self.calculate_tiles_in_frame()
        # Updating tiles that need to be updated:
        self.dynamic_tiles_in_frame.update()

        # Drawing indicators for enemies:
        self.draw_hostile_indicators()
        # Ensuring that there is a quest board in the map:
        if self.quest_board is not None:
            self.draw_quest_board_indicator()
            if self.quest_board in self.depth_tiles_in_frame:
                # Only updating quest board information if it is in the frame:
                self.update_quest_board_views()
