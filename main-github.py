from typing import Union

VERSION = (1, 7, 3)
NETWORK = False

from threading import Thread
from random import randint, random
from sys import exit
from time import sleep
from json import loads
from requests import get
from time import time as get_time
from os.path import exists, abspath
from subprocess import run as run_cmd
from controls import *
from wget import download as wget_download

import pygame

print_list = ["", ""]
qq = 0
online = False
nk_name = ""
config = {
    "show_locus": False
}


class ReqsThread(Thread):
    def __init__(self, func, d: bool = True):
        super(ReqsThread, self).__init__(daemon=d)
        self.res = 0
        self.error = None
        self.func = func

    def run(self):
        try:
            self.res = self.func()
        except Exception as e:
            self.res = -1
            self.error = e


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos: Union[tuple, list], group):
        super().__init__(group)
        self.r = 5
        self.player_spacing = self.r * 2

        self.image = pygame.Surface((self.r * 2, self.r * 2)).convert_alpha()
        self.image.fill((240, 240, 240, 0))
        pygame.draw.circle(self.image, "red", (self.r, self.r), self.r)
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
            self.on_player = True
        else:
            self.on_player = False

    def update(self, dt, player_pos: Union[tuple, list], player_size: Union[tuple, list],
               screen: pygame.Surface = None):
        self.goto_player(player_pos, player_size)
        self.move(dt)
        self.update_rect()
        self.check_is_on_player(player_pos, player_size)
        if screen is not None:
            pygame.draw.line(screen, (95, 226, 222), self.pos, player_pos, width=1)


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


class Mouse(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.image = pygame.Surface((1, 1)).convert_alpha()
        self.image.fill((0, 0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = pygame.mouse.get_pos()

    def update(self, dt, screen_size):
        self.rect.center = pygame.mouse.get_pos()


class Game:
    def __init__(self):
        pygame.init()
        # 数据段
        self.keys = {"e": False}
        self.sleep_time = [0, 1]

        self.px = 300
        self.developer = False
        self.died = False
        self.input_qq = False
        self.in_head = False
        self.tools = Tools()
        self.balls = []
        self.resolution = (1280, 720)
        # self.background = pygame.image.load("./res/img/bg/bg.png")
        self.bg_color = (240, 240, 240, 255)
        self.title = "弹球游戏 - by 爱喝牛奶の涛哥"

        # 调用段
        self.screen = pygame.display.set_mode(self.resolution)
        self.screen.fill(self.bg_color)
        self.display = self.screen.convert_alpha()
        pygame.display.flip()
        pygame.display.set_caption(self.title, self.title)
        pygame.display.set_icon(pygame.image.load("./res/img/icon/icon.jpg"))

        self.all_spr = pygame.sprite.Group()
        self.ball_spr = pygame.sprite.Group()
        self.input_boxs = pygame.sprite.Group()
        self.text_boxs = pygame.sprite.Group()

        self.player = Player((620, 340), self.all_spr)
        self.mouse = Mouse(self.all_spr)

        if NETWORK:
            self.req = Reqs()
            self.tips_info = ""
        else:
            self.tips_info = "\n您使用的是Github源码版本, 该版本为离线版本, 故您无法登录"

        self.clock = pygame.time.Clock()

    def create_ball(self, group):
        px = self.px

        while True:
            pos = (randint(0, self.screen.get_width()), randint(0, self.screen.get_height()))
            # if (self.player.pos[0] - round((self.player.image.get_size()[0] // 2) * 1.5)) <= pos[0] <= \
            #         (self.player.pos[0] + round((self.player.image.get_size()[0] // 2) * 1.5)) and \
            #         (self.player.pos[1] - round((self.player.image.get_size()[1] // 2) * 1.5)) <= pos[1] <= \
            #         (self.player.pos[1] + round((self.player.image.get_size()[1] // 2) * 1.5)):
            #     pass
            if self.player.pos[0] - px <= pos[0] <= self.player.pos[0] + px and self.player.pos[1] - px <= pos[1] <= \
                    self.player.pos[1] + px:
                pass
            else:
                break
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit(0)
        self._create_ball(pos, group)

    def _create_ball(self, pos: Union[tuple, list], group):
        self.balls.append(Ball(pos, group))

    def create_ball_thread(self):
        while not self.died:
            sleep_time = randint(*self.sleep_time) + random()
            if sleep_time >= 0:
                sleep(sleep_time)
            if not self.died:
                self.create_ball(self.ball_spr)

    @staticmethod
    def __write_qq():
        global qq

        with open("qq.txt", "w+") as qf:
            qf.write(str(qq))

    def update_ui(self, ver: list or tuple, url: str, wait_time: float = 1.5):
        ver_str = ""
        for item in ver:
            ver_str += f"{item}."
        ver_str = ver_str[:-1]

        url = self.req.url_root + url

        self.tools.draw_text(self.screen, "发现新版本 V{}".format(ver_str), (500, 300), 35, stop_time=0)
        self.tools.draw_text(self.screen, f"正在下载: {url}", (10, 340), 35, stop_time=0)
        if "https://" in url.lower() or "http://" in url.lower():
            res = ReqsThread(lambda: wget_download(url))
            res.start()

            i = 1
            low_time = get_time()
            while res.res == 0:
                self.screen.fill(self.bg_color)

                self.tools.draw_text(self.screen, "发现新版本 V{}".format(ver_str), (500, 300), 35, stop_time=0)
                if i == 1:
                    self.tools.draw_text(self.screen, f"正在下载: {url}.", (10, 340), 35, stop_time=0)
                elif i == 2:
                    self.tools.draw_text(self.screen, f"正在下载: {url}..", (10, 340), 35, stop_time=0)
                elif i == 3:
                    self.tools.draw_text(self.screen, f"正在下载: {url}...", (10, 340), 35, stop_time=0)
                else:
                    self.tools.draw_text(self.screen, f"正在下载: {url}", (10, 340), 35, stop_time=0)
                    i = 0

                if get_time() - low_time > 0.7:
                    i += 1
                    low_time = get_time()

                pygame.event.get()
                pygame.display.update()

            if res.res != -1:
                abs_path = abspath(res.res)

                self.screen.fill(self.bg_color)

                self.tools.draw_text(self.screen, "下载完成~ {}".format(abs_path), (500, 300), 35, stop_time=1.5)

                run_cmd("start update.exe -f {}".format(abs_path), shell=True)

                exit()
            else:
                self.screen.fill(self.bg_color)

                self.tools.draw_text(self.screen, "下载失败 {}".format(res.error), (500, 300), 35, stop_time=1.5)

    def input_qq_ui(self):
        global qq, online, nk_name

        if not NETWORK:  # 离线版本退出
            return

        if online is not True:
            self.input_qq = True
            if exists('qq.txt'):
                try:
                    with open("qq.txt", "r+") as qf:
                        qq = int(qf.read())

                    nk_name = self.req.get_nk(qq)
                    if nk_name != -1:
                        # self.tools.draw_text(self.screen, "登陆成功, 昵称：{}".format(nk_name), (330, 300), 35, stop_time=1.5)
                        online = True
                        nk_name = nk_name
                        self.input_qq = False
                        return
                    else:
                        pass
                except Exception as e:
                    pass

            self.input_qq = True
            input_box = InputBox(self.input_boxs, pygame.Rect(100, 300, self.screen.get_width() - 120, 55), 35,
                                 def_text="请输入QQ号", input_type=1)
            input_box.active = True

            while self.input_qq:
                self.screen.fill(self.bg_color)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit(0)
                    if event.type == pygame.KEYUP and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q):
                        self.input_qq = False
                    if self.input_qq:
                        input_box.event(event)
                if input_box.active is False and input_box.done is True:
                    try:
                        qq = int(input_box.text)
                        nk_name = self.req.get_nk(qq)
                        if nk_name != -1:
                            self.tools.draw_text(self.screen, "登陆成功, 昵称：{}".format(nk_name), (330, 300), 35,
                                                 color="green", stop_time=1.5)
                            self.__write_qq()
                            online = True
                            nk_name = nk_name
                            self.input_qq = False
                            return
                        else:
                            self.tools.draw_text(self.screen, "您的QQ号输入有误！无法成功获取昵称！", (300, 650), 35,
                                                 stop_time=0)
                    except Exception as e:
                        self.tools.draw_text(self.screen, "请输入正确的QQ号！", (470, 650), 35, stop_time=0)
                self.tools.draw_text(self.screen, "登陆", (10, 300), 40, stop_time=0)
                self.clock.tick(60)
                if self.input_qq:
                    self.input_boxs.update(False)
                    self.input_boxs.draw(self.screen)
                    pygame.display.update()
        else:
            self.input_qq = True
            self.screen.fill(self.bg_color)
            self.tools.draw_text(self.screen, "按 Delete 键以退出登陆 (账户: {})".format(nk_name), (250, 300), 35,
                                 color="red", stop_time=0)
            pygame.display.update()
            while online and self.input_qq:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        exit(0)
                    if e.type == pygame.KEYUP and (e.key == pygame.K_ESCAPE or e.key == pygame.K_q):
                        self.input_qq = False
                    if e.type == pygame.KEYUP and e.key == pygame.K_DELETE:
                        qq = 0
                        self.__write_qq()
                        online = False
            if not online:
                self.screen.fill(self.bg_color)
                self.tools.draw_text(self.screen, "退出登录成功", (550, 300), 35, color="red", stop_time=1.5)
                pygame.display.update()
                self.input_qq = False

        self.input_boxs = pygame.sprite.Group()

    def bulletin_ui(self):
        self.screen.fill(self.bg_color)

        bulletin: dict = self.req.get_bulletin()
        if bulletin["code"] == "200":
            bulletin_info = bulletin["msg"]

            if len(bulletin_info) > 0:
                self.tools.draw_text(self.screen, "公告", (530, 10), 50, stop_time=0)
                self.tools.draw_text(self.screen, bulletin_info, (10, 100), 30, stop_time=3)

    def header_ui(self, skip_head: bool):
        if NETWORK:
            res = self.req.update()
            if res is not None:
                update_url = res[0]
                latest_version = res[1]
                self.update_ui(latest_version, update_url)

        if skip_head is not True:
            if NETWORK:
                self.input_qq_ui()
                self.bulletin_ui()

            self.in_head = True
            while self.in_head:
                self.screen.fill(self.bg_color)

                self.tools.draw_text(self.screen, "弹球游戏", (10, 30), 100, stop_time=0)
                self.tools.draw_text(self.screen, "保证您不被弹球碰到", (10, 150), 40, stop_time=0)
                self.tools.draw_text(self.screen, "使用 WASD 或 ↑↓←→(上下左右) 进行移动",
                                     (10, 200), 35, stop_time=0)

                self.tools.draw_text(self.screen, f"当前版本：V{VERSION}", (1300, 683), 25, stop_time=0)
                if not online:
                    self.tools.draw_text(self.screen, "离线模式" + self.tips_info,
                                         (1300, 5), 25, color="red", stop_time=0)
                    if NETWORK:
                        self.tools.draw_text(self.screen, "您没有登陆！", (300, 500), 50, color="red", stop_time=0)
                        self.tools.draw_text(self.screen, "登陆即可成绩云同步并保存最高成绩!", (300, 570), 50,
                                             color="green",
                                             stop_time=0)
                else:
                    self.tools.draw_text(self.screen, nk_name,
                                         (1300, 37), 25, color="green", stop_time=0)
                    self.tools.draw_text(self.screen, "在线模式",
                                         (1300, 5), 25, color="green", stop_time=0)
                if NETWORK:
                    self.tools.draw_text(self.screen, "按下\"Q\"以打开登录/登出界面",
                                         (10, 240), 35, stop_time=0)
                # self.tools.draw_text(self.screen, "注意：\n您可以按下\"E\"手动增加弹球数量",
                #                      (10, 300), 35, color="red", stop_time=0)
                self.tools.draw_text(self.screen, "按下任意键以开始", (500, 650), 35, stop_time=0)
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        exit(0)
                    if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit(0)
                    if e.type == pygame.KEYUP and e.key == pygame.K_q:
                        self.input_qq_ui()
                    elif e.type == pygame.KEYUP:
                        self.in_head = False

                self.clock.tick(60)
                pygame.display.update()

    def ender_ui(self):

        global print_list
        text_box_append = False

        if online and NETWORK:
            res = ReqsThread(lambda: self.req.main(len(self.balls)))
            res.start()

        for i in range(50 if NETWORK else 100):
            pygame.event.get()
            sleep(0.01)

        while True:
            self.screen.fill(self.bg_color)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit(0)

                if e.type == pygame.KEYUP and e.key == pygame.K_q:
                    self.input_qq_ui()
                elif e.type == pygame.KEYUP:
                    if online and NETWORK:
                        try:
                            if res.res != 0:
                                return True
                        except UnboundLocalError as e:
                            return True
                    else:
                        return True

            if online and NETWORK:
                try:
                    if type(res.res) == dict:
                        self.tools.draw_text(self.screen, "个人历史最高成绩: {} 分".format(res.res["personal_tallest"]),
                                             (150, 310),
                                             50,
                                             stop_time=0)

                        self.tools.draw_text(self.screen, "个人排名: {}".format(res.res["rank"]), (150, 370), 50,
                                             stop_time=0)
                    elif res.res == 0:
                        self.tools.draw_text(self.screen, print_list[1], (150, 310), 50, stop_time=0)
                    elif res.res == -1:
                        self.tools.draw_text(self.screen, "成绩上传&获取失败", (150, 310), 50, stop_time=0)
                        # self.tools.draw_text(self.screen, print_list[1], (150, 400), 40, stop_time=0)
                        if text_box_append is False:
                            TextBox(self.text_boxs, self.screen.get_size(), (150, 400), print_list[1], 40)
                            text_box_append = True
                            self.text_boxs.update(0)
                        self.text_boxs.draw(self.screen)
                except UnboundLocalError as e:
                    pass
            else:
                if NETWORK:
                    self.tools.draw_text(self.screen, "您没有登陆！", (150, 310), 50, color="red", stop_time=0)
                    self.tools.draw_text(self.screen, "登陆即可成绩云同步并保存最高成绩 (按\"Q\"登陆)", (150, 370), 50,
                                         color="green",
                                         stop_time=0)
                self.tools.draw_text(self.screen, self.tips_info[2:],
                                     (1300, 5), 25, color="red", stop_time=0)
            if print_list[0] != "":
                self.tools.draw_text(self.screen, "成绩上传&获取失败", (150, 310), 50, stop_time=0)
                self.tools.draw_text(self.screen, print_list[0], (150, 400), 40, stop_time=0)

                print_list[0] = ""

            self.tools.draw_text(self.screen, "最终得分：{}".format(len(self.balls)), (150, 190), 50, color="blue",
                                 stop_time=0)
            self.tools.draw_text(self.screen, "您失败了！3秒后按下任意键继续...(按\"ESC\"退出)", (150, 250), 50,
                                 stop_time=0)
            self.tools.draw_text(self.screen, f"当前版本：V{VERSION}", (1300, 683), 25, stop_time=0)

            dt = self.clock.tick(60) / 1000
            pygame.display.update()

    def online_ui(self):
        global online

        running = True

        if online:

            while running:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        exit(0)
                    if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit(0)

    def main_ui(self, skip_head: bool = False):

        self.header_ui(skip_head)

        Thread(target=self.create_ball_thread, daemon=True).start()
        sleep(0.1)
        while not self.died:
            self.display.fill(self.bg_color)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit(0)
                if self.developer:
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_e:
                        self.keys["e"] = True
                    elif e.type == pygame.KEYUP and e.key == pygame.K_e:
                        self.keys["e"] = False
                if e.type == pygame.KEYUP and e.key == pygame.K_F12:
                    # self.developer = not self.developer  # 反向
                    self.developer = False

                if e.type == pygame.KEYUP and e.key == pygame.K_q:
                    self.input_qq_ui()

            for ball in self.balls:
                if ball.on_player:
                    self.died = True

            if self.keys["e"]:
                self.create_ball(self.ball_spr)

            if not online:
                self.tools.draw_text(self.display, "离线模式" + self.tips_info,
                                     (1300, 5), 25, color="red", stop_time=0)
            else:
                self.tools.draw_text(self.display, nk_name,
                                     (1300, 37), 25, color="green", stop_time=0)
                self.tools.draw_text(self.display, "在线模式",
                                     (1300, 5), 25, color="green", stop_time=0)

            dt = self.clock.tick(60) / 1000
            self.all_spr.draw(self.display)
            self.ball_spr.draw(self.display)
            self.all_spr.update(dt, self.screen.get_size())
            self.ball_spr.update(dt, self.player.pos, self.player.image.get_size(),
                                 self.display if config["show_locus"] else None)

            self.tools.draw_text(self.display, "得分: {}".format(len(self.balls)), (10, 10), 35, color=(0, 0, 226),
                                 stop_time=0)
            self.tools.draw_text(self.display, f"当前版本：V{VERSION}", (1300, 683), 25, bg_color=None, stop_time=0)

            self.screen.blit(self.display, (0, 0))
            pygame.display.update()

        return self.ender_ui()


if __name__ == "__main__":
    game = Game()
    run = game.main_ui()
    while run:
        game = Game()
        run = game.main_ui(run)
