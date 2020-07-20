# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2019/10/29 19:10"
__doc__ = """ 豆瓣电影爬取"""


import requests
from lxml import etree

# 1.将目标上的页面抓取下来
headers = {
    'User-Agetnt': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
    'Referer': 'https://movie.douban.com/cinema/nowplaying/hefei/'
}
url = 'https://movie.douban.com/cinema/nowplaying/shanghai/'

request = requests.get(url, headers=headers)
text = request.text
# text返回一个经过解码后的字符串,使用于编码规范的网站
# content返回一个原生的字符串，直接从网页上抓取未经过处理的字符串，是bytes类型，需要decode

html = etree.HTML(text)
movie_ul = html.xpath("//ul[@class='lists']")[0]
# print(etree.tostring(movie_ul, encoding='utf-8').decode('utf-8'))
movie_li = html.xpath(".//li[@class='list-item']")
movies = []
for li in movie_li:
    i = movie_li.index(li)
    title = li.xpath("@data-title")     # 电影名
    score = li.xpath("@data-score")     # 评分
    duration = li.xpath("@data-duration")       # 时长
    actors = li.xpath("@data-actors")           # 主演
    directors = li.xpath("@data-director")      # 导演
    poster = li.xpath(".//img/@src")            # 海报链接
    movie = {
        'title': title,
        'score': score,
        'duration': duration,
        'actors': actors,
        'directors': directors,
        'poster': poster
    }
    movies.append(movie)

print(movies)
# 2.根据一定规则提取
