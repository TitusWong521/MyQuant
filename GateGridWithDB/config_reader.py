# -*- coding=utf-8 -*-
# python37
from configparser import ConfigParser, NoOptionError
from logger import logger

class Config(object):
    def __init__(self, config_file_path):
        self.config = ConfigParser()
        self.config_file_path = config_file_path
        self.load_config()

    def load_config(self):
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
