# -*- coding: utf-8 -*-
import logging
from logging import handlers
import os


logger = logging.getLogger('MyQuant')
logger.setLevel(logging.DEBUG)

if not os.path.isdir('./logs/'):
    os.mkdir('./logs/')

th = handlers.TimedRotatingFileHandler(filename='./logs/log', when='D', backupCount=30,
                                       encoding='utf-8')

format = '%(asctime)s [%(module)s] %(levelname)s [%(lineno)d] %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'
format_str = logging.Formatter(format, datefmt)
th.suffix = "%Y-%m-%d.log"
th.setFormatter(format_str)
th.setLevel(logging.INFO)
logger.addHandler(th)
