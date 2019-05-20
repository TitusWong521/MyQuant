import numpy as np
import pandas as pd
from talib import ATR
import talib

# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    # context内引入全局变量s1
    context.BU = get_dominant_future('BU')
    context.RB = get_dominant_future('RB')
    context.I = get_dominant_future('I')
    context.J = get_dominant_future('J')
    context.P = get_dominant_future('P')
    context.CF = get_dominant_future('CF')
    context.future = [context.BU, context.RB, context.I,context.J, context.P,context.CF]
    # context.future = [context.BU]
    # context.future88=['BU88', 'RB88', 'I88', 'J88', 'P88', 'CF88']
    
    # 设置回测的保证金率为10%
    #context.marin_rate = 10
    # 滑点
    #context.slippage = 1
    # 设置佣金费率为万分之1
    #context.commission = 0.01
    
    # 初始化时订阅合约行情。订阅之后的合约行情会在handle_bar中进行更新。
    subscribe(context.future)
    # 初始化context.last_main_symbol
    context.last_main_symbol = []
    context.long_period = 20
    context.short_period = 30
    context.period = 100

    
# before_trading此函数会在每天日盘交易开始前被调用，当天只会被调用一次
def before_trading(context):
    context.BU = get_dominant_future('BU')
    context.RB = get_dominant_future('RB')
    context.I = get_dominant_future('I')
    context.J = get_dominant_future('J')
    context.P = get_dominant_future('P')
    context.CF = get_dominant_future('CF')
    context.future = [context.BU, context.RB, context.I,context.J, context.P,context.CF]
    # context.future = [context.BU]
    
    if context.last_main_symbol != context.future:
        context.last_main_symbol = context.future
        subscribe(context.last_main_symbol)


# 你选择的期货数据更新将会触发此段逻辑，例如日线或分钟线更新
def handle_bar(context, bar_dict):
    for security in context.last_main_symbol:
        # 账户持仓
        position = context.portfolio.positions[security]
        # 多单和空单的仓位都是也就是空仓
        if position.buy_quantity == 0 and position.sell_quantity ==0:
            market_in(context, bar_dict, security)
        # 如果不是空仓
        elif position.buy_quantity >0 or position.sell_quantity >0:
            stop_loss(context, bar_dict, security)
            market_add(context, bar_dict, security)
            market_out(context, bar_dict, security)
    
    
def market_in(context, bar_dict, security):
    hist = history_bars(security, context.period, '1d', ['high','low','close'])
    
    # 按照context.long_period计算每一天对应的 ATR(平均真实振幅)值，然后取最后一天的值返回
    N_long = ATR(hist['high'], hist['low'], hist['close'], timeperiod=context.long_period)[-1]
    # 按照context.short_period计算每一天对应的 ATR(平均真实振幅)值，然后取最后一天的值返回
    N_short = ATR(hist['high'], hist['low'], hist['close'], timeperiod=context.short_period)[-1]
    
    close = hist['close']
    # print('*************************************************************')
    # macd短期均线  macdsignal是长期均线
    # 短穿长 为金叉
    macd,macdsignal,macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    # print('*************************************************************')
    
    # 买入手数
    amount_long = int(context.portfolio.cash*0.001/N_long)
    amount_short = int(context.portfolio.cash*0.001/N_short)
    # 最新价大于前20天的最高价
    if macd[-1] > macdsignal[-1] and amount_long >0 and bar_dict[security].last>max(hist['high'][-20:-1]):
        buy_open(security, amount_long)
        print("buy_open")
    # 最新价小于前40天的最高价
    if macd[-1] < macdsignal[-1] and amount_short >0 and bar_dict[security].last<min(hist['low'][-40:-1]):
        sell_open(security, amount_short)
        print("sell_open")

 
def market_add(context, bar_dict, security):
    hist = history_bars(security, context.period, '1d', ['high','low','close'])
    N_long = ATR(hist['high'], hist['low'], hist['close'], timeperiod=context.long_period)[-1]
    N_short = ATR(hist['high'], hist['low'], hist['close'], timeperiod=context.short_period)[-1]
    close = hist['close']
    position = context.portfolio.positions[security]
    macd,macdsignal,macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    amount_long = int(context.portfolio.cash*0.001/N_long)
    amount_short = int(context.portfolio.cash*0.001/N_short)
    if amount_long>0 and macd[-1] > macdsignal[-1] and bar_dict[security].last > (position.buy_avg_holding_price + 2*N_long):
        buy_open(security, amount_long)
        print("buy_add")
            
    if amount_short>0 and macd[-1] < macdsignal[-1] and bar_dict[security].last < (position.sell_avg_holding_price - 2*N_short):
        sell_open(security, amount_short)
        print("sell_add")
    
def stop_loss(context, bar_dict, security):
    hist = history_bars(security, context.period, '1d', ['high','low','close'])
    N_long = ATR(hist['high'], hist['low'], hist['close'], timeperiod=context.long_period)[-1]
    N_short = ATR(hist['high'], hist['low'], hist['close'], timeperiod=context.short_period)[-1]
    position = context.portfolio.positions[security]

    # buy_avg_holding_price	float	多头持仓均价
    if position.buy_quantity >0 and bar_dict[security].last < (position.buy_avg_holding_price - 0.5 *N_long):
        # 多单清仓
        sell_close(security,position.buy_quantity)
        print("long_stop_loss")
    
    # sell_avg_holding_price	float	空头持仓均价
    if position.sell_quantity >0 and bar_dict[security].last > (position.sell_avg_holding_price + 0.5*N_short):
        # 空单清仓
        buy_close(security,position.sell_quantity)
        print("short_stop_loss")

def market_out(context, bar_dict, security):
    position = context.portfolio.positions[security]
    
    if position.buy_quantity >0 :
        if bar_dict[security].last > 1.15*position.buy_avg_holding_price:
            sell_close(security,position.buy_quantity)
            print("long_succeed")
            
    if position.sell_quantity >0:
        if bar_dict[security].last < 0.9*position.sell_avg_holding_price:
            buy_close(security,position.sell_quantity)
            print("short_succeed")

# 回测结果：
# 转自米宽社区
# 多品种商品期货海龟策略，策略运行时间为2017/5/1 到 2017/8/20， 按分钟回测
# 回测收益： 183.481%
# 回测年化收益：3175.906%
# 夏普比率： 3.4070
# 最大回撤： 25.735%
