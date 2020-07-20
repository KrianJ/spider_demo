# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2020/7/4 15:45"
__doc__ = """ 抓取今日头条街拍图片
1.在索引页中提取详情页url：
    先看document文件的preview和response，再看XHR文件的。可以看出是由ajax加载，在xhr中找到请求的json数据链接，从json数据中提取每个详情页的url
"""

import requests
from requests.exceptions import RequestException
from urllib.parse import urlencode
import json
import re


def get_page_index(offset, keyword):
    """抓取索引页内容"""
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'referer': 'https://www.toutiao.com/ch/news_image/'
    }
    data = {
        'aid': 24,
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'en_qc': 1,
        'cur_tab': 1,
        'from': 'search_tab',
        'pd': 'synthesis',
    }
    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except RequestException:
        print("请求索引页失败")
        return None


def parse_page_index(html):
    """解析获取的json，得到详情页url"""
    data = json.loads(html)
    if data and 'data' in data.keys():
        for item in data.get('data'):
            yield item.get('article_url')


def get_page_datail(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'accept-encoding': 'gzip, deflate, br'
        }
    data = {
        'aid': 24,
        'app_name': 'toutiao-web',
        'offset': 0,
        'count': 5,
    }
    try:
        response = requests.get(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求详情页出错")
        return None


if __name__ == '__main__':
    html = get_page_index(0, '街拍')
    for url in parse_page_index(html):
        if url:
            url = 'https://www.' + url[7:]
            html_detail = get_page_datail(url)
            print(html_detail)
        break

