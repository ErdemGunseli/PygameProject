import os
import sqlite3
from items import *


# TODO: DO NOT MODIFY UNNECESSARILY BEFORE FINISHING PROJECT - Maybe at the end:
#  If further performance increase is required, do not do autosave
#  and only save data when the game is paused or level changed.

# A helper class for the relational database: [TESTED & FINALISED]
class DatabaseHelper:
    # Setting types:
    FRAME_RATE_LIMIT = 0
    SHOW_FRAME_RATE = 1
    AUDIO_VOLUME = 2

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
        # Starting values are inserted into each table so that when entering values, we can just UPDATE:
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

        # Player Stats Table:
        cursor.execute("""CREATE TABLE PLAYER_STATS(
                                   TYPE INTEGER PRIMARY KEY NOT NULL,
                                   VALUE REAL
                                   )""")

        # Inserting Tentative Player Stats:
        cursor.executemany("INSERT INTO PLAYER_STATS VALUES(?, ?)",
                           [(Player.CURRENT_LEVEL_ID, 0),
                            (Player.FULL_HEALTH, 0),
                            (Player.CURRENT_HEALTH, 0),  # TODO: If Unused, Remove:
                            (Player.SPEED_MULTIPLIER, 1),
                            (Player.DAMAGE_MULTIPLIER, 1),
                            (Player.STEALTH_MULTIPLIER, 1),
                            (Player.INVULNERABILITY_DURATION, 300)])  # TODO: If Unused, Remove:


        # Player inventory table:
        cursor.execute("""CREATE TABLE IF NOT EXISTS INVENTORY(
                            ITEM_NAME STRING PRIMARY KEY NOT NULL,
                            QUANTITY INTEGER NOT NULL
                        )""")

        # Inserting Inventory Items:
        cursor.executemany("INSERT INTO INVENTORY VALUES(?, ?)",
                           [(KNIGHT_SWORD, 1),
                            # (LANCE, 1),
                            # (BATTLE_AXE, 1),
                            # (RAPIER, 1),
                            # (TRIDENT, 1),
                            # (LONGSWORD, 1),
                            # (CLUB, 1),
                            # (FORK, 1),
                            # (HAMMER, 1),
                            # (KATANA, 1),
                            # (SPEAR, 1),
                            # (NUN_CHUCKS, 1),
                            # (STICK, 1),
                            # (BONE, 1),
                            (LESSER_HEALING, 3),
                            # (NORMAL_HEALING, 3),
                            # (GREATER_HEALING, 3),
                            # (SUPER_HEALING, 3)
                            ])

        connection.commit()
        connection.close()

    def delete_saves(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        # Deleting all tables one by one:
#        cursor.execute("DROP TABLE IF EXISTS SETTINGS")
        cursor.execute("DROP TABLE IF EXISTS SETTINGS")
        cursor.execute("DROP TABLE IF EXISTS PLAYER_STATS")
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

    def get_player_stats(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM PLAYER_STATS")

        cursor_return = cursor.fetchall()
        stats = {}
        if cursor_return is not None:
            for key, value in cursor_return:
                stats[key] = value

        connection.commit()
        connection.close()

        return stats

    def update_player_stats(self, player_stats):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        for stat_type in player_stats:
            cursor.execute("UPDATE PLAYER_STATS SET VALUE=? WHERE TYPE=?", [player_stats[stat_type], stat_type])

        connection.commit()
        connection.close()

    def get_player_inventory(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM INVENTORY")

        inventory_return = cursor.fetchall()
        inventory = {}
        if inventory_return is not None:
            for index, (item_name, quantity) in enumerate(inventory_return):
                inventory_item = Utils().get_item(self.game, item_name)
                inventory[inventory_item] = quantity

        connection.commit()
        connection.close()

        return inventory

    def update_player_inventory(self, player_inventory):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        # Deleting items previously stored in the inventory:
        cursor.execute("DELETE FROM INVENTORY")

        for item in player_inventory:
            # Adding item:
            item_name = item.get_name()
            cursor.execute("INSERT INTO INVENTORY VALUES(?, ?)", [item_name, player_inventory[item]])

        connection.commit()
        connection.close()

    def get_player(self):
        return Player(self.game, self.get_player_stats(), self.get_player_inventory())
