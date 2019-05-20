# -*- coding=utf-8 -*-
#! python3
import time
import requests
import simplejson

class MATest:
    def __init__(self):
        self.filepath = 'DataSource20170313.csv'
        self.listprice = []
        self.short = 5
        self.long = 10
        self.listshort = []
        self.listlong = []
        self.lastprice = 0.0
        self.balance = 100000.0
        self.BTCnum = 0.0

    '''
    将文件信息载入到程序中
    '''
    def loadfile(self):
        with open(self.filepath, 'r') as f:
            lineindex = 0
            for line in f.readlines():
                # print(line)
                if lineindex == 0:
                    lineindex += 1
                    continue
                else:
                    self.listprice.append(float(line.split(',')[1]))
        print('文件信息载入成功, 数据长度为%d' % len(self.listprice))
    
    '''
    index是listprice开始计算MA的序号
    flag是标记长均线或者短均线的标记位，True=short，False=long
    注：index < len(listprice) - short/long + 1
    '''
    def getsum(self, index, flag):
        length = 0
        sum = 0
        if flag:
            length = self.short
        else:
            length = self.long
        for i in range(index - 1, index + length - 1):
            sum += self.listprice[i]
        return sum

    '''
    获取短均线数据
    '''
    def getshort(self):
        self.listshort = [self.getsum(i+1, True)/self.short for i in range(0, len(self.listprice) - self.short + 1)]
        print('获取短均线成功, 数据长度为%d' % len(self.listshort))

    '''
    获取长均线数据
    '''
    def getlong(self):
        self.listlong = [self.getsum(i+1, False)/self.long for i in range(0, len(self.listprice) - self.long + 1)]
        print('获取长均线成功, 数据长度为%d' % len(self.listlong))

    def trade(self):
        # 将现有价格，短均线价格，长均线价格归一化
        self.listprice = self.listprice[self.long -1 : ]
        self.listshort = self.listshort[self.long - self.short - 1 : ]
        for i in range(0, len(self.listlong) -1):
            sub1 = self.listshort[i] - self.listlong[i]
            sub2 = self.listshort[i + 1] - self.listlong[i + 1]
            # time.sleep(2)
            if sub1 < 0 and sub1 * sub2 < 0:
                if self.balance <= 0:
                    continue
                self.BTCnum = self.balance / self.listprice[i]
                print('买入' + str(self.balance) + '元, 共' + str(self.BTCnum) + '个BTC!')
                self.lastprice = self.listprice[i]
                self.balance = 0
            if sub1 > 0 and sub1 * sub2 < 0:
                if self.BTCnum <= 0.0:
                    continue
                if self.listprice[i] > self.lastprice:
                    self.balance = self.BTCnum * self.listprice[i]
                    print('卖出' + str(self.BTCnum) + '个BTC, 共' + str(self.balance) + '元!')
                    self.BTCnum = 0

if __name__ == '__main__':
    mat = MATest()
    mat.loadfile()
    mat.getshort()
    mat.getlong()
    mat.trade()
    print('账户余额为：%d!' % mat.balance)
