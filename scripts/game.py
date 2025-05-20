import pygame
import random

from scripts.entities.ground import Ground
from scripts.entities.enemy import Enemy
from scripts.entities.player import Player
from scripts.entities.bullet import Bullet
from scripts.entities.reticle import Reticle
from scripts.entities.scenery import Scenery
import scripts.utils.constants as c
import scripts.utils.tools as tools
from scripts.utils.button import Button


class Game:
    def __init__(self):
        self.window = pygame.display.set_mode(c.SCREEN_SIZE)
        self.font = pygame.font.SysFont(None, c.TILE_SIZE)
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
        self.score = 0
        # Scenery
        self.scenery = Scenery()
        # Load Objects
        self.all_sprites = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.enemy_bullet_group = pygame.sprite.Group()
        self.menu_sprites = pygame.sprite.Group()
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
            
            if self.paused == True:
                
                self.pause_menu()
            else:
                [self.event_controls(event) for event in pygame.event.get()]
                self.update()
                self.render()
                self.dt = self.clock.tick(self.fps) / 1000.0
                self.current_time += self.dt

    def resume(self):
        self.paused = False

    def pause_menu(self):
        self.menu_sprites.add(Button(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2, self.resume))
        self.menu_sprites.add(self.reticle)
        self.menu_sprites.update()
        self.render_menu()

    def event_controls(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN or pygame.KEYUP or pygame.MOUSEBUTTONDOWN:
            self.keys = pygame.key.get_pressed()
            if self.keys[pygame.K_p]:
                self.paused = True

    def update(self):
        for ground in self.ground_group:
            ground_speed = ground.update(self.current_time)
        if not ground_speed:
            ground_speed = 0.0

        # Update Background Scroll Speed
        self.scenery.update(ground_speed)

        # Update Player Sprite Physics
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

        # Update Enemy Sprite Physics
        for enemy in self.enemy_group:
            enemy_bullets = enemy.update(self.dt, self.player.rect.center)
            if enemy_bullets:
                self.all_sprites.add(enemy_bullets)
        
        self.reticle.update(self.dt)
        self.bullet_group.update(self.dt)
        self.enemy_bullet_group.update(self.dt)

        # Adjust Sprite Positions
        [ground.adjust_position() for ground in self.ground_group]
        self.scenery.adjust_position()

        self.player.adjust_position(self.ground_group, self.enemy_group, self.enemy_bullet_group)
        
        for enemy in self.enemy_group:
            self.score += enemy.adjust_position(self.bullet_group)
        
        [enemy.adjust_position(self.bullet_group) for enemy in self.enemy_group]
        [bullet.adjust_position() for bullet in self.bullet_group]
        [bullet.adjust_position() for bullet in self.enemy_bullet_group]
        
        # Increase Score Based on Ground Speed
        self.score += ground_speed * self.dt
        
        # Check Player State
        if not self.player.alive:
            self.running = False

    def render(self):
        self.window.fill((0, 0, 0))
        self.scenery.draw(self.window)
        self.all_sprites.draw(self.window)
        font_render = self.font.render(f"score: {int(self.score)}", True, (255, 255, 255))
        health_render = self.font.render(f"health: {self.player.health}", True, (255, 255, 255))
        self.window.blit(font_render, (0, 0))
        self.window.blit(health_render, (0, c.TILE_SIZE))
        pygame.display.update()

    def render_menu(self):
        #self.window.fill((0, 0, 0))
        self.menu_sprites.draw(self.window)
        pygame.display.update()
