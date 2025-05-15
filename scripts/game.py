import pygame
import random
from scripts.ground import Ground
from scripts.enemy import Enemy
from scripts.player import Player
from scripts.bullet import Bullet
from scripts.reticle import Reticle
from scripts.scenery import Scenery
from scripts import constants as c
from scripts import tools as tools


class Game:
    def __init__(self):
        self.window = pygame.display.set_mode(c.SCREEN_SIZE)
        self.font = pygame.font.SysFont(None, 100)
        self.clock = pygame.time.Clock()
        self.fps = 60
        # Forces
        self.dt = 0.0
        self.current_time = 0.0
        self.enemy_timer = 0.0
        # States
        self.running = True
        self.paused = False
        self.keys = {}
        # Scenery
        self.scenery = Scenery()
        # Load Objects
        self.all_sprites = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.enemy_bullet_group = pygame.sprite.Group()
        self.player = Player(self.bullet_group)
        self.all_sprites.add([self.player])
        self.grounds = [Ground(c.SCREEN_WIDTH * platform) for platform in range(2)]
        self.all_sprites.add(self.grounds)
        self.ground_group.add(self.grounds)
        self.enemies = [Enemy(self.enemy_bullet_group) for _ in range(3)]
        self.all_sprites.add(self.enemies)
        self.enemy_group.add(self.enemies)
        self.reticle = Reticle()
        self.all_sprites.add(self.reticle)

    def loop(self):
        self.clock.tick(self.fps)
        while self.running:
            [self.event_controls(event) for event in pygame.event.get()]
            self.update()
            self.render()
            self.dt = self.clock.tick(self.fps) / 1000.0
            self.current_time += self.dt

    def event_controls(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN or pygame.KEYUP or pygame.MOUSEBUTTONDOWN:
            self.keys = pygame.key.get_pressed()

    def update(self):
        ground_speed = self.ground_group.update(self.current_time)
        self.scenery.update(ground_speed)
        bullets = self.player.update(self.dt, ground_speed, self.keys)
        if bullets:
            self.all_sprites.add(bullets)
        # Spawn New Enemies
        if self.current_time - self.enemy_timer > 5:
            new_enemy = Enemy(self.enemy_bullet_group)
            self.enemies.append(new_enemy)
            self.enemy_group.add([new_enemy])
            self.all_sprites.add([new_enemy])
            self.enemy_timer = self.current_time
        for enemy in self.enemy_group:
            enemy_bullets = enemy.update(self.dt, self.player.rect.center)
            if enemy_bullets:
                self.all_sprites.add(enemy_bullets)
        self.reticle.update(self.dt)
        self.bullet_group.update()
        self.enemy_bullet_group.update()
        # Adjust Positions
        [ground.adjust_position() for ground in self.ground_group]
        self.scenery.adjust_position()
        self.player.adjust_position(self.ground_group, self.enemy_group, self.enemy_bullet_group)
        [enemy.adjust_position(self.bullet_group) for enemy in self.enemy_group]
        [bullet.adjust_position() for bullet in self.bullet_group]
        [bullet.adjust_position() for bullet in self.enemy_bullet_group]
        # Adjust Player State
        if not self.player.alive:
            self.running = False

    def render(self):
        self.window.fill((0, 0, 0))
        self.scenery.draw(self.window)
        self.all_sprites.draw(self.window)
        pygame.display.update()
