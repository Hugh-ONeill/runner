import pygame
import asyncio
import sys
from scripts.game import Game
import scripts.utils.constants as c

async def main():
    
    pygame.init()
    pygame.display.set_caption(c.CAPTION)
    pygame.mouse.set_visible(False)
    game = Game()
    while game.running:
        game.loop()
    pygame.display.quit()
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    asyncio.run(main())
