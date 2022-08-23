from __future__ import annotations
from threading import Thread
from random import randint, random
from sys import exit
from time import sleep
from json import loads
from requests import get
from time import asctime
import pygame

print_list = [""]


class SendInfo:
    def __init__(self):
        self.get_nk_name_url = """https://api.lixingyong.com/api/qq?id={}"""
        self.sand_url = """http://milk.onlyacat233.top:8081/post"""
        # self.sand_url = """http://192.168.1.103:8081/post"""
        self.ua = {
            "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/104.0.5112.102 Safari/537.36 Edg/104.0.1293.63"""
        }
        self.ua_key = {
            "User-Agent": "awa-{}".format(asctime())
        }

    def get_nk(self, qq_number: int):
        res = loads(get(self.get_nk_name_url.format(qq_number), headers=self.ua).text)
        if "code" in res:
            return -1
        else:
            return res['nickname']

    def sand(self, qq_number: int, score: int):
        global print_list
        nk_name = self.get_nk(qq_number)
        if nk_name != -1:
            self.ua_key = {
                "User-Agent": "awa-{}".format(asctime())
            }
            try:
                res = get(self.sand_url, params={
                    "nk_name": nk_name,
                    "qq": str(qq_number),
                    "score": score
                }, headers=self.ua_key)
                dic = loads(res.text)
                if dic["code"] == "200":
                    return dic
                else:
                    return -1
            except Exception as e:
                print_list[0] = "服务器连接失败 ({})".format(e)
                return -1
        else:
            print_list[0] = "请核实qq号是否正确"
            return -2

    @staticmethod
    def read():
        global print_list
        try:
            with open("qq.txt", "r+", encoding="utf-8") as qf:
                qq = int(qf.read())
                return qq
        except Exception as e:
            print(e)
            with open("qq.txt", "w+", encoding="utf-8") as qf:
                pass
            print_list[0] = "qq号输入错误或没有输入,请在 ./qq.txt 中输入qq号(不要换行)"
            return -1

    def main(self, score: int):
        qq = self.read()
        if qq != -1:
            return self.sand(qq, score)


class Tools:
    def __init__(self):
        self.font_file = './res/font/MiSans-Light.ttf'
        self.clock = pygame.time.Clock()

    def draw_text(self, surface: pygame.Surface, text: str, pos: tuple | list, size: int,
                  color: tuple | list = (0, 0, 0), stop_time: float | str = 1.5):
        f = pygame.font.Font(self.font_file, size)
        f_surface = f.render(text, True, color, (240, 240, 240))
        surface.blit(f_surface, pos)
        if type(stop_time) == float or type(stop_time) == int:
            for i in range(round(stop_time * 100)):
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        exit(0)
                pygame.event.get()
                pygame.display.update()
                sleep(0.01)
        else:
            if stop_time == "wait_key":
                while True:
                    for e in pygame.event.get():
                        if e.type == pygame.QUIT:
                            pygame.quit()
                            exit(0)
                        if e.type == pygame.KEYUP:
                            return
                    pygame.event.get()
                    pygame.display.update()
                    sleep(0.01)


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos: tuple | list, group):
        super().__init__(group)
        self.r = 5
        self.player_spacing = 10

        self.image = pygame.Surface((10, 10)).convert()
        self.image.fill((240, 240, 240, 0))
        pygame.draw.circle(self.image, "red", (5, 5), self.r)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        self.speed = 100
        self.abs_rect = (*self.pos, self.pos[0] + self.image.get_width(), self.pos[1] + self.image.get_height())
        self.on_player = False

    def move(self, dt):
        if self.direction.magnitude():
            self.direction = self.direction.normalize()

        self.pos.x = self.pos.x + self.direction.x * self.speed * dt
        self.pos.y = self.pos.y + self.direction.y * self.speed * dt

        self.rect.center = self.pos

    def goto_player(self, player_pos: tuple | list, player_size: tuple | list):
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

    def check_is_on_player(self, player_pos: tuple | list, player_size: tuple | list):
        player_rect = (
            player_pos[0] - player_size[0] // 2, player_pos[1] - player_size[1] // 2,
            player_pos[0] + player_size[0] // 2,
            player_pos[1] + player_size[1] // 2)

        if player_rect[0] < self.pos[0] < player_rect[2] and player_rect[1] < self.pos[1] < player_rect[3]:
            self.on_player = True
        else:
            self.on_player = False

    def update(self, dt, player_pos: tuple | list, player_size: tuple | list):
        self.goto_player(player_pos, player_size)
        self.move(dt)
        self.update_rect()
        self.check_is_on_player(player_pos, player_size)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos: tuple | list, group):
        super().__init__(group)
        # 创建段
        # self.image= pygame.image.load()
        self.image = pygame.Surface((20, 40)).convert()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2()
        self.speed = 200

        # 修改段
        self.image.fill((0, 0, 0))

    def event(self, screen_size: tuple | list):
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

    def move(self, dt):
        if self.direction.magnitude():
            self.direction = self.direction.normalize()

        self.pos.x = self.pos.x + self.direction.x * self.speed * dt
        self.pos.y = self.pos.y + self.direction.y * self.speed * dt

        self.rect.center = self.pos

    def update(self, dt, screen_size: tuple | list):
        self.event(screen_size)
        self.move(dt)


class Game:
    def __init__(self):
        pygame.init()
        # 数据段
        self.sleep_time = [0, 1]

        self.fail = False
        self.balls = []
        self.resolution = (1280, 720)
        # self.background = pygame.image.load("./res/img/bg/bg.png")
        self.bg_color = (240, 240, 240)
        self.title = "弹球游戏 - by 爱喝牛奶の涛哥"

        # 调用段
        self.screen = pygame.display.set_mode(self.resolution)
        self.screen.fill(self.bg_color)
        self.display = self.screen.convert()
        pygame.display.flip()
        pygame.display.set_caption(self.title, self.title)
        pygame.display.set_icon(pygame.image.load("./res/img/icon/icon.jpg"))

        self.all_spr = pygame.sprite.Group()
        self.ball_spr = pygame.sprite.Group()

        self.player = Player((620, 340), self.all_spr)

        self.req = SandInfo()

        self.clock = pygame.time.Clock()

    def create_ball(self, pos: tuple | list, group):
        self.balls.append(Ball(pos, group))

    def create_ball_thread(self):
        while not self.fail:
            sleep(randint(*self.sleep_time) + random())
            self.create_ball((randint(0, self.screen.get_width()), randint(0, self.screen.get_height())),
                             self.ball_spr)

    def get_rank(self):
        ...

    def mainloop(self, skip_head: bool = False):
        tools = Tools()
        if skip_head is not True:
            tools.draw_text(self.screen, "弹球游戏", (10, 30), 100, stop_time=0)
            tools.draw_text(self.screen, "保证您不会被弹球碰到", (10, 150), 40, stop_time=0)
            tools.draw_text(self.screen, "使用 WASD 或 ↑↓←→(上下左右) 进行移动 (您也可以按下\"E\"手动增加弹球数量)",
                            (10, 200), 35, stop_time=0)
            tools.draw_text(self.screen, "按下任意键以开始", (500, 650), 35, stop_time="wait_key")

        Thread(target=self.create_ball_thread, daemon=True).start()
        while not self.fail:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit(0)
                if e.type == pygame.KEYUP and e.key == pygame.K_e:
                    self.create_ball((randint(0, self.screen.get_width()), randint(0, self.screen.get_height())),
                                     self.ball_spr)

            for obj in self.balls:
                if obj.on_player:
                    self.fail = True

            dt = self.clock.tick(60) / 1000
            self.display.fill(self.bg_color)
            tools.draw_text(self.display, "得分: {}".format(len(self.balls)), (10, 10), 35, stop_time=0)
            self.all_spr.draw(self.display)
            self.ball_spr.draw(self.display)
            self.all_spr.update(dt, self.screen.get_size())
            self.ball_spr.update(dt, self.player.pos, self.player.image.get_size())
            self.screen.blit(self.display, (0, 0))
            pygame.display.update()

        res = self.req.main(len(self.balls))

        if type(res) == dict:
            tools.draw_text(self.screen, "个人历史最高成绩: {} 分".format(res["personal_tallest"]), (150, 310), 50, stop_time=0)
            tools.draw_text(self.screen, "个人排名: {}".format(res["rank"]), (150, 370), 50, stop_time=0)

        if print_list[0] != "":
            tools.draw_text(self.screen, "成绩上传&获取失败", (150, 310), 50, stop_time=0)
            tools.draw_text(self.screen, print_list[0], (150, 400), 40, stop_time=0)
            print_list[0] = ""

        tools.draw_text(self.screen, "您失败了！3秒后按下任意键继续...(按\"ESC\"退出)", (150, 250), 50, stop_time=1)
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit(0)
                if e.type == pygame.KEYUP:
                    return True
            dt = self.clock.tick(60) / 1000


if __name__ == "__main__":
    game = Game()
    run = game.mainloop()
    while run:
        game = Game()
        run = game.mainloop(run)

# test = SandInfo()
# print(test.main(51))
