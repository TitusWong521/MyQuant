from strats.grid.grid import GridStrat
from strats.grid.data_loader import DataLoader
import requests
import time
import base64
import traceback
from utils.config_reader import Config
from utils.logger import logger
from utils.mailhelper import MailHelper


def oper(per, per1):
    # todo: buy and sell code base on trade depth
    pass

# load config file
cfg = Config()
cfg.set_cfg_path('./cfg/app.config')
# init mail helper
mail_helper = MailHelper(cfg.get('global.mail_name'), base64.b64decode(cfg.get('global.mail_pass')[3:-3]).decode('utf-8'))
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
grid = GridStrat(float(cfg.get('grid.start_value')),
                 float(cfg.get('grid.lowest')),
                 float(cfg.get('grid.highest')),
                 int(cfg.get('grid.parts')),
                 oper,
                 oper,
                 token_name=cfg.get('grid.token', '').upper())
while True:
    try:
        time.sleep(int(cfg.get('grid.timespan')))
        if cfg.is_changed:
            mail_subject, mail_content = grid.update(float(cfg.get('grid.lowest')), float(cfg.get('grid.highest')),
                                                     int(cfg.get('grid.parts')))
            cfg.is_changed = False
            if int(cfg.get('grid.mail_reminder')):
                mail_helper.sendmail(cfg.get('grid.mail_list'), mail_subject, mail_content)
        data = data_loader.get_data(cfg.get('grid.platform'), cfg.get('grid.token'))
    except:
        logger.error(traceback.format_exc())
        continue
    else:
        flag, mail = grid.run_data(data)
        if int(cfg.get('grid.mail_reminder')) and flag:
            mail_helper.sendmail(cfg.get('grid.mail_list'), mail[0], mail[1])

