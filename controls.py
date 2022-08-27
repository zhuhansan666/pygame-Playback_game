from typing import Union
from types import FunctionType

import pygame
from math import ceil
from time import sleep, time


# class InputBox:
#     def __init__(self, rect: pygame.Rect, font_size: int, def_text: str = "") -> None:
#         """
#         rect，传入矩形实体，传达输入框的位置和大小
#         """
#         self.boxBody: pygame.Rect = rect
#         self.color_inactive = pygame.Color((100, 100, 100))  # 未被选中的颜色
#         self.color_active = pygame.Color('black')  # 被选中的颜色
#         self.color = self.color_inactive  # 当前颜色，初始为未激活颜色
#         self.active = False
#         self.text = ''
#         self.done = False
#         self.font_file = './res/font/MiSans-Light.ttf'
#         self.font = pygame.font.Font(self.font_file, font_size)
#         self.def_text = def_text
#
#     def dealEvent(self, event: pygame.event.Event):
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             if self.boxBody.collidepoint(event.pos):  # 若按下鼠标且位置在文本框
#                 self.active = not self.active
#             else:
#                 self.active = False
#             self.color = self.color_active if (
#                 self.active) else self.color_inactive
#         if event.type == pygame.KEYDOWN:  # 键盘输入响应
#             if self.active:
#                 if event.key == pygame.K_RETURN:
#                     self.done = True
#                     self.active = False
#                     self.color = self.color_inactive
#                 elif event.key == pygame.K_BACKSPACE:
#                     self.text = self.text[:-1]
#                 else:
#                     self.text += event.unicode
#
#     def draw(self, screen: pygame.surface.Surface):
#         txtSurface = self.font.render(
#             self.text, True, self.color)  # 文字转换为图片
#         width = max(200, txtSurface.get_width() + 10)  # 当文字过长时，延长文本框
#         self.boxBody.w = width
#         if len(self.text) <= 0:
#             font_surface = self.font.render(
#                 self.def_text, True, self.color_inactive)
#             width = max(200, font_surface.get_width() + 10)
#             self.boxBody.w = width
#             screen.blit(font_surface, (self.boxBody.x + 5, self.boxBody.y + 5))
#         screen.blit(txtSurface, (self.boxBody.x + 5, self.boxBody.y + 5))
#         pygame.draw.rect(screen, self.color, self.boxBody, 2)


class Tools:
    def __init__(self):
        self.font_file = './res/font/MiSans-Light.ttf'
        self.clock = pygame.time.Clock()

    def draw_text(self, surface: pygame.Surface, text: str, pos: Union[tuple, list], size: int,
                  color: Union[str, tuple, list] = (0, 0, 0), bg_color=(240, 240, 240),
                  stop_time: Union[float, str] = 1.5):
        pos = list(pos)
        f = pygame.font.Font(self.font_file, size)
        text_list = text.split("\n")
        for i in range(len(text_list)):
            if type(text_list[i]) == str:
                f_surface = f.render(text_list[i], True, color, bg_color)
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
                        if e.type == pygame.KEYUP and pygame.display.get_active():
                            return
                    pygame.event.get()
                    pygame.display.update()
                    sleep(0.01)


class TextBox(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, screen_size: Union[tuple, list, pygame.math.Vector2],
                 pos: Union[tuple, list, pygame.math.Vector2], text: str, size: int, alignment_type: str = "topleft",
                 functions: Union[FunctionType or None, FunctionType or None, FunctionType or None] = (
                 None, None, None),
                 surface_size: Union[tuple, list, pygame.math.Vector2] = (None, None),
                 color: Union[tuple, list, str] = (0, 0, 0), bg_color: Union[tuple, list, str] = None):
        super().__init__(group)
        self.font_file = './res/font/MiSans-Light.ttf'
        self.abs_size = None

        self.screen_size = screen_size
        self.pos = pos
        self.text = text
        self.size = size
        self.alignment_type = alignment_type
        self.functions = functions
        self.surface_size = surface_size
        self.color = color
        self.bg_color = bg_color

        self.mouse_button_presses = []
        for i in range(len(pygame.mouse.get_pressed())):
            self.mouse_button_presses.append(0)

        self.font = pygame.font.Font(self.font_file, self.size)
        self.create_surface()

    def create_surface(self):
        self.abs_size = [self.screen_size[0] - self.pos[0], self.screen_size[1] - self.pos[1]]
        if self.surface_size[0] is not None:
            self.abs_size[0] = self.surface_size[0]

        if self.surface_size[1] is not None:
            self.abs_size[1] = self.surface_size[1]

        self.image = pygame.Surface(self.abs_size).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        self.rect = self.image.get_rect(**{self.alignment_type: self.pos})

        i = -1
        split_texts = self.text.split("\n")  # 自动换行预操作
        while True:
            text = split_texts[0]  # 取值, 获取每行的文字
            font_surface = self.font.render(text, True, self.color, self.bg_color)  # 生成surface(包含上一次超出的字符)

            if font_surface.get_width() > self.image.get_width():  # 如果字符超过屏幕大小
                one_width = font_surface.get_width() / len(text)  # 求平均每个字符的大小
                unexposed_size = len(text) - ceil(
                    (font_surface.get_width() - self.image.get_width()) / one_width)  # 算出没有超出的字符数(向下取整)
                font_surface = self.font.render(text[:unexposed_size], True, self.color, self.bg_color)  # 未超出的部分
                split_texts[0] = text[unexposed_size + 1:]  # 超出的直接覆盖
            else:
                split_texts.pop(0)  # 移除避免重复

            i += 1  # 行数自加以换行

            self.image.blit(font_surface, (0, i * self.font.get_linesize()))  # blit并乘行的index

            if len(split_texts) <= 0:  # 循环完退出
                break

    def event(self):
        mouse_events = pygame.mouse.get_pressed()
        i = 0
        for mouse_event in mouse_events:
            mouse_pos = pygame.mouse.get_pos()
            func = self.functions[i]
            if mouse_event and self.rect.collidepoint(mouse_pos) and (self.mouse_button_presses[i] == 0 or
                                                                      self.mouse_button_presses[i] == 2):
                self.mouse_button_presses[i] = 1
            if func is not None and self.mouse_button_presses[i] == 1 and mouse_event is not True:
                func()
                self.mouse_button_presses[i] = 2

            i += 1

    def update(self, dt):
        self.event()


class InputBox(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, rect: pygame.Rect, font_size: int, color=(100, 100, 100, 127),
                 active_color='black', def_text: str = "", cursor_hied_time: float = 0.5,
                 cursor_show_time: float = 0.5, press_time: float = 0.5, once_press_time: float = 0.03, input_type: int=1):
        """
        输入框
        :param group: pygame group
        :param rect: pygame rect
        :param font_size: int, font size
        :param color: not active color
        :param active_color: active color
        :param def_text: default text
        :param cursor_hied_time: cursor hied time (sec)
        :param cursor_show_time: cursor show time (sec)
        :param press_time: press check time (sec)
        :param once_press_time: between pressed one and one sleep time (sec)
        :param input_type: int, 1 : number box (number only), 2 : int & letters box 3 : all utf-8 string.
        """
        super().__init__(group)
        self.rect: pygame.Rect = rect
        self.def_size = (self.rect.width, self.rect.height)
        self.color_inactive = color  # 未被选中的颜色
        self.color_active = active_color  # 被选中的颜色
        self.color = self.color_inactive  # 当前颜色，初始为未激活颜色

        self.active = False
        self.text = ""
        self.done = False

        self.font_file = './res/font/MiSans-Light.ttf'
        self.font = pygame.font.Font(self.font_file, font_size)
        self.def_text = def_text

        self.cursor_str = ""
        self.cursor_settings = [cursor_hied_time, cursor_show_time]  # hied_time, show_time
        self.cursor_times = [-1, -1]  # hied_time, show_time
        self.cursor_type = False  # False -> hied / True -> show

        self.input_type = input_type

        self.keys = {
            pygame.K_BACKSPACE: False
        }
        self.keys_time = {
            pygame.K_BACKSPACE: time()
        }
        self.press_last_times = {
            pygame.K_BACKSPACE: time()
        }
        self.press_time: float = press_time
        self.once_press_time: float = once_press_time

        self.create_surface()

    @staticmethod
    def __is_float(string: str):
        try:
            float(string)
            return True
        except Exception as e:
            return False

    def cursor(self):
        if self.active:
            if -1 in self.cursor_times:  # 初始化
                for i in range(len(self.cursor_times)):
                    if self.cursor_times[i] == -1:
                        self.cursor_times[i] = time() - self.cursor_settings[0] + 0.1
            else:
                if self.cursor_type is False:
                    if time() - self.cursor_times[0] >= self.cursor_settings[0]:
                        self.cursor_type = True
                        self.cursor_times[1] = time()
                elif self.cursor_type is True:
                    if time() - self.cursor_times[1] >= self.cursor_settings[1]:
                        self.cursor_type = False
                        self.cursor_times[0] = time()

        if self.active:  # 显示
            if self.cursor_type is True:
                self.cursor_str = "|"
            elif self.cursor_type is False:
                self.cursor_str = ""
        else:
            self.cursor_str = ""

    def create_surface(self):
        txt_surface = self.font.render(
            self.text, True, self.color)
        width = max(self.rect.w, txt_surface.get_width() + 10)
        height = max(self.rect.h, txt_surface.get_height() + 10)
        self.rect.width, self.rect.height = width, height
        self.image = pygame.Surface((width, height + 10)).convert_alpha()
        self.image.fill((0, 0, 0, 0))

    def event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):  # 若按下鼠标且位置在文本框
                self.done = False
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
                else:
                    self.done = False
                    if event.key == pygame.K_BACKSPACE:
                        self.keys_time[pygame.K_BACKSPACE] = time()
                        self.keys[pygame.K_BACKSPACE] = True
                        self.text = self.text[:-1]
                    else:
                        if self.input_type == 1:
                            if self.__is_float(event.unicode):
                                self.text += event.unicode
                        elif self.input_type == 2:
                            if event.unicode.isalnum():
                                self.text += event.unicode
                        elif self.input_type == 3:
                            self.text += event.unicode

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_BACKSPACE:
                self.keys[pygame.K_BACKSPACE] = False

    def press(self):
        if self.keys[pygame.K_BACKSPACE] is True and time() - self.keys_time[pygame.K_BACKSPACE] > self.press_time\
                and time() - self.press_last_times[pygame.K_BACKSPACE] >= self.once_press_time:
            self.press_last_times[pygame.K_BACKSPACE] = time()
            self.text = self.text[:-1]

    def change_surface(self):
        txt_surface = self.font.render(self.text + self.cursor_str, True, self.color)
        width = max(self.rect.w, txt_surface.get_width() + 10)
        height = max(self.rect.h, txt_surface.get_height() + 10)
        self.rect.width, self.rect.height = width, height

        if self.rect.width >= self.def_size[0] and width > self.def_size[0]:
            width = txt_surface.get_width() + 10
            height = txt_surface.get_height() + 10
            self.rect.width, self.rect.height = width, height
        else:
            width, height = self.rect.width, self.rect.height

        self.image = pygame.Surface((width, height + 10)).convert_alpha()
        self.image.fill((0, 0, 0, 0))

        if len(self.text) <= 0:
            font_surface = self.font.render(
                self.def_text, True, self.color_inactive)

            if self.rect.width >= self.def_size[0] and width > self.def_size[0]:
                width = font_surface.get_width() + 10
                height = font_surface.get_height() + 10
                self.rect.width, self.rect.height = width, height
            else:
                width, height = self.rect.width, self.rect.height

            self.image.blit(font_surface, (10, 5))

        self.image.blit(txt_surface, (5, 5))
        pygame.draw.rect(self.image, self.color, (0, 0, self.rect.w, height), 2)

        pygame.image.save(self.image, "./test.png")

    def change_color(self):
        self.color = self.color_active if (
            self.active) else self.color_inactive

    def update(self, event: pygame.event.Event):
        self.change_color()
        if event is not False:
            self.event(event)
        self.press()
        self.cursor()
        self.change_surface()
