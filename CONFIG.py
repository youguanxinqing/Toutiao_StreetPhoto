# 文章浏览页
URL = "https://www.toutiao.com/search_content/?"


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
    "Host": "www.toutiao.com"
}

PARAMS = {
    "offset": 0,
    "format": "json",
    "keyword": "街拍",
    "autoload": "true",
    "count": 20,
    "cur_tab": 3,
    "from": "gallery"
}

# 失败链接
FAILURE_URL = []

# 图片目录
IMGDIR = ""

# 数据库链接所需要的数据
HOST = "localhost"
PORT = 27017
