import pygame

import scripts.utils.tools as tools
import scripts.utils.constants as c


class Button(pygame.sprite.Sprite):
    def __init__(self, x:int=0, y:int=0, action=None):
        super().__init__()
        self.image = pygame.Surface((2 * c.TILE_SIZE, c.TILE_SIZE)).convert_alpha()
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.image.fill('green')
        self.action = action

    def hovered(self) -> bool:
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def clicked(self) -> bool:
        return self.hovered() and pygame.mouse.get_pressed()[0]

    def update(self):
        if self.hovered():
            self.image.fill('red')
            if self.clicked():
                self.image.fill('blue')
                if self.action:
                    self.action()