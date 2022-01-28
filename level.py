import pygame
from platform import Platform
from player import Player
from utils import *


class Level:
    def __init__(self, levelData, surface):
        # Receiving map and surface
        
        self.displaySurface = surface
        self.setUpLevel(levelData)

        # How close to the edge the player must be for the screen to start scrolling:
        self.xShiftStart = int(screenWidth / 5)
        self.yShiftStart = int(screenHeight / 5)

        # How much the level will shift by each frame - depends on player movement
        self.levelXShift = 0
        self.levelYShift = 0

    def setUpLevel(self, layout):    
        self.platforms = pygame.sprite.Group()

        # Instance of player stored here!
        # I only want a single player!
        self.player = pygame.sprite.GroupSingle()

        # Enumerate gives us row index and row data
        for rowIndex, row in enumerate(layout):
          
            # Cycling through each column of each row:
            for columnIndex, object in enumerate(row):

                position = (columnIndex * platformSize, rowIndex * platformSize)

                # If we are supposed to have a platform:
                if (object == "X"):
                    # Create Platform at required location
                    myPlatform = Platform(position, platformSize)
                    # Add to platform group
                    self.platforms.add(myPlatform)

                elif (object == "P"):
                    # Create Player at the required location
                    myPlayer = Player(position)  
                    # Add to player group
                    self.player.add(myPlayer)  


    def calculateShift(self): #TODO: Maybe Player Centered Always???
        myPlayer = self.player.sprite
        playerX = myPlayer.rect.centerx
        playerY = myPlayer.rect.centery
        directionX = myPlayer.direction.x
        directionY = myPlayer.direction.y

        # If the player is towards the edge of the screen, scroll the map:

        # If beyond limit and going left, stop player & shift map right:
        if (playerX < self.xShiftStart) and (directionX < 0):

            # So that the level shift isn't set to 0 once the player speed is set to 0
            if myPlayer.getXSpeed() != 0:
                self.levelXShift = myPlayer.getXSpeed()

            myPlayer.setXSpeed(0)

        # If beyond limit and going right, stop player & shift map left:
        elif (playerX > screenWidth - self.xShiftStart) and (directionX > 0):  
            if myPlayer.getXSpeed() != 0:
                self.levelXShift = -myPlayer.getXSpeed()

            myPlayer.setXSpeed(0)

        # Otherwise, stop shift and allow player to be moved:
        else:
            self.levelXShift = 0
            myPlayer.setXSpeed(7)


       # Same for y-axis:    
        if (playerY < self.yShiftStart) and (directionY < 0):

            # So that the level shift isn't set to 0 once the player speed is set to 0
            if myPlayer.getYSpeed() != 0:
                self.levelYShift = myPlayer.getYSpeed()

            myPlayer.setYSpeed(0)

        elif (playerY > screenHeight - self.yShiftStart) and (directionY > 0):  
            if myPlayer.getYSpeed() != 0:
                self.levelYShift = -myPlayer.getYSpeed()

            myPlayer.setYSpeed(0)

        else:
            self.levelYShift = 0
            myPlayer.setYSpeed(7) 

    def run(self):
        # Update Level
        self.platforms.update(self.levelXShift, self.levelYShift)

        # Drawing Platforms
        self.platforms.draw(self.displaySurface) 


        # Update Player
        self.player.update()

        # Drawing Player
        self.player.draw(self.displaySurface)


        # Calculating shift of the level
        self.calculateShift()