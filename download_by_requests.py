from requests import get
from g import ReqsThread
from os import path as os_path
from os import makedirs
from traceback import format_exc


class RequestsDownload:
    def __init__(self, url: str, path: str, filename: str = None, use_thread: bool = True, d: bool = True,
                 chunk_size: int = 1024, auto_cover: bool = True, headers: dict = None):
        self.url = url
        self.path = os_path.normpath(path)
        self.filename = filename if filename is not None else False
        self.thread = use_thread
        self.d = d
        self.chunk = chunk_size
        self.cover = auto_cover
        self.headers = headers if headers is not None else {}

        self.errors = []

        self.total_size = None
        self.total_size_mib = None
        self.download_size = 0
        self.download_size_mib = 0
        self.finished = 0

        self.filepath = None

    def filename_init(self):
        if self.filename is not False:
            self.filepath = os_path.join(self.path, self.filename)

    def check_file(self):
        if self.filename is not None:
            if not (os_path.exists(self.path) and os_path.isdir(self.path)):
                try:
                    makedirs(self.path)
                    if not (os_path.exists(self.path) and os_path.isdir(self.path)):
                        raise RuntimeError("文件夹创建失败: 未知原因")
                except Exception as e:
                    self.errors.append(["创建文件夹", e, format_exc()])
                    return -1
            elif os_path.exists(self.path) and os_path.exists(self.filepath):
                if not self.cover:
                    self.errors.append(["文件已存在", "", ""])
                    return -1
                else:
                    return 0
        return -1

    def download(self):
        self.download_size = 0

        try:
            res = get(self.url, stream=True, headers=self.headers)
        except Exception as e:
            self.errors.append(["请求下载的文件", e, format_exc()])
            return -1

        self.total_size = int(res.headers['content-length'])
        if self.filename is False:
            file_name = res.headers["Content-Disposition"].split(";")[1][1:].replace("filename=", "")
            self.filename = file_name

        self.filename_init()
        self.check_file()

        if res.status_code == 200:
            self.total_size_mib = self.total_size / 1024 / 1024
            try:
                with open(self.filepath, "wb") as file:
                    for data in res.iter_content(chunk_size=self.chunk):
                        file.write(data)
                        self.download_size += len(data)

                        self.finished = self.download_size / self.total_size * 100
                        self.download_size_mib = self.download_size / 1024 / 1024
                        if self.finished > 100:
                            self.finished = 100
            except Exception as e:
                self.errors.append(["创建文件", e, format_exc()])
                return -1
            return 1
        else:
            self.errors.append(["访问", f"Error Code: {res.status_code}", f"Error Code: {res.status_code}"])
            return -1

    def main(self):
        if self.thread:
            t = ReqsThread(self.download, d=self.d)
            t.start()
            return t
        else:
            return self.download()
