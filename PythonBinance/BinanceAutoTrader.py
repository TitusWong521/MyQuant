# -*- coding=utf-8 -*-
# python35
from data_handler import DataHandler
import traceback
import logging
import time


def get_day():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


logger = logging.getLogger('BinanceAutoTrader')
logger.setLevel(level= logging.INFO)
handler = logging.FileHandler(get_day() + '.log', encoding="UTF-8")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - LINE %(lineno)-d: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == '__main__':
    handler = DataHandler('./config_user.txt', logger)
    while True:
        try:
            trade_balance, target_balance = handler.get_balance()
            best_buy, best_sell = handler.get_best_order_price()
            handler.send_buy_order(target_balance, best_buy)
            handler.send_sell_order(trade_balance, best_sell)
        except Exception as ex:
            ex_message = traceback.format_exc()
            logger.error(ex_message)
            continue
        finally:
            time.sleep(1)


