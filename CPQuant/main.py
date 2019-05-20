import json
import time
import traceback
from CoinparkAPI import CoinparkAPI

def get_all_assets():
    # 查看账户资产 ETH USDT
    assets_data = json.loads(api.get_assets(1))
    assets = assets_data['result'][0]['result']['assets_list']
    # print(assets)
    eth_count = [coin['balance'] for coin in assets if coin['coin_symbol'] == 'ETH'][0]
    usdt_count = [coin['balance'] for coin in assets if coin['coin_symbol'] == 'USDT'][0]
    print('当前账户内的ETH余额为 %f, USDT余额为 %f' % (eth_count, usdt_count))
    return eth_count, usdt_count

def get_price(coin_pair):
    # 查看当前深度信息
    depth_data = json.loads(api.get_depth(coin_pair, 200))
    bids_data = depth_data['result'][0]['result']['bids']
    print('当前买一价为 %s' % bids_data[0]['price'])
    asks_data = depth_data['result'][0]['result']['asks']
    print('当前卖一价为 %s' % asks_data[0]['price'])
    bid_first = bids_data[0]['price']
    ask_first = asks_data[0]['price']
    price = (float(bid_first) + float(ask_first)) / 2.0
    print('现在以 %.4f 的价格下单' % price)
    return price

if __name__ == '__main__':
    api_key = 'cc8cb5229056423cfdc329839e026d6bff37e651'
    api_secret = '7f0333304c7fa816572a6b9767ef3a9e662efac3'
    api = CoinparkAPI(api_key, api_secret)
    coin_pair = 'ETH_USDT'
    trade_count = 0.0
    while True:
        try:
            eth_count, usdt_count = get_all_assets()
            price = get_price(coin_pair)
            
            # 准备卖出
            amount = 0.0
            order_id = 0
            if float(usdt_count / price) < eth_count:
                amount = float(usdt_count / price)
            else:
                amount = eth_count
            random_index = api.get_random_int()
            
            # 卖出
            sell_data = json.loads(api.do_trade(random_index, pair, 2, price, amount, price * amount))
            # 查看卖出单是否成功下单
            if random_index == int(sell_data['result'][0]['index']):
                order_id = int(sell_data['result'][0]['result'])
            # 查询卖出单详细信息
            order_data = json.loads(api.get_order(order_id))
            
            # 买入
            buy_data = {}
            if order_data['result'][0]['result']['status'] == '1':
                random_index = api.get_random_int()
                buy_data = json.loads(api.do_trade(random_index, pair, 1, price, amount, price * amount))
                # 查看买入单是否成功下单
                if random_index == int(buy_data['result'][0]['index']):
                    order_id = int(buy_data['result'][0]['result'])
                # 查询卖出单详细信息
                order_data = json.loads(api.get_order(order_id))
            elif order_data['result'][0]['result']['status'] == '2':
                random_index = api.get_random_int()
                _price = float(order_data['result'][0]['result']['price'])
                _amount = float(order_data['result'][0]['result']['unexecuted'])
                buy_data = json.loads(api.do_trade(random_index, pair, 1, _price, _amount, _price * _amount))
                # 查看买入单是否成功下单
                if random_index == int(buy_data['result'][0]['index']):
                    order_id = int(buy_data['result'][0]['result'])
                # 查询卖出单详细信息
                order_data = json.loads(api.get_order(order_id))
            if order_data['result'][0]['result']['status'] == '1':
                _price = float(order_data['result'][0]['result']['price'])
                _deal_amount = float(order_data['result'][0]['result']['deal_amount'])
                trade_count += _price * _deal_amount
                print('此次交易成功完成! 2分钟后会进行下一次交易，请稍等...')
        except Exception as ex:
            print('程序出错, 请检查!\n错误信息为: %s\n 详细信息为: %s' % (str(ex.args), str(traceback.format_exc())))
        finally:

            time.sleep(120)
