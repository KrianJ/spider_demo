# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2019/12/17 20:35"
__doc__ = """ """

import requests
from lxml import etree
import json
from time import time

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36 Edg/79.0.309.51',
    }


def get_urls(DOMAIN_URL):
    """获取所有页面的所有章节url: chapter_urls"""
    chapter_urls = []
    for page in range(1, 36):
        page_url = DOMAIN_URL + '_' + str(page)
        resp = requests.get(page_url, headers=headers)
        text = resp.content.decode('utf-8')
        html = etree.HTML(text)
        # 获取当前目录页所有章节url
        book_list = html.xpath("//div[@class='book_last']//a")
        chapter_DOMAIN = "https://m.39shubao.com/"
        for chapter in book_list:
            # title = chapter.xpath(".//text()")[0]
            suffix_href = chapter.xpath(".//@href")[0]
            chapter_url = chapter_DOMAIN + suffix_href      # 生成本章chapter_url
            chapter_urls.append(chapter_url)                # 添加该章节url进chapter_urls
    return chapter_urls


def get_content(url):
    """获取章节网页中的标题和内容,保存到字典chapter"""
    chapter = []
    resp = requests.get(url, headers=headers)
    text = resp.content.decode('utf-8')
    html = etree.HTML(text)
    # 获取小说标题和内容
    title = html.xpath(".//div[@id='nr_title']/text()")[0]
    content = html.xpath(".//div[@id='nr1']/text()")
    content = ''.join(content).replace(' ', '')
    chapter.append(title)
    chapter.append(content)
    return chapter


def main():
    start_time = time()
    domain_url = "https://m.39shubao.com/0/893"  # url公共域名
    url_list = get_urls(domain_url)
    for url in url_list:
        chapter = get_content(url)
        # 将得到的章节名：章节内容以追加('a+')的方式写进txt
        with open('noval.txt', 'a+', encoding='utf-8') as fp:
            fp.write(chapter[0] + '\n')
            fp.write(chapter[1] + '\n')
    run_time = time() - start_time
    print(run_time)


if __name__ == '__main__':
    # main()
    domain_url = "https://m.39shubao.com/0/893"  # url公共域名
    url_list = get_urls(domain_url)
    print(len(url_list))
