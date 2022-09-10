import pygame
from controls import *
from sys import exit
from time import time
from pyperclip import paste


class Choose:
    def __init__(self, screen: pygame.Surface = None):
        self.screen = screen

        self.bg_color = (240, 240, 240)

        self.tools = Tools()

        self.done = None

        self.text = [
            "创建房间",
            "加入房间",
        ]

        self.choose = 0

        self.events = {

        }

    def reset_text(self):
        self.text = [
            "创建房间",
            "加入房间",
        ]

    def init(self, screen: pygame.Surface):
        if self.screen is None:
            self.screen = screen

    def redraw(self):
        self.screen.fill(self.bg_color)

        for i in range(len(self.text)):
            if i == self.choose:
                self.text[i] += " ←"
            self.tools.draw_text(self.screen, self.text[i], (510, 10 + 50 * i), 35, stop_time=0)

    def change_choose(self, num):
        if num < 0:
            if self.choose > 0:
                self.choose += num
        elif num > 0:
            if self.choose < len(self.text) - 1:
                self.choose += num

    def __exit(self):
        pygame.quit()
        exit(0)

    def event(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.change_choose(-1)
        if keys[pygame.K_DOWN]:
            self.change_choose(1)
        if keys[pygame.K_RETURN]:
            self.done = self.choose

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.__exit()
            if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                self.__exit()

    def mainloop(self):
        while self.done is None:
            self.event()

            self.redraw()
            self.reset_text()

            pygame.display.update()


class CreateRoom:
    def __init__(self, screen: pygame.Surface = None):
        self.screen = screen

        self.bg_color = (240, 240, 240)

        self.tools = Tools()

        self.all_spr = pygame.sprite.Group()
        self.input_box = pygame.sprite.Group()

        self.done = False
        self.keys = {
            pygame.K_RETURN: False
        }
        self.tips: list = ["", ""]

        self.res = None

        self.__init()

    def init(self, screen: pygame.Surface):
        if self.screen is None:
            self.screen = screen

    def __init(self):
        self.input_boxs = [
            InputBox(self.input_box, pygame.Rect(100, 170, self.screen.get_width() - 210, 35), 35,
                     def_text="房间名称(若需输入中文请复制粘贴)", input_type=3, paste=paste),
            InputBox(self.input_box, pygame.Rect(100, 250, self.screen.get_width() - 210, 35), 35,
                     def_text="房间描述(若需输入中文请复制粘贴)", input_type=3, paste=paste),
        ]

        self.input_boxs[0].active = True

    def __exit(self):
        # pygame.quit()
        # exit(0)
        self.done = True

    def event(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.__exit()
            if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                self.__exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                self.keys[pygame.K_RETURN] = True
            if e.type == pygame.KEYUP and e.key == pygame.K_RETURN:
                if self.keys[pygame.K_RETURN] is True:
                    self.keys[pygame.K_RETURN] = False
                    self.set_done()

            self.input_box.update(e)

    def set_done(self):
        self.tips: list = ["", ""]
        if self.input_boxs[0].done and len(self.input_boxs[0].text) > 0:
            texts = [self.input_boxs[0].text, self.input_boxs[1].text]
            if len(texts[1]) <= 0:
                texts[1] = "-"
            self.res = texts
            self.done = True
        else:
            self.tips[0] = "房间名不能为空"
            self.input_boxs[0].active = True

    def redraw(self):
        self.input_box.update(False)

        self.screen.fill(self.bg_color)

        self.input_box.draw(self.screen)

        if self.tips[0] != "":
            self.tools.draw_text(self.screen, self.tips[0], (100, 120), 35, stop_time=0)
        elif self.tips[1] != "":
            self.tools.draw_text(self.screen, self.tips[1], (100, 200), 35, stop_time=0)

    def mainloop(self):
        while not self.done:
            self.event()
            self.redraw()

            pygame.display.update()


class RoomIDShow:
    def __init__(self, roomid: Union[str, int], create: bool, screen: pygame.Surface = None):
        if type(roomid) == int:
            roomid = str(roomid)

        self.screen = screen

        self.bg_color = (240, 240, 240)

        self.tools = Tools()

        self.all_spr = pygame.sprite.Group()

        self.done = False
        self.roomid = roomid
        self.create = create

    def init(self, screen: pygame.Surface):
        if self.screen is None:
            self.screen = screen

    def __exit(self):
        # pygame.quit()
        # exit(0)
        self.done = True

    def event(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.__exit()
            if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                self.__exit()

    def redraw(self):
        self.screen.fill(self.bg_color)

        if self.create:
            self.tools.draw_text(self.screen, f"房间创建成功：{self.roomid} (按空格以复制房间号并返回)", (100, 200), 35,
                                 stop_time=0)
        else:
            self.done = True
            self.tools.draw_text(self.screen, f"房间创建失败", (100, 200), 35, stop_time=1.5)

    def mainloop(self):
        while not self.done:
            self.event()
            self.redraw()

            pygame.display.update()


class JoinUi:
    def __init__(self, screen: pygame.Surface = None):
        self.screen = screen

        self.bg_color = (240, 240, 240)

        self.tools = Tools()

        self.input_box = pygame.sprite.Group()

        self.done = False
        self.keys = {
            pygame.K_RETURN: False,
            pygame.K_LCTRL: False,
        }
        self.tips: list = [""]

        self.res = None

        self.__init()

    def init(self, screen: pygame.Surface):
        if self.screen is None:
            self.screen = screen

    def __init(self):
        self.input_boxs = [
            InputBox(self.input_box, pygame.Rect(100, 170, self.screen.get_width() - 210, 35), 35,
                     def_text="请输入房间号(仅数字)",
                     input_type=1, paste=paste),
        ]

        self.input_boxs[0].active = True

    def __exit(self):
        # pygame.quit()
        # exit(0)
        self.done = True

    def event(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.__exit()
            if e.type == pygame.KEYUP and e.key == pygame.K_ESCAPE:
                self.__exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
                self.keys[pygame.K_RETURN] = True
            if e.type == pygame.KEYUP and e.key == pygame.K_RETURN:
                if self.keys[pygame.K_RETURN] is True:
                    self.keys[pygame.K_RETURN] = False
                    self.set_done()

            self.input_box.update(e)

    def set_done(self):
        self.tips: list = [""]
        if self.input_boxs[0].done and len(self.input_boxs[0].text) > 0:
            texts = self.input_boxs[0].text
            self.res = texts
            self.done = True
        else:
            self.tips[0] = "房间号不能为空"
            self.input_boxs[0].active = True

    def redraw(self):
        self.input_box.update(False)

        self.screen.fill(self.bg_color)

        self.input_box.draw(self.screen)

        if self.tips[0] != "":
            self.tools.draw_text(self.screen, self.tips[0], (100, 120), 35, stop_time=0)

    def mainloop(self):
        while not self.done:
            self.event()
            self.redraw()

            pygame.display.update()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)

    while True:
        test = Choose(screen)
        test.mainloop()
        if test.done == 0:
            test2 = CreateRoom(screen)
            test2.mainloop()
            if test2.res is not None:
                test3 = RoomIDShow(-1, True, screen)
                test3.mainloop()
        elif test.done == 1:
            test3 = JoinUi(screen)
            test3.mainloop()
