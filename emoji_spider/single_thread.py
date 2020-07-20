# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2019/11/16 14:17"
__doc__ = """ 单线程同步下载表情包"""

import requests
from lxml import etree
from urllib import request
import os
import re


def parse_page(page_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
    }
    resp = requests.get(page_url, headers=headers)
    text = resp.text
    # parser = etree.HTMLParser(encoding='utf-8')
    html = etree.HTML(text)

    content_html = html.xpath("//div[@class='col-sm-9 center-wrap']")[0]               # 待提取html块
    imgs = content_html.xpath("..//img[@class='lazy image_dtb img-responsive']")           # 表情图
    # titles = content_html.xpath("..//div[@class='random_title']")                          # 表情总标题
    count = 0
    for img in imgs:
        count += 1         # 防止重名
        """图片原始地址在data-original属性里面，名字在alt属性里面"""
        img_url = img.get('data-original')
        img_alt = img.get('alt')
        alt = re.sub(r"[\/\\\:\?？\*\.，。！、<>|]", '', img_alt)     # 文件名不能包含 \ / : ? " * < > |
        # os模块获取文件扩展名split extension
        suffix = os.path.splitext(img_url)[1]                 # <class tuple>: name + suffix
        filename = alt + str(count) + suffix
        # urllib模块下request下载图片到路径
        request.urlretrieve(img_url, 'images/'+filename)


def main():
    for page in range(1, 101):
        url = "http://www.doutula.com/article/list/?page=%d" % page
        parse_page(url)


if __name__ == '__main__':
    main()

