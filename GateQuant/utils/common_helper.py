#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
import time
import itchat

def log(coin, content):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    filename = coin + '-' + time.strftime('%Y%m%d', time.localtime(time.time()))
    content = timestamp + '\t' + content + '\n'
    print(content)
    with open('.\\Logs\\' + filename + '.log', 'a+') as f:
        f.write(content)
    return content

def get_conf(conf_item):
    with open('.\\app.conf', 'r') as f:
        content = f.readlines()
    for line in content:
        if conf_item in line:
            # print(line.split('=')[1].split('$$')[0])
            return line.split('=')[1].split('$$')[0]

def print_cur_status(total_pool, dic_total_coin):
    output = '当前持仓为: \n'
    temp = ''
    for key in dic_total_coin:
        temp += '%s: %.6f 个\t' % (key, dic_total_coin[key])
    return output + temp