# -*- coding:utf-8 -*-
__Author__ = "KrianJ wj_19"
__Time__ = "2019/11/26 16:35"
__doc__ = """ 12306抢票"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class Ticket(object):
    def __init__(self):
        self.login_url = 'https://kyfw.12306.cn/otn/login/init'
        self.initmy_url = 'https://kyfw.12306.cn/otn/view/index.html'
        self.search_url = 'https://kyfw.12306.cn/otn/leftTicket/init'
        self.passengers_url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        self.username = '15524656191'
        self.pwd = '19961014'
        self.driver = webdriver.Firefox(executable_path=r'D:\Tools\geckodriver.exe')

    def wait_input(self):
        # 表单输入
        self.from_station = '上海'
        self.to_station = '北京'
        self.depart_time = '2019-12-12'
        self.passengers = '汪健'
        self.trains = 'G102'
        # self.from_station = input('出发地：')
        # self.to_station = input('目的地：')
        # self.depart_time = input('出发时间(yyyy-MM-dd)：')
        # self.passengers = input('购票人姓名(多人以","隔开):').split(',')
        # self.trains = input('购买车次(多车次用","隔开)：').split(',')

    def _login(self):
        """登陆12306"""
        self.driver.get(self.login_url)
        self.username_input = self.driver.find_element(By.ID, 'username')
        self.pwd_input = self.driver.find_element(By.ID, 'password')
        self.username_input.send_keys(self.username)
        self.pwd_input.send_keys(self.pwd)

        # 利用显示等待
        # 直到url是等于initmy_url才认为是登陆成功
        WebDriverWait(self.driver, 2000).until(
            ec.url_to_be(self.initmy_url)
        )
        print("登陆成功")

    def _order_ticket(self):
        """订票流程"""
        # 1. 跳转到查询余票界面
        self.driver.get(self.search_url)

        # 2. 等待购票信息输入是否正确
        WebDriverWait(self.driver, 2000).until(
            ec.text_to_be_present_in_element_value((By.ID, 'fromStationText'), self.from_station)
        )       # 出发地

        WebDriverWait(self.driver, 2000).until(
            ec.text_to_be_present_in_element_value((By.ID, 'toStationText'), self.to_station)
        )       # 目的地

        WebDriverWait(self.driver, 2000).until(
            ec.text_to_be_present_in_element_value((By.ID, 'train_date'), self.depart_time)
        )       # 出发日期

        # 3. 等待查询按钮是否可用
        WebDriverWait(self.driver, 2000).until(
            ec.element_to_be_clickable((By.ID, 'query_ticket'))
        )

        # 4. 如果可用则执行点击查询
        self.searchBtn = self.driver.find_element(By.ID, 'query_ticket')
        self.searchBtn.click()

        # 5. 等待车次信息显示出来
        WebDriverWait(self.driver, 2000).until(
            ec.presence_of_element_located((By.XPATH, ".//tbody[@id='queryLeftTable']/tr"))
        )

        # 6. 找到所有没有datatrain属性的tr标签
        tr_list = self.driver.find_elements(By.XPATH, ".//tbody[@id='queryLeftTable']/tr[not(@datatran)]")

        # 7. 遍历所有满足条件的tr标签
        for tr in tr_list:
            train_number = tr.find_element(By.CLASS_NAME, 'number').text
            if train_number in self.trains:
                left_tickets = tr.find_element(By.XPATH, './/td[4]').text
                if left_tickets == '有' or left_tickets.isdigit:
                    orderBtn = tr.find_element(By.CLASS_NAME, 'btn72')
                    orderBtn.click()
                    # 等待是否来到确认乘客的界面
                    WebDriverWait(self.driver, 2000).until(
                        ec.url_to_be(self.passengers_url)
                    )
                    # self.driver.get(self.passengers_url)

    def run(self):
        self.wait_input()
        self._login()
        self._order_ticket()


if __name__ == '__main__':
    spider = Ticket()
    spider.run()
