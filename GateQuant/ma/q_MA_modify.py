#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

'''
双均线策略: 5min & 4Hour
'''
from utils.gateAPI import GateIO
from utils.mailhelper import MailHelper
from utils.common_helper import log, get_conf, print_cur_status
import json
import time
import traceback

def get_MA(coin, gate_query):
    json_data = json.loads(gate_query.candle(coin, 15, 4))
    json_data['data'].reverse()
    #获取短均线值
    data_mins = [float(json_data['data'][index][-1]) for index in range(len(json_data['data'])) if index % 4 == 0 and index / 4 < 6]
    cur_short = sum(data_mins[:-1]) / float(len(data_mins) - 1)
    last_short = sum(data_mins[1:]) / float(len(data_mins) - 1)
    #获取长均线值
    data_hours = [float(json_data['data'][index][-1]) for index in range(len(json_data['data'])) if index % 240 == 0 and index / 240 < 5]
    cur_long = sum(data_hours[:-1]) / float(len(data_hours) - 1)
    last_long = sum(data_hours[1:]) / float(len(data_hours) - 1)
    log('modify-' + coin, '%.6f, %.6f, %.6f, %.6f' % (cur_short, last_short, cur_long, last_long))
    return cur_short, last_short, cur_long, last_long

def check_signal(coin, MA_values):
    cur_short, last_short, cur_long, last_long = MA_values
    if (cur_long - cur_short) * (last_long - last_short) < 0:
        if cur_short > cur_long:
            return -1
        else:
            return 1
    else:
        return 0

def get_ask_bid(coin, gate_query):
    return gate_query.orderBook(coin)

def buy(coin, orders, total_pool, gate_trade):
    content = ''
    orders['asks'].reverse()
    order_ammount = [float(orders['asks'][index][0]) * float(orders['asks'][index][1]) for index in range(len(orders['asks']))]
    sums = [sum(order_ammount[:index+1])  for index in range(len(order_ammount)) if sum(order_ammount[:index+1]) < total_pool]
    if len(sums) < 1:
        buy_count = total_pool / float(orders['asks'][0][0])
        # gate_trade.buy(coin, float(orders['asks'][0][0], buy_count))
        content = content + log('modify-' + coin, '以【%.6f】的价格买入了【%.6f】个，总价值为【%.6f】' % (float(orders['asks'][0][0]), buy_count, total_pool))
        return buy_count, content
    else:
        total_count = 0.0
        for index in range(len(sums)):
            total_count = total_count + float(orders['asks'][index][1])
            # gate_trade.buy(coin, float(orders['asks'][index][0]), float(orders['asks'][index][1]))
            content = content + log('modify-' + coin, '以【%.6f】的价格买入了【%.6f】个，总价值为【%.6f】' % (float(orders['asks'][index][0]), float(orders['asks'][index][1]), float(orders['asks'][index][0]) * float(orders['asks'][index][1])))
        rest_pool = total_pool - sums[-1]
        buy_count = rest_pool / float(orders['asks'][len(sums)][0])
        # gate_trade.buy(coin, float(orders['asks'][len(sums)][0], buy_count))
        content = content + log('modify-' + coin, '以【%.6f】的价格买入了【%.6f】个，总价值为【%.6f】' % (float(orders['asks'][len(sums)][0]), buy_count, rest_pool))
        content = content + log('modify-' + coin, '以上总共买入了价值【%s】的【%s】' % (total_pool, coin))
        return total_count + buy_count, content

def sell(coin, orders, total_count, gate_trade):
    content = ''
    order_ammount = [float(orders['bids'][index][1]) for index in range(len(orders['bids']))]
    sums = [sum(order_ammount[:index+1])  for index in range(len(order_ammount)) if sum(order_ammount[:index+1]) < total_count]
    if len(sums) < 1:
        # gate_trade.sell(coin, float(orders['bids'][0][0], total_count))
        content = content + log('modify-' + coin, '以【%.6f】的价格卖出了【%.6f】个，总价值为【%.6f】' % (float(orders['bids'][0][0]), total_count, float(orders['bids'][0][0]) * total_count))
        return float(orders['bids'][0][0]) * total_count, content
    else:
        total_pool = 0.0
        for index in range(len(sums)):
            # gate_trade.sell(coin, float(orders['bids'][index][0]), float(orders['bids'][index][1]))
            total_pool = total_pool + float(orders['bids'][index][0]) * float(orders['bids'][index][1])
            content = content + log('modify-' + coin, '以【%.6f】的价格卖出了【%.6f】个，总价值为【%.6f】' % (float(orders['bids'][index][0]), float(orders['bids'][index][1]), float(orders['bids'][index][0]) * float(orders['bids'][index][1])))
        rest_count = total_count - sums[-1]
        # gate_trade.sell(coin, float(orders['bids'][len(sums)][0], rest_count))
        content = content + log('modify-' + coin, '以【%.6f】的价格卖出了【%.6f】个，总价值为【%.6f】' % (float(orders['bids'][len(sums)][0]), rest_count, rest_count * float(orders['bids'][len(sums)][0])))
        content = content + log('modify-' + coin, '以上总共卖出了价值【%s】的【%s】' % (total_pool + rest_count * float(orders['bids'][len(sums)][0]), coin))
        return total_pool + rest_count * float(orders['bids'][len(sums)][0]), content

def start_script(coin, total_pool, total_count):
    # Provide constants
    API_QUERY_URL = 'data.gateio.io'
    API_TRADE_URL = 'api.gateio.io'
    log('modify-' + coin, '开始测试...初始资金池为 %d' % total_pool)
    buy_sell_flag = True
    mail_helper = MailHelper(get_conf('my_sender'), get_conf('my_pass'))
    # Create a gate class instance
    gate_query = GateIO(API_QUERY_URL, get_conf('apiKey'), get_conf('secretKey'))
    gate_trade = GateIO(API_TRADE_URL, get_conf('apiKey'), get_conf('secretKey'))
    while True:
        try:
            content = ''
            signal = check_signal(coin, get_MA(coin, gate_query))
            if signal == 1:
                if buy_sell_flag:
                    total_count, content = buy(coin, get_ask_bid(coin, gate_query), total_pool, gate_trade)
                    buy_sell_flag = False
                    total_pool = 0.0
                    content = content + log('modify-' + coin, '当前持仓为: 【现金】 %.6f, 【%s】 %.6f 个' % (total_pool, coin, total_count))
                    mail_helper.sendmail(get_conf('my_user'), get_conf('subject') % ('modify-' + coin), content)
                else:
                    log('modify-' + coin, '取消买入【%s】动作，因为最近已经买入过' % coin + '\n当前持仓为: 【现金】 %.6f, 【%s】 %.6f 个' % (total_pool, coin, total_count))
            elif signal == -1:
                if not buy_sell_flag:
                    total_pool, content = sell(coin, get_ask_bid(coin, gate_query), total_count, gate_trade)
                    buy_sell_flag = True
                    total_count = 0.0
                    content = content + log('modify-' + coin, '当前持仓为: 【现金】 %.6f, 【%s】 %.6f 个' % (total_pool, coin, total_count))
                    mail_helper.sendmail(get_conf('my_user'), get_conf('subject') % ('modify-' + coin), content)
                else:
                    log('modify-' + coin, '取消卖出【%s】动作，因为最近已经卖出过' % coin + '\n当前持仓为: 【现金】 %.6f, 【%s】 %.6f 个' % (total_pool, coin, total_count))
            time.sleep(60)
        except Exception as ex:
            content = log('modify-' + coin, 'ERROR\t' + str(ex.args) + str(traceback.format_exc()))
            mail_helper.sendmail(get_conf('my_warn_user'), get_conf('subject') % ('modify-' + coin), content)
            time.sleep(60)
            continue


if __name__ == '__main__':
    # import win_unicode_console
    # win_unicode_console.enable()
    # 设置策略池
    lst_coin = ['eos_usdt']
    # For回测用，设置初始资金池
    total_pool = 3000.0
    total_count = 0.0
    start_script(lst_coin[0], total_pool, total_count)