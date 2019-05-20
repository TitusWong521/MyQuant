import random
from HttpUtils import getSign, doApiRequest, doApiRequestWithApikey

class CoinparkAPI:
    def __init__(self, api_key, api_secret):
        self.__apiKey = api_key
        self.__secretKey = api_secret
        self.info_url = 'https://api.coinpark.cc/v1/mdata'
        self.transfer_url = 'https://api.coinpark.cc/v1/transfer'
        self.order_url = 'https://api.coinpark.cc/v1/orderpending'

    def get_random_int():
        return random.randint(0, 20000)

    # 查询交易对
    def get_pairList(self):
        cmds = [
            {
                'cmd': "api/pairList",
                'body': {}
            }
        ]
        return doApiRequest(self.info_url, cmds)

    # 查询k线
    def get_kline(self, pair, period, size):
        cmds = [
            {
                'cmd': "api/kline",
                'body': {
                    'pair': pair,   # 交易对，如BIX_BTC
                    'period': period,   # k线周期，取值 ['1min', '3min', '5min', '15min', '30min', '1hour', '2hour', '4hour', '6hour', '12hour', 'day', 'week']
                    'size': size    # 要几条，1-1000，不传返回1000
                }
            }
        ]
        return doApiRequest(self.info_url, cmds)

    # 查询全币种市场行情
    def get_marketAll(self):
        cmds = [
            {
                'cmd': "api/marketAll",
                'body': {}
            }
        ]
        return doApiRequest(self.info_url, cmds)

    # 查询单币种市场行情
    def get_market(self, pair):
        cmds = [
            {
                'cmd': "api/market",
                'body': {
                    'pair': pair
                }
            }
        ]
        return doApiRequest(self.info_url, cmds)

    # asks  卖方深度, bids  买方深度
    # 查询市场深度
    def get_depth(self, pair, size):
        cmds = [
            {
                'cmd': "api/depth",
                'body': {
                    'pair': pair,
                    'size': size    # 要几条，1-200，不传返回200
                }
            }
        ]
        return doApiRequest(self.info_url, cmds)

    # side  交易方向，1-买，2-卖
    # 查询成交记录
    def get_deals(self, pair, size):
        cmds = [
            {
                'cmd': "api/deals",
                'body': {
                    'pair': pair,
                    'size': size    # 要几条，1-200，不传返回200
                }
            }
        ]
        return doApiRequest(self.info_url, cmds)

    # 查询市场ticker
    def get_ticker(self, pair):
        cmds = [
            {
                'cmd': "api/ticker",
                'body': {
                    'pair': pair
                }
            }
        ]
        return doApiRequest(self.info_url, cmds)

    # select    
    # 普通账户资产
    def get_assets(self, select):
        cmds = [
            {
                'cmd': "transfer/assets",
                'body': {
                    'select': select    # 可选，1-请求所有币种资产明细，不传-各币种总资产合计
                }
            }
        ]
        return doApiRequestWithApikey(self.transfer_url, cmds, self.__apiKey, self.__secretKey)

    # status    状态,  -2：审核不通过；-1: 用户撤销；0:待审核; 1:审核通过（待发币）;  2: 发币中； 3：发币完成
    # 提现信息
    def get_withdrawInfo(self, id):
        cmds = [
            {
                'cmd': "transfer/withdrawInfo",
                'body': {
                    'id': id    # 提现 id
                }
            }
        ]
        return doApiRequestWithApikey(self.transfer_url, cmds, self.__apiKey, self.__secretKey)

    
    # 返回结果：
    # {
    #     "result": 34,     //返回委托单id
    #     "index": 12345,   //用户自定义随机数
    #     "cmd":"orderpending/trade"
    # }
    # 下单
    def do_trade(self, index, pair, order_side, price, amount, money):
        cmds = [
            {
                'cmd': "orderpending/trade",
                'index': index,
                'body': {
                    'pair': pair,
                    'account_type': 0,   # 账户类型，0-普通账户，1-信用账户
                    'order_type': 2,   # 交易类型，1-市价单，2-限价单
                    'order_side': order_side,   # 交易方向，1-买，2-卖
                    'pay_bix': 1,   # 是否bix抵扣手续费，0-不抵扣，1-抵扣
                    'price':  price,   # 委托价格
                    'amount': amount,   # 委托数量
                    'money': money   # 委托金额
                }
            }
        ]
        return doApiRequestWithApikey(self.order_url, cmds, self.__apiKey, self.__secretKey)

    # 返回结果：
    # {
    #     "result":"撤销中",
    #     "index": 12345,   //用户自定义随机数
    #     "cmd":"orderpending/cancelTrade"
    # }
    # 撤单
    def do_cancelTrade(self, index, orders_id):
        cmds = [
            {
                'cmd': "orderpending/cancelTrade",
                'index': index,
                'body': {
                    'orders_id': orders_id
                }
            }
        ]
        return doApiRequestWithApikey(self.order_url, cmds, self.__apiKey, self.__secretKey)

    # 返回结果：
    # {
    #     "result":{
    #         "count":1,
    #         "page":1,
    #         "items":[
    #             {
    #                 "id":159,
    #                 "createdAt": 1512756997000,
    #                 "account_type":0,                       //账户类型 0-普通账户，1-信用账户
    #                 "coin_symbol":"LTC",                    //交易币种
    #                 "currency_symbol":"BTC",                //定价币种
    #                 "order_side":2,                         //交易方向，1-买，2-卖
    #                 "order_type":2,                         //订单类型，1-市价单，2-限价单
    #                 "price":"0.00900000",                   //委托价格，市价单是0
    #                 "amount":"1.00000000",                  //委托数量，市价买单是0
    #                 "money":"0.00900000",                   //委托金额，市价卖单是0
    #                 "deal_amount":"0.00000000",             //已成交数量
    #                 "deal_percent":"0.00%",                 //成交百分比
    #                 "unexecuted":"0.00000000",              //未成交数量
    #                 "status":1                              //状态，1-待成交，2-部分成交，3-完全成交，4-部分撤销，5-完全撤销，6-待撤销
    #             }
    #         ]
    #     },
    #     "cmd":"orderpending/orderPendingList"
    # }
    # 当前委托
    def get_orderPendingList(self, page, size, pair= '', account_type= '', coin_symbol= '', currency_symbol= '', order_side= ''):
        cmds = [
            {
                'cmd': "orderpending/orderPendingList",
                'body': {
                    'pair': pair,                       # 交易对,兼容参数
                    'account_type': account_type,       # 账户类型，0-普通账户，1-信用账户
                    'page': page,                       # 第几页，从1开始
                    'size': size,                       # 要几条
                    'coin_symbol': coin_symbol,         # 交易币种
                    'currency_symbol': currency_symbol, # 定价币种
                    'order_side': order_side            # 交易方向，1-买，2-卖
                }
            }
        ]
        return doApiRequestWithApikey(self.order_url, cmds, self.__apiKey, self.__secretKey)

    # 返回结果：
    # {
    #     "result":{
    #         "count":1,
    #         "page":1,
    #         "items":[
    #             {
    #                 "id":159,
    #                 "createdAt": 1512756997000,
    #                 "account_type":0,                       //账户类型 0-普通账户，1-信用账户
    #                 "coin_symbol":"LTC",                    //交易币种
    #                 "currency_symbol":"BTC",                //定价币种
    #                 "order_side":2,                         //交易方向，1-买，2-卖
    #                 "order_type":2,                         //订单类型，1-市价单，2-限价单
    #                 "price":"0.00900000",                   //委托价格，市价单是0
    #                 "amount":"1.00000000",                  //委托数量，市价买单是0
    #                 "money":"0.00900000",                   //委托金额，市价卖单是0
    #                 "deal_price":"0.00900000",              //成交均价
    #                 "deal_amount":"1.00000000",             //已成交数量
    #                 "deal_money":"0.00900000",              //已成交金额
    #                 "deal_percent":"100%",                  //成交百分比
    #                 "status":3                              //状态，1-待成交，2-部分成交，3-完全成交，4-部分撤销，5-完全撤销，6-待撤销
    #             }
    #         ]
    #     },
    #     "cmd":"orderpending/pendingHistoryList"
    # }
    # 历史委托
    def get_pendingHistoryList(self, page, size, pair= '', account_type= '', coin_symbol= '', currency_symbol= '', order_side= '', hide_cancel = 1):
        cmds = [
            {
                'cmd': "orderpending/pendingHistoryList",
                'body': {
                    'pair': pair,                       # 交易对,兼容参数
                    'account_type': account_type,       # 账户类型，0-普通账户，1-信用账户
                    'page': page,                       # 第几页，从1开始
                    'size': size,                       # 要几条
                    'coin_symbol': coin_symbol,         # 交易币种
                    'currency_symbol': currency_symbol, # 定价币种
                    'order_side': order_side,           # 交易方向，1-买，2-卖
                    'hide_cancel': hide_cancel          # 隐藏已撤销订单，0-不隐藏，1-隐藏
                }
            }
        ]
        return doApiRequestWithApikey(self.order_url, cmds, self.__apiKey, self.__secretKey)

    # 返回结果：
    # {
    #     "result":{
    #         "id":159,
    #         "createdAt": 1512756997000,
    #         "account_type":0,                       //账户类型 0-普通账户，1-信用账户
    #         "pair":"LTC_BTC",                       //交易对
    #         "coin_symbol":"LTC",                    //交易币种
    #         "currency_symbol":"BTC",                //定价币种
    #         "order_side":2,                         //交易方向，1-买，2-卖
    #         "order_type":2,                         //订单类型，1-市价单，2-限价单
    #         "price":"0.00900000",                   //委托价格，市价单是0
    #         "amount":"1.00000000",                  //委托数量，市价买单是0
    #         "money":"0.00900000",                   //委托金额，市价卖单是0
    #         "deal_amount":"0.00000000",             //已成交数量
    #         "deal_percent":"0.00%",                 //成交百分比
    #         "unexecuted":"0.00000000",              //未成交数量
    #         "status":1                              //状态，1-待成交，2-部分成交，3-完全成交，4-部分撤销，5-完全撤销，6-待撤销
    #     },
    #     "cmd":"orderpending/order"
    # }
    # 委托单详情
    def get_order(self, id):
        cmds = [
            {
                'cmd': "orderpending/order",
                'body': {
                    'id': id   # //委托单id
                }
            }
        ]
        return doApiRequestWithApikey(self.order_url, cmds, self.__apiKey, self.__secretKey)

    # 返回结果：
    # {
    #     "result":{
    #         "count":1,              //记录总数
    #         "page":1,               //当前第几页
    #         "items":[               //记录明细
    #             {
    #                 "id":228,
    #                 "createdAt": 1512756997000,
    #                 "account_type":0,                           //账户类型 0-普通账户，1-信用账户
    #                 "coin_symbol":"LTC",                        //交易币种
    #                 "currency_symbol":"BTC",                    //定价币种
    #                 "order_side":2,                             //交易方向，1-买，2-卖
    #                 "order_type":2,                             //订单类型，1-市价单，2-限价单
    #                 "price":"0.00886500",                       //成交价格
    #                 "amount":"1.00000000",                      //成交量
    #                 "money":"0.00886500",                       //成交额，单位是定价币种
    #                 "fee":0                                     //手续费
    #             }
    #         ]
    #     },
    #     "cmd":"orderpending/orderHistoryList"
    # }
    # 成交明细
    def get_orderHistoryList(self, page, size, pair= '', account_type= '', coin_symbol= '', currency_symbol= '', order_side= ''):
        cmds = [
            {
                'cmd': "orderpending/orderHistoryList",
                'body': {
                    'pair': pair,                       # 交易对,兼容参数
                    'account_type': account_type,       # 账户类型，0-普通账户，1-信用账户
                    'page': page,                       # 第几页，从1开始
                    'size': size,                       # 要几条
                    'coin_symbol': coin_symbol,         # 交易币种
                    'currency_symbol': currency_symbol, # 定价币种
                    'order_side': order_side            # 交易方向，1-买，2-卖
                }
            }
        ]
        return doApiRequestWithApikey(self.order_url, cmds, self.__apiKey, self.__secretKey)