# -*- coding=utf-8 -*-
# python35
from bs4 import BeautifulSoup

class GetData(object):
    def __init__(self, driver):
        self.__driver = driver

    def DriverGet(self, url, resource, params={}):
        filters = [str(key) + '=' + str(value) for key, value in params.items()]
        self.__driver.get(url + '/' + resource + '?' + '&'.join(filters))
        print(url + '/' + resource + '?' + '&'.join(filters))
        soap = BeautifulSoup(self.__driver.page_source, 'html.parser')
        return soap.text


