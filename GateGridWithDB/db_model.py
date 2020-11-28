# -*- coding=utf-8 -*-
# python37
import os
from peewee import *
import time

db = SqliteDatabase('griddata.db')

class BaseModel(Model):
    class Meta:
        database = db

class account_status(BaseModel):
    timestamp = CharField(null=False)
    usdt = CharField(null=False)
    token_name = CharField(null=False)
    token_count = CharField(null=False)
    cur_price = CharField(null=False)
    balance = CharField(null=False)

class oper_his(BaseModel):
    timestamp = CharField(null=False)
    type = CharField(null=False)
    cur_price = CharField(null=False)
    balance = CharField(null=False)
    token_name = CharField(null=False)
    trade_count = CharField(null=True)
    grid_lowest = CharField(null=True)
    grid_highest = CharField(null=True)
    grid_parts = CharField(null=True)

def create_db():
    if not os.path.isfile('griddata.db'):
        db.connect()
        db.create_tables([account_status, oper_his])
        time.sleep(5)

def insert(type, paras):
    if type == 'account_status':
        status = account_status.create(
            timestamp=paras[0],
            usdt=paras[1],
            token_name=paras[2],
            token_count=paras[3],
            cur_price=paras[4],
            balance=paras[5],
        )
        status.save()
    elif type == 'oper_his':
        oper = oper_his.create(
            timestamp=paras[0],
            type=paras[1],
            cur_price=paras[2],
            balance=paras[3],
            token_name=paras[4],
            trade_count=paras[5],
            grid_lowest=paras[6],
            grid_highest=paras[7],
            grid_parts=paras[8],
        )
        oper.save()
    else:
        pass
