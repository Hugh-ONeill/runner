import pygame
import random
import math

import scripts.utils.constants as c
import scripts.utils.tools as tools


class Bullet(pygame.sprite.Sprite):
    def __init__(self, angle, x:int=0, y:int=0):
        super().__init__()
        self.bullet = tools.get_sprite('general', 'bullet', 0, 0, 8, 8)
        self.rect = self.bullet.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.dt = 0.0
        self.angle = angle
        self.speed_magnitude = 5
        self.vel_x = self.speed_magnitude * math.cos(self.angle)
        self.vel_y = self.speed_magnitude * math.sin(self.angle)
        self.image = pygame.transform.rotate(self.bullet, -math.degrees(self.angle))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
    
    def update(self):
        # Remove when off the screen
        if self.rect.x < 0 or self.rect.x > c.SCREEN_WIDTH or self.rect.y < 0 or self.rect.y > c.SCREEN_HEIGHT:
            self.kill()

    def adjust_position(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
