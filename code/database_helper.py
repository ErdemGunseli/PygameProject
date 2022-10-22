import os
import sqlite3
from player import *
from strings import *
from items import *


# A helper class for the relational database: [DONE]
class DatabaseHelper:
    # Setting types:
    FRAME_RATE_LIMIT = 0
    SHOW_FRAME_RATE = 1
    AUDIO_VOLUME = 2

    # Item Types (storing these here as the Weapon and Potion classes do not need them):
    WEAPON = 0
    POTION = 1

    def __init__(self, game):
        # The game is passed as an argument to access some of its attributes and methods:
        self.game = game

        # Name of the relational database:
        self.database = "database.db"

        # Checking if the database already exists.
        # If it does, no need to set it up again:
        if not os.path.isfile(self.database): self.set_up_tables()

    def set_up_tables(self):
        # Creating database tables:
        # Starting values are inserted into each table so that when entering values, we can just use UPDATE:
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        # Settings Table:
        cursor.execute("""CREATE TABLE IF NOT EXISTS SETTINGS(
                                   TYPE INTEGER PRIMARY KEY NOT NULL,
                                   VALUE REAL NOT NULL
                                   )""")

        # Defaults for Settings:
        cursor.executemany("INSERT INTO SETTINGS VALUES(?, ?)",
                           [(self.FRAME_RATE_LIMIT, 60),
                            (self.SHOW_FRAME_RATE, 0),
                            (self.AUDIO_VOLUME, 0.5)])

        # Levels Table:
        connection.execute("""CREATE TABLE IF NOT EXISTS LEVELS(
                                   ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                   NAME TEXT UNIQUE NOT NULL,
                                   FOLDER_PATH TEXT UNIQUE NOT NULL,
                                   R INTEGER NOT NULL,
                                   G INTEGER NOT NULL,
                                   B INTEGER NOT NULL
                                   )""")

        # Inserting Level Paths, Names, RGB Background Colours:
        level_folder = "../level_maps"
        cursor.executemany("INSERT INTO LEVELS VALUES(NULL, ?, ?, ?, ?, ?)",
                           [("Test Map", level_folder + "/" + "test_map/map.tmx", 145, 171, 23)])

        # Player Stats Table:
        cursor.execute("""CREATE TABLE PLAYER_STATS(
                                   TYPE INTEGER PRIMARY KEY NOT NULL,
                                   VALUE REAL
                                   )""")

        # Inserting Tentative Player Stats:
        cursor.executemany("INSERT INTO PLAYER_STATS VALUES(?, ?)",
                           [(Player.CURRENT_LEVEL_ID, 0),
                            (Player.FULL_HEALTH, 0),
                            (Player.CURRENT_HEALTH, 0),
                            (Player.SPEED_MULTIPLIER, 1),
                            (Player.MELEE_DAMAGE_MULTIPLIER, 1),
                            (Player.MELEE_COOLDOWN_MULTIPLIER, 1),
                            (Player.MAGIC_DAMAGE_MULTIPLIER, 1),
                            (Player.MAGIC_COOLDOWN_MULTIPLIER, 1),
                            (Player.INVULNERABILITY_DURATION, 500)])

        # All Items Table:
        # LENGTH is in tile size. Aspect ratio is protected when re-sizing so no need for another dimension.
        cursor.execute("""CREATE TABLE IF NOT EXISTS ITEMS(
                            NAME STRING PRIMARY KEY NOT NULL,
                            IMAGE_PATH STRING NOT NULL,
                            LENGTH REAL NOT NULL,
                            TYPE INTEGER NOT NULL
                            )""")

        item_folder = "../assets/images/weapons"
        cursor.executemany("INSERT INTO ITEMS VALUES(?, ?, ?, ?)",
                           [(KNIGHT_SWORD, item_folder + "/" + "sword", 0.6, self.WEAPON),
                            (LANCE, item_folder + "/" + "lance", 1.2, self.WEAPON),
                            (BATTLE_AXE, item_folder + "/" + "axe", 0.7, self.WEAPON),
                            (RAPIER, item_folder + "/" + "rapier", 0.7, self.WEAPON),
                            (Trident, item_folder + "/" + "sai", 0.6, self.WEAPON)])
        # TODO: Insert Potion / Magic Items Here:

        # Weapon Properties Table:
        cursor.execute("""CREATE TABLE IF NOT EXISTS WEAPON_PROPERTIES(
                        ITEM_NAME PRIMARY KEY NOT NULL,
                        DAMAGE FLOAT NOT NULL,
                        COOLDOWN FLOAT NOT NULL
                        )""")

        # Inserting Weapon Properties:
        cursor.executemany("INSERT INTO WEAPON_PROPERTIES VALUES(?, ?, ?)",
                           [(KNIGHT_SWORD, 10, 750),
                            (LANCE, 30, 1000),
                            (BATTLE_AXE, 35, 1200),
                            (RAPIER, 10, 300),
                            (Trident, 25, 850)])

        # Potion Properties Table:
        cursor.execute("""CREATE TABLE IF NOT EXISTS POTION_PROPERTIES(
                        ITEM_NAME PRIMARY KEY NOT NULL,
                        HEALTH_BOOST FLOAT NOT NULL,
                        MOVEMENT_SPEED_MULTIPLIER FLOAT NOT NULL,
                        ATTACK DAMAGE MULTIPLIER FLOAT NOT NULL,
                        MAGIC DAMAGE MULTIPLIER FLOAT NOT NULL
                        )""")
        # TODO: Insert Potion Properties Here:

        # Player inventory table:
        cursor.execute("""CREATE TABLE IF NOT EXISTS INVENTORY(
                            ITEM_NAME STRING PRIMARY KEY NOT NULL,
                            QUANTITY INTEGER NOT NULL
                        )""")

        # Inserting Inventory Items:
        # TODO: Only add 1 weapon and maybe 3 health potions:
        cursor.executemany("INSERT INTO INVENTORY VALUES(?, ?)",
                           [(KNIGHT_SWORD, 1),
                            (LANCE, 2),
                            (BATTLE_AXE, 3),
                            (RAPIER, 4),
                            (Trident, 5)])

        connection.commit()
        connection.close()

    def delete_saves(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        # Deleting all tables one by one:
        # Even need to delete item property tables since the values would be inserted twice:
        cursor.execute("DROP TABLE IF EXISTS SETTINGS")
        cursor.execute("DROP TABLE IF EXISTS LEVELS")
        cursor.execute("DROP TABLE IF EXISTS PLAYER_STATS")
        cursor.execute("DROP TABLE IF EXISTS ITEMS")
        cursor.execute("DROP TABLE IF EXISTS WEAPON_PROPERTIES")
        cursor.execute("DROP TABLE IF EXISTS POTION_PROPERTIES")
        cursor.execute("DROP TABLE IF EXISTS INVENTORY")

        self.set_up_tables()

        connection.commit()
        connection.close()

    def get_setting(self, setting_type):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        # Retrieving desired setting:
        cursor.execute("SELECT VALUE FROM SETTINGS WHERE TYPE=?", [setting_type])

        cursor_return = cursor.fetchone()
        if cursor_return is not None:
            result = float(cursor_return[0])
        else:
            result = None

        connection.commit()
        connection.close()

        return result

    def update_setting(self, setting_type, value):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        # Updating the record (we know it exists since we added default values in constructor):
        cursor.execute("UPDATE SETTINGS SET VALUE = ? WHERE TYPE = ? ", [value, setting_type])

        connection.commit()
        connection.close()

    def get_map_path(self, level_id):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        # Retrieving desired level path:
        cursor.execute("SELECT FOLDER_PATH FROM LEVELS WHERE ID=?", [level_id])

        cursor_return = cursor.fetchone()
        if cursor_return is not None:
            path = cursor_return[0]
        else:
            path = None

        connection.commit()
        connection.close()

        return path

    def get_background_colour(self, level_id):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        # Retrieving desired level path:
        cursor.execute("SELECT R, G, B FROM LEVELS WHERE ID=?", [level_id])

        cursor_return = cursor.fetchone()

        if cursor_return is not None:
            colour = cursor_return
        else:
            colour = (0, 0, 0)

        connection.commit()
        connection.close()

        return colour

    def get_player_stats(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        # Retrieving desired level:
        cursor.execute("SELECT * FROM PLAYER_STATS")

        cursor_return = cursor.fetchall()
        stats = {}
        if cursor_return is not None:
            for item in cursor_return:
                stats[item[0]] = item[1]

        connection.commit()
        connection.close()

        return stats

    def update_player_stats(self, player_stats):
        # Parameter name player_object to avoid shadows:
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        for stat_type in player_stats:
            cursor.execute("UPDATE PLAYER_STATS SET VALUE=? WHERE TYPE=?", [player_stats[stat_type], stat_type])

        connection.commit()
        connection.close()

    def get_player_inventory(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        # Retrieving inventory:
        cursor.execute("SELECT * FROM INVENTORY")

        inventory_return = cursor.fetchall()
        inventory = {}
        if inventory_return is not None:

            for index, item in enumerate(inventory_return):
                name = inventory_return[index][0]
                quantity = inventory_return[index][1]

                # Retrieving item path and type:
                cursor.execute("SELECT IMAGE_PATH, TYPE, LENGTH FROM ITEMS WHERE NAME=?", [name])
                item_return = cursor.fetchone()
                item_path = item_return[0]
                item_type = item_return[1]
                item_length = item_return[2]

                # Instantiating correct class based on item type:
                match item_type:

                    case self.WEAPON:
                        # Retrieving weapon properties:
                        cursor.execute("SELECT DAMAGE, COOLDOWN FROM WEAPON_PROPERTIES WHERE ITEM_NAME=?", [name])
                        weapon_return = cursor.fetchone()
                        damage = weapon_return[0]
                        cooldown = weapon_return[1]

                        inventory_item = Weapon(self.game, name, damage, cooldown, item_path, (item_length, item_length))

                    case _:
                        inventory_item = None


                inventory[inventory_item] = quantity

        connection.commit()
        connection.close()

        return inventory

    def update_player_inventory(self, player_inventory):
        # Parameter name player_object to avoid shadows:
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        for item in player_inventory:
            item_name = item.get_name()

            # First checking if item is in inventory to update or add:
            cursor.execute("SELECT * FROM INVENTORY WHERE NAME=?", [item_name])
            if len(cursor.fetchall()) > 0:
                # If the item is already in inventory, just update quantity:
                cursor.execute("UPDATE INVENTORY SET QUANTITY=? WHERE NAME=?", [item])
            else:
                # If the item is not in the inventory add it:
                cursor.execute("INSERT INTO INVENTORY VALUES(?, ?)", [item_name, player_inventory[item_name]])

        connection.commit()
        connection.close()
