# -*- coding=utf-8 -*-
# python37
from binance.client import Client
from API.BinanceAPI import Binance

if __name__ == '__main__':
    api_key = 'FMIHF3i4y45kBpkkEArIFZv5gHzM8vrG7g5I5zZcOJCeOt2A7g4byWYvtiNP9pia'
    api_secret = 'gLbL8hrwwd3AuxbnRHVnkpCFNiUNQcmxLHmEcXrRfrwP8OamRgudZVwy1bK7n3kh'
    binance = Binance(api_key, api_secret)
    print(binance.depth('IOSTBTC'))
    # print(binance.test_order())
    # print(binance.open_orders('IOSTBTC'))


