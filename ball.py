from typing import Union
from g import inform

import pygame


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos: Union[tuple, list], group):
        super().__init__(group)
        self.r = 5
        self.player_spacing = self.r

        self.image = pygame.Surface((self.r * 2, self.r * 2)).convert_alpha()
        self.image.fill((240, 240, 240, 0))
        pygame.draw.circle(self.image, "red", (self.r, self.r), self.r)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        self.speed = 100
        self.abs_rect = (*self.pos, self.pos[0] + self.image.get_width(), self.pos[1] + self.image.get_height())

    def move(self, dt):
        if self.direction.magnitude():
            self.direction = self.direction.normalize()

        self.pos.x = self.pos.x + self.direction.x * self.speed * dt
        self.pos.y = self.pos.y + self.direction.y * self.speed * dt

        self.rect.center = self.pos

    def goto_player(self, player_pos: Union[tuple, list], player_size: Union[tuple, list]):
        if self.pos[0] - player_pos[0] > (player_size[0] // 2 - self.player_spacing):
            self.direction.x -= 1
        elif self.pos[0] - player_pos[0] < -(player_size[0] // 2 - self.player_spacing):
            self.direction.x += 1
        else:
            self.direction.x = 0

        if self.pos[1] - player_pos[1] > (player_size[1] // 2 - self.player_spacing):
            self.direction.y -= 1
        elif self.pos[1] - player_pos[1] < -(player_size[1] // 2 - self.player_spacing):
            self.direction.y += 1
        else:
            self.direction.y = 0

    def update_rect(self):
        self.abs_rect = (*self.pos, self.pos[0] + self.image.get_width(), self.pos[1] + self.image.get_height())

    def check_is_on_player(self, player_pos: Union[tuple, list], player_size: Union[tuple, list]):
        player_rect = (
            player_pos[0] - player_size[0] // 2, player_pos[1] - player_size[1] // 2,
            player_pos[0] + player_size[0] // 2,
            player_pos[1] + player_size[1] // 2)

        if any((player_rect[0] < (self.pos[0] - self.r) < player_rect[2],
                player_rect[0] < (self.pos[0] + self.r) < player_rect[2])) and any((
                player_rect[1] < self.pos[1] - self.r < player_rect[3], player_rect[1] < self.pos[1] + self.r <
                                                              player_rect[3])):
            inform.player_died = True

    def update(self, dt, player_pos: Union[tuple, list], player_size: Union[tuple, list],
               screen: pygame.Surface = None):
        self.goto_player(player_pos, player_size)
        self.move(dt)
        self.update_rect()
        self.check_is_on_player(player_pos, player_size)
        if screen is not None:
            pygame.draw.line(screen, (95, 226, 222), self.pos, player_pos, width=1)
