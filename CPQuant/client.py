from CoinparkAPI import CoinparkAPI

api_key = 'cc8cb5229056423cfdc329839e026d6bff37e651'
api_secret = '7f0333304c7fa816572a6b9767ef3a9e662efac3'
api = CoinparkAPI(api_key, api_secret)

# print(api.get_pairList())
# print(api.get_kline('BIX_ETH', '15min', 50))
# print(api.get_marketAll())
# print(api.get_market('BIX_ETH'))
# print(api.get_depth('BIX_ETH', 20))
# print(api.get_deals('BIX_ETH', 20))
# print(api.get_ticker('BIX_ETH'))
print(api.get_assets(1))
# print(api.get_orderPendingList(1, 10))
# print(api.get_orderPendingList(1, 10))
# print(api.get_orderHistoryList(1, 10))