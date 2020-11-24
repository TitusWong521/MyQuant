# -*- coding=utf-8 -*-
# python37
import dill
from grid_strat import GridStrat
from data_loader import DataLoader
import time
import requests
import base64
import traceback
from config_reader import Config
from logger import logger
from apscheduler.schedulers.background import BackgroundScheduler
from db_model import create_db, insert

def get_time():
    return time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))

def trade_reminder(reminds, mode=None):
    url = r'https://sc.ftqq.com/SCU108142Te3389e6c15b3491545b65780e559503d5f27661e050c0.send?text={}&desp={}'
    text = '【网格策略】触发新交易' if mode == None else f'【网格策略】{mode}'
    desp = '[{}]: {}'.format(get_time(), reminds)
    requests.get(url.format(text, desp))

def run_grid():
    global data_loader
    global grid
    global cfg
    try:
        if cfg.is_changed:
            reminds = grid.update(float(cfg.get('grid.lowest')), float(cfg.get('grid.highest')),
                                                     int(cfg.get('grid.parts')))
            cfg.is_changed = False
        data = data_loader.get_data(cfg.get('grid.platform'), cfg.get('grid.token'))
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

def save_grid_status():
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

if __name__ == '__main__':
    # load config file
    cfg = Config()
    cfg.set_cfg_path('./app.config')

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
                         env=cfg.get('global.env', '').upper())
    grid.trade = data_loader.trade

    create_db()

    scheduler = BackgroundScheduler()
    scheduler.add_job(run_grid, trigger='interval', seconds=int(cfg.get('grid.timespan')),
                      id='run_grid', replace_existing=True)
    scheduler.start()

    while True:
        save_grid_status()
        time.sleep(int(cfg.get('save.timespan')))
