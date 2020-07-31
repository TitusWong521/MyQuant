from strats.grid.grid import GridStrat
import requests
import time
import base64
from utils.config_reader import Config
from utils.logger import logger
from utils.mailhelper import MailHelper


def oper(per):
    # todo: buy and sell code base on trade depth
    pass

# load config file
cfg = Config()
cfg.set_cfg_path('./cfg/app.config')
# init mail helper
mail_helper = MailHelper(cfg.get('global.mail_name'), base64.b64decode(cfg.get('global.mail_pass')).decode('utf-8'))

# online back test
grid = GridStrat(float(cfg.get('grid.start_value')),
                 float(cfg.get('grid.lowest')),
                 float(cfg.get('grid.highest')),
                 int(cfg.get('grid.parts')),
                 oper,
                 oper,
                 mail_helper,
                 cfg.get('grid.mail_list'),
                 token_name=cfg.get('grid.token', '').upper())
url = r'https://api.gateio.ws/api/v4/spot/tickers?currency_pair=eos_usdt'
while True:
    try:
        time.sleep(int(cfg.get('grid.timespan')))
        if cfg.is_changed:
            grid.update(float(cfg.get('grid.lowest')), float(cfg.get('grid.highest')), int(cfg.get('grid.parts')))
            cfg.is_changed = False
        data = requests.get(url).json()
    except:
        continue
    else:
        prices = [data[0]['highest_bid'], data[0]['highest_bid'], data[0]['lowest_ask']]
        logger.info(prices)
        grid.run_data(prices)
