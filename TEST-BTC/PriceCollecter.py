# -*- coding=utf-8 -*-
#! python3
import time
import requests
import simplejson

class PriceCollecter:
    def __init__(self):
        self.dataindex = 0
        self.isFirstRun = True
        self.qeuryUrl = r'https://www.okcoin.cn/api/v1/ticker.do?symbol=btc_cny'
        self.filepath = r'pricedata.csv'

    def getjson(self):
        text = requests.get(self.qeuryUrl).text
        jsonstr = simplejson.JSONDecoder().decode(text)
        return jsonstr
    
    def parsejson(self, jsonstr):
        timestamp = time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(int(jsonstr['date'])))
        last = jsonstr['ticker']['last']
        buy = jsonstr['ticker']['buy']
        sell = jsonstr['ticker']['sell']
        high = jsonstr['ticker']['high']
        low = jsonstr['ticker']['low']
        vol = jsonstr['ticker']['vol']
        return timestamp + ',' + last + ',' + buy + ',' + sell + ',' + high + ',' + low + ',' + vol + ','

    def writefile(self):
        while True:
            with open(self.filepath, 'a+') as f:
                if self.isFirstRun:
                    print('正在写表头信息...')
                    f.write('服务器时间,最新成交价,买一价,卖一价,最高价,最低价,24小时成交量,\n')
                    print('表头信息写入成功...')
                    self.isFirstRun = False
                else:
                    self.dataindex += 1
                    print('正在写第%d条信息...' % self.dataindex)
                    tempstr = self.parsejson(self.getjson())
                    print('正在处理：%s' % tempstr)
                    f.write(tempstr + '\n')
                    f.flush()
                    print('信息写入完成！')
                    f.close()
                    time.sleep(60)

if __name__ == '__main__':
    pc = PriceCollecter()
    pc.writefile()