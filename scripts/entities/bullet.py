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
        self.speed_magnitude = 400
        self.vel_x = self.speed_magnitude * math.cos(self.angle)
        self.vel_y = self.speed_magnitude * math.sin(self.angle)
        self.image = pygame.transform.rotate(self.bullet, -math.degrees(self.angle))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.true_x = x
        self.true_y = y
    
    def update(self, delta_time):
        self.dt = delta_time
        # Remove when off the screen
        if self.rect.centerx < 0 or self.rect.centerx > c.SCREEN_WIDTH or self.rect.centery < 0 or self.rect.centery > c.SCREEN_HEIGHT:
            self.kill()

    def adjust_position(self):
        self.true_x += self.vel_x * self.dt
        self.rect.centerx = round(self.true_x)
        self.true_y += self.vel_y * self.dt
        self.rect.centery = round(self.true_y)
