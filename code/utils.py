import pygame
from os import walk
from strings import *
from assets import *
import random


# Converts float value to a percentage string:
def percentage_format(float_value):
    return "{}%".format(round(float_value * 100))


# Places all image surfaces in a directory into a list:
def import_images(folder_path):
    images = []

    for _, __, image_files in walk(folder_path):
        # Iterable contains a tuple with the following items:
        #   0: path to the folder
        #   1: List of folders in path
        #   2: list of files in our current path <- We are only interested in this.

        for image_file in image_files:
            # The full path of image:
            full_path = folder_path + "/" + image_file

            image_surface = pygame.image.load(full_path).convert_alpha()
            images.append(image_surface)

    return images


# Resizes an image whilst protecting the aspect ratio:
def resize_image(image, size):
    current_image_size = image.get_size()
    width = current_image_size[0]
    height = current_image_size[1]

    if (width / size[0]) > (height / size[1]):
        scale_factor = size[0] / width
        width = size[0]
        height *= scale_factor
    else:
        scale_factor = size[1] / height
        height = size[1]
        width *= scale_factor

    return pygame.transform.scale(image, (width, height))


# A simple function that just returns the range of a numeric iterable:
def get_range(values):
    return max(values) - min(values)


# An algorithm that returns the intersection point of two line segments:
def get_segment_intersection(points1, points2):
    (x1, y1), (x2, y2) = points1
    (x3, y3), (x4, y4) = points2

    denominator = ((x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4))

    if denominator == 0: return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator

    if not 0 <= t <= 1: return None

    return x1 + t * (x2 - x1), y1 + t * (y2 - y1)

# Returns True or False. Chance to return True is passed as the argument:
def decision(probability):
    # random.random() returns a random float between 0 and 1:
    return random.random() < probability


# Contains data relating to the non-user-modifiable aspects of the game: [TESTED & FINALISED]
class Utils:
    # The following data was previously in the database.
    # However, there was no point in storing this data in the database because:
    #  1. Data is not user-modifiable.
    #  2. Game isn't client-server so if any changes were to be made to this data,
    #   a re-download would be necessary either way.

    # Using constants throughout to avoid string references when accessing the data,
    # and for autocomplete when referencing the data:
    NAME = 0
    PATH = 1
    COLOUR = 2
    # The minimum number of tiles that should fit the length and width of the screen:
    MIN_TILE_COUNT = 3
    MUSIC = 4

    level_folder = "../level_maps"
    weapon_folder = "../assets/images/weapons"
    potion_folder = "../assets/images/potions"

    LEVELS = {
        0: {NAME: "Forest Battle", PATH: path.format(level_folder, "test_map/map.tmx"),
            COLOUR: (145, 171, 23), MIN_TILE_COUNT: 15, MUSIC: LEVEL_1_MUSIC},
        1: {NAME: "Showdown", PATH: path.format(level_folder, "test_map_2/map.tmx"),
            COLOUR: (145, 171, 23), MIN_TILE_COUNT: 10, MUSIC: LEVEL_2_MUSIC},
    }
    INDICATOR_DISTANCE = 30  # How close the player needs to be to an enemy in tiles for an indicator to be shown.
    INDICATOR_RADIUS = 0.35  # The radius of the hostile indicator in tiles.

    WEAPON = 5
    POTION = 6
    LENGTH = 7
    USE_DURATION = 8
    DAMAGE = 9
    HEALING = 10
    TYPE = 11

    ITEMS = {
        # Weapons:
        KNIGHT_SWORD: {PATH: path.format(weapon_folder, "sword"),
                       LENGTH: 0.6, USE_DURATION: 750, DAMAGE: 300, TYPE: WEAPON},
        LANCE: {PATH: path.format(weapon_folder, "lance"),
                LENGTH: 1.2, USE_DURATION: 1000, DAMAGE: 300, TYPE: WEAPON},
        BATTLE_AXE: {PATH: path.format(weapon_folder, "axe"),
                     LENGTH: 0.7, USE_DURATION: 1200, DAMAGE: 320, TYPE: WEAPON},
        RAPIER: {PATH: path.format(weapon_folder, "rapier"),
                 LENGTH: 0.7, USE_DURATION: 300, DAMAGE: 220, TYPE: WEAPON},
        TRIDENT: {PATH: path.format(weapon_folder, "trident"),
                  LENGTH: 0.6, USE_DURATION: 850, DAMAGE: 600, TYPE: WEAPON},
        LONGSWORD: {PATH: path.format(weapon_folder, "longsword"),
                    LENGTH: 0.8, USE_DURATION: 1100, DAMAGE: 400, TYPE: WEAPON},
        CLUB: {PATH: path.format(weapon_folder, "club"),
               LENGTH: 0.7, USE_DURATION: 500, DAMAGE: 150, TYPE: WEAPON},
        FORK: {PATH: path.format(weapon_folder, "fork"),
               LENGTH: 0.7, USE_DURATION: 950, DAMAGE: 190, TYPE: WEAPON},
        HAMMER: {PATH: path.format(weapon_folder, "hammer"),
                 LENGTH: 0.7, USE_DURATION: 1150, DAMAGE: 220, TYPE: WEAPON},
        KATANA: {PATH: path.format(weapon_folder, "katana"),
                 LENGTH: 0.7, USE_DURATION: 350, DAMAGE: 500, TYPE: WEAPON},
        SPEAR: {PATH: path.format(weapon_folder, "spear"),
                LENGTH: 1, USE_DURATION: 900, DAMAGE: 290, TYPE: WEAPON},
        NUN_CHUCKS: {PATH: path.format(weapon_folder, "nun_chucks"),
                     LENGTH: 1, USE_DURATION: 450, DAMAGE: 450, TYPE: WEAPON},
        STICK: {PATH: path.format(weapon_folder, "stick"),
                LENGTH: 1, USE_DURATION: 400, DAMAGE: 180, TYPE: WEAPON},
        BONE: {PATH: path.format(weapon_folder, "bone"),
               LENGTH: 0.5, USE_DURATION: 600, DAMAGE: 150, TYPE: WEAPON},

        # Potions:
        LESSER_HEALING: {PATH: path.format(potion_folder, "lesser_healing"), USE_DURATION: 200,
                         LENGTH: 0.5, HEALING: 10, TYPE: POTION},
        NORMAL_HEALING: {PATH: path.format(potion_folder, "normal_healing"), USE_DURATION: 500,
                         LENGTH: 0.65, HEALING: 25, TYPE: POTION},
        GREATER_HEALING: {PATH: path.format(potion_folder, "greater_healing"), USE_DURATION: 800,
                          LENGTH: 0.8, HEALING: 50, TYPE: POTION},
        SUPER_HEALING: {PATH: path.format(potion_folder, "super_healing"), USE_DURATION: 1000,
                        LENGTH: 0.95, HEALING: 100, TYPE: POTION},
    }

    HEALTH = 12
    SPEED = 13
    ALERT_RADIUS = 14
    WEAPON_DROPS = 15
    POTION_DROPS = 16
    EQUIP_CHANCE = 17
    DROP_CHANCE = 18
    # How long it takes for enemies to recover after using an item:
    # For players, there is no such game mechanic.
    RECOVERY_DURATION = 19

    ENEMIES = {
        DEMON: {HEALTH: 250, SPEED: 4, ALERT_RADIUS: 10, RECOVERY_DURATION: 850,
                PATH: "../assets/images/characters/enemies/demon",
                WEAPON_DROPS: {BATTLE_AXE: {EQUIP_CHANCE: 0.3, DROP_CHANCE: 0.5},
                               TRIDENT: {EQUIP_CHANCE: 0.1, DROP_CHANCE: 0},
                               LONGSWORD: {EQUIP_CHANCE: 0.6, DROP_CHANCE: 0.8}},

                POTION_DROPS: {
                    GREATER_HEALING: {EQUIP_CHANCE: 0.6, DROP_CHANCE: 0.9},
                    SUPER_HEALING: {EQUIP_CHANCE: 0.4, DROP_CHANCE: 0.9}}
                },

        WARRIOR: {HEALTH: 180, SPEED: 6, ALERT_RADIUS: 15, RECOVERY_DURATION: 700,
                  PATH: "../assets/images/characters/enemies/warrior",
                  WEAPON_DROPS: {LANCE: {EQUIP_CHANCE: 0.2, DROP_CHANCE: 0.8},
                                 KATANA: {EQUIP_CHANCE: 0.3, DROP_CHANCE: 0.5},
                                 SPEAR: {EQUIP_CHANCE: 0.2, DROP_CHANCE: 0.7},
                                 NUN_CHUCKS: {EQUIP_CHANCE: 0.3, DROP_CHANCE: 0.5},
                                 LONGSWORD: {EQUIP_CHANCE: 0.3, DROP_CHANCE: 0.9}},

                  POTION_DROPS: {NORMAL_HEALING: {EQUIP_CHANCE: 0.6, DROP_CHANCE: 0.9},
                                 GREATER_HEALING: {EQUIP_CHANCE: 0.4, DROP_CHANCE: 0.9}}
                  },

        SKELETON: {HEALTH: 200, SPEED: 4, ALERT_RADIUS: 7, RECOVERY_DURATION: 1500,
                   PATH: "../assets/images/characters/enemies/skeleton",
                   WEAPON_DROPS: {CLUB: {EQUIP_CHANCE: 0.2, DROP_CHANCE: 0.4},
                                  FORK: {EQUIP_CHANCE: 0.1, DROP_CHANCE: 0.4},
                                  HAMMER: {EQUIP_CHANCE: 0.1, DROP_CHANCE: 0.5},
                                  STICK: {EQUIP_CHANCE: 0.2, DROP_CHANCE: 0.7},
                                  RAPIER: {EQUIP_CHANCE: 0.1, DROP_CHANCE: 0.3},
                                  BONE: {EQUIP_CHANCE: 0.3, DROP_CHANCE: 0.8}},

                   POTION_DROPS: {LESSER_HEALING: {EQUIP_CHANCE: 0.9, DROP_CHANCE: 0.8},
                                  NORMAL_HEALING: {EQUIP_CHANCE: 0.1, DROP_CHANCE: 0.6}}
                   },
    }

    def get_name(self, level_id):
        return self.LEVELS[level_id][self.NAME]

    def get_level_path(self, level_id):
        return self.LEVELS[level_id][self.PATH]

    def get_level_colour(self, level_id):
        return self.LEVELS[level_id][self.COLOUR]

    def get_min_tile_count(self, level_id):
        return self.LEVELS[level_id][self.MIN_TILE_COUNT]

    def get_music(self, level_id):
        return self.LEVELS[level_id][self.MUSIC]

    def get_item(self, game, item_name):
        # Importing items inside the function to avoid circular imports:
        import items

        item_image_path = self.ITEMS[item_name][self.PATH]
        item_type = self.ITEMS[item_name][self.TYPE]
        length = self.ITEMS[item_name][self.LENGTH]
        use_duration = self.ITEMS[item_name][self.USE_DURATION]

        # Pattern matching to instantiate correct class:
        match item_type:

            case self.WEAPON:
                damage = self.ITEMS[item_name][self.DAMAGE]
                item = items.Weapon(game, item_name, damage, use_duration, item_image_path, (length, length))

            case self.POTION:
                healing = self.ITEMS[item_name][self.HEALING]
                item = items.Potion(game, item_name, healing, use_duration, item_image_path, (length, length))

            case _:
                item = None

        return item

    def get_random_drop(self, game, enemy_name, drop_type):
        # Possible drops for the enemy:
        drops = self.ENEMIES[enemy_name][drop_type]
        # The probability of each item being selected:
        weights = [drops[drop][self.EQUIP_CHANCE] for drop in drops]
        # The item selected:
        item_name = random.choices(list(drops), weights=weights)[0]

        # Obtaining the item with this name and returning:
        return self.get_item(game, item_name)

    def get_drop_chance(self, enemy_name, item_name):
        # Importing items inside the function to avoid circular imports:

        drop_type = None
        if item_name in self.ENEMIES[enemy_name][self.POTION_DROPS]:
            drop_type = self.POTION_DROPS
        elif item_name in self.ENEMIES[enemy_name][self.WEAPON_DROPS]:
            drop_type = self.WEAPON_DROPS

        return self.ENEMIES[enemy_name][drop_type][item_name][self.DROP_CHANCE]

    def get_enemy(self, game, enemy_name):
        # Importing Enemy from characters inside the function to avoid circular imports:
        from characters import Enemy

        health = self.ENEMIES[enemy_name][self.HEALTH]
        speed = self.ENEMIES[enemy_name][self.SPEED]
        alert_radius = self.ENEMIES[enemy_name][self.ALERT_RADIUS]
        recovery_duration = self.ENEMIES[enemy_name][self.RECOVERY_DURATION]

        # All enemies always equip a weapon and potion:
        # They have a chance to drop each when they die (depending on what they are carrying):
        weapon = self.get_random_drop(game, enemy_name, self.WEAPON_DROPS)
        potion = self.get_random_drop(game, enemy_name, self.POTION_DROPS)

        path = self.ENEMIES[enemy_name][self.PATH]

        return Enemy(game, enemy_name, {Enemy.FULL_HEALTH: health, Enemy.CURRENT_HEALTH: health, Enemy.SPEED: speed,
                                        Enemy.ALERT_RADIUS: alert_radius, Enemy.RECOVERY_DURATION: recovery_duration,
                                        Enemy.INVULNERABILITY_DURATION: 100},
                     {weapon: 1, potion: 1}, path)
