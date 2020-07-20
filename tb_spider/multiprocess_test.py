# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2020/7/18 10:20"
__doc__ = """ 多进程爬虫"""

from tb_spider.details_by_selenium import *
from multiprocessing import Process, Queue, Pool, Manager
import time


if __name__ == '__main__':
    s_time = time.time()

    pool = Pool(processes=10)
    urls = get_urls()
    url_q = Queue()
    for url in urls:
        url_q.put(url)
    process_list = []

    for index, url in enumerate(urls):
        r = pool.apply_async(func=run, args=(url_q, ))

    pool.close()
    pool.join()

    r_time = time.time() - s_time
    print(r_time)

