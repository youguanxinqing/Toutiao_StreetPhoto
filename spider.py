import re
import os
import time
import json
import pymongo
import requests

from urllib import parse
from hashlib import md5

from CONFIG import *


def get_one_html(url, tries=3):
    """
    获取一页的请求内容
    :param url:
    :param tries:
    :return:
    """
    try:
        response = requests.get(url=url, headers=HEADERS)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
    except:
        if tries <= 0:
            print("【请求url失败】：", url)
            FAILURE_URL.append(url)
            return None
        else:
            print("【进入循环请求】")
            get_one_html(url, tries-1)
    else:
        # print(response.url)
        return response.text

def extract_font_json(data):
    """
    提取浏览页的JSON数据
    :param data:
    :return:
    """
    data = json.loads(data)
    if "data" in data.keys():
        for item in data.get("data"):
            yield {
                "article_url": item.get("article_url"),
                "title": item.get("title"),
                "image_count": item.get("image_count")
            }



def extract_detail_data(html):
    """
    提取详情页的图片链接
    :param html:
    :return:
    """
    imgUrls = re.findall(r'\\"url_list\\":\[{\\"url\\":\\"(.*?)\\"},', html)

    for imgurl in imgUrls:
        yield imgurl


def download_img(url):
    """
    下载图片
    :param url:
    :return:
    """
    global IMGDIR

    # print("img:", url)
    response = requests.get(url=url)
    if response.status_code == 200:
        with open(IMGDIR+"/"+md5(response.content).hexdigest()+".jpg", "wb") as file:
            file.write(response.content)



def init():
    """
    初始化：
    1. 创建images文件夹
    2. 链接数据库，并返回集合对象
    :return:
    """
    dirName = "images"
    curDir = os.path.dirname(__file__)
    if not os.path.exists("{curdir}/{dirname}".format(curdir=curDir, dirname=dirName)):
        os.mkdir(dirName)


    CLIENT = pymongo.MongoClient(host="localhost", port=PORT)
    db = CLIENT.images
    collection = db.toutiao

    return collection

def main():

    collection = init()

    # 空白计数器，连续无此请求空白网页，退出程序
    blankCount = 0
    for offset in range(0, 1000, 20):
        time.sleep(1)
        # 构建请求query参数
        PARAMS["offset"] = offset
        data = get_one_html(url=URL+parse.urlencode(PARAMS))
        if not data:
            if blankCount >= 5:
                print("【程序结束】")
                return None
            else:
                print("【获取空白页】")
                blankCount += 1
                continue

        blankCount = 0
        # 获取一个“包”(链接，标题，图片数，图片路径，图片链接)
        for package in extract_font_json(data):
            print(package)
            # 为每一个图集创建一个文件夹
            global  IMGDIR
            IMGDIR = "images/{imgdir}".format(imgdir=package["title"])
            if not os.path.exists(IMGDIR):
                os.mkdir(IMGDIR)

            # 获取详情页源码
            html = get_one_html(package["article_url"])
            if not html:
                continue

            # 获取图片链接，并存放在package
            package["imgs_path"] = os.path.abspath(os.path.dirname(IMGDIR))
            package["imgs"] = []
            for imgurl in extract_detail_data(html):
                # print(imgurl)
                imgurl = imgurl.replace("\\\\", "")
                download_img(imgurl)
                package["imgs"].append(imgurl)

            # 存放数据库
            collection.insert_one(package)

if __name__ == "__main__":
    main()
    print("【失败链接：】", FAILURE_URL)