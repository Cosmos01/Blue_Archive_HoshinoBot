import hoshino
import nonebot
import re
import traceback
from .ba_calendar.generate import *
from .utils import *
from .moudle.ba_logo import draw_pic

HELP_STR = '''
碧蓝档案综合插件
`ba日历` : 本群订阅服务器日历，需要先订阅(见第三条)，默认取第一位，需要调整顺序先off掉其他服
`ba(日/国/db日/en日/国际/db国际)服日历` : 指定服务器日程
`ba(日/国/db日/en日/国际/db国际)服日历 on/off` : 订阅/取消订阅指定服务器的日历推送
`ba日历 time 时:分` : 设置日历推送时间
`ba日历 status` : 本群日历推送设置
`ba日历 cardimage` : (go-cqhttp限定)切换是否使用cardimage模式发送日历图片
`(日/国际服)总力一图流` : 当前总力一图流,为空时默认日服
`ba来一井/ba十连/ba单抽` : 模拟抽卡
`ba更新卡池` : 更新角色列表、卡池、资源文件，默认会自动更新
`ba氪金+@目标` : 恢复抽卡次数，可@多个目标
`ba角色列表` : 列出所有角色头像及昵称
`ba查询+角色名或昵称` : 查询角色信息
`国服/国际服+千里眼/未来视` : 获取卡池排期和抽卡推荐
`ba攻略(攻略查询、/攻略)+关键词` : 查询攻略,支持模糊查询,关键词可以是学生/地图/活动等，使用`杂图`关键词获取详情 
`balogo+上文/下文` : 生成你游风格logo,上下文使用`/`分隔
'''.strip()

sv = hoshino.Service('ba_calendar', enable_on_default=False, help_=HELP_STR, bundle='ba日历')

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
            json.dump(group_data, f, ensure_ascii=False, indent=2)
    except:
        traceback.print_exc()


async def send_calendar(group_id):
    bot = hoshino.get_bot()
    available_group = await sv.get_enable_groups()
    if str(group_id) not in group_data or int(group_id) not in available_group:
        return
    for server in group_data[str(group_id)]['server_list']:
        img = await generate_day_schedule(server)
        base64_str = img_to_base64str(img)
        if 'cardimage' not in group_data[group_id] or not group_data[group_id]['cardimage']:
            msg = f'[CQ:image,file={base64_str}]'
        else:
            msg = f'[CQ:cardimage,file={base64_str}]'
        for _ in range(3):  # 失败重试3次
            try:
                await bot.send_group_msg(group_id=int(group_id), message=msg)
                sv.logger.info(f'群{group_id}推送{server}日历成功')
                break
            except Exception as e:
                sv.logger.info(f'群{group_id}推送{server}日历失败: \n{e}')
            await asyncio.sleep(60)


def update_group_schedule(group_id):
    group_id = str(group_id)
    if group_id not in group_data:
        return
    nonebot.scheduler.add_job(
        send_calendar,
        'cron',
        args=(group_id,),
        id=f'ba_calendar_{group_id}',
        replace_existing=True,
        hour=group_data[group_id]['hour'],
        minute=group_data[group_id]['minute']
    )


@sv.on_rex(r'^ba([endb日国际台韩美]{1,4})?服?日[历程](.*)')
async def start_scheduled(bot, ev):
    group_id = str(ev['group_id'])
    server_name = ev['match'].group(1)
    if server_name == '日':
        server = 'jp'
    elif server_name == '国':
        server = 'cn'
    elif server_name in ["国际", "台", "韩", "美"]:
        server = 'global'
    elif server_name == 'en日':
        server = 'en-jp'
    elif server_name == 'db日':
        server = 'db-jp'
    elif server_name == 'db国际':
        server = 'db-global'
    elif group_id in group_data and len(group_data[group_id]['server_list']) > 0:
        server = group_data[group_id]['server_list'][0]
    else:
        server = 'jp'
    cmd = ev['match'].group(2)
    if not cmd:
        img = await generate_day_schedule(server)
        base64_str = img_to_base64str(img)
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
            match = re.search(r'(\d*):(\d*)', cmd)
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


@nonebot.on_startup
async def startup():
    load_data()
    for group_id in group_data:
        update_group_schedule(group_id)


@sv.on_prefix(('balogo', 'ba标题'))
async def send_ba_logo(bot, ev):
    try:
        match_message = ev.message.extract_plain_text().strip()
        split = match_message.split('/', 1)
        if len(split) != 2:
            await bot.send(ev, '请检查输入是否正确，前后文本使用/分隔')
            return
        upper = split[0]
        downer = split[1]
        img_raw = draw_pic(front=upper, back=downer)
        img = BytesIO()
        img_raw.save(img, format='png')
        img_bytes: bytes = img.getvalue()
        img_raw.close()
        img.close()
        await bot.send(ev, img_content_to_cqcode(img_bytes))
    except OSError:
        await bot.send(ev, '生成失败……请检查字体文件设置是否正确')
    except IndexError:
        await bot.send(ev, '生成失败……请检查命令格式是否正确，前后文本请使用/分隔')
    except Exception:
        await bot.send(ev, '请检查指令是否正确，前后文本请使用/分隔')