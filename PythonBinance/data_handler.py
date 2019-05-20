# -*- coding=utf-8 -*-
# python35
from binance.client import BinanceRESTAPI, BinanceWebSocketAPI
import time


class DataHandler(object):
    def __init__(self, config_file, logger):
        self.logger = logger
        self.print('主程序初始化中...')
        self.logger = logger
        self.api_key, self.api_secret, self.trade_symbol, self.target_symbol = self.get_api(config_file)
        self.symbol = self.trade_symbol + self.target_symbol
        self.rest_client = BinanceRESTAPI(self.api_key, self.api_secret)
        self.ws_client = BinanceWebSocketAPI(self.api_key)
        self.precision = self.get_precision()
        self.time_span = self.get_client_time() - self.get_server_time() + 500
        self.print('客户端时间相对服务器时间的时间间隔为: {}.'.format(str(self.time_span)))
        self.print('主程序初始化完成.')

    def get_precision(self):
        all_symbol_precision = self.rest_client.exchangeInfo()
        for symbol in all_symbol_precision.symbols:
            if symbol['symbol'] == self.symbol:
                if symbol['status'] != 'TRADING':
                    self.print('{}/{}交易对现在不能交易, 软件会在5秒后自动关闭!'.
                                      format(self.trade_symbol, self.target_symbol), type='error')
                    time.sleep(5)
                    exit(0)
                self.print('当前标的的交易最小精度为: {}.'.format(str(symbol['filters'][0]['tickSize'])))
                return float(symbol['filters'][0]['tickSize'])

    def get_client_time(self):
        return int(time.time() * 1000)

    def get_server_time(self):
        return self.rest_client.server_time().server_time

    def print(self, message, type='info'):
        # print(message)
        if type == 'info':
            self.logger.info(message)
        elif type == 'error':
            self.logger.error(message)

    def get_api(self, config_file):
        self.print('读取配置文件中...')
        api_key = api_secret = trade_symbol = target_symbol = ''
        with open(config_file, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if 'api_key' in line:
                api_key = line.replace('\n', '').split('=')[-1]
            elif 'api_secret' in line:
                api_secret = line.replace('\n', '').split('=')[-1]
            elif 'trade_symbol' in line:
                trade_symbol = line.replace('\n', '').split('=')[-1]
            elif 'target_symbol' in line:
                target_symbol = line.replace('\n', '').split('=')[-1]
        self.print('读取配置文件完成.')
        return api_key, api_secret, trade_symbol, target_symbol

    def get_first_price(self):
        self.print('获取买卖一价中...')
        depth = self.rest_client.depth(symbol=self.symbol, limit=10)
        first_buy, first_sell = depth.get_bids_highest_price(), depth.get_asks_lowest_price()
        self.print('买卖一价分别为: {}, {}.'.format(str(first_buy), str(first_sell)))
        return first_buy, first_sell

    def get_best_order_price(self):
        self.print('生成最佳交易价格中...')
        depth = self.rest_client.depth(symbol=self.symbol, limit=10)
        first_buy, first_sell = float(depth.get_bids_highest_price()), float(depth.get_asks_lowest_price())
        best_buy = '%f' % (first_buy + self.precision)
        best_sell = '%f' % (first_sell - self.precision)
        self.print('生成的最佳买入卖出价格分别为: {}, {}.'.format(str(best_buy), str(best_sell)))
        return best_buy, best_sell

    def get_balance(self):
        self.print('获取账户相关资产余额中...')
        account = self.rest_client.account(timestamp=self.get_client_time() - self.time_span)
        trade_asset = [balance for balance in account.balances if balance.asset == self.trade_symbol]
        self.print('账户资产中[{}]余额为: {}, 另有: {}被冻结.'
                   .format(self.trade_symbol, str(trade_asset[0].free), str(trade_asset[0].locked)))
        target_asset = [balance for balance in account.balances if balance.asset == self.target_symbol]
        self.print('账户资产中[{}]余额为: {}, 另有: {}被冻结.'
                   .format(self.target_symbol, str(target_asset[0].free), str(target_asset[0].locked)))
        if float(trade_asset[0].locked) - 0 > 1e-6 or float(target_asset[0].locked) - 0 > 1e-6:
            self.print('相关资产有冻结, 取消相关订单中...')
            orders = self.rest_client.current_open_orders(symbol=self.symbol,
                                                          timestamp=self.get_client_time() - self.time_span)
            for order in orders:
                order = self.rest_client.cancel_order(self.symbol, order.id, order.client_order_id,
                                                      timestamp=self.get_client_time() - self.time_span)
                self.print_order(order)
            self.print('相关资产有冻结, 取消相关订单完成.')
            trade, target = float(trade_asset[0].free) + float(trade_asset[0].locked), \
                            float(target_asset[0].free) + float(target_asset[0].locked)
        else:
            trade, target = float(trade_asset[0].free), float(target_asset[0].free)
        self.print('获取账户相关资产余额完成.')
        return trade, target

    def send_sell_order(self, quantity, price):
        self.print('生成卖单中...')
        order = self.rest_client.new_order(self.symbol, "SELL", "LIMIT", "IOC", quantity, price,
                                           timestamp=self.get_client_time()-self.time_span)
        self.print_order(order)
        self.print('生成卖单完成.')

    def send_buy_order(self, quantity, price):
        self.print('生成买单中...')
        order = self.rest_client.new_order(self.symbol, "BUY", "LIMIT", "IOC", quantity, price,
                                           timestamp=self.get_client_time() - self.time_span)
        self.print_order(order)
        self.print('生成买单完成.')

    def print_order(self, order):
        self.print('订单编号：{}'.format(str(order.id)))
        self.print('订单状态：{}'.format(str(order.status)))
        self.print('订单类型：{}'.format(str(order.type)))
        self.print('订单方向：{}'.format(str(order.side)))

    def get_order_status(self, order):
        order = self.rest_client.query_order(self.symbol, order_id=order.id, orig_client_order_id=order.client_order_id,
                                             timestamp=self.get_client_time() - self.time_span)
        return order.status, order.type, order.side

