import pygame
from utils import platformSize


PLAYERCOLOUR = (200, 20, 40)

class Player(pygame.sprite.Sprite):

    def __init__(self, position):
        super().__init__()

        self.image = pygame.Surface((32,64))
        self.image.fill(PLAYERCOLOUR)
        self.rect = self.image.get_rect(topleft = position)

        # Speed of the player when the player is moving:
        self.xSpeed = 7
        self.ySpeed = 7

        # Vector so we can do operations with it more easily:
        self.direction = pygame.math.Vector2(0,0)

    def getInput(self):
        keyPressed = pygame.key.get_pressed()

        # If D has been pressed and A has not been pressed, move right
        if keyPressed[pygame.K_d] and not keyPressed[pygame.K_a]:
            self.direction.x = 1

        # If A has been pressed and D has not been pressed, move left
        elif keyPressed[pygame.K_a] and not keyPressed[pygame.K_d]:
             self.direction.x = -1

        # Cheat Keys Will Be Removed
        elif keyPressed[pygame.K_w]:
            self.direction.y = -1
        elif keyPressed[pygame.K_s]:
            self.direction.y = 1   

        else:
            self.direction.x = 0
            self.direction.y = 0

    def update(self):
        self.getInput()
        self.calculatePosition()
          


    def calculatePosition(self):
        self.rect.x += self.direction.x * self.xSpeed    
        self.rect.y += self.direction.y * self.ySpeed  

    def getXSpeed(self): return self.xSpeed

    def setXSpeed(self, speed): self.xSpeed = speed    

    def getYSpeed(self): return self.ySpeed

    def setYSpeed(self, speed): self.ySpeed = speed    

    def getRect(self): return self.rect    
