# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2019/11/4 20:51"
__doc__ = """ 中国天气网爬虫"""


import requests
from bs4 import BeautifulSoup


def get_soup(url):
    """传递url, 得到soup"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36 Edg/78.0.276.24',
        'Referer': 'http://www.weather.com.cn/textFC/db.shtml'
    }
    resp = requests.get(url, headers=headers)
    text = resp.content.decode('utf-8')
    # 使用html5lib解析器保证最大容错率
    soup = BeautifulSoup(text, 'html5lib')
    # soup = BeautifulSoup(text, 'lxml')      # 无法容错港澳台地区的不规范标签
    return soup


def get_new_url(url):
    """对传递的url中提取新的url，组成待爬取的url列表"""
    DOMAIN_URL = "http://www.weather.com.cn"    # 主域名
    url_list = []
    soup = get_soup(url)
    ul = soup.find_all("ul", class_='lq_contentboxTab2')[0]
    alist = ul.find_all('a')
    for a in alist:
        suffix = a.attrs['href']                # 域名后缀
        full_url = DOMAIN_URL + suffix          # 完整域名
        url_list.append(full_url)
    return url_list


def parse_page(url):
    """对传递的url解析，提取出目标数据"""
    soup = get_soup(url)
    contentboxTab = soup.select("div .contentboxTab")[0]   # 待爬取内容

    """顶部信息"""
    top_info = contentboxTab.find('h1')      # 顶部简要信息
    # 获取简略信息(天气预报|所在地区|发布时间) & 当前日期标签
    title = list(top_info.stripped_strings)[2:]
    print("当前爬取地区和发布时间:", ''.join(title))
    weather_day = contentboxTab.find_all("li", class_='selected')[0]  # <class Tag>
    print('日期:', weather_day.string)

    """# 接下来对每个省/直辖市的具体信息进行解析,每个省/直辖市对应一个(div .conMidtab2 > table)"""
    provinces_part = contentboxTab.find_all('div', class_='conMidtab')[0]
    provinces = provinces_part.find_all('div', class_='conMidtab2')   # 所有省市所在div

    for province in provinces:
        table = province.find('table')
        trs = table.find_all('tr')[2:]      # 前两个tr不是数据

        pro_name = list(trs[0].find('td', class_='rowsPan').stripped_strings)[0]     # 当前table的省市名称(proname)
        print("当前省份/直辖市:", pro_name)
        print("城市及天气情况：")
        for tr in trs:
            tds = tr.find_all('td', class_='')
            city_td = list(tds[0].stripped_strings)[0]
            day_weather = list(tds[1].stripped_strings)[0]
            day_temper = list(tds[3].stripped_strings)[0]
            night_weather = list(tds[4].stripped_strings)[0]
            night_temper = list(tds[6].stripped_strings)[0]
            print(city_td, "白天天气:", day_weather, day_temper, "晚间天气:", night_weather, night_temper)
        print('*'*30)


def parse_gat(gat_url):
    soup = get_soup(gat_url)

    contentboxTab = soup.select("div .contentboxTab")[0]  # 待爬取内容
    provinces = contentboxTab.find_all('div', class_='conMidtab2')[0]  # 港澳台合体区
    tables = provinces.find_all('table')  # 港澳台三个table
    for table in tables:
        trs = table.find_all('tr')[2:]  # 前两个tr不是数据

        pro_name = list(trs[0].find('td', class_='rowsPan').stripped_strings)[0]  # 当前table的省市名称(proname)
        print("当前省份/直辖市:", pro_name)
        print("城市及天气情况：")

        for tr in trs:
            tds = tr.find_all('td', class_='')
            city_td = list(tds[0].stripped_strings)[0]
            day_weather = list(tds[1].stripped_strings)[0]
            day_temper = list(tds[3].stripped_strings)[0]
            night_weather = list(tds[4].stripped_strings)[0]
            night_temper = list(tds[6].stripped_strings)[0]
            print(city_td, "白天天气:", day_weather, day_temper, "晚间天气:", night_weather, night_temper)
        print('*' * 30)


def main():
    entry_url = "http://www.weather.com.cn/textFC/hb.shtml"
    url_list = get_new_url(entry_url)
    print("全国各省市主要城市天气情况")
    for url in url_list:
        if "gat" in url:
            parse_gat(url)
        else:
            parse_page(url)


if __name__ == '__main__':
    main()
    # parse_gat()
