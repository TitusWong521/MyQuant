class GridStrat():
    def __init__(self, start_value, lowest, highest, parts, buy, sell):
        self.start_value = float(start_value)
        self.money = float(start_value)
        self.token = 0.0
        self.last_price = None
        self.lowest = float(lowest)
        self.highest = float(highest)
        self.parts = parts
        self.buy = buy
        self.sell = sell
        self.init_grid()

    def __str__(self):
        percent = self.percent_levels[self.last_price_index] * 100 if self.last_price_index != None else 0.00
        assets = self.money + self.token * self.last_price
        earn_ratio = 100 * (assets - self.start_value) / self.start_value
        return '账户初始资产为:\t{:.4f}\t当前资产为:\t{:.4f}\t当前收益率为:\t{:.2f} %\n' \
               '持仓比例为:\t{:.2f} %\n持仓详情: \t{:.4f} USDT\t{:.4f} TOKEN [last price: {:.4f}]'\
            .format(self.start_value, assets, earn_ratio, percent, self.money, self.token, self.last_price)

    def init_grid(self):
        price_part_value = (self.highest - self.lowest) / self.parts
        percent_part_value = 1 / self.parts
        self.price_levels = [round(self.highest - index * price_part_value, 4) for index in range(self.parts + 1)]
        self.percent_levels = [round(0 + index * percent_part_value, 4) for index in range(self.parts + 1)]
        self.price_levels[-1] = self.lowest
        self.percent_levels[-1] = 1.0000
        self.last_price_index = None

    def update(self, highest, lowest, parts):
        self.highest = highest
        self.lowest = lowest
        self.parts = parts
        self.init_grid()

    def run_data(self, data):
        self.run_next(data)

    def run_datas(self, datas, dates=None):
        if dates:
            for data, date in zip(datas, dates):
                self.run_next(data, date)
        else:
            for data in datas:
                self.run_next(data)

    def run_next(self, value, date=''):
        value = float(value)
        self.last_price = value
        if self.last_price_index == None:
            for i in range(len(self.price_levels)):
                if value > self.price_levels[i]:
                    self.last_price_index = i
                    self.order_target_percent(value, target=self.percent_levels[self.last_price_index], date=date)
                    return
        else:
            signal = False
            cur_percent = self.percent_levels[self.last_price_index]
            while True:
                upper = None
                lower = None
                if self.last_price_index > 0:
                    upper = self.price_levels[self.last_price_index - 1]
                if self.last_price_index < len(self.price_levels) - 1:
                    lower = self.price_levels[self.last_price_index + 1]
                # 还不是最轻仓，继续涨，就再卖一档
                if upper != None and value > upper:
                    self.last_price_index = self.last_price_index - 1
                    signal = True
                    continue
                # 还不是最重仓，继续跌，再买一档
                if lower != None and value < lower:
                    self.last_price_index = self.last_price_index + 1
                    signal = True
                    continue
                break
            if signal:
                self.order_target_percent(value, target=self.percent_levels[self.last_price_index] - cur_percent, date=date)

    def order_target_percent(self, value, target, date=''):
        if target > 0:
            self.buy(target * self.start_value)
            print('{} -> buy {:.4f} USDT on price [{:.4f}]'.format(date, target * self.start_value, value))
            self.money -= target * self.start_value
            self.token += (target * self.start_value) / value
        elif target < 0:
            self.sell(0 - target * self.start_value)
            print('{} -> sell {:.4f} USDT on price [{:.4f}]'.format(date, 0 - target * self.start_value, value))
            self.money -= target * self.start_value
            self.token += (target * self.start_value) / value
        else:
            print('target=0, do nothing.')


def oper(per):
    pass

if __name__ == '__main__':
    grid = GridStrat(1000.0, 15.0, 25.0, 10, oper, oper)
    with open('binance-segment.csv', 'r') as f:
        lines = f.readlines()
    datas = [line.strip().split(',')[4] for line in lines[1:] if len(line.strip()) > 0]
    dates = [line.strip().split(',')[0] for line in lines[1:] if len(line.strip()) > 0]
    grid.run_datas(datas, dates)
    print(grid)