# -*- coding=utf-8 -*-
# python37
from flask import Flask, url_for, redirect
from db_model import *
import time
import matplotlib.pyplot as plt
from matplotlib.pyplot import annotate

app = Flask('GridInfo')
host = '119.3.78.178'
port = 8888
# app = Flask('GridInfo', static_folder='static')

@app.route('/accountinfo')
def accountinfo():
    init_status = account_status.get(account_status.id == 1)
    last_status = account_status.get(account_status.id == account_status.select().count())
    earn_ratio = 100 * (float(last_status.balance) - float(init_status.balance)) / float(init_status.balance)
    percent = 100 * (float(last_status.balance) - float(last_status.usdt)) / float(last_status.balance)
    last_time = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(int(last_status.timestamp)))
    status_desc = [
        '账户初始资产为:\t{:.4f}\t'.format(float(init_status.balance)),
        '{}时资产为:\t{:.4f}'.format(last_time, float(last_status.balance)),
        '当前收益率为:\t{:.2f} %'.format(earn_ratio),
        '持仓比例为:\t{:.2f} %'.format(percent),
        '持仓详情: \t{:.4f} usdt\t{:.4f} {} [last price: {:.4f}]'.format(float(last_status.usdt),
                                                                     float(last_status.token_count),
                                                                     last_status.token_name,
                                                                     float(last_status.cur_price))
    ]
    return '<br>'.join(status_desc)

@app.route('/operinfo')
def operinfo():
    last_oper = oper_his.get(oper_his.id == oper_his.select().count())
    last_time = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(int(last_oper.timestamp)))
    oper_type = '买入' if last_oper.type == 'buy' else '卖出'
    oper_desc = [
        f'最近一次操作是在: {last_time}',
        f'在{last_oper.token_name}价格为{last_oper.cur_price} USDT时，{oper_type} {last_oper.trade_count} USDT',
        f'交易结束时，账户资产约为: {"%.4f" % float(last_oper.balance)} USDT'
    ]
    return '<br>'.join(oper_desc)


@app.route('/gridchart')
def gridchart():
    account_datas = account_status.filter(token_name='eos')
    times = [time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(int(account_data.timestamp)))
             for account_data in account_datas]
    indexes = [int(account_data.id) for account_data in account_datas]
    prices = [float(account_data.cur_price) for account_data in account_datas]
    norm_prices = [price/max(prices) for price in prices]
    min_price_index = norm_prices.index(min(norm_prices))
    max_price_index = norm_prices.index(max(norm_prices))
    balances = [float(account_data.balance) for account_data in account_datas]
    norm_balances = [balance / max(balances) for balance in balances]
    min_balance_index = norm_balances.index(min(norm_balances))
    max_balance_index = norm_balances.index(max(norm_balances))
    fig, ax = plt.subplots(1, 1)
    plt.plot(indexes, norm_prices, c='blue', label='EOS')
    annotate(f"{'%.4f' % prices[0]}",
             xy=(0, norm_prices[0]), xycoords='data',
             xytext=(15, -20), textcoords='offset points', fontsize=10, color='purple',
             arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    annotate(f"{'%.4f' % prices[min_price_index]}",
             xy=(min_price_index, norm_prices[min_price_index]), xycoords='data',
             xytext=(-50, 15), textcoords='offset points', fontsize=10, color='purple',
             arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    annotate(f"{'%.4f' % prices[-1]}",
             xy=(len(norm_prices) - 1, norm_prices[-1]), xycoords='data',
             xytext=(5, 30), textcoords='offset points', fontsize=10, color='purple',
             arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    if max_price_index not in [0, min_price_index, len(norm_prices) - 1]:
        annotate(f"{'%.4f' % prices[max_price_index]}",
                 xy=(max_price_index, norm_prices[max_price_index]), xycoords='data',
                 xytext=(0, 30), textcoords='offset points', fontsize=10, color='purple',
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    plt.plot(indexes, norm_balances, c='red', label='GRID')
    annotate(f"{'%.4f' % balances[0]}",
             xy=(0, norm_balances[0]), xycoords='data',
             xytext=(15, -45), textcoords='offset points', fontsize=10, color='purple',
             arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    annotate(f"{'%.4f' % balances[min_balance_index]}",
             xy=(min_balance_index, norm_balances[min_balance_index]), xycoords='data',
             xytext=(-50, 15), textcoords='offset points', fontsize=10, color='purple',
             arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    annotate(f"{'%.4f' % balances[-1]}",
             xy=(len(norm_balances) - 1, norm_balances[-1]), xycoords='data',
             xytext=(5, 30), textcoords='offset points', fontsize=10, color='purple',
             arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    if max_price_index not in [0, min_price_index, len(norm_prices) - 1]:
        annotate(f"{'%.4f' % balances[max_price_index]}",
                 xy=(max_price_index, norm_balances[max_price_index]), xycoords='data',
                 xytext=(0, 30), textcoords='offset points', fontsize=10, color='purple',
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
    # plt.plot(prices, c='blue', label='EOS')
    # plt.plot(balances, c='red', label='GRID')
    plt.legend(loc='best')
    plt.title(f'Grid Status Chart({times[0]} ~ {times[-1]})')
    plt.savefig('./static/gridchart.png')
    # return redirect(url_for('static', filename='gridchart.png'))
    return f"http://{host}:{port}{url_for('static', filename='gridchart.png')}"

if __name__ == '__main__':
    app.run('0.0.0.0', port=port, debug=True)
