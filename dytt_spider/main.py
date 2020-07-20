# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2019/10/29 19:55"
__doc__ = """ 电影天堂电影爬取"""


from lxml import etree
import requests

BASE_DOMAIN = 'https://www.dy2018.com'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
}


def get_detail_urls(url):
    __doc__ = """参数：某一页电影列表url，输出：该页所有电影的详情页url(list)"""
    response = requests.get(url, headers=headers)
    text = response.content.decode('gbk')           # gbk解码
    html = etree.HTML(text)                         # 转换成xpath解析字符串

    detail_urls_suffix = html.xpath("//div[@class='co_content8']//table[@class='tbspan']//a[2]/@href")  # 获取每个电影详情页的域名后缀(list)
    detail_urls = map(lambda url: BASE_DOMAIN+url, detail_urls_suffix)           # url从detail_url_suffix里面取，和BASE_DOMAIN组合成完整链接
    return detail_urls


def parse_detail_page(detail_url):
    resp = requests.get(detail_url, headers=headers)
    text = resp.content.decode('gbk')
    html = etree.HTML(text)
    movie_info = {}

    def parse_info(info, rule):     # 待提取文本修改规则
        return info.replace(rule, '').strip()

    infos = html.xpath(".//div[@id='Zoom']/p/text()")   # 详情页所有文本信息
    for index, info in enumerate(infos):                # 将目标文本存入movie_info字典
        # print(info)
        if info.startswith("◎译　　名"):
            info = parse_info(info, "◎译　　名")
            movie_info['title'] = info
        elif info.startswith("◎年　　代"):
            info = parse_info(info, "◎年　　代")
            movie_info['year'] = info
        elif info.startswith("◎产　　地"):
            info = parse_info(info, "◎产　　地")
            movie_info['country'] = info
        elif info.startswith("◎类　　别"):
            info = parse_info(info, "◎类　　别")
            movie_info['category'] = info
        elif info.startswith("◎豆瓣评分"):
            info = parse_info(info, "豆瓣评分")
            movie_info['score'] = info
        elif info.startswith("◎片　　长"):
            info = parse_info(info, "◎片　　长")
            movie_info['duration'] = info
        elif info.startswith("◎导　　演"):
            info = parse_info(info, "◎导　　演")
            movie_info['directors'] = info
        elif info.startswith("◎主　　演"):
            info = parse_info(info, "◎主　　演")
            # 截取演员的所有p标签文本
            actors = [info]
            for x in range(index+1, len(infos)):
                actor = infos[x].strip()
                if actor.startswith("◎"):
                    break
                actors.append(actor)
            movie_info['actors'] = actors
        elif info.startswith("◎简　　介"):
            for x in range(index + 1, len(infos)):
                profile = infos[x].strip()
                if actor.startswith("◎"):
                    break
            movie_info["profile"] = profile
    download_link =html.xpath("//td[@bgcolor='#fdfddf']/a/@href")       # 获取movie下载链接
    movie_info['link'] = download_link

    return movie_info


def spider():
    __doc__ = """将所有功能集成到spider函数，方便直接调用"""
    base_url = "https://www.dy2018.com/html/bikan/index{}.html"
    movies = []
    for x in range(2, 8):       # 需要提取的电影页数
        page = '_' + str(x)
        url = base_url.format(page)             # 组合成7页完整的电影列表的list
        detail_urls = get_detail_urls(url)
        for detail_url in detail_urls:
            movie = parse_detail_page(detail_url)
            # print(movie)
            movies.append(movie)
            # print(movie)

    import codecs
    # 因为txt文件默认编码是gbk，所以需要修改成utf-8编码
    with codecs.open('movie_info.txt', 'w', 'utf-8') as f:
        for line in movies:
            f.write(str(line)+'\n')
        f.close()


if __name__ == '__main__':
    spider()
