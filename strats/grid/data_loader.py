# -*- coding: utf-8 -*-
import requests

huobi_access_key = ''
huobi_secret_key = ''
gate_access_key = ''
gate_secret_key = ''

huobi_market_api = 'https://api.huobi.pro/market/'
huobi_account_api = 'https://api.huobi.pro/v1/account/'
huobi_order_api = 'https://api.huobi.pro//v1/order/'


print(requests.get('https://api.huobi.pro/market/history/kline?symbol=btcusdt&size=10&interval=5min').json())

