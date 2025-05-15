import pygame
import random
import math
import scripts.constants as c
import scripts.tools as tools

class Ground(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pygame.Surface([c.SCREEN_WIDTH, c.SCREEN_HEIGHT])
        self.image.fill((0, 255, 0))
        self.image = tools.get_sprite('ground', 0, 0, 500)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.top = c.GROUND_HEIGHT
        self.speed = 1.0
        self.chasm = 0
        self.current_time = 0.0

    def update(self, current_time: float) -> float:
        self.current_time = current_time
        self.speed = 20 * math.log(self.current_time / 100 + 1)
        return self.speed

    def adjust_position(self):
        self.rect.x -= round(self.speed)
        if self.rect.right < (-1 * self.chasm):
            # Reset position with randomized height and width
            self.chasm = abs(random.gauss(8 * c.TILE_SIZE, 4 * c.TILE_SIZE))
            self.image = tools.get_sprite('ground', 0, 0, 500 - self.chasm // 3)
            self.rect = self.image.get_rect()
            self.rect.x = c.SCREEN_WIDTH
            self.rect.top = c.GROUND_HEIGHT - abs(random.gauss(0, c.TILE_SIZE))
