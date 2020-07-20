# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2020/7/17 15:09"
__doc__ = """ 使用selenium + Beautiful抓取内存条详细参数"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from bs4 import BeautifulSoup
# 数据库
from tb_spider.config import *
import pymongo
import re
# 多进程
from multiprocessing import Process, Queue, Pool, Manager
from functools import partial


"""MongoDB配置"""
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
col = db['monitor']

"""爬取配置"""
# 1.使用chrome浏览器
chrome_option = webdriver.ChromeOptions()
chrome_option.add_argument('headless')
chrome_option.add_experimental_option('excludeSwitches', ['enable-automation'])     # 使用开发者模式
driver = webdriver.Chrome(options=chrome_option)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})

# driver_path = 'D:\py_env\spider_demo\Scripts\chromedriver.exe'
driver = webdriver.Chrome(options=chrome_option)

# 定义显式等待
wait = WebDriverWait(driver, 10)


def get_urls():
    """从mongodb中获取商品url"""
    query = {'href': {'$exists': True}}
    items = col.find(query)
    urls = [item['href'] for item in items]
    return urls


def judge_flag(driver):
    """判断当前网页是天猫还是淘宝"""
    flag = -1
    if '.tmall.' in driver.current_url:
        flag = 1        # 天猫的url
    elif '.taobao.' in driver.current_url:
        flag = 0        # 淘宝的url
    return flag


def switch_page(url):
    """打开新的一页并将driver切换到该页"""
    window_handle = driver.execute_script("window.open('%s')" % url)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return None


def get_item_page(url):
    """获取页面类型(flag)和源代码"""
    driver.get(url)
    flag = judge_flag(driver)
    # close_login = wait.until(
    #     EC.element_to_be_clickable((By.CSS_SELECTOR, '#sufei-dialog-close'))
    # )
    # close_login.click()
    return flag, driver.page_source


def parse_html(html, flag):
    """根据flag和源代码解析网页"""
    html = BeautifulSoup(html, 'lxml')

    # 根据url类型解析参数表单
    if flag == 1:
        try:
            ul = html.select('#J_AttrUL')[0]
        except IndexError or TimeoutError:
            print("未找到商品页面，已下架或被删除(天猫)")
            return None
    elif flag == 0:
        try:
            ul = html.select('#attributes > ul')[0]
        except IndexError or TimeoutError:
            print("未找到商品页面，以下架或被删除(淘宝)")
            return None
    else:
        print('illegal url')
        return None

    # 获取详细参数
    params = {}
    try:
        attrs = ul.find_all('li')
        for attr in attrs:
            # 将参数分割成key_value形式
            attr = attr.text
            pattern = re.compile(r'[：:]')
            key_val = re.split(pattern=pattern, string=attr)
            params[key_val[0]] = key_val[1].strip()
        params['url'] = driver.current_url
    except Exception:
        print('未获取到目标数据')
    return params


def save_to_mongo(params, COLLECTION):
    """持久化至mongodb"""
    try:
        # if db[COLLECTION].update_one({'url': params['url']}, {'$set': params}, upsert=True):
        #     # print('保存成功!')
        #     return None
        if db[COLLECTION].insert_one(params):
            return True
    except Exception:
        # print("存储到mongodb失败", params)
        return False


"""多进程组件"""
def run(url, index):
    """多进程运行单元"""
    count = 0
    if 'click.simba' not in url:
        url = 'http:' + url
    if index == 0:
        flag, html = get_item_page(url)
        params = parse_html(html=html, flag=flag)
    else:
        switch_page(url)
        flag = judge_flag(driver)
        html = driver.page_source
        params = parse_html(html=html, flag=flag)

    save_tag = save_to_mongo(params, 'test')
    if save_tag:
        count += 1
        print(driver.title)
        print('已插入%d条商品信息' % count)
    else:
        print('商品信息插入失败，对应url为：', url)


def multi_run(urls: list):
    # 建立进程池
    pool = Pool(processes=4)
    # 先run一个index=0的
    run(urls[0], 0)
    # 固定index参数，方便传入map函数中
    par = partial(run, index=1)
    pool.map(par, urls[1:len(urls)])
    # 等待所有进程结束并关闭进程
    pool.close()
    pool.join()
    return None


if __name__ == '__main__':
    s_time = time.time()

    urls = get_urls()
    """单进程"""
    count = 0
    for index, url in enumerate(urls):
        if 'click.simba' not in url:
            url = 'http:' + url         # 不加http协议网页可能找不到页面

        # 根据标签页执行不同selenium行为
        if index == 0:
            flag, html = get_item_page(url)
            params = parse_html(html=html, flag=flag)
        else:
            # 转到当前url
            switch_page(url)
            # 判断网页类型(tmall/taobao)
            flag = judge_flag(driver)
            # 解析参数
            html = driver.page_source
            params = parse_html(html=html, flag=flag)

        # 存储至mongodb
        save_tag = save_to_mongo(params, 'test')
        if save_tag:
            count += 1
            print(driver.title)
            print('已插入%d条商品信息' % count)
        else:
            print('商品信息插入失败，对应url为：', url)
        # time.sleep(1)

    r_time = time.time() - s_time
    print(r_time)
    









