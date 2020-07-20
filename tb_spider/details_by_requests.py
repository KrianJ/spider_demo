# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2020/7/11 15:14"
__doc__ = """ 使用requests，BeautifulSoup+多线程爬取显示器的详细参数"""

import pymongo
import requests
from requests.exceptions import ConnectionError, ReadTimeout
from bs4 import BeautifulSoup
import re
import urllib3
import time
from tb_spider.parse_url import get_data_from_url
import threading
from queue import Queue


class crawl_detail():
    def __init__(self):
        self.client = pymongo.MongoClient('localhost')
        self.db = self.client['taobao']
        self.col = self.db['monitor']
        self.retries = 5

    def get_records(self):
        """获取集合中每个记录的url"""
        query = {'href': {'$exists': True}}
        records = self.col.find(query)
        return records

    def get_random_proxy(self):
        """
        get random proxy from proxypool
        :return: proxy
        """
        proxypool_url = 'http://127.0.0.1:5555/random'
        return requests.get(proxypool_url).text.strip()

    def parse_url(self, url, data={}):
        """解析商品详情页
        :param url: 详情页url
        :return 该商品各项参数
        """
        """请求参数"""
        # 随机user-agent
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.85 Safari/537.36 Edg/84.0.522.35',
                   'referer': 'https://s.taobao.com/search?q=%E6%98%BE%E7%A4%BA%E5%99%A8&imgfile=&commend=all&ssid=s5-e&search_type=item&sourceId=tb.index&spm=a21bo.2017.201856-taobao-item.1&ie=utf8&initiative_id=tbindexz_20170306',
                   'cookie': 'hng=CN%7Czh-CN%7CCNY%7C156; lid=%E6%89%BE%E4%B8%8D%E5%88%B0aro; enc=lVpxV1GaTL3mk7bxeEjBOmlA1KN0nK6tcFibhTs2B2wSC12binFqDeG4iuHzlu%2BpqvgFwjDGA2BPhhICioq0yA%3D%3D; cna=UhFHFh0tS3wCAcp53wEwk6X/; cq=ccp%3D1; _m_h5_tk=3dee1c70a1fe16a57409af8e886f0c3a_1594539405841; _m_h5_tk_enc=be3c4c77965372676a6a695fdfc0fdc6; sgcookie=EAqtbU6GNPYvpqwULm0D5; t=ea7bf8dde8cb9e8738062bae73d9aea6; _tb_token_=f6f5ea485b3be; cookie2=7c2315c3bc6fe7037f982caa6cd7a0f5; pnm_cku822=098%23E1hvJvvUvbpvUpCkvvvvvjiPnLFO1jrWPscZAjEUPmPvzjYVP2SWzjEVPszv1jrPRLyCvvpvvhCvvphvC9vhphvvvvyCvhQCylxxj4mzDb01Ux8x9C9aRfU6pwethb8rjC69D70Od34AVA3lYb8rj8t%2Bm7z9digBbFZHAno1bdIOwyL9wfIOVBrz8YcvVXu1bFZHuphvmvvvpLUX6PpDkphvC9hvpyP96byCvm9vvhCvvvvvvvvvBGwvvvhWvvCj1Qvvv3QvvhNjvvvmjvvvBGwvvvUw2QhvCPMMvvm5vpvhvvCCBv%3D%3D; l=eBEBodkgOjJOiaGsBOfZnurza779tIRAguPzaNbMiOCP_uf95_VRWZlMKNTpCnGVh6uXR3rK3bBbBeYBqn06rVm1a6Fy_Ckmn; isg=BCgogMAS48DKkc9GhLq535p0-RY6UYxbf8uToeJZNaOWPcinimBi6al_NdXNDUQz',
                   'accept-encoding': 'gzip, deflate, br',
                   'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        }
        # data = {'ns': 1}
        # 代理ip
        proxies = {'http': 'http://' + self.get_random_proxy()}

        # 发送get请求
        try:
            s = requests.session()
            # s.keep_alive = False
            response = s.get(url, headers=headers, proxies=proxies, data=data)
            if response.status_code != 200:
                url, data = get_data_from_url(url)
                # new_proxies = {'http': 'http://' + self.get_random_proxy()}
                return self.parse_url(url, data=data)
        except ConnectionError:
            # 若连接失败，则解析重定位之后的url，向请求中加入data
            self.retries = self.retries - 1
            if self.retries:
                url, data = get_data_from_url(url)
                return self.parse_url(url, data=data)
            print('超出最大尝试次数')
            return None

        response.close()
        html = BeautifulSoup(response.text, 'lxml')

        params = {}
        # 详细参数表单ul
        if '.tmall.' in url or 'click.simba' in url:
            # 天猫的ul
            ul = html.select('#J_AttrUL')[0]
        elif '.taobao.' in url:
            # 淘宝的ul
            ul = html.select('#attributes > ul')[0]

        try:
            attrs = ul.find_all('li')
            for attr in attrs:
                # 将参数分割成key_value形式
                attr = attr.text
                pattern = re.compile(r'[：:]')
                key_val = re.split(pattern=pattern, string=attr)
                params[key_val[0]] = key_val[1].strip()
            params['url'] = url
        except Exception:
            print('未获取到目标数据')
        return params

    def get_params(self, item):
        """
        获取商品url，得到详细参数
        :param item: 单条记录（商品）
        :return: 该商品详细参数
        """
        id = item['_id']
        url = item['href']
        if url.startswith('http'):
            params = self.parse_url(url)
        else:
            params = self.parse_url('http:' + url)
        return id, params


def run(items, thread_name):
    spider = crawl_detail()
    # 读取所有商品
    # 遍历商品url，获取详细参数并存入mongodb
    count = 0
    while items.empty() is not True:
        item = item_queue.get()
        _id, params = spider.get_params(item)
        if params is not None:
            count += 1
            update = spider.db.monitor_detail.update_one({'_id': _id}, {'$set': params}, upsert=True)
            print("线程%s: 已插入第%d条商品参数" % (thread_name, count))
        else:
            print('未获取到该id详细参数：%s' % _id)
        time.sleep(1)
    print('累计爬取%d条商品详细参数' % count)
    spider.client.close()


if __name__ == '__main__':
    # 忽视警告
    urllib3.disable_warnings()
    # 获取mongodb中的商品记录
    spider = crawl_detail()
    items = spider.get_records()

    # 构造并填充线程安全的FIFO队列
    item_queue = Queue(5000)
    for item in items:
        item_queue.put(item)
    # 创建线程
    threads = []
    for i in range(1):
        thread = threading.Thread(target=run, args=(item_queue, i))
        threads.append(thread)
    # 启动线程
    for j in range(1):
        threads[j].start()
        print('线程%d启动' % j)
    for t in threads:
        t.join()
    print("all threads end")




