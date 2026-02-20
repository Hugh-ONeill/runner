import pygame
import sys
from scripts.game import Game
import scripts.utils.constants as c

def main():
    pygame.init()
    pygame.display.set_caption(c.CAPTION)
    pygame.mouse.set_visible(False)
    while True:
        game = Game()
        game.loop()
        if not game.restart:
            break
    pygame.display.quit()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
