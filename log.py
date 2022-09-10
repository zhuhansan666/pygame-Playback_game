from os import mkdir
from os.path import normpath, exists, join, isdir, basename, splitext, split
from os.path import split as ospath_split
from platform import platform, architecture, node, machine
from time import localtime, strftime
from types import FunctionType
from typing import Optional

from psutil import virtual_memory


class Logging:
    """
    日志写入
    """

    def __init__(self, log_def_info: FunctionType = None):
        """
        :param log_def_info: 回调函数, 应返回默认写入(即创建文件时)的日志内容(末尾不会自动换行)
        """
        self.__log_path = None
        self.__log_dir_created: bool = False

        self.log_file = "./log/$(now_time)$.log"

        self.__log_path = ospath_split(self.log_file)[0]
        self.__log_file_name = basename(self.log_file)

        log_path_file_list = splitext(self.__log_file_name)

        self.full_log_file = join(self.__log_path, log_path_file_list[0] + ".full" + log_path_file_list[1])

        self.time_f = "%Y-%m-%d"
        self.time_f_all = "%Y-%m-%d %H:%M:%S"
        self.default_encode = "utf-8"

        if log_def_info is not None:
            self.default_log_info = log_def_info()
        else:
            self.default_log_info = self.set_def_log_info()

        self.init()
        self.write_log(None)

    @staticmethod
    def set_def_log_info():
        try:
            from wmi import WMI

            w = WMI()

            gpu_lst = []
            for v in w.Win32_VideoController():
                gpu_lst.append(v.caption)

            cpu_lst = []
            for c in w.Win32_Processor():
                cpu_lst.append(c.name)

        except ImportError as e:
            cpu_lst = "Unknown: System does not support"
            gpu_lst = "Unknown: System does not support"

        mem = virtual_memory()
        total_mem = round(mem.total / 1024 / 1024 / 1024, 3)  # 转化为Gib

        return "{}\n{}\nsystem-version: {}\nsystem-bit: {}\ncpu-type: {}\ncomputer-name: {}" \
               "\ntotal-memory: {} Gib\nCPU: {}\nGPU: {}\n{}\n".format(strftime("%Y-%m-%d %H:%M:%S", localtime()),
                                                                       "-" * 100, platform(),
                                                                       architecture()[0], machine(),
                                                                       node(), total_mem, str(cpu_lst), str(gpu_lst),
                                                                       "-" * 100)

    def init(self):
        if not exists(self.__log_path) or not isdir(self.__log_path):  # 没有log文件夹
            try:
                mkdir(self.__log_path)
                if exists(self.__log_path) and isdir(self.__log_path):
                    self.__log_dir_created = True
                else:
                    print(f"[{self.get_ftime_date()}] log文件夹 ({self.__log_path}) 创建失败: 未知错误")
            except Exception as e:
                print(f"[{self.get_ftime_date()}] log文件夹 ({self.__log_path}) 创建失败: {e}")
        else:
            self.__log_dir_created = True

    def get_ftime_date(self):
        return strftime(self.time_f, localtime())

    def get_ftime(self):
        return strftime(self.time_f_all, localtime())

    def write_log(self, info: Optional[str], add_time: bool = True, log_type: int = 1, encoding: str = None,
                  filename: str = None):
        self.init()
        # 文件编码格式化
        encoding = encoding if encoding is not None else self.default_encode

        # log文件名称格式化
        if filename is not None:
            filename = filename.rstrip()
            filename = filename if filename[-4:] == ".log" else filename + ".log"

        # info内容格式化
        if info is not None:
            info = info if type(info) == str else str(info)
            info = info if info[-2:] == "\n" else info + "\n"
            info = info if add_time is not True else f"[{self.get_ftime()}] {info}"

        # 文件名初始化
        if log_type == 1:
            if filename is not None:
                _filename = join(self.__log_path, filename)
            else:
                _filename = self.log_file.replace("$(now_time)$", self.get_ftime_date())
        elif log_type == 2:
            print(info)
            if filename is not None:
                _filename = join(self.__log_path, filename)
            else:
                _filename = self.full_log_file.replace("$(now_time)$", self.get_ftime_date())
        else:
            print(f"[{self.get_ftime()}] log_type 错误, 已停止写入")
            return

        _filename = normpath(_filename)

        if not exists(_filename) and not isdir(_filename):
            try:
                with open(_filename, "w+", encoding=encoding) as cf:
                    cf.write(self.default_log_info)
            except Exception as e:
                print(f"[{self.get_ftime()}] {_filename} 创建失败: {e}")
        else:
            if not isdir(_filename):
                info = info if info is not None else ""
                try:
                    with open(_filename, "a+", encoding=encoding) as log_f:
                        log_f.write(info)
                except Exception as e:
                    print(f"[{self.get_ftime()}] {_filename} 写入失败: {e}")
            else:
                print(f"[{self.get_ftime()}] {_filename} 是一个文件夹")
