#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8

'''
Provide user specific data and interact with gate.io
'''
from gateAPI import GateIO
import json

## 填写 apiKey APISECRET
apiKey = '49FC12E2-D3BC-4067-BC7F-C0FD77C9ABBB'
secretKey = '5ab4c52fb90df2cce7c917db507c4286afb5b33bc15761c509b7cd5ce972e5ca'
## Provide constants
API_QUERY_URL = 'data.gateio.io'
API_TRADE_URL = 'api.gateio.io'
## Create a gate class instance
gate_query = GateIO(API_QUERY_URL, apiKey, secretKey)
gate_trade = GateIO(API_TRADE_URL, apiKey, secretKey)
# print(gate_query.orderBook('eos_usdt'))
# with open('temp.txt', 'w+') as f:
#     f.write(str(gate_query.marketlist()))
print(gate_query.marketlist()['data'][0:5])
# Trading Pairs
# print(gate_query.pairs())

## Below, use general methods that query the exchange

#  Market Info
# print(gate_query.marketinfo())

# Market Details
# print(gate_query.marketlist())

# Ticker
# print(gate_query.ticker('eos_usdt'))

# Tickers
# print(gate_query.tickers())

# OrderBook
# print(gate_query.orderBook('eos_usdt'))

# Depth
# print(gate_query.orderBooks())

# orders
# print(gate_query.openOrders())

# Candle
# print(gate_query.candle('eos_usdt', 5, 0.1))

## Below, use methods that make use of the users keys

# Ticker
# print(gate_query.ticker('btc_usdt'))

# Market depth of pair
# print(gate_query.orderBook('btc_usdt'))

# Trade History
# print(gate_query.tradeHistory('gtc_usdt'))

# Get account fund balances
# print(gate_trade.balances())

# get new address
# print(gate_trade.depositAddres('btc'))

# get deposit withdrawal history
# print(gate_trade.depositsWithdrawals('1469092370', '1569092370'))

# Place order buy
# print(gate_trade.buy('etc_usdt', '0.001', '123'))

# Place order sell
# print(gate_trade.sell('etc_btc', '0.001', '123'))

# Cancel order
# print(gate_trade.cancelOrder('267040896', 'etc_btc'))

# Cancel all orders
# print(gate_trade.cancelAllOrders('0', 'etc_btc'))

# Get order status
# print(gate_trade.getOrder('267040896', 'eth_btc'))

# Get my last 24h trades
# print(gate_trade.mytradeHistory('etc_btc', '267040896'))

# withdraw
# print(gate_trade.withdraw('btc', '88', btcAddress))