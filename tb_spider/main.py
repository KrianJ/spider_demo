# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2020/7/10 9:45"
__doc__ = """ selenium抓取淘宝页面"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
import time
from bs4 import BeautifulSoup
from random import randint
# 数据库
from tb_spider.config import *
import pymongo

"""MongoDB配置"""
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

"""爬取配置"""
# chromedriver修改标识
# a = 'asdjflasutopfhvcZLmcfl'
# b = 'WangJianZuiShuaiWJZSwj'
# 1.使用chrome浏览器
chrome_option = webdriver.ChromeOptions()
# chrome_option.add_argument('headless')
chrome_option.add_experimental_option('excludeSwitches', ['enable-automation'])     # 使用开发者模式
driver = webdriver.Chrome(options=chrome_option)
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})

# 2.使用火狐浏览器
# driver_path = r'D:\Tools\geckodriver.exe'
# driver = webdriver.Firefox(executable_path=driver_path)

# 定义显式等待
wait = WebDriverWait(driver, 10)


def search(key_word):
    """
    搜索商品名，并返回第一页源码
    :return 第一页索引页源码"""
    driver.get('https://www.taobao.com/')
    try:
        # 搜索input
        input_ele = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))
        )
        # 搜索button
        search_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button'))
        )
    finally:
        pass
    # 模拟行为
    input_ele.send_keys(key_word)
    search_btn.click()
    # 使用selenium搜索需要登录
    login()
    time.sleep(10)
    return None


def get_track(distance):      # distance为传入的总距离
    """将轨迹长度拆分，模拟登录验证行为"""
    tracks = []
    steps = randint(4, 6)
    for step in range(steps):
        if step < steps-1:
            offset = randint(6, 12)  # 每段位移的偏移量
            step_dis = distance // steps - offset
            tracks.append(step_dis)
        else:
            tracks.append(distance-sum(tracks))
    return tracks


def move_to_gap(slider, tracks):     # slider是要移动的滑块,tracks是要传入的移动轨迹

    action = ActionChains(driver)
    action.click_and_hold(slider).perform()  # perform()用来执行ActionChains中存储的行为
    for x in tracks:
        ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
    time.sleep(0.5)
    ActionChains(driver).release().perform()


def login():
    """淘宝自动化登录"""
    try:
        # 账号/密码input
        username = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#fm-login-id'))
        )
        password = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#fm-login-password'))
        )
        username.send_keys('18395327553')   # 用户名
        password.send_keys('zPq19961014')      # 密码
        # 登录button
        login_submit = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#login-form > div.fm-btn > button'))
        )
        time.sleep(3)

        # 滑动验证：使用ActionChains拖动滑块
        slip_square = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#nc_1_n1z'))
        )
        move_to_gap(slip_square, get_track(258))

        # 点击登录
        login_submit.click()
    finally:
        pass


def to_page(page_number):
    """跳转到指定索引页
    :return 指定索引页源码"""
    print('正在跳转至%d页' % page_number)
    try:
        # 进入指定索引页
        page_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input'))
        )
        submit = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit'))
        )
        page_input.clear()
        page_input.send_keys(page_number)
        submit.click()
        # 停顿2s
        time.sleep(2)
        # 判断是否成功跳转
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number))
        )
    except TimeoutException:
        # 超时递归调用
        to_page(page_number)
    finally:
        return driver.page_source


def parse_index(html):
    """解析商品索引页, 获取当前索引页所有商品的基本信息
    :param 索引页html
    :returns 商品基本信息"""
    bs = BeautifulSoup(html, 'lxml')
    items = bs.find_all('div', attrs={'class': 'ctx-box J_MouseEneterLeave J_IconMoreNew'})
    all_info = []
    for item in items:
        """获取每件商品的基本信息: 价格，销量，链接，商品名，店名，地址"""
        single_info = {
            'price': item.find('div', attrs={'class': 'price g_price g_price-highlight'}).text.strip(),
            'sales': item.find('div', attrs={'class': 'deal-cnt'}).text.strip(),
            'href': item.find('a', attrs={'class': 'J_ClickStat'})['href'],
            'title': item.find('div', attrs={'class': 'row row-2 title'}).text.strip(),
            'merchant': item.find('div', attrs={'class': 'shop'}).text.strip(),
            'location': item.find('div', attrs={'class': 'location'}).text.strip()
        }
        # 基本信息
        all_info.append(single_info)
    return all_info


def save_to_mongo(result, MONGO_TABLE):
    try:
        if db[MONGO_TABLE].insert(result):
            print('保存成功!')
    except Exception:
        print("存储到mongodb失败", result)


if __name__ == '__main__':
    key_word = '主板'
    kw_trans = '主板'
    try:
        search(key_word)
        for page in range(1, 3):
            html = to_page(page)
            items = parse_index(html)
            save_to_mongo(items, kw_trans)
    except Exception:
        print('出错了，老铁')
    finally:
        driver.close()
        client.close()

