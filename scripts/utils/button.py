import pygame

import scripts.utils.constants as c


class Button(pygame.sprite.Sprite):
    def __init__(self, x: int = 0, y: int = 0, action=None, label: str = ""):
        super().__init__()
        self.label = label
        self.font = pygame.font.SysFont(None, c.TILE_SIZE)
        if label:
            text_w = self.font.size(label)[0]
            width = text_w + 2 * c.TILE_SIZE
        else:
            width = 2 * c.TILE_SIZE
        height = int(1.5 * c.TILE_SIZE)
        self.image = pygame.Surface((width, height)).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.action = action
        self._draw('green')

    def _draw(self, color):
        self.image.fill(color)
        if self.label:
            text = self.font.render(self.label, True, (255, 255, 255))
            text_rect = text.get_rect(
                center=(self.image.get_width() // 2, self.image.get_height() // 2)
            )
            self.image.blit(text, text_rect)

    def hovered(self) -> bool:
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def clicked(self) -> bool:
        return self.hovered() and pygame.mouse.get_pressed()[0]

    def update(self):
        if self.hovered():
            self._draw('red')
            if self.clicked():
                self._draw('blue')
                if self.action:
                    self.action()
        else:
            self._draw('green')
