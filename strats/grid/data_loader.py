# -*- coding: utf-8 -*-
from __future__ import print_function
import gate_api


class DataLoader():
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.init_apis()

    def init_apis(self):
        for exchange in self.api_keys:
            if exchange == 'gateio':
                configuration = gate_api.Configuration()
                configuration.key = self.api_keys['gateio'][0]
                configuration.secret = self.api_keys['gateio'][1]
                self.gateio_spot_api = gate_api.SpotApi(gate_api.ApiClient(configuration))
            elif exchange == 'huobipro':
                pass
            else:
                raise Exception('Unsupported exchange!')

    def get_data(self, exchange, token):
        if exchange == 'gateio':
            return self._get_gateio_data(token)
        elif exchange == 'huobipro':
            return self._get_huobipro_data(token)
        else:
            raise Exception('Unsupported exchange!')

    def _get_gateio_data(self, token):
        close = self.gateio_spot_api.list_tickers(currency_pair='{}_usdt'.format(token.lower()))[0].last
        order_book = self.gateio_spot_api.list_order_book(currency_pair='{}_usdt'.format(token.lower()))
        depth = order_book.asks, order_book.bids
        return close, depth

    def _get_huobipro_data(self, token):
        # huobi_market_api = 'https://api.huobi.pro/market/'
        # huobi_account_api = 'https://api-aws.huobi.pro/v1/account/'
        # huobi_order_api = 'https://api-aws.huobi.pro//v1/order/'
        #
        # headers = {
        #     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        #     'accept-encoding': 'gzip, deflate, br',
        #     'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        #     'sec-fetch-mode': 'navigate',
        #     'sec-fetch-site': 'none',
        #     'sec-fetch-user': '?1',
        #     'upgrade-insecure-requests': '1',
        #     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36',
        # }
        #
        # close_api = huobi_market_api + 'trade?symbol={}usdt'.format(token.lower())
        # depth_api = huobi_market_api + 'depth?symbol={}usdt&type=step0&depth=10'.format(token.lower())
        # close = requests.get(close_api, headers=headers).json()['tick']['data'][0]['price']
        # depth = requests.get(depth_api, headers=headers).json()['tick']
        # return close, depth
        pass

