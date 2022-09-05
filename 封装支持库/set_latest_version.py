from requests import get

key = "114514@19181"

class Request:
    def __init__(self):
        self.url_root = """http://218.73.96.22:8081/"""
        self.url_update_version = self.url_root + """api/update_version"""

    def update_version(self):
        try:
            res = get(self.url_update_version, params={
                "key": key,
                "ver": str(input("请输入版本,以\".\"分割: ").replace(" ", "").split("."))
            })
            print(res.text)
        except Exception as e:
            print(repr(e))


req = Request()
req.update_version()
