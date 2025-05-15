import pygame

import scripts.utils.tools as tools

class Reticle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = tools.get_sprites('reticle', 'reticle', 8, 0, 0, 16, 16)
        self.frame = 0
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect()
        self.dt = 0.0
        self.current_time = 0.0
        self.reticle_timer = 0.0

    def update(self, delta_time: float):
        self.dt = delta_time
        self.current_time += self.dt
        mx, my = pygame.mouse.get_pos()
        self.rect.centerx = mx
        self.rect.centery = my
        self.animate()

    def animate(self):
        if self.current_time - self.reticle_timer > 0.15:
            if self.frame < len(self.frames) - 1:
                self.frame += 1
            else:
                self.frame = 0
            self.image = self.frames[self.frame]
            self.reticle_timer = self.current_time