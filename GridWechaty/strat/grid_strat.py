# -*- coding: utf-8 -*-
import time
from utils.logger import logger

class GridStrat():
    def __init__(self, start_value, lowest, highest, parts, trade, exchange, token_name, fee=0.002):
        self.start_value = float(start_value)
        self.money = float(start_value)
        self.token = 0.0
        self.last_price = None
        self.last_price_index = None
        self.last_percent = 0.0
        self.lowest = float(lowest)
        self.highest = float(highest)
        self.parts = parts
        self.trade = trade
        self.fee = fee
        self.exchange = exchange
        self.token_name = token_name
        self.init_grid()

    def __str__(self):
        percent = int(self.last_percent * 100)
        assets = self.money + self.token * self.last_price
        earn_ratio = 100 * (assets - self.start_value) / self.start_value
        return '\n'.join(['账户初始资产为:\t{:.4f}\t当前资产为:\t{:.4f}'.format(self.start_value, assets),\
               '当前收益率为:\t{:.2f} %'.format(earn_ratio),\
               '持仓比例为:\t{:.2f} %'.format(percent), \
               '持仓详情: \t{:.4f} usdt\t{:.4f} {} [last price: {:.4f}]'.format(self.money, self.token, self.token_name,
                                                                            self.last_price)])

    def init_grid(self):
        price_part_value = (self.highest - self.lowest) / self.parts
        percent_part_value = 1 / self.parts
        self.price_levels = [round(self.highest - index * price_part_value, 4) for index in range(self.parts + 1)]
        self.percent_levels = [round(0 + index * percent_part_value, 4) for index in range(self.parts + 1)]
        self.price_levels[-1] = self.lowest
        self.percent_levels[-1] = 1.0000

    def update(self, lowest, highest, parts):
        self.lowest = lowest
        self.highest = highest
        self.parts = parts
        self.last_price_index = None
        self.init_grid()
        logs = ['Update grid at [lowest]: {}, [highest]: {}, [parts]: {}'.format(lowest, highest, parts), ]
        logs.append(self.__str__())
        logger.info('\n'.join(logs))
        return '\n'.join(logs)

    def run_data(self, data, date=''):
        return self.run_next(data, date=date)

    def run_datas(self, datas, dates=None):
        if dates:
            for data, date in zip(datas, dates):
                self.run_next(data, date)
        else:
            for data in datas:
                self.run_next(data, )

    def run_next(self, data, date=''):
        date = date if date != '' else time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))
        close, depth = data
        if self.last_price_index == None:
            for i in range(len(self.price_levels)):
                if float(close) > self.price_levels[i]:
                    self.last_price_index = i
                    target = self.percent_levels[self.last_price_index] - self.last_percent
                    if target != 0.0:
                        return True, self.order_target_percent(float(close), depth, target, date=date)
        else:
            signal = False
            while True:
                upper = None
                lower = None
                if self.last_price_index > 0:
                    upper = self.price_levels[self.last_price_index - 1]
                if self.last_price_index < len(self.price_levels) - 1:
                    lower = self.price_levels[self.last_price_index + 1]
                # 还不是最轻仓，继续涨，就再卖一档
                if upper and float(close) > upper:
                    self.last_price_index = self.last_price_index - 1
                    signal = True
                    continue
                # 还不是最重仓，继续跌，再买一档
                if lower and float(close) < lower:
                    self.last_price_index = self.last_price_index + 1
                    signal = True
                    continue
                break
            if signal:
                target = self.percent_levels[self.last_price_index] - self.last_percent
                if target != 0.0:
                    return True, self.order_target_percent(float(close), depth, target, date=date)
            else:
                return False, []

    def order_target_percent(self, close, depth, target, date=''):
        print('target', target)
        logs = []
        self.last_price = close
        logs.append('-' * 9 + '\tTrade info start\t' + '-' * 9)
        is_trade_done = False
        if target > 0:
            if self.percent_levels[self.last_price_index] - target == 0:
                usdt_ammount = target * self.money
            else:
                usdt_ammount = round(target * self.money / (1 - self.last_percent), 4)
            for price, volumn in depth[0]:
                price, volumn = float(price), float(volumn)
                if usdt_ammount > price * volumn:
                    order_volumn = volumn
                else:
                    order_volumn = round(usdt_ammount / price, 4)
                    is_trade_done = True
                self.trade(self.exchange, self.token_name, price, order_volumn, 'buy')
                logs.append('{} -> buy {:.4f} usdt (~ {:.4f} {}) on price [{:.4f}]'
                            .format(date, price * order_volumn, order_volumn, self.token_name, price))
                logs.append('Total trade fee: {:.4f} usdt.'.format(price * order_volumn * self.fee))
                self.token += order_volumn * (1 - self.fee)
                self.money -= price * order_volumn
                usdt_ammount -= price * order_volumn
                if is_trade_done:
                    break
        else:
            token_ammount = abs(target * self.token / self.last_percent)
            for price, volumn in depth[1]:
                price, volumn = float(price), float(volumn)
                if token_ammount > volumn:
                    order_volumn = volumn
                else:
                    order_volumn = token_ammount
                    is_trade_done = True
                self.trade(self.exchange, self.token_name, price, order_volumn, 'sell')
                logs.append('{} -> sell {:.4f} {} (~ {:.4f} usdt) on price [{:.4f}]'
                            .format(date, order_volumn, self.token_name, order_volumn * price, price))
                logs.append('Total trade fee: {:.4f} {}.'.format(order_volumn * self.fee, self.token_name))
                token_ammount -= order_volumn
                self.token -= order_volumn
                self.money += order_volumn * price * (1 - self.fee)
                if is_trade_done:
                    break
        self.last_percent += target
        logs.append(self.__str__())
        logs.append('-' * 9 + '\tTrade info end\t' + '-' * 9)
        _ = [logger.info(log) for log in logs]
        return '\n'.join(logs)
