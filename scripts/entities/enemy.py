import pygame
import random
import math

import scripts.utils.constants as c
import scripts.utils.tools as tools
from scripts.entities.bullet import Bullet


class Enemy(pygame.sprite.Sprite):
    def __init__(self, bullet_group: pygame.sprite.Group):
        super().__init__()
        self.image = pygame.Surface([c.TILE_SIZE, c.TILE_SIZE])
        self.frames = tools.get_sprites('enemy', 'enemy', 8)
        self.hurting_images = tools.get_sprites('enemy', 'enemy_hurting', 4)
        self.shooting_images = tools.get_sprites('enemy', 'enemy_shooting', 4)
        self.frame = 0
        self.dt = 0.0
        self.current_time = 0.0
        self.flap_cycle_timer = 0
        self.shoot_cycle_timer = 0
        self.hurt_cycle_timer = 0
        self.action_timer = 0
        self.swoop_timer = 0
        self.shoot_timer = 0
        self.spawn_timer = 0
        self.hurt_timer = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = random.choice([c.SCREEN_WIDTH + c.TILE_SIZE, -1 * c.TILE_SIZE])
        self.rect.top = c.ENEMY_HEIGHT + random.gauss(0, c.TILE_SIZE)
        self.state = c.SPAWN
        self.player_position = [0, 0]
        self.bullets = bullet_group
        self.bullet_timer = 0
        self.health = 3
        self.kill_bonus = 100

    def update(self, delta_time: float, player_position: [int]):
        self.dt = delta_time
        self.current_time += self.dt
        self.player_position = player_position
        self.action()
        self.animate()
        return self.bullets

    def adjust_position(self, bullet_group: pygame.sprite.Group) -> int:
        #for bullet in bullet_group:
        #[self.adjust_for_collisions(bullet) for bullet in bullet_group if pygame.rect.Rect.colliderect(self.hitbox, bullet)]
        bonus = 0
        for bullet in bullet_group:
            if pygame.sprite.collide_mask(self, bullet):
                bonus += self.adjust_for_collisions(bullet)
        #for bullet in pygame.sprite.spritecollide(self, bullet_group, False):
        #    self.adjust_for_collisions(bullet)
        return bonus

    def action(self):
        match self.state:
            case c.SPAWN:
                self.spawning()
            case c.FLAP:
                self.flapping()
                if self.current_time - self.action_timer > 10:
                    random.choice([self.swooping(), self.shooting()])
                    self.action_timer = self.current_time
                    self.swoop_timer = self.current_time
                    self.shoot_timer = self.current_time
                    self.hurt_timer = self.current_time
            case c.SWOOP:
                self.swooping()
                if self.current_time - self.swoop_timer > 10:
                    self.action_timer = self.current_time
                    self.swoop_timer = self.current_time
                    self.hurt_timer = self.current_time
                    self.state = c.FLAP
            case c.SHOOT:
                self.shooting()
                if self.current_time - self.shoot_timer > 1:
                    self.action_timer = self.current_time
                    self.shoot_timer = self.current_time
                    self.hurt_timer = self.current_time
                    self.state = c.FLAP
            case c.HURT:
                self.hurting()
                if self.current_time - self.hurt_timer > 2:
                    self.hurt_timer = self.current_time
                    self.state = c.FLAP

    def animate(self):
        match self.state:
            case c.SPAWN | c.SWOOP | c.FLAP:
                if self.current_time - self.flap_cycle_timer > 0.1:
                    if self.frame < 7:
                        self.frame += 1
                    else:
                        self.frame = 0
                    self.flap_cycle_timer = self.current_time
                self.image = self.frames[self.frame]
            case c.HURT:
                if self.current_time - self.hurt_cycle_timer > 0.1:
                    if self.frame < 3:
                        self.frame += 1
                    else:
                        self.frame = 0
                    self.hurt_cycle_timer = self.current_time
                self.image = self.hurting_images[self.frame]
            case c.SHOOT:
                if self.current_time - self.shoot_cycle_timer > 0.1:
                    if self.frame < 3:
                        self.frame += 1
                    else:
                        self.frame = 0
                    self.shoot_cycle_timer = self.current_time
                self.image = self.shooting_images[self.frame]

    def flapping(self):
        self.state = c.FLAP
        self.rect.x += math.cos(self.current_time) * random.choice([1, 2, 3])
        self.rect.top -= math.sin(self.current_time) * random.choice([0, 1, 2])

    def swooping(self):
        self.state = c.SWOOP
        self.rect.x += math.cos(self.current_time) * random.choice([1, 2, 3])
        self.rect.top += math.sin(self.current_time) * random.choice([2, 3, 4])

    def shooting(self):
        self.state = c.SHOOT
        if self.current_time - self.bullet_timer > 2:
            bullet = Bullet(self.get_shooting_angle(), self.rect.centerx, self.rect.centery)
            self.bullets.add(bullet)
            self.bullet_timer = self.current_time

    def get_shooting_angle(self):
        offset = (self.player_position[1] - self.rect.centery, self.player_position[0] - self.rect.centerx)
        return math.atan2(*offset)

    def spawning(self):
        self.state = c.SPAWN
        # Change direction based on which side of the enemy screen spawned in
        direction = -1 if self.rect.x < c.SCREEN_WIDTH // 2 else 1
        if self.current_time - self.spawn_timer < 10:
            self.rect.x -= direction * abs(math.cos(self.current_time)) * random.choice([1, 2, 3])
            self.rect.top += math.sin(self.current_time) * random.choice([0, 1, 2])
        else:
            self.state = c.FLAP
            self.action_timer = self.current_time

    def hurting(self) -> int:
        self.state = c.HURT
        #self.image = self.hurting_images[0]
        if self.health == 0:
            self.kill()
            return self.kill_bonus
        else:
            return 0

    def adjust_for_collisions(self, bullet: Bullet) -> int:
        bullet.kill()
        self.health -= 1
        self.hurt_timer = self.current_time
        return self.hurting()
