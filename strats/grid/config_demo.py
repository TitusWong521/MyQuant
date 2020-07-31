from utils.config_reader import Config
import time

cfg = Config()
cfg.set_cfg_path('./app.config')

while True:
    print(cfg.get('app.name'))
    print(cfg.get('app.class', 'nothing'))
    time.sleep(5)


