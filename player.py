from typing import Union
import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, pos: Union[tuple, list], group: pygame.sprite.Group):
        super().__init__(group)
        # 创建段
        # self.image = pygame.image.load()
        self.image = pygame.Surface((20, 40)).convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        self.speed = 200

        # 修改段
        self.image.fill((0, 0, 0))

    def event(self, screen_size: Union[tuple, list]):
        keys = pygame.key.get_pressed()

        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.pos.y > 0:
            self.direction.y = -1
        elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.pos.y < screen_size[1]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.pos.x > 0:
            self.direction.x = -1
        elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.pos.x < screen_size[0]:
            self.direction.x = 1
        else:
            self.direction.x = 0

    def move(self, dt, screen_size: Union[tuple, list]):
        if self.direction.magnitude():
            self.direction = self.direction.normalize()

        self.pos.x = self.pos.x + self.direction.x * self.speed * dt
        self.pos.y = self.pos.y + self.direction.y * self.speed * dt

        if self.pos.x < 0:
            self.pos.x = 0
        elif self.pos.x > screen_size[0]:
            self.pos.x = screen_size[0]

        if self.pos.y < 0:
            self.pos.y = 0
        elif self.pos.y > screen_size[1]:
            self.pos.y = screen_size[1]

        self.rect.center = self.pos

    def update(self, dt, screen_size: Union[tuple, list]):
        self.event(screen_size)
        self.move(dt, screen_size)
