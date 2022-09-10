VERSION = (1, 7, 9)

from threading import Thread
from log import Logging


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


class Information:
    def __init__(self):
        self.print_lst = ["", ""]
        self.qq = ""
        self.nk_name = ""
        self.online = False
        self.offline = False
        self.player_died = False

        self.output_full_log = False

        self.config_file = "config.json"
        self.config_file_autowrite = True
        self.default_config = {
            "show_locus": False,
            "sleep_time": [0, 1],
            "output_full_log": True,
        }


inform = Information()
logging = Logging()
