from __future__ import annotations

VERSION = (1, 6, 0)

from threading import Thread
from random import randint, random
from sys import exit
from time import sleep
from json import loads
from requests import get
from time import time as getTime
from os.path import exists
from subprocess import run
import pygame

print_list = ["", ""]
qq = 0
online = False
nk_name = ""


class ReqsThread(Thread):
    def __init__(self, func, d: bool = True):
        super(ReqsThread, self).__init__(daemon=d)
        self.res: dict | int = 0
        self.func = func

    def run(self):
        self.res = self.func()


class Tools:
    def __init__(self):
        self.font_file = './res/font/MiSans-Light.ttf'
        self.clock = pygame.time.Clock()

    def draw_text(self, surface: pygame.Surface, text: str, pos: tuple | list, size: int,
                  color: str | tuple | list = (0, 0, 0), stop_time: float | str = 1.5):
        pos = list(pos)
        f = pygame.font.Font(self.font_file, size)
        text_list = text.split("\n")
        for i in range(len(text_list)):
            if type(text_list[i]) == str:
                f_surface = f.render(text_list[i], True, color, (240, 240, 240))
                if surface.get_width() - (f_surface.get_width() + pos[0]) <= 0:
                    if f_surface.get_width() > surface.get_width():
                        pos[0] = 10
                    else:
                        pos[0] = surface.get_width() - f_surface.get_width() - 10
                pos[1] = pos[1] + i * f_surface.get_height()
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


class InputBox:
    def __init__(self, rect: pygame.Rect, font_size: int, def_text: str = "") -> None:
        """
        rect，传入矩形实体，传达输入框的位置和大小
        """
        self.boxBody: pygame.Rect = rect
        self.color_inactive = pygame.Color((100, 100, 100))  # 未被选中的颜色
        self.color_active = pygame.Color('black')  # 被选中的颜色
        self.color = self.color_inactive  # 当前颜色，初始为未激活颜色
        self.active = False
        self.text = ''
        self.done = False
        self.font_file = './res/font/MiSans-Light.ttf'
        self.font = pygame.font.Font(self.font_file, font_size)
        self.def_text = def_text

    def dealEvent(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.boxBody.collidepoint(event.pos):  # 若按下鼠标且位置在文本框
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if (
                self.active) else self.color_inactive
        if event.type == pygame.KEYDOWN:  # 键盘输入响应
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.done = True
                    self.active = False
                    self.color = self.color_inactive
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, screen: pygame.surface.Surface):
        txtSurface = self.font.render(
            self.text, True, self.color)  # 文字转换为图片
        width = max(200, txtSurface.get_width() + 10)  # 当文字过长时，延长文本框
        self.boxBody.w = width
        if len(self.text) <= 0:
            font_surface = self.font.render(
                self.def_text, True, self.color_inactive)
            width = max(200, font_surface.get_width() + 10)
            self.boxBody.w = width
            screen.blit(font_surface, (self.boxBody.x + 5, self.boxBody.y + 5))
        screen.blit(txtSurface, (self.boxBody.x + 5, self.boxBody.y + 5))
        pygame.draw.rect(screen, self.color, self.boxBody, 2)


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos: tuple | list, group):
        super().__init__(group)
        self.r = 5
        self.player_spacing = self.r

        self.image = pygame.Surface((self.r * 2, self.r * 2)).convert()
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

        if any((player_rect[0] < (self.pos[0] - self.r) < player_rect[2],
                player_rect[0] < (self.pos[0] + self.r) < player_rect[2])) and any((
                player_rect[1] < self.pos[1] - self.r < player_rect[3], player_rect[1] < self.pos[1] + self.r <
                                                                        player_rect[3])):
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
        self.keys = {"e": False}
        self.sleep_time = [0, 1]

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
        self.display = self.screen.convert()
        pygame.display.flip()
        pygame.display.set_caption(self.title, self.title)
        pygame.display.set_icon(pygame.image.load("./res/img/icon/icon.jpg"))

        self.all_spr = pygame.sprite.Group()
        self.ball_spr = pygame.sprite.Group()

        self.player = Player((620, 340), self.all_spr)

        self.req = Reqs()

        self.clock = pygame.time.Clock()

    def create_ball(self, group):
        px = 220

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

    def _create_ball(self, pos: tuple | list, group):
        self.balls.append(Ball(pos, group))

    def create_ball_thread(self):
        while not self.died:
            sleep(randint(*self.sleep_time) + random())
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

        self.tools.draw_text(self.screen, "发现新版本 V{}\n{}".format(ver_str, url), (500, 300), 35, stop_time=wait_time)
        if "https://" in url.lower() or "http://" in url.lower():
            run("explorer {}".format(url), shell=True)

    def input_qq_ui(self):
        global qq, online, nk_name

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
            input_box = InputBox(pygame.Rect(500, 300, 0, 55), 32, "请输入QQ号")
            input_box.active = True
            input_box.color = input_box.color_active
            while self.input_qq:
                self.screen.fill(self.bg_color)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit(0)
                    if event.type == pygame.KEYUP and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q):
                        self.input_qq = False
                    if self.input_qq:
                        input_box.dealEvent(event)
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
                            self.tools.draw_text(self.screen, "您的QQ号输入有误！无法成功获取昵称！", (300, 650), 35, stop_time=0)
                    except Exception as e:
                        self.tools.draw_text(self.screen, "请输入正确的QQ号！", (470, 650), 35, stop_time=0)
                self.tools.draw_text(self.screen, "登陆", (410, 300), 40, stop_time=0)
                self.clock.tick(60)
                if self.input_qq:
                    input_box.draw(self.screen)
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

    def bulletin_ui(self):
        self.screen.fill(self.bg_color)

        bulletin: dict = self.req.get_bulletin()
        if bulletin["code"] == "200":
            bulletin_info = bulletin["msg"]

            if len(bulletin_info) > 0:
                self.tools.draw_text(self.screen, "公告", (530, 10), 50, stop_time=0)
                self.tools.draw_text(self.screen, bulletin_info, (10, 100), 30, stop_time=3)

    def header(self, skip_head: bool):
        res = self.req.update()
        if res is not None:
            update_url = res[0]
            latest_version = res[1]
            self.update_ui(latest_version, update_url)

        if skip_head is not True:
            self.input_qq_ui()
            self.bulletin_ui()
            self.in_head = True
            while self.in_head:
                self.screen.fill(self.bg_color)

                self.tools.draw_text(self.screen, "弹球游戏", (10, 30), 100, stop_time=0)
                self.tools.draw_text(self.screen, "保证您不被弹球碰到", (10, 150), 40, stop_time=0)
                self.tools.draw_text(self.screen, "使用 WASD 或 ↑↓←→(上下左右) 进行移动",
                                     (10, 200), 35, stop_time=0)
                if not online:
                    self.tools.draw_text(self.screen, "离线模式",
                                         (1300, 5), 25, color="red", stop_time=0)
                    self.tools.draw_text(self.screen, "您没有登陆！", (300, 500), 50, color="red", stop_time=0)
                    self.tools.draw_text(self.screen, "登陆即可成绩云同步并保存最高成绩!", (300, 570), 50, color="green",
                                         stop_time=0)
                else:
                    self.tools.draw_text(self.screen, nk_name,
                                         (1300, 37), 25, color="green", stop_time=0)
                    self.tools.draw_text(self.screen, "在线模式",
                                         (1300, 5), 25, color="green", stop_time=0)

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

    def ender(self):
        global print_list

        if online:
            res = ReqsThread(lambda: self.req.main(len(self.balls)))
            res.start()

        for i in range(50):
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
                    if online:
                        try:
                            if res.res != 0:
                                return True
                        except UnboundLocalError as e:
                            return True
                    else:
                        return True

            if online:
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
                        self.tools.draw_text(self.screen, print_list[1], (150, 400), 40, stop_time=0)
                except UnboundLocalError as e:
                    pass
            else:
                self.tools.draw_text(self.screen, "您没有登陆！", (150, 310), 50, color="red", stop_time=0)
                self.tools.draw_text(self.screen, "登陆即可成绩云同步并保存最高成绩 (按\"Q\"登陆)", (150, 370), 50, color="green",
                                     stop_time=0)
            if print_list[0] != "":
                self.tools.draw_text(self.screen, "成绩上传&获取失败", (150, 310), 50, stop_time=0)
                self.tools.draw_text(self.screen, print_list[0], (150, 400), 40, stop_time=0)

            self.tools.draw_text(self.screen, "您失败了！3秒后按下任意键继续...(按\"ESC\"退出)", (150, 250), 50, stop_time=0)

            pygame.display.update()

            dt = self.clock.tick(60) / 1000

    print_list[0] = ""

    def mainloop(self, skip_head: bool = False):

        self.header(skip_head)

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
                    self.developer = not self.developer  # 反向

                if e.type == pygame.KEYUP and e.key == pygame.K_q:
                    self.input_qq_ui()

            for obj in self.balls:
                if obj.on_player:
                    self.died = True

            if self.keys["e"]:
                self.create_ball(self.ball_spr)

            if not online:
                self.tools.draw_text(self.display, "离线模式",
                                     (1300, 5), 25, color="red", stop_time=0)
            else:
                self.tools.draw_text(self.display, nk_name,
                                     (1300, 37), 25, color="green", stop_time=0)
                self.tools.draw_text(self.display, "在线模式",
                                     (1300, 5), 25, color="green", stop_time=0)

            dt = self.clock.tick(60) / 1000
            self.tools.draw_text(self.display, "得分: {}".format(len(self.balls)), (10, 10), 35, color=(0, 0, 226),
                                 stop_time=0)
            self.all_spr.draw(self.display)
            self.ball_spr.draw(self.display)
            self.all_spr.update(dt, self.screen.get_size())
            self.ball_spr.update(dt, self.player.pos, self.player.image.get_size())
            self.screen.blit(self.display, (0, 0))
            pygame.display.update()

        return self.ender()


if __name__ == "__main__":
    game = Game()
    run = game.mainloop()
    while run:
        game = Game()
        run = game.mainloop(run)
