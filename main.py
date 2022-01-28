import pygame
from utils import *
from level import Level



#Colours:
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (50,50,255)
YELLOW = (255,255,0)

pygame.init()
screen = pygame.display.set_mode((screenWidth, screenHeight))
#TODO: seticon


# Creating Level
level = Level(levelMap, screen)


pygame.display.set_caption("Platformer")

done = False

clock = pygame.time.Clock()


while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
      
    screen.fill(BLACK)
    

    level.run()

  
    pygame.display.flip()

    clock.tick(60)


pygame.quit()