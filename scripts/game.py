import pygame
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
        self.big_font = pygame.font.SysFont(None, c.TILE_SIZE * 3)
        self.clock = pygame.time.Clock()
        self.fps = 60
        # Forces
        self.dt = 0.0
        self.current_time = 0.0
        self.enemy_timer = 0.0
        # States
        self.running = True
        self.show_menu = True
        self.paused = False
        self.game_over = False
        self.restart = False
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
            if self.show_menu:
                self.main_menu_screen()
            elif self.paused:
                self.pause_menu()
            elif self.game_over:
                self.game_over_screen()
            else:
                for event in pygame.event.get():
                    self.event_controls(event)
                self.update()
                self.render()
                self.dt = self.clock.tick(self.fps) / 1000.0
                self.current_time += self.dt

    def resume(self):
        self.paused = False
        self.menu_sprites.empty()

    def pause_menu(self):
        if not self.menu_sprites:
            self.menu_sprites.add(Button(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 2, self.resume, "resume"))
            self.menu_sprites.add(self.reticle)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        self.menu_sprites.update()
        self.render_menu()

    def event_controls(self, event: pygame.event.Event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type in (pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN):
            self.keys = pygame.key.get_pressed()
            if self.keys[pygame.K_p]:
                self.paused = True

    def update(self):
        ground_speed = 0.0
        for ground in self.ground_group:
            ground_speed = ground.update(self.current_time)

        # Update Background Scroll Speed
        self.scenery.update(ground_speed)

        # Update Player Sprite Physics
        bullets = self.player.update(self.dt, ground_speed, self.keys)
        if bullets:
            self.all_sprites.add(bullets)

        # Spawn New Enemies (faster as score increases)
        spawn_interval = max(2.0, 5.0 - self.score / 500)
        if self.current_time - self.enemy_timer > spawn_interval:
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
        for ground in self.ground_group:
            ground.adjust_position()
        self.scenery.adjust_position()

        self.player.adjust_position(self.ground_group, self.enemy_group, self.enemy_bullet_group)

        for enemy in self.enemy_group:
            self.score += enemy.adjust_position(self.bullet_group)
        for bullet in self.bullet_group:
            bullet.adjust_position()
        for bullet in self.enemy_bullet_group:
            bullet.adjust_position()

        # Increase Score Based on Ground Speed
        self.score += ground_speed * self.dt

        # Clean up dead and off-screen enemies
        for enemy in self.enemies:
            if enemy.rect.right < -c.TILE_SIZE or enemy.rect.left > c.SCREEN_WIDTH + c.TILE_SIZE:
                enemy.kill()
        self.enemies = [e for e in self.enemies if e.alive()]

        # Check Player State
        if not self.player.alive:
            self.game_over = True

    def render(self):
        self.window.fill((0, 0, 0))
        self.scenery.draw(self.window)
        self.all_sprites.draw(self.window)
        font_render = self.font.render(f"score: {int(self.score)}", True, (255, 255, 255))
        health_render = self.font.render(f"health: {self.player.health}", True, (255, 255, 255))
        self.window.blit(font_render, (0, 0))
        self.window.blit(health_render, (0, c.TILE_SIZE))
        pygame.display.update()

    def main_menu_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

        if not self.menu_sprites:
            self._menu_bg = pygame.Surface(c.SCREEN_SIZE)
            self._menu_bg.fill((20, 20, 30))
            title_text = self.big_font.render(c.CAPTION, True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 3))
            self._menu_bg.blit(title_text, title_rect)
            start_btn = Button(
                c.SCREEN_WIDTH // 2 - 80, c.SCREEN_HEIGHT // 2 + 20,
                self._do_start, "start"
            )
            quit_btn = Button(
                c.SCREEN_WIDTH // 2 + 80, c.SCREEN_HEIGHT // 2 + 20,
                self._do_quit, "quit"
            )
            self.menu_sprites.add(start_btn, quit_btn, self.reticle)

        self.menu_sprites.update()
        self.window.blit(self._menu_bg, (0, 0))
        self.menu_sprites.draw(self.window)
        pygame.display.update()
        self.clock.tick(self.fps)

    def _do_start(self):
        self.show_menu = False
        self.menu_sprites.empty()

    def game_over_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

        if not self.menu_sprites:
            # capture and dim the last game frame
            self._game_over_bg = self.window.copy()
            dim = pygame.Surface(c.SCREEN_SIZE)
            dim.set_alpha(128)
            dim.fill((0, 0, 0))
            self._game_over_bg.blit(dim, (0, 0))
            # bake static text into the background
            go_text = self.big_font.render("GAME OVER", True, (255, 255, 255))
            go_rect = go_text.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 3))
            self._game_over_bg.blit(go_text, go_rect)
            score_text = self.font.render(f"score: {int(self.score)}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(c.SCREEN_WIDTH // 2, c.SCREEN_HEIGHT // 3 + 60))
            self._game_over_bg.blit(score_text, score_rect)
            # buttons
            restart_btn = Button(
                c.SCREEN_WIDTH // 2 - 80, c.SCREEN_HEIGHT // 2 + 20,
                self._do_restart, "restart"
            )
            quit_btn = Button(
                c.SCREEN_WIDTH // 2 + 80, c.SCREEN_HEIGHT // 2 + 20,
                self._do_quit, "quit"
            )
            self.menu_sprites.add(restart_btn, quit_btn, self.reticle)

        self.menu_sprites.update()
        self.window.blit(self._game_over_bg, (0, 0))
        self.menu_sprites.draw(self.window)
        pygame.display.update()
        self.clock.tick(self.fps)

    def _do_restart(self):
        self.restart = True
        self.running = False

    def _do_quit(self):
        self.running = False

    def render_menu(self):
        #self.window.fill((0, 0, 0))
        self.menu_sprites.draw(self.window)
        pygame.display.update()
