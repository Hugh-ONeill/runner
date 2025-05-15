import pygame

import scripts.utils.constants as c


def keybinding(keys, binding):
    if keys:
        match binding:
            case c.UP:
                return keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_x]
            case c.LEFT:
                return keys[pygame.K_LEFT] or keys[pygame.K_a]
            case c.RIGHT:
                return keys[pygame.K_RIGHT] or keys[pygame.K_d]
            case c.DOWN:
                return keys[pygame.K_DOWN] or keys[pygame.K_s]
            case c.ACTION:
                return keys[pygame.K_c] or pygame.mouse.get_pressed()[0]

def get_sprite(sprite_folder: str, sprite_filename: str, x:int = 0, y:int = 0, width:int = c.TILE_SIZE, height:int = c.TILE_SIZE):
    sprite_sheet = pygame.image.load(f"data/{sprite_folder}/{sprite_filename}.png").convert_alpha()
    image = pygame.Surface([width, height])
    rect = image.get_rect()
    image.blit(sprite_sheet, (0, 0), (x, y, width, height))
    image.set_colorkey((0,0,0))
    image = pygame.transform.scale(image, 
        (int(rect.width * c.SIZE_MULTIPLIER), 
        int(rect.height * c.SIZE_MULTIPLIER)))
    return image

def get_sprites(sprite_folder: str, sprite_filename_base: str, frames:int, x:int = 0, y:int = 0, width:int = c.TILE_SIZE, height:int = c.TILE_SIZE):
    return [get_sprite(sprite_folder, f"{sprite_filename_base}_{frame}", x, y, width, height) for frame in range(frames)]