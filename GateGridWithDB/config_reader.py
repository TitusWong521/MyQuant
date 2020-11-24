# -*- coding=utf-8 -*-
# python37
import os
import threading
from configparser import ConfigParser, NoOptionError
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from logger import logger


class ConfigFileModifyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        cfg = Config()
        cfg.is_changed = True
        cfg.load_config()


class Config(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        self.is_changed = False
        logger.info('正在初始化配置文件...')
        self.config = ConfigParser()

    def __new__(cls, *args, **kwargs):
        if not hasattr(Config, '_instance'):
            with Config._instance_lock:
                if not hasattr(Config, '_instance'):
                    Config._instance = object.__new__(cls)
        return Config._instance

    def _init_config_file_observer(self):
        logger.info('正在设置配置文件监控...')
        event_handler = ConfigFileModifyHandler()
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(self.config_file_path), recursive=False)
        observer.setDaemon(True)
        observer.start()

    def set_cfg_path(self, config_file_path):
        self.config_file_path = config_file_path
        self.load_config()
        self._init_config_file_observer()

    def load_config(self):
        logger.info('正在重新加载配置...')
        self.config.read(self.config_file_path, 'utf-8')

    def get(self, key, default=None):
        """
        获取配置
        :param str key: 格式 [section].[key] 如：app.name
        :param Any default: 默认值
        :return:
        """
        map_key = key.split('.')
        if len(map_key) < 2:
            return default
        section = map_key[0]
        if not self.config.has_section(section):
            return default
        option = '.'.join(map_key[1:])
        try:
            return self.config.get(section, option)
        except NoOptionError:
            return default

    def set_paras(self, paras):
        """
        获取配置
        :param str key: 格式 [section].[key] 如：app.name
        :param value: 要设置的值
        :return:
        """
        for key, value in paras.items():
            map_key = key.split('.')
            if len(map_key) > 1:
                section = map_key[0]
                if self.config.has_section(section):
                    option = '.'.join(map_key[1:])
                    self.config.set(section, option, value)
        try:
            return self.config.write(open(self.config_file_path, 'w'))
        except NoOptionError:
            return ''


if __name__ == '__main__':
    cfg = Config()
    cfg.set_cfg_path('../cfg/app.config')
    print(cfg)
    cfg.set_paras({
        'grid.highest': '3.6',
        'grid.lowest': '2.6',
    })
    print(cfg)
