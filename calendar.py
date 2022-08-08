import base64
from .ba_calendar.generate import *
from .raid_img import get_raid_img
import hoshino
import nonebot
import os
import re
import traceback
from .student_info import get_student_info

HELP_STR = '''
碧蓝档案活动日历
ba日历 : 查看本群订阅服务器日历
ba[日]服日历 : 查看指定服务器日程
ba[日]服日历 on/off : 订阅/取消订阅指定服务器的日历推送
ba日历 time 时:分 : 设置日历推送时间
ba日历 status : 查看本群日历推送设置
[日国國美台]?[际際]?[服]?总力一图流 : 查看当前总力一图流,服务器名为空时默认日服
'''.strip()

sv = hoshino.Service('ba_calendar',enable_on_default=False, help_=HELP_STR, bundle='ba查询')

group_data = {}

def load_data():
    path = os.path.join(os.path.dirname(__file__), 'data.json')
    if not os.path.exists(path):
        return
    global group_data
    try:
        with open(path, encoding='utf8') as f:
            group_data = json.load(f)
    except:
        traceback.print_exc()

def save_data():
    path = os.path.join(os.path.dirname(__file__), 'data.json')
    try:
        with open(path, 'w', encoding='utf8') as f:
            json.dump(group_data , f, ensure_ascii=False, indent=2)
    except:
        traceback.print_exc()

async def send_calendar(group_id):
    bot = hoshino.get_bot()
    available_group = await sv.get_enable_groups()
    if str(group_id) not in group_data or int(group_id) not in available_group:
        return
    for server in group_data[str(group_id)]['server_list']:
        im = await generate_day_schedule(server)
        base64_str = im2base64str(im)
        if 'cardimage' not in group_data[group_id] or not group_data[group_id]['cardimage']:
            msg = f'[CQ:image,file={base64_str}]'
        else:
            msg = f'[CQ:cardimage,file={base64_str}]'
        for _ in range(5): #失败重试5次
            try:
                await bot.send_group_msg(group_id=int(group_id), message = msg)
                sv.logger.info(f'群{group_id}推送{server}日历成功')
                break
            except:
                sv.logger.info(f'群{group_id}推送{server}日历失败')
            await asyncio.sleep(60)

def update_group_schedule(group_id):
    group_id = str(group_id)
    if group_id not in group_data:
        return
    nonebot.scheduler.add_job(
        send_calendar, 
        'cron', 
        args = (group_id,), 
        id = f'ba_calendar_{group_id}', 
        replace_existing = True, 
        hour = group_data[group_id]['hour'], 
        minute = group_data[group_id]['minute']
        )

@sv.on_rex(r'^ba([日国台韩美])?[际際]?服?日[历程](.*)')
async def start_scheduled(bot, ev):
    group_id = str(ev['group_id'])
    server_name = ev['match'].group(1)
    if server_name == '日':
        server = 'jp'
    elif server_name in ["国","台","韩","美"]:
        server = 'global'
    elif group_id in group_data and len(group_data[group_id]['server_list']) > 0:
        server = group_data[group_id]['server_list'][0]
    else:
        server = 'jp'
    cmd = ev['match'].group(2)
    if not cmd:
        im = await generate_day_schedule(server)
        base64_str = im2base64str(im)
        if 'cardimage' not in group_data[group_id] or not group_data[group_id]['cardimage']:
            msg = f'[CQ:image,file={base64_str}]'
        else:
            msg = f'[CQ:cardimage,file={base64_str}]'
    else:
        if group_id not in group_data:
            group_data[group_id] = {
                'server_list': [],
                'hour': 8, 
                'minute': 0,
                'cardimage': False,
            }
        if not hoshino.priv.check_priv(ev, hoshino.priv.ADMIN):
            msg = '权限不足'
        elif 'on' in cmd:
            if server not in group_data[group_id]['server_list']:
                group_data[group_id]['server_list'].append(server)
            save_data()
            msg = f'{server}日程推送已开启'
        elif 'off' in cmd:
            if server in group_data[group_id]['server_list']:
                group_data[group_id]['server_list'].remove(server)
            save_data()
            msg = f'{server}日程推送已关闭'
        elif 'time' in cmd:
            match = re.search( r'(\d*):(\d*)', cmd)
            if not match or len(match.groups()) < 2:
                msg = '请指定推送时间'
            else:
                group_data[group_id]['hour'] = int(match.group(1))
                group_data[group_id]['minute'] = int(match.group(2))
                msg = f"推送时间已设置为: {group_data[group_id]['hour']}:{group_data[group_id]['minute']:02d}"
            save_data()
        elif 'status' in cmd:
            msg = f"订阅日历: {group_data[group_id]['server_list']}"
            msg += f"\n推送时间: {group_data[group_id]['hour']}:{group_data[group_id]['minute']:02d}"
        elif 'cardimage' in cmd:
            if 'cardimage' not in group_data[group_id] or not group_data[group_id]['cardimage']:
                group_data[group_id]['cardimage'] = True
                msg = f'已切换为cardimage模式'
            else:
                group_data[group_id]['cardimage'] = False
                msg = f'已切换为标准image模式'
            save_data()
        else:
            msg = '指令错误'
        update_group_schedule(group_id)
        save_data()
    await bot.send(ev, msg)


@sv.on_rex(r'([日国國美台])?[际際]?[服]?总力一图流')
async def raid_img(bot, ev):
    server_name = ev['match'].group(1)
    if server_name == "日" or server_name == None:
        server_name = "日"
    else:
        server_name = "國際"

    raid_img = await get_raid_img(server_name)
    if raid_img == "":
        await bot.send(ev, "获取图片失败")
        return
    await bot.send(ev, f'[CQ:image,file={raid_img}]')


@sv.on_prefix('ba查询')
async def send_student_info(bot, ev):
    nickname = ev.message.extract_plain_text()
    msgs = get_student_info(nickname)
    if msgs == None:
        await bot.send(ev, "获取角色信息失败,请检查角色是否存在,或提交补充角色昵称")
        return
    await bot.send_group_forward_msg(group_id=ev.group_id,messages=msgs)

    
@nonebot.on_startup
async def startup():
    load_data()
    for group_id in group_data:
        update_group_schedule(group_id)
        
@sv.scheduled_job('cron', hour='8', jitter=1)
async def auto_load_data():
    load_data()
