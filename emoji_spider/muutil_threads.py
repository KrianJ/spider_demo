# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2019/11/16 21:22"
__doc__ = """ 多线程异步下载"""


import threading
from queue import Queue
import requests
from lxml import etree
from urllib import request
import os
import re


class Producer(threading.Thread):
    __doc__ = """生产者线程"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
    }

    def __init__(self, page_queue, img_queue,  *args, **kwargs):
        """向构造函数中传递page_queue和img_queue两个参数"""
        super(Producer, self).__init__(*args, **kwargs)     # 继承父类参数
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()         # 将队列中一个url出队
            self.parse_page(url)                # 解析出队的url，这里产生img_queue入队

    def parse_page(self, page_url):
        """解析url_page，最后将tuple(img_url, filename)入队img_queue"""
        resp = requests.get(page_url, headers=self.headers)
        text = resp.text
        # parser = etree.HTMLParser(encoding='utf-8')
        html = etree.HTML(text)

        # content_html = html.xpath("//div[@class='col-sm-9 center-wrap']")[0]  # 待提取html块
        imgs = html.xpath("//img[@class='lazy image_dtb img-responsive']")  # 表情图

        count = 0
        for img in imgs:
            count += 1  # 防止重名
            """图片原始地址在data-original属性里面，名字在alt属性里面"""
            img_url = img.get('data-original')
            img_alt = img.get('alt')
            alt = re.sub(r"[\/\\\:\?？\*\.，。！、<>|]", '', img_alt)  # 文件名不能包含 \ / : ? " * < > |
            # os模块获取文件扩展名split extension
            suffix = os.path.splitext(img_url)[1]  # <class tuple>: name + suffix
            filename = alt + str(count) + suffix
            self.img_queue.put((img_url, filename))


class Consumer(threading.Thread):
    __doc__ = """消费者进程负责将生产者线程生产的img_url下载到本地"""

    def __init__(self, page_queue, img_queue,  *args, **kwargs):
        """向构造函数中传递page_queue和img_queue两个参数"""
        super(Consumer, self).__init__(*args, **kwargs)         # 继承父类参数
        self.img_queue = img_queue
        self.page_queue = page_queue

    def run(self):
        """不断在img_queue中取出img_url，下载到本地"""
        while True:
            if self.img_queue.empty() and self.page_queue.empty():
                break
            img_url, filename = self.img_queue.get()
            request.urlretrieve(img_url, 'images/' + filename)  # 下载图片到images文件夹
            print(filename + "下载完成！！")


def main():
    page_queue = Queue(100)
    img_queue = Queue(5000)
    # 将所有待爬取page入队，一共爬取100页
    for page in range(1, 101):
        url = "http://www.doutula.com/article/list/?page=%d" % page
        page_queue.put(url)

    for x in range(5):
        """5个生产者线程"""
        t = Producer(page_queue, img_queue)
        t.start()
    for y in range(5):
        """5个消费者线程"""
        t = Consumer(page_queue, img_queue)
        t.start()


if __name__ == '__main__':
    main()

