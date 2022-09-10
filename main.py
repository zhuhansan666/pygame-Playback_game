import traceback
from os.path import exists, abspath
from random import uniform, randint, random
from subprocess import run as run_cmd
from threading import Thread
from time import time as get_time

import pygame
from wget import download as wget_download

# my pkg
from ball import Ball

from controls import *

from g import VERSION
from g import ReqsThread
from g import inform, logging

from player import Player

try:
    from req import Reqs
except ImportError:
    NETWORK = False
else:
    NETWORK = True

try:
    from config import config

    for k, w in inform.default_config.items():
        if k not in config:
            config[k] = w
except ImportError:
    config = inform.default_config

inform.output_full_log = config["output_full_log"]


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
        self.default_sleep_time = [0, 1]
        self.sleep_time = config["sleep_time"]

        self.px = 300
        self.developer = False
        self.pause = False
        self.died = False
        self.input_qq = False
        self.in_head = False
        self.bulletin = False
        self.update = False
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

        self.black_sur = pygame.Surface(self.display.get_size()).convert_alpha()
        self.black_sur.fill((0, 0, 0, 130))

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
            try:
                sleep_time = uniform(*self.sleep_time) + random()
                if sleep_time >= 0:
                    sleep(sleep_time)
                if not self.died and not self.pause:
                    self.create_ball(self.ball_spr)
            except Exception as e:
                logging.write_log(f"创建球发生错误: {e}")
                if inform.output_full_log:
                    logging.write_log(f"创建球发生错误: \"{traceback.format_exc()}\"", log_type=2)

    @staticmethod
    def __write_qq():
        try:
            with open("qq.txt", "w+") as qf:
                qf.write(str(inform.qq))
        except Exception as e:
            logging.write_log(f"qq.txt 写入失败: {e}")
            if inform.output_full_log:
                logging.write_log(f"qq.txt 写入失败: \"{traceback.format_exc()}\"", log_type=2)

    def update_ui(self, ver: list or tuple, url: str):
        self.update = True

        ver_str = ""
        for item in ver:
            ver_str += f"{item}."
        ver_str = ver_str[:-1]

        url = self.req.url_root + url

        self.tools.draw_text(self.screen, "发现新版本 V{}".format(ver_str), (500, 300), 35, stop_time=0)
        self.tools.draw_text(self.screen, f"正在下载: {url}", (10, 340), 35, stop_time=0)
        if "https://" in url.lower() or "http://" in url.lower():
            logging.write_log(f"更新版本: V{ver_str} ({url})")
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

                self.update = False

                exit()
            else:
                self.screen.fill(self.bg_color)

                self.tools.draw_text(self.screen, "下载失败 {}".format(res.error), (500, 300), 35, stop_time=1.5)

    def input_qq_ui(self):

        if not NETWORK:  # 离线版本退出
            return

        if inform.online is not True:
            self.input_qq = True
            if exists('qq.txt'):
                try:
                    with open("qq.txt", "r+") as qf:
                        inform.qq = int(qf.read())

                    inform.nk_name = self.req.get_nk(inform.qq)
                    if inform.nk_name != -1:
                        inform.online = True
                        inform.nk_name = inform.nk_name
                        self.input_qq = False
                        return
                    else:
                        pass
                except ValueError:  # 非int
                    pass
                except Exception as e:
                    logging.write_log(f"qq.txt 读取错误: {e}")
                    if inform.output_full_log:
                        logging.write_log(f"qq.txt 读取错误: \"{traceback.format_exc()}\"", log_type=2)

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
                        inform.offline = True
                        self.input_qq = False
                    if self.input_qq:
                        input_box.event(event)
                if input_box.active is False and input_box.done is True:
                    try:
                        inform.qq = int(input_box.text)
                        inform.nk_name = self.req.get_nk(inform.qq)
                        if inform.nk_name != -1:
                            self.tools.draw_text(self.screen, "登陆成功, 昵称：{}".format(inform.nk_name), (330, 300),
                                                 35,
                                                 color="green", stop_time=1.5)
                            self.__write_qq()
                            inform.online = True
                            inform.nk_name = inform.nk_name
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
            self.tools.draw_text(self.screen, "按 Delete 键以退出登陆 (账户: {})".format(inform.nk_name), (250, 300),
                                 35,
                                 color="red", stop_time=0)
            pygame.display.update()
            while inform.online and self.input_qq:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        exit(0)
                    if e.type == pygame.KEYUP and (e.key == pygame.K_ESCAPE or e.key == pygame.K_q):
                        inform.offline = True
                        self.input_qq = False
                    if e.type == pygame.KEYUP and e.key == pygame.K_DELETE:
                        inform.qq = ""
                        self.__write_qq()
                        inform.online = False
            if not inform.online:
                self.screen.fill(self.bg_color)
                self.tools.draw_text(self.screen, "退出登录成功", (550, 300), 35, color="red", stop_time=1.5)
                pygame.display.update()
                self.input_qq = False

        self.input_boxs = pygame.sprite.Group()

    def bulletin_ui(self):
        bulletin: dict = self.req.get_bulletin()

        if bulletin["code"] == "200":
            bulletin_info = bulletin["msg"]

            if len(bulletin_info) > 0:
                temp_group = pygame.sprite.Group()
                TextBox(temp_group, self.screen.get_size(), (10, 100), bulletin_info.replace("<br>", "\n"), 30)

                while self.input_qq:  # 等待qq输入完成
                    pygame.event.get()
                    sleep(0.1)

                self.bulletin = True
                for i in range(300):
                    self.screen.fill(self.bg_color)

                    self.tools.draw_text(self.screen, "公告", (530, 10), 50, stop_time=0)
                    temp_group.draw(self.screen)

                    pygame.event.get()
                    pygame.display.update()

                    sleep(0.01)
                self.bulletin = False

    def header_ui(self, skip_head: bool):
        if NETWORK:
            def check_all():
                res = self.req.update()
                if res is not None:
                    update_url = res[0]
                    latest_version = res[1]
                    self.update_ui(latest_version, update_url)

            update_t = Thread(target=check_all, daemon=True)
            update_t.start()

        if skip_head is not True:
            if NETWORK:
                def bulletin_ui_thread():
                    self.bulletin_ui()

                t = Thread(target=bulletin_ui_thread, daemon=True)
                t.start()
            else:
                t = None

            if NETWORK:
                update_t.join()

            self.in_head = True

            while self.in_head:

                if t is None or not any((self.bulletin, self.update)) or not t.is_alive():
                    self.screen.fill(self.bg_color)

                    self.tools.draw_text(self.screen, "弹球游戏", (10, 30), 100, stop_time=0)
                    self.tools.draw_text(self.screen, "保证您不被弹球碰到", (10, 150), 40, stop_time=0)
                    self.tools.draw_text(self.screen, "使用 WASD 或 ↑↓←→(上下左右) 进行移动",
                                         (10, 200), 35, stop_time=0)

                    self.tools.draw_text(self.screen, f"当前版本：V{VERSION}", (1300, 683), 25, stop_time=0)
                    if not inform.online:
                        self.tools.draw_text(self.screen, "离线模式" + self.tips_info,
                                             (1300, 5), 25, color="red", stop_time=0)
                        if NETWORK:
                            self.tools.draw_text(self.screen, "您没有登陆！", (300, 500), 50, color="red", stop_time=0)
                            self.tools.draw_text(self.screen, "登陆即可成绩云同步并保存最高成绩!", (300, 570), 50,
                                                 color="green",
                                                 stop_time=0)
                    else:
                        self.tools.draw_text(self.screen, inform.nk_name,
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

                    pygame.display.update()

                    if not any((self.bulletin, self.update)) and not inform.online and not inform.offline:
                        self.input_qq_ui()

                    self.clock.tick(60)

    def ender_ui(self):

        text_box_append = False

        if inform.online and NETWORK:
            if self.sleep_time == self.default_sleep_time:
                res = ReqsThread(lambda: self.req.main(len(self.balls)))
                res.start()
            else:
                res = None
                inform.print_lst[1] = '您的球生成时间与服务端不匹配\n您修改了(config file["sleep_time"])' \
                                      '\n您可删除 config file 以重新配置'

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
                    if inform.online and NETWORK:
                        try:
                            if res is not None and res.res != 0:
                                return True
                            elif res is None:
                                return True
                        except UnboundLocalError as e:
                            return True
                    else:
                        return True

            if inform.online and NETWORK:
                try:
                    if res is not None and type(res.res) == dict:
                        self.tools.draw_text(self.screen, "个人历史最高成绩: {} 分".format(res.res["personal_tallest"]),
                                             (150, 310),
                                             50,
                                             stop_time=0)

                        self.tools.draw_text(self.screen, "个人排名: {}".format(res.res["rank"]), (150, 370), 50,
                                             stop_time=0)
                    elif res is not None and res.res == 0:
                        self.tools.draw_text(self.screen, inform.print_lst[1], (150, 310), 50, stop_time=0)
                    elif res is not None and res.res == -1:
                        self.tools.draw_text(self.screen, "成绩上传&获取失败", (150, 310), 50, stop_time=0)
                        # self.tools.draw_text(self.screen, inform.print_lst[1], (150, 400), 40, stop_time=0)
                        if text_box_append is False:
                            TextBox(self.text_boxs, self.screen.get_size(), (150, 400), inform.print_lst[1], 40)
                            text_box_append = True
                            self.text_boxs.update(0)
                        self.text_boxs.draw(self.screen)
                    elif res is None:
                        self.tools.draw_text(self.screen, inform.print_lst[1], (150, 310), 40, stop_time=0)
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
            if inform.print_lst[0] != "":
                self.tools.draw_text(self.screen, "成绩上传&获取失败", (150, 310), 50, stop_time=0)
                self.tools.draw_text(self.screen, inform.print_lst[0], (150, 400), 40, stop_time=0)

                inform.print_lst[0] = ""

            self.tools.draw_text(self.screen, "最终得分：{}".format(len(self.balls)), (150, 190), 50, color="blue",
                                 stop_time=0)
            self.tools.draw_text(self.screen, "您失败了！3秒后按下任意键继续...(按\"ESC\"退出)", (150, 250), 50,
                                 stop_time=0)
            self.tools.draw_text(self.screen, f"当前版本：V{VERSION}", (1300, 683), 25, stop_time=0)

            dt = self.clock.tick(60) / 1000
            pygame.display.update()

    def online_ui(self):

        running = True

        if inform.online:

            while running:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        pygame.quit()
                        exit(0)
                    if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit(0)

    def main_ui(self, skip_head: bool = False):
        def sleep_and_pause(sec: float):
            if sec > 0:
                sleep(sec)
            self.pause = False

        self.header_ui(skip_head)

        Thread(target=self.create_ball_thread, daemon=True).start()
        # sleep(0.1)

        while not self.died:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if e.type == pygame.KEYUP and (e.key == pygame.K_ESCAPE or e.key == pygame.K_SPACE):
                    self.pause = not self.pause
                if self.developer:
                    if e.type == pygame.KEYDOWN and e.key == pygame.K_e:
                        self.keys["e"] = True
                    elif e.type == pygame.KEYUP and e.key == pygame.K_e:
                        self.keys["e"] = False
                if e.type == pygame.KEYUP and e.key == pygame.K_F12:
                    # self.developer = not self.developer  # 反向
                    self.developer = False

                if e.type == pygame.KEYUP and e.key == pygame.K_q:
                    self.pause = True
                    self.input_qq_ui()
                    Thread(target=lambda: sleep_and_pause(0.3), daemon=True).start()

            if inform.player_died:
                self.died = True

            if self.keys["e"]:
                self.create_ball(self.ball_spr)

            self.screen.fill(self.bg_color)
            self.display.fill(self.bg_color)

            dt = self.clock.tick(60) / 1000

            self.all_spr.draw(self.display)
            self.ball_spr.draw(self.display)

            if not inform.online:
                self.tools.draw_text(self.display, "离线模式" + self.tips_info,
                                     (1300, 5), 25, color="red", stop_time=0)
            else:
                self.tools.draw_text(self.display, inform.nk_name,
                                     (1300, 37), 25, color="green", stop_time=0)
                self.tools.draw_text(self.display, "在线模式",
                                     (1300, 5), 25, color="green", stop_time=0)

            self.tools.draw_text(self.display, "得分: {}".format(len(self.balls)), (10, 10), 35, color=(0, 0, 226),
                                 stop_time=0)
            self.tools.draw_text(self.display, f"当前版本：V{VERSION}", (1300, 683), 25, bg_color=None, stop_time=0)

            if pygame.display.get_active() and not self.pause:
                self.all_spr.update(dt, self.screen.get_size())
                self.ball_spr.update(dt, self.player.pos, self.player.image.get_size(),
                                     self.display if config["show_locus"] else None)

            else:
                self.display.blit(self.black_sur, (0, 0))
                self.tools.draw_text(self.display, "已暂停", (1300, 100), 100, stop_time=0)

            self.screen.blit(self.display, (0, 0))
            pygame.display.update()

        inform.player_died = False
        return self.ender_ui()


if __name__ == "__main__":
    game = Game()
    run = game.main_ui()
    while run:
        game = Game()
        run = game.main_ui(run)
