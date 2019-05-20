# -*- coding=utf-8 -*-
# python35
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading
import random
import time


class FuckBuy(object):
    def __init__(self, account, password, user_agent):
        options = webdriver.ChromeOptions()
        options.add_argument('user-agent="{}"'.format(random.choice(user_agent)))
        self.driver = webdriver.Chrome(chrome_options=options)
        self.account = account
        self.password = password

    def exec(self):
        print('准备转到登陆页面...')
        self.driver.get('https://www.biss.com/#/login')
        username = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="app"]/div/div[2]/div/form/div[1]/div/div/input')))
        print('准备输入账户信息...')
        username.send_keys(self.account)
        password = self.driver.find_element_by_xpath(
            '//*[@id="app"]/div/div[2]/div/form/div[2]/div/div/input')
        password.send_keys(self.password)
        login = self.driver.find_element_by_xpath(
            '//*[@id="app"]/div/div[2]/div/form/div[3]/div/button')
        print('准备登陆...')
        login.send_keys(Keys.ENTER)
        time.sleep(15)
        print('成功登陆, 准备转到购买页面...')
        self.driver.get('https://www.biss.com/#/cryptocurrency')
        print('当前账号是 [{}], 软件将在21:00:02准时启动...'.format(self.account))
        while True:
            try:
                ele_hour = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="app"]/div/div[2]/div[1]/div[1]/div/div[1]/div[2]/div[3]/ul/li[1]')))
                ele_minute = self.driver.find_element_by_xpath(
                    '//*[@id="app"]/div/div[2]/div[1]/div[1]/div/div[1]/div[2]/div[3]/ul/li[2]')
                ele_second = self.driver.find_element_by_xpath(
                    '//*[@id="app"]/div/div[2]/div[1]/div[1]/div/div[1]/div[2]/div[3]/ul/li[3]')
                hour = ele_hour.text
                minute = ele_minute.text
                second = ele_second.text
                print('抢购倒计时: {}:{}:{}'.format(hour, minute, second))
                if hour == '00':
                    if minute == '00':
                        if second in ['01', '02']:
                            print()
                            break
                    else:
                        time.sleep(2)
                else:
                    time.sleep(60)
            except:
                continue
        retry_count = 0
        while True:
            retry_count += 1
            print('第{}次尝试: 准备输入要购买的USDT数量...'.format(retry_count))
            ele_usdt_cnt = self.driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/div[1]/div/div[1]/div[1]/div/div[3]/input')
            backspace = 3
            while backspace > 0:
                backspace -= 1
                ele_usdt_cnt.send_keys(Keys.BACK_SPACE)
            ele_usdt_cnt.clear()
            ele_usdt_cnt.send_keys('8')
            ele_usdt_cnt.send_keys('9')
            ele_usdt_cnt.send_keys('0')
            print('输入数量成功, 准备点击购买...')
            ele_submit_btn = self.driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/div[1]/div/div[1]/div[1]/div/div[9]/button')
            ele_submit_btn.send_keys(Keys.RETURN)
            ele_biss_balance = self.driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[2]/div[2]/div[2]/div[1]/div[1]/div/div[1]/div[2]/div/div[1]/div/span[2]')
            biss_balance = str(ele_biss_balance.text).split(' ')[0]
            if biss_balance == '0':
                print('本次购买不成功, 即将进行下一次尝试...')
                continue
            else:
                print('!!!!!!!!!!恭喜恭喜, 成功抢到!!!!!!!!!!')
                print('账户: [{}], Biss余额: [{}] !!!'.format(self.account, biss_balance))
                break

    def run(self):
        t = threading.Thread(target=self.exec)  # 开启并行线程
        t.setDaemon(True)
        t.start()

