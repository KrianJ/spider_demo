# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2020/7/2 11:48"
__doc__ = """ 猫眼电影"""

import json
from multiprocessing import Pool
import requests
import re

headers = {'Host': 'maoyan.com',
        'User-Agent': 'Mizilla/5.0',
        'Referer': 'https://maoyan.com/board/2'}
proxies = {
    'http': '222.90.110.194'
}


def get_page(url):
    """获取单个页面"""
    try:
        response = requests.get(url=url, headers=headers, proxies=proxies)
        if response.status_code == 200:
            return response.content.decode('utf-8')
    except requests.RequestException:
        return False


def parse_page(html):
    """使用正则表达式解析单个页面的html"""
    # re.S匹配任意字符（包括换行符）
    pattern = re.compile(
        '<dd>.*?board-index.*?>(\d+)</i>.*?data-src="(.*?)".*?"name"><a'
        + '.*?>(.*?)</a>.*?"star">(.*?)</p>.*?"releasetime">(.*?)</p>'
        + '.*?"integer">(.*?)</i>.*?"fraction">(.*?)</i>.*?</dd>', re.S
            )
    items = re.findall(pattern, html)
    movies = []
    for item in items:
        movie = {
            'rank': item[0],
            'poster': item[1],
            'title': item[2],
            'stars': item[3].strip()[3:],
            'time': item[4].strip(),
            'score': item[5] + item[6]
        }
        movies.append(movie)
    return movies


def write_to_json(content):
    with open('result.json', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()


def main(offset):
    start_url = 'https://maoyan.com/board/4?offset='
    url = start_url + str(offset)
    html = get_page(url)
    movies = parse_page(html)
    for movie in movies:
        write_to_json(movie)


if __name__ == '__main__':
    from time import time
    start = time()

    # for page_num in range(10):
    #     main(page_num * 10)
    # 使用多线程进程池
    pool = Pool()
    pool.map(main, [i*10 for i in range(10)])

    runtime = time() - start
    print(runtime)

