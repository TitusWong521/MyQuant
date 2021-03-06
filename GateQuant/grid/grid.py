import requests
import time
from utils.logger import logger

class GridStrat():
    def __init__(self, start_value, lowest, highest, parts, buy, sell, fee=0.002):
        self.start_value = float(start_value)
        self.money = float(start_value)
        self.token = 0.0
        self.last_price = None
        self.last_price_index = None
        self.lowest = float(lowest)
        self.highest = float(highest)
        self.parts = parts
        self.buy = buy
        self.sell = sell
        self.fee = fee
        self.init_grid()

    def __str__(self):
        percent = self.percent_levels[self.last_price_index] * 100 if self.last_price_index != None else 0.00
        assets = self.money + self.token * self.last_price
        earn_ratio = 100 * (assets - self.start_value) / self.start_value
        return '账户初始资产为:\t{:.4f}\t当前资产为:\t{:.4f}\t当前收益率为:\t{:.2f} %\n' \
               '持仓比例为:\t{:.2f} %\n持仓详情: \t{:.4f} USDT\t{:.4f} TOKEN [last price: {:.4f}]'\
            .format(self.start_value, assets, earn_ratio, percent, self.money, self.token, self.last_price)

    def init_grid(self):
        price_part_value = (self.highest - self.lowest) / self.parts
        percent_part_value = 1 / self.parts
        self.price_levels = [round(self.highest - index * price_part_value, 4) for index in range(self.parts + 1)]
        self.percent_levels = [round(0 + index * percent_part_value, 4) for index in range(self.parts + 1)]
        self.price_levels[-1] = self.lowest
        self.percent_levels[-1] = 1.0000
        self.last_price_index = self.last_price_index if self.last_price_index != None else None

    def update(self, lowest, highest, parts):
        self.lowest = lowest
        self.highest = highest
        self.parts = parts
        self.init_grid()

    def run_data(self, prices, date=''):
        self.run_next(prices, date=date)

    def run_datas(self, datas, dates=None):
        if dates:
            for prices, date in zip(datas, dates):
                self.run_next(prices, date)
        else:
            for prices in datas:
                self.run_next(prices, )

    def run_next(self, prices, date=''):
        date = date if date != '' else time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        prices = [float(value) for value in prices]
        if self.last_price_index == None:
            for i in range(len(self.price_levels)):
                if prices[0] > self.price_levels[i]:
                    self.last_price_index = i
                    self.order_target_percent(prices, target=self.percent_levels[self.last_price_index], date=date)
                    return
        else:
            signal = False
            cur_percent = self.percent_levels[self.last_price_index]
            while True:
                upper = None
                lower = None
                if self.last_price_index > 0:
                    upper = self.price_levels[self.last_price_index - 1]
                if self.last_price_index < len(self.price_levels) - 1:
                    lower = self.price_levels[self.last_price_index + 1]
                # 还不是最轻仓，继续涨，就再卖一档
                if upper != None and prices[0] > upper:
                    self.last_price_index = self.last_price_index - 1
                    signal = True
                    continue
                # 还不是最重仓，继续跌，再买一档
                if lower != None and prices[0] < lower:
                    self.last_price_index = self.last_price_index + 1
                    signal = True
                    continue
                break
            if signal:
                self.order_target_percent(prices, target=self.percent_levels[self.last_price_index] - cur_percent, date=date)

    def order_target_percent(self, prices, target, date=''):
        self.last_price = prices[0]
        logger.info('-' * 15 + '\tTrade info start\t' + '-' * 15)
        usdt_ammount = abs(target * self.start_value)
        buy_token_ammount = abs(target * self.start_value) / prices[2]
        sell_token_ammount = abs(target * self.start_value) / prices[1]
        if target > 0:
            self.buy(usdt_ammount)
            logger.info('{} -> buy {:.4f} usdt on price [{:.4f}]'.format(date, usdt_ammount, prices[2]))
            logger.info('Total trade fee: {:.4f} usdt.'.format(usdt_ammount * self.fee))
            self.money -= usdt_ammount
            self.token += buy_token_ammount
        else:
            self.sell(sell_token_ammount)
            logger.info('{} -> sell {:.4f} token on price [{:.4f}]'.format(date, sell_token_ammount, prices[1]))
            logger.info('Total trade fee: {:.4f} token.'.format(sell_token_ammount * self.fee))
            self.money += usdt_ammount
            self.token -= sell_token_ammount
        logger.info(self.__str__())
        logger.info('-' * 15 + '\tTrade info end\t' + '-' * 15)


def oper(per):
    # todo: buy and sell code base on trade depth
    pass

if __name__ == '__main__':
    # offline back test
    # One Phase Backtest
    grid = GridStrat(30.0, 16.0, 21.0, 10, oper, oper)
    with open('./backtest/binance-segment.csv', 'r') as f:
        lines = f.readlines()
    datas = [(line.strip().split(',')[4], line.strip().split(',')[4], line.strip().split(',')[4])
             for line in lines[1:] if len(line.strip()) > 0]
    dates = [line.strip().split(',')[0] for line in lines[1:] if len(line.strip()) > 0]
    grid.run_datas(datas, dates)
    logger.info('*' * 60)
    logger.info('*' * 60)
    # Three Phase Backtest
    # Phase I
    grid = GridStrat(30.0, 16.0, 19.0, 10, oper, oper)
    with open('./backtest/data_seg_1.csv', 'r') as f:
        lines = f.readlines()
    datas = [(line.strip().split(',')[4], line.strip().split(',')[4], line.strip().split(',')[4])
             for line in lines[1:] if len(line.strip()) > 0]
    dates = [line.strip().split(',')[0] for line in lines[1:] if len(line.strip()) > 0]
    grid.run_datas(datas, dates)
    # Phase II
    logger.info('*' * 60)
    grid.update(16.0, 21.0, 10)
    with open('./backtest/data_seg_2.csv', 'r') as f:
        lines = f.readlines()
    datas = [(line.strip().split(',')[4], line.strip().split(',')[4], line.strip().split(',')[4])
             for line in lines[1:] if len(line.strip()) > 0]
    dates = [line.strip().split(',')[0] for line in lines[1:] if len(line.strip()) > 0]
    grid.run_datas(datas, dates)
    # Phase III
    logger.info('*' * 60)
    grid.update(19.0, 21.0, 10)
    with open('./backtest/data_seg_3.csv', 'r') as f:
        lines = f.readlines()
    datas = [(line.strip().split(',')[4], line.strip().split(',')[4], line.strip().split(',')[4])
             for line in lines[1:] if len(line.strip()) > 0]
    dates = [line.strip().split(',')[0] for line in lines[1:] if len(line.strip()) > 0]
    grid.run_datas(datas, dates)
    # # online back test
    # grid = GridStrat(30.0, 2.5, 3.5, 10, oper, oper)
    # url = r'https://api.gateio.ws/api/v4/spot/tickers?currency_pair=eos_usdt'
    # while True:
    #     try:
    #         time.sleep(5)
    #         data = requests.get(url).json()
    #         # import json
    #         # data = json.loads('[{"currency_pair":"EOS_USDT","last":"3.0048","lowest_ask":"3.0057","highest_bid":"3.0048","change_percentage":"0.16","base_volume":"3006525.0399649714","quote_volume":"9224791.90830031750964","high_24h":"3.1479","low_24h":"2.9701"}]')
    #     except:
    #         continue
    #     else:
    #         prices = [data[0]['highest_bid'], data[0]['highest_bid'], data[0]['lowest_ask']]
    #         grid.run_data(prices)
