import asyncio
import os
import dill
from typing import Optional, Union
from wechaty import Wechaty, Contact
from wechaty.user import Message, Room
from strat.grid_strat import GridStrat
from strat.data_loader import DataLoader
import time
import requests
import base64
import traceback
from utils.config_reader import Config
from utils.logger import logger
from utils.mail_helper import MailHelper
from apscheduler.schedulers.asyncio import AsyncIOScheduler

os.environ['WECHATY_PUPPET']= 'wechaty-puppet-hostie'
os.environ['WECHATY_PUPPET_HOSTIE_TOKEN'] = 'puppet_donut_25e31edab29faf7d'
url = r'https://sc.ftqq.com/SCU108142Te3389e6c15b3491545b65780e559503d5f27661e050c0.send?text={}&desp={}'
bot: Optional[Wechaty] = None
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
grid_cache = './utils/grid_cache.pkl'
try:
    grid = dill.load(open(grid_cache, 'rb'))
except:
    logger.error(traceback.format_exc())
    grid = GridStrat(float(cfg.get('grid.start_value')),
                     float(cfg.get('grid.lowest')),
                     float(cfg.get('grid.highest')),
                     int(cfg.get('grid.parts')),
                     data_loader.trade,
                     cfg.get('grid.platform').lower(),
                     cfg.get('grid.token', '').lower())
grid.trade = data_loader.trade

def get_time():
    return time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time()))

async def on_scan(status, qrcode, timestamp):
    print('status: {}'.format(status))
    print('qrcode: {}'.format(qrcode))
    print('timestamp: {}'.format(timestamp))
    prompt = 'Scan QR Code to login: {}\nhttps://wechaty.github.io/qrcode/{}'.format(status, qrcode)
    text = 'Wechat scaning...'
    desp = '[{}]: {}'.format(get_time(), prompt)
    requests.get(url.format(text, desp))

async def on_login(user):
    prompt = 'User {} logged in.'.format(user)
    text = 'Wechaty logged in'
    desp = '[{}]: {}'.format(get_time(), prompt)
    requests.get(url.format(text, desp))

async def on_logout(user):
    prompt = 'User {} logged out'.format(user)
    text = 'Wechaty abnormal logout!'
    desp = '[{}]: {}, pls re-login asap.'.format(get_time(), prompt)
    requests.get(url.format(text, desp))

async def on_error(error):
    text = 'Wechaty error!'
    desp = '[{}]: Wechaty error - [{}], pls check.'.format(get_time(), str(error))
    requests.get(url.format(text, desp))

async def on_room_join(room, inviteeList, inviter, timestamp):
    if room.payload.topic in ['ChatOps - Donut', '量化动态播报']:
        conversation: Union[Room, Contact] = room
        for invitee in inviteeList:
            await conversation.ready()
            await conversation.say('欢迎<{}>进群，感谢<{}>的邀请！'.format(invitee.payload.name, inviter.payload.name))
            target_friend = bot.Contact.load('wzhwno1')
            await target_friend.say('<{}>已于<{}>被<{}>邀请进入群聊<{}>！'
                                    .format(invitee.payload.name, timestamp, inviter.payload.name, room.payload.topic))

async def on_room_leave(room, removeeList, remover, timestamp):
    print('room: {}'.format(str(room)))
    print('removeeList: {}'.format(str(removeeList)))
    print('remover: {}'.format(str(remover)))
    print('timestamp: {}'.format(str(timestamp)))
    if room.payload.topic in ['ChatOps - Donut', '量化动态播报']:
        conversation: Union[Room, Contact] = room
        for removee in removeeList:
            await conversation.ready()
            await conversation.say('<{}>已退群，期待下次再见！'.format(removee.payload.name))
            target_friend = bot.Contact.load('wzhwno1')
            await target_friend.say('<{}>已于<{}>退出群聊<{}>！'
                                    .format(removee.payload.name, timestamp, room.payload.topic))

async def on_message(msg: Message):
    from_contact = msg.talker()
    text = msg.text()
    room = msg.room()
    if text == '#ding':
        conversation: Union[
            Room, Contact] = from_contact if room is None else room
        await conversation.ready()
        await conversation.say('dong')

async def wechat():
    global bot
    bot = Wechaty()
    bot.on('scan', on_scan)
    bot.on('login', on_login)
    bot.on('message', on_message)
    bot.on('room-join', on_room_join)
    bot.on('room-leave', on_room_leave)
    bot.on('logout', on_logout)
    bot.on('error', on_error)
    await bot.start()

async def run_grid():
    try:
        if cfg.is_changed:
            mail_content = grid.update(float(cfg.get('grid.lowest')), float(cfg.get('grid.highest')),
                                                     int(cfg.get('grid.parts')))
            cfg.is_changed = False
            if int(cfg.get('grid.mail_reminder')):
                mail_helper.sendmail(cfg.get('grid.mail_list'), '[GRID SCRIPT]: Strat cfg update!', mail_content)
            if int(cfg.get('grid.wechat_reminder')):
                target_friend = bot.Contact.load('wzhwno1')
                await target_friend.say(mail_content)
                room = bot.Room.load("18887123951@chatroom")
                await room.ready()
                conversation: Union[Room, Contact] = room
                await conversation.ready()
                await conversation.say(mail_content)
        data = data_loader.get_data(cfg.get('grid.platform'), cfg.get('grid.token'))
    except:
        logger.error(traceback.format_exc())
    else:
        flag, mail = grid.run_data(data)
        if flag:
            grid.trade = None
            dill.dump(grid, open(grid_cache, 'wb'))
            grid.trade = data_loader.trade
            if int(cfg.get('grid.mail_reminder')):
                mail_helper.sendmail(cfg.get('grid.mail_list'), 'GRID SCRIPT NEW TRADE', mail)
            if int(cfg.get('grid.wechat_reminder')):
                target_friend = bot.Contact.load('wzhwno1')
                await target_friend.say(mail)
                room = bot.Room.load("18887123951@chatroom")
                await room.ready()
                conversation: Union[Room, Contact] = room
                await conversation.ready()
                await conversation.say(mail)

async def grid_schedule():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_grid, trigger='interval', seconds=int(cfg.get('grid.timespan')), id='run_grid')
    scheduler.start()

async def main():
    wechat_task = asyncio.create_task(wechat())
    grid_task = asyncio.create_task(grid_schedule())
    await asyncio.gather(wechat_task, grid_task)

asyncio.run(main())