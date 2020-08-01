# -*- coding: utf-8 -*-
import requests
import time
from utils.logger import logger

class GridStrat():
    def __init__(self, start_value, lowest, highest, parts, trade, exchange, token_name, fee=0.002):
        self.start_value = float(start_value)
        self.money = float(start_value)
        self.token = 0.0
        self.last_price = None
        self.last_price_index = None
        self.lowest = float(lowest)
        self.highest = float(highest)
        self.parts = parts
        self.trade = trade
        self.fee = fee
        self.exchange = exchange
        self.token_name = token_name
        self.init_grid()

    def __str__(self):
        percent = self.percent_levels[self.last_price_index] * 100 if self.last_price_index != None else 0.00
        assets = self.money + self.token * self.last_price
        earn_ratio = 100 * (assets - self.start_value) / self.start_value
        return '账户初始资产为:\t{:.4f}\t当前资产为:\t{:.4f}'.format(self.start_value, assets),\
               '当前收益率为:\t{:.2f} %'.format(earn_ratio),\
               '持仓比例为:\t{:.2f} %'.format(percent), \
               '持仓详情: \t{:.4f} usdt\t{:.4f} {} [last price: {:.4f}]'.format(self.money, self.token, self.token_name,
                                                                            self.last_price)

    def init_grid(self):
        price_part_value = (self.highest - self.lowest) / self.parts
        percent_part_value = 1 / self.parts
        self.price_levels = [round(self.highest - index * price_part_value, 4) for index in range(self.parts + 1)]
        self.percent_levels = [round(0 + index * percent_part_value, 4) for index in range(self.parts + 1)]
        self.price_levels[-1] = self.lowest
        self.percent_levels[-1] = 1.0000
        self.last_price_index = self.last_price_index if self.last_price_index != None else None

    def update(self, lowest, highest, parts):
        # todo: 修改策略后，网格的持仓比例等显示异常，对应的买入卖出操作也需要审查
        self.lowest = lowest
        self.highest = highest
        self.parts = parts
        self.init_grid()
        infos = ['Update grid at [lowest]: {}, [highest]: {}, [parts]: {}'.format(lowest, highest, parts), ]
        for info in self.__str__():
            infos.append(info)
        logger.info('\n'.join(infos))
        return '[GRID SCRIPT]: Strat cfg update!', '\n'.join(infos)

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
                    return True, self.order_target_percent(
                        float(close), depth, target=self.percent_levels[self.last_price_index], date=date)
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
                if upper != None and float(close) > upper:
                    self.last_price_index = self.last_price_index - 1
                    signal = True
                    continue
                # 还不是最重仓，继续跌，再买一档
                if lower != None and float(close) < lower:
                    self.last_price_index = self.last_price_index + 1
                    signal = True
                    continue
                break
            if signal:
                return True, self.order_target_percent(
                    float(close), depth, target=self.percent_levels[self.last_price_index] - cur_percent, date=date)
            else:
                return False, []

    def order_target_percent(self, close, depth, target, date=''):
        logs = []
        self.last_price = close
        logs.append('-' * 15 + '\tTrade info start\t' + '-' * 15)
        if self.money == self.start_value:
            usdt_ammount = abs(target * self.start_value)
        else:
            usdt_ammount = abs(target * (self.money / (1 - self.percent_levels[self.last_price_index])))
        if target > 0:
            mail_subject = '[GRID SCRIPT]: buy {:.4f} usdt arround price [{:.4f}]'.format(usdt_ammount, close)
            for price, volumn in depth[0]:
                price, volumn = float(price), float(volumn)
                order_ammount = price * volumn
                if usdt_ammount > order_ammount:
                    self.trade(self.exchange, self.token_name, price, volumn, 'buy')
                    logs.append('{} -> buy {:.4f} usdt/ {:.4f} {} on price [{:.4f}]'
                                .format(date, order_ammount, volumn, self.token_name, price))
                    logs.append('Total trade fee: {:.4f} usdt.'.format(order_ammount * self.fee))
                    usdt_ammount -= order_ammount
                    self.token += volumn
                    self.money -= order_ammount
                    self.money -= order_ammount * self.fee
                    continue
                else:
                    order_volumn = round(usdt_ammount / price, 4)
                    self.trade(self.exchange, self.token_name, price, order_volumn, 'buy')
                    logs.append('{} -> buy {:.4f} usdt/ {:.4f} {} on price [{:.4f}]'
                                .format(date, usdt_ammount, order_volumn, self.token_name, price))
                    logs.append('Total trade fee: {:.4f} usdt.'.format(usdt_ammount * self.fee))
                    self.token += order_volumn
                    self.money -= usdt_ammount
                    self.money -= usdt_ammount * self.fee
                    break
        else:
            mail_subject = '[GRID SCRIPT]: sell {:.4f} usdt of {} arround price [{:.4f}]'\
                .format(usdt_ammount, self.token_name, close)
            for price, volumn in depth[1]:
                price, volumn = float(price), float(volumn)
                order_ammount = price * volumn
                if usdt_ammount > order_ammount:
                    self.trade(self.exchange, self.token_name, price, volumn, 'sell')
                    logs.append('{} -> sell {:.4f} {}/ {:.4f} usdt on price [{:.4f}]'
                                .format(date, volumn, self.token_name, order_ammount, price))
                    logs.append('Total trade fee: {:.4f} {}.'.format(volumn * self.fee, self.token_name))
                    usdt_ammount -= order_ammount
                    self.token -= volumn
                    self.token -= volumn * self.fee
                    self.money += order_ammount
                    continue
                else:
                    order_volumn = round(usdt_ammount / price, 4)
                    self.trade(self.exchange, self.token_name, price, order_volumn, 'sell')
                    logs.append('{} -> sell {:.4f} {}/ {:.4f} usdt on price [{:.4f}]'
                                .format(date, order_volumn, self.token_name, usdt_ammount, price))
                    logs.append('Total trade fee: {:.4f} {}.'.format(order_volumn * self.fee, self.token_name))
                    self.token -= order_volumn
                    self.token -= order_volumn * self.fee
                    self.money += usdt_ammount
                    break
        for log in self.__str__():
            logs.append(log)
        logs.append('-' * 10 + '\tTrade info end\t' + '-' * 10)
        _ = [logger.info(log) for log in logs]
        return mail_subject, '\n'.join(logs)

