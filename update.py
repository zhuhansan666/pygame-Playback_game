import traceback
from subprocess import run as run_cmd
from sys import argv, exit
from os.path import exists, isdir, normpath, abspath
from os import remove
from threading import Thread
from time import time as get_time
from typing import Union
from controls import TextBox, Tools
from time import sleep
import pygame

from g import logging


def init(argvs: Union[tuple, list]):
    _dic = {
        "file": None,
    }

    i = 0
    for a in argvs[1:]:
        if a == "-f" or a == "-file":
            try:
                f = abspath(argvs[i + 2])
                if exists(f) and isdir(f) is not True:
                    _dic["file"] = normpath(f)
            except IndexError:
                pass
        i += 1

    return _dic


class Update:
    def __init__(self):
        pygame.init()
        self.bg_color = (240, 240, 240)
        self.title = "Updater / 更新助手"

        pygame.display.set_caption(self.title, self.title)
        pygame.display.set_icon(pygame.image.load("./res/img/icon/icon.jpg"))

        self.all_spr = pygame.sprite.Group()
        self.tools = Tools()

        self.screen = pygame.display.set_mode((1280, 720))

        self.screen.fill(self.bg_color)

    def __decompress_core(self, __file: str):
        self.thread = Thread(target=lambda: run_cmd([abspath("./res/dll/7z.exe"), "x", "-y", "-r", "-mmt",
                                                     f"-o./", __file], shell=True))
        self.thread.start()

    def mainloop(self, _file: str):
        self.__decompress_core(_file)

        self.screen.fill(self.bg_color)
        self.tools.draw_text(self.screen, f"正在解压...", (500, 300), 35, stop_time=0)

        while self.thread.is_alive():
            pygame.event.get()
            pygame.display.update()

        sleep(0.5)
        self.screen.fill(self.bg_color)
        self.tools.draw_text(self.screen, f"解压完成", (500, 300), 35, stop_time=3)
        try:
            remove(_file)
        except Exception as e:
            logging.write_log(f"update -> 删除 \"{_file}\" 发生错误: {e}")
            logging.write_log(f"update -> 删除 \"{_file}\" 发生错误: \"{traceback.format_exc()}\"")


if __name__ == "__main__":
    dic = init(argv)
    file = dic["file"]
    if file is not None:
        test = Update()
        test.mainloop(file)
        logging.write_log(f"update -> {file} 解压成功")
        run_cmd("start main.exe", shell=True)
        exit(0)
    else:
        logging.write_log(f"update -> 错误: 文件名未传入")
        exit(1)
