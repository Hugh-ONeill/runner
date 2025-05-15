import math
import pygame

import scripts.utils.constants as c
import scripts.utils.tools as tools
from scripts.entities.bullet import Bullet


class Player(pygame.sprite.Sprite):
    def __init__(self, bullet_group: pygame.sprite.Group):
        super().__init__()
        self.falling_sprite = tools.get_sprite('player', "falling")
        self.frames = tools.get_sprites('player', "running", 12)
        self.jumping_sprite = tools.get_sprite('player', "jumping")
        self.hurting_sprites = tools.get_sprites('player', "hurting", 4)
        self.standing_sprite = tools.get_sprite('player', "standing")
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = c.TILE_SIZE
        self.rect.bottom = c.GROUND_HEIGHT
        # Forces
        self.dt = 0.0
        self.x_vel = 0.0
        self.y_vel = 0.0
        self.max_x_vel = c.MAX_WALK_SPEED
        self.max_y_vel = c.MAX_Y_VEL
        self.min_x_vel = c.MIN_WALK_SPEED
        self.x_accel = c.WALK_ACCEL
        self.gravity = c.GRAVITY
        # States
        self.state = c.WALK
        self.can_jump = True
        self.can_shoot = True
        self.bullet_timer = 0
        self.facing_right = True
        self.health = 3        
        self.frame = 0
        self.current_time = 0
        self.walk_cycle_timer = 0
        self.hurt_cycle_timer = 0
        self.bullets = bullet_group

    def update(self, delta_time: float, ground_speed: float, keys: dict[pygame.key.ScancodeWrapper, bool]):
        self.dt = delta_time
        self.current_time += self.dt
        self.handle_state(keys)
        self.animate(ground_speed)
        return self.bullets

    def handle_state(self, keys: dict[pygame.key.ScancodeWrapper, bool]):
        match self.state:
            case c.STAND:
                self.standing(keys)
            case c.WALK:
                self.walking(keys)
            case c.JUMP:
                self.jumping(keys)
            case c.FALL:
                self.falling(keys)
            case c.HURT:
                self.falling(keys)

    def adjust_position(self, ground_group: pygame.sprite.Group, enemy_group: pygame.sprite.Group, enemy_bullet_group: pygame.sprite.Group):
        self.rect.x += round(self.x_vel)
        for ground in pygame.sprite.spritecollide(self, ground_group, False):
            self.adjust_for_x_collisions(ground)
        for enemy in pygame.sprite.spritecollide(self, enemy_group, False):
            if self.state != c.HURT:
                self.health -= 1
            self.adjust_for_x_enemy_collisions(enemy)
        for enemy in pygame.sprite.spritecollide(self, enemy_bullet_group, False):
            if self.state != c.HURT:
                self.health -= 1
            self.adjust_for_x_enemy_collisions(enemy)
            enemy.kill()
        self.rect.y += round(self.y_vel)
        for ground in pygame.sprite.spritecollide(self, ground_group, False):
            self.adjust_for_y_collisions(ground)
        for enemy in pygame.sprite.spritecollide(self, enemy_group, False):
            if self.state != c.HURT:
                self.health -= 1
            self.adjust_for_y_enemy_collisions(enemy)
        for enemy in pygame.sprite.spritecollide(self, enemy_bullet_group, False):
            if self.state != c.HURT:
                self.health -= 1
            self.adjust_for_y_enemy_collisions(enemy)
            enemy.kill()
        self.check_if_falling(ground_group)
        self.check_if_dying()
        self.clamp()

    def animate(self, ground_speed: float):
        match self.state:
            case c.WALK | c.STAND:
                if self.current_time - self.walk_cycle_timer > self.calculate_animation_speed(ground_speed):
                    if self.frame < 11:
                        self.frame += 1
                    else:
                        self.frame = 0
                    self.walk_cycle_timer = self.current_time
                self.image = self.frames[self.frame]
            case c.JUMP:
                self.image = self.jumping_sprite
            case c.FALL:
                self.image = self.falling_sprite
            case c.HURT:
                if self.current_time - self.hurt_cycle_timer > 0.1:
                    if self.frame < 3:
                        self.frame += 1
                    else:
                        self.frame = 0
                    self.hurt_cycle_timer = self.current_time
                self.image = self.hurting_sprites[self.frame]

    # State Functions

    def shoot(self):
        if self.current_time - self.bullet_timer > 1:
            bullet = Bullet(self.get_shooting_angle(), self.rect.centerx, self.rect.centery)
            self.bullets.add([bullet])
            self.bullet_timer = self.current_time

    def get_shooting_angle(self):
        mouse = pygame.mouse.get_pos()
        offset = (mouse[1] - self.rect.centery, mouse[0] - self.rect.centerx)
        return math.atan2(*offset)

    def standing(self, keys: dict[pygame.key.ScancodeWrapper, bool]):
        self.able_to_jump(keys)
        self.able_to_shoot(keys)
        self.x_vel = 0
        self.y_vel = 0
        
        if tools.keybinding(keys, c.ACTION):
            if self.can_shoot:
                self.shoot()
        if tools.keybinding(keys, c.UP):
            if self.can_jump:
                self.state = c.JUMP
                self.y_vel = c.JUMP_VEL
        elif tools.keybinding(keys, c.LEFT):
            self.facing_right = False
            self.state = c.WALK
        elif tools.keybinding(keys, c.RIGHT):
            self.facing_right = True
            self.state = c.WALK

    def walking(self, keys: dict[pygame.key.ScancodeWrapper, bool]):
        self.able_to_jump(keys)
        self.able_to_shoot(keys)
        self.max_x_vel = c.MAX_WALK_SPEED
        self.x_accel = c.WALK_ACCEL

        if tools.keybinding(keys, c.ACTION):
            if self.can_shoot:
                self.shoot()
        if tools.keybinding(keys, c.UP):
            if self.can_jump:
                self.state = c.JUMP
                # Boost "running" jump
                if abs(self.x_vel) > c.MAX_WALK_SPEED - 1.5:
                    self.y_vel = c.FAST_JUMP_VEL
                else:
                    self.y_vel = c.JUMP_VEL
        if tools.keybinding(keys, c.LEFT):
            self.facing_right = False
            # Quick turn from the right
            if self.x_vel > 0:
                self.x_accel = c.TURNABOUT
            # Increase speed towards left within bounds
            if self.x_vel > (-1 * self.max_x_vel):
                self.x_vel -= self.x_accel 
                if self.x_vel > (-1 * self.min_x_vel):
                    self.x_vel = (-1 * self.min_x_vel)
            elif self.x_vel < (-1 * self.max_x_vel):
                self.x_vel += self.x_accel
        elif tools.keybinding(keys, c.RIGHT):
            self.facing_right = True
            # Quick turn from the left
            if self.x_vel < 0:
                self.x_accel = c.TURNABOUT
            # Increase speed towards right within bounds
            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel
                if self.x_vel < self.min_x_vel:
                    self.x_vel = self.min_x_vel
            elif self.x_vel > self.max_x_vel:
                self.x_vel -= self.x_accel
        else:
            # Slide to a stop
            if self.facing_right:
                if self.x_vel > 0:
                    self.x_vel -= self.x_accel
                else:
                    self.x_vel = 0
                    self.state = c.STAND
            else:
                if self.x_vel < 0:
                    self.x_vel += self.x_accel
                else:
                    self.x_vel = 0
                    self.state = c.STAND

    def jumping(self, keys: dict[pygame.key.ScancodeWrapper, bool]):
        self.gravity = c.JUMP_GRAVITY
        # Slow jump
        if self.y_vel < self.max_y_vel:
            self.y_vel += self.gravity
        # Fast fall after top of jump arc
        if self.y_vel >= 0:
            self.gravity = c.GRAVITY
            self.state = c.FALL
        if tools.keybinding(keys, c.ACTION):
            if self.can_shoot:
                self.shoot()
        if tools.keybinding(keys, c.LEFT):
            if self.x_vel > (-1 * self.max_x_vel):
                self.x_vel -= self.x_accel
        elif tools.keybinding(keys, c.RIGHT):
            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel
        # End jump before top of arc
        if not tools.keybinding(keys, c.UP):
            self.gravity = c.GRAVITY
            self.state = c.FALL

    def falling(self, keys: dict[pygame.key.ScancodeWrapper, bool]):
        if self.y_vel < c.MAX_Y_VEL:
            self.y_vel += self.gravity
        if tools.keybinding(keys, c.ACTION):
            if self.can_shoot:
                self.shoot()
        # Double-Jump
        if tools.keybinding(keys, c.UP):
            if self.can_jump:
                self.state = c.JUMP
                self.can_jump = False
                self.y_vel = c.JUMP_VEL
        if tools.keybinding(keys, c.LEFT):
            if self.x_vel > (-1 * self.max_x_vel):
                self.x_vel -= self.x_accel
        elif tools.keybinding(keys, c.RIGHT):
            if self.x_vel < self.max_x_vel:
                self.x_vel += self.x_accel

    # Collision Functions

    def adjust_for_x_collisions(self, collider: pygame.sprite.Sprite):
        if self.rect.x < collider.rect.x:
            self.rect.right = collider.rect.left
            # Pinched off of screen
            if self.rect.left < 0:
                self.y_vel = c.JUMP_VEL
                self.health -= 1
                self.state = c.HURT
            self.x_vel = 1
        else:
            self.rect.left = collider.rect.right
            self.x_vel = -1

    def adjust_for_x_enemy_collisions(self, collider: pygame.sprite.Sprite):
        if self.rect.x < collider.rect.x:
            self.rect.right = collider.rect.left
            self.x_vel = c.BUMP_VEL
        else:
            self.rect.left = collider.rect.right
            self.x_vel = -c.BUMP_VEL

    def adjust_for_y_collisions(self, collider: pygame.sprite.Sprite):
        if self.rect.y <= collider.rect.y:
            # Stand on top of obstacle
            self.rect.bottom = collider.rect.top
            self.y_vel = 0
            self.state = c.WALK
        else:
            # Bump against top obstacle
            self.rect.top = collider.rect.bottom
            self.y_vel = c.BUMP_VEL
            self.state = c.FALL

    def adjust_for_y_enemy_collisions(self, collider: pygame.sprite.Sprite):
        if self.rect.y <= collider.rect.y:
            # Bump away from obstacle
            self.rect.bottom = collider.rect.top
            self.y_vel = -c.BUMP_VEL
            self.state = c.HURT
        else:
            # Bump against top obstacle
            self.rect.top = collider.rect.bottom
            self.y_vel = c.BUMP_VEL
            self.state = c.HURT

    def check_if_falling(self, colliders: pygame.sprite.Group):
        self.rect.y += 1
        if not pygame.sprite.spritecollideany(self, colliders):
            if self.state != c.JUMP and self.state != c.HURT:
                self.state = c.FALL
        self.rect.y -= 1

    def check_if_dying(self):
        if self.health < 1 or self.rect.bottom > c.SCREEN_HEIGHT:
            self.alive = False

    def clamp(self):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > c.SCREEN_WIDTH:
            self.rect.right = c.SCREEN_WIDTH

    # Animation Functions

    def calculate_animation_speed(self, ground_speed: float):
        if not self.x_vel:
            self.x_vel = 0
        if not ground_speed:
            ground_speed = 0
        animation_speed = 0.13 - self.x_vel * .013 * ground_speed
        return animation_speed

    # State Helpers

    def able_to_jump(self, keys: dict[pygame.key.ScancodeWrapper, bool]):
        if not tools.keybinding(keys, c.UP):
            self.can_jump = True

    def able_to_shoot(self, keys: dict[pygame.key.ScancodeWrapper, bool]):
        if not tools.keybinding(keys, c.ACTION):
            self.can_shoot = True
