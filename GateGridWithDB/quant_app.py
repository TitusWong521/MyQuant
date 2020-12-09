# -*- coding=utf-8 -*-
# python37
import dill
import random
from grid_strat import GridStrat
from data_loader import DataLoader
import time
import requests
import base64
import traceback
from config_reader import Config
from logger import logger
# from db_model import create_db, insert
from db_model import insert
from apscheduler.schedulers.background import BackgroundScheduler
import urllib3

def get_time():
    return time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))


def trade_reminder(reminds, mode=None):
    url = r'https://sc.ftqq.com/SCU108142Te3389e6c15b3491545b65780e559503d5f27661e050c0.send?text={}&desp={}'
    text = '【网格策略】触发新交易' if mode == None else f'【网格策略】{mode}'
    desp = '[{}]: {}'.format(get_time(), reminds)
    requests.get(url.format(text, desp))


def run_grid():
    rand = random.randint(0, 10000)
    logger.info(f'Function <run_grid-{rand}> is running...')
    global data_loader
    global grid
    global cfg
    try:
        cfg_new = Config('./app.config')
        if cfg.get('grid.lowest') != cfg_new.get('grid.lowest') \
                or cfg.get('grid.highest') != cfg_new.get('grid.highest') \
                or cfg.get('grid.parts') != cfg_new.get('grid.parts'):
            cfg = cfg_new
            logger.info("网格参数有更新，即将更新网格程序")
            reminds = grid.update(float(cfg.get('grid.lowest')), float(cfg.get('grid.highest')),
                                  int(cfg.get('grid.parts')))
            trade_reminder(reminds, '网格参数更新')
        data = data_loader.get_data(cfg.get('grid.platform'), cfg.get('grid.token'))
    except urllib3.exceptions.ReadTimeoutError:
        pass
    except urllib3.exceptions.MaxRetryError:
        pass
    except:
        logger.error(traceback.format_exc())
        trade_reminder(traceback.format_exc(), '出错信息')
    else:
        flag, reminds = grid.run_data(data)
        if flag:
            grid.trade = None
            dill.dump(grid, open(grid_cache, 'wb'))
            grid.trade = data_loader.trade
            trade_reminder(reminds)
    logger.info(f'Function <run_grid-{rand}> is done.')


def save_grid_status():
    rand = random.randint(0, 10000)
    logger.info(f'Function <save_grid_status-{rand}> is running...')
    global data_loader
    global grid
    global cfg
    usdt = grid.money
    token_name = cfg.get('grid.token')
    token_count = grid.token
    cur_price = data_loader.get_data(cfg.get('grid.platform'), cfg.get('grid.token'))[0]
    balance = usdt + token_count * float(cur_price)
    paras = [str(item) for item in [int(time.time()), usdt, token_name, token_count, cur_price, balance]]
    insert('account_status', paras)
    logger.info(f'Function <save_grid_status-{rand}> is done.')


# load config file
cfg = Config('./app.config')

# init data loader
api_keys = {
    'gateio': [
        base64.b64decode(cfg.get('global.gateio_api_key')[3:-3]).decode('utf-8'),
        base64.b64decode(cfg.get('global.gateio_api_secret')[3:-3]).decode('utf-8')
    ],
    'huobipro': [
        base64.b64decode(cfg.get('global.huobipro_api_key')[3:-3]).decode('utf-8'),
        base64.b64decode(cfg.get('global.huobipro_api_secret')[3:-3]).decode('utf-8')
    ],
}
data_loader = DataLoader(api_keys)
# online back test
grid_cache = './grid_cache.pkl'
try:
    grid = dill.load(open(grid_cache, 'rb'))
except:
    logger.error(traceback.format_exc())
    trade_reminder(traceback.format_exc(), '出错信息')
    grid = GridStrat(float(cfg.get('grid.start_value')),
                     float(cfg.get('grid.lowest')),
                     float(cfg.get('grid.highest')),
                     int(cfg.get('grid.parts')),
                     data_loader.trade,
                     cfg.get('grid.platform').lower(),
                     cfg.get('grid.token', '').lower(),
                     cfg.get('grid.last_trade_price', '0.0'),
                     env=cfg.get('global.env', '').upper())
grid.trade = data_loader.trade

save_grid_status()

scheduler = BackgroundScheduler()
scheduler.add_job(run_grid, trigger='interval', seconds=int(cfg.get('grid.timespan')), id='run_grid',
                  replace_existing=True)
scheduler.add_job(save_grid_status, trigger='interval', seconds=int(cfg.get('save.timespan')), id='save_grid_status',
                  replace_existing=True)
scheduler.start()
trade_reminder('网格已经开始运行！', '开始运行提示')

while True:
    pass
