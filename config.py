import traceback
from json import loads, dumps
from os import path as os_path


# my pkg
from g import logging
from g import inform

config_file = inform.config_file

if os_path.exists(config_file) and os_path.isfile(config_file):
    with open(config_file, "r+", encoding="utf-8") as f:
        try:
            json_dic = loads(f.read())
        except Exception as e:
            logging.write_log(f"{config_file} 读取错误: {e}")
            if inform.output_full_log:
                logging.write_log(f"{config_file} 读取错误: \"{traceback.format_exc()}\"")
elif inform.config_file_autowrite:
    with open(config_file, "w+", encoding="utf-8", newline='\n') as f:
        try:
            f.write(dumps(inform.default_config, indent=4) + "\n")
            json_dic = inform.default_config
        except Exception as e:
            logging.write_log(f"{config_file} 写入错误: {e}")
            if inform.output_full_log:
                logging.write_log(f"{config_file} 写入错误: \"{traceback.format_exc()}\"")


config = json_dic
