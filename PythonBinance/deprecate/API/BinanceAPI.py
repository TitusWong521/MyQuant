# -*- coding=utf-8 -*-
# python35
from selenium import webdriver
from API.GetData import GetData
from API.HttpUtils import httpPost, getSign
import time

class Binance(object):
    def __init__(self, api_key, api_secret):
        self.__url = 'https://api.binance.com'
        self.__apiKey = api_key
        self.__secretKey = api_secret
        self.__driver = GetData(webdriver.PhantomJS())

    # 获取币种交易深度
    def depth(self, token_pair):
        URL = "api/v1/depth"
        params = {
            'symbol': token_pair,
            'limit': 10
        }
        return self.__driver.DriverGet(self.__url, URL, params)


    # 查看账户当前挂单
    def open_orders(self, token_pair):
        URL = "api/v3/openOrders"
        params = {
            'api_key': self.__apiKey,
            'symbol': token_pair,
            'timestamp': int(round(time.time()*1000))
        }
        signature = getSign(params, self.__secretKey)
        params['signature'] = signature
        return self.__driver.DriverGet(self.__url, URL, params)



    # 测试下单接口: 用于测试订单请求，但不会提交到撮合引擎
    def test_order(self):
        URL = "/api/v3/order/test"
        params = {
        }
        return self.__driver.DriverGet(self.__url, URL, params)

