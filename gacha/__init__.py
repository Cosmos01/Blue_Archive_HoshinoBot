import os
import random
from collections import defaultdict

from hoshino import Service, priv, util
from hoshino.typing import *
from hoshino.util import DailyNumberLimiter, concat_pic, pic2b64, silence

from . import chara
from .gacha import Gacha

try:
    import ujson as json
except:
    import json

sv_help = '''
[ba十连] 转蛋模拟
[ba单抽] 转蛋模拟
[ba来一井] 2w4钻！
[ba查看卡池] 模拟卡池&出率
[ba切换卡池] 更换模拟卡池
'''.strip()
sv = Service('blue_gacha', help_=sv_help)
jewel_limit = DailyNumberLimiter(15000)
tenjo_limit = DailyNumberLimiter(3)

JEWEL_EXCEED_NOTICE = f'您今天已经抽过{jewel_limit.max}钻，已经没钻啦，明早五点再来吧！'
TENJO_EXCEED_NOTICE = f'您今天已经抽过{tenjo_limit.max}张天井券，已经没钻啦，明早五点再来吧！'
POOL = ('JP', 'MIX', 'GLOBAL')
DEFAULT_POOL = POOL[0]

_blue_pool_config_file = os.path.expanduser('~/.hoshino/blue_group_pool_config.json')
_blue_group_pool = {}
try:
    with open(_blue_pool_config_file, encoding='utf8') as f:
        _blue_group_pool = json.load(f)
except FileNotFoundError as e:
    sv.logger.warning('blue_group_pool_config.json not found, will create when needed.')
_blue_group_pool = defaultdict(lambda: DEFAULT_POOL, _blue_group_pool)


def dump_blue_pool_config():
    with open(_blue_pool_config_file, 'w', encoding='utf8') as f:
        json.dump(_blue_group_pool, f, ensure_ascii=False)


@sv.on_fullmatch(('ba查看卡池'))
async def gacha_info(bot, ev: CQEvent):
    gid = str(ev.group_id)
    gacha = Gacha(_blue_group_pool[gid])
    up_chara = gacha.up
    up_chara = map(lambda x: str(chara.fromname(x, star=3).icon.cqcode) + x, up_chara)
    up_chara = '\n'.join(up_chara)
    await bot.send(ev,
                   f"本期碧蓝档案卡池主打的角色：\n{up_chara}\nUP角色合计={(gacha.up_prob / 10):.1f}% 3★出率={(gacha.s3_prob) / 10:.1f}%")


POOL_NAME_TIP = '请选择以下卡池\n> 切换卡池jp\n> 切换卡池tw\n> 切换卡池b\n> 切换卡池mix'


@sv.on_prefix('ba切换卡池', 'ba选择卡池')
async def set_pool(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '只有群管理才能切换卡池', at_sender=True)
    name = util.normalize_str(ev.message.extract_plain_text())
    if not name:
        await bot.finish(ev, POOL_NAME_TIP, at_sender=True)
    elif name in ('国际', '国际服', '台', '美', '韩', '台服', '美服', '韩服' 'global', 'GLOBAL'):
        name = 'GLOBAL'
    elif name in ('日', '日服', 'jp', 'JP'):
        name = 'JP'
    elif name in ('混', '混合', 'mix', 'MIX'):
        name = 'MIX'
    elif name in ('MIKA', 'mika', '未花', '猩猩'):
        name = 'MIKA'
    else:
        await bot.finish(ev, f'未知服务器地区 {POOL_NAME_TIP}', at_sender=True)
    gid = str(ev.group_id)
    _blue_group_pool[gid] = name
    dump_blue_pool_config()
    await bot.send(ev, f'卡池已切换为{name}池', at_sender=True)
    await gacha_info(bot, ev)


async def check_jewel_num(bot, ev: CQEvent):
    if not jewel_limit.check(ev.user_id):
        await bot.finish(ev, JEWEL_EXCEED_NOTICE, at_sender=True)


async def check_tenjo_num(bot, ev: CQEvent):
    if not tenjo_limit.check(ev.user_id):
        await bot.finish(ev, TENJO_EXCEED_NOTICE, at_sender=True)


@sv.on_fullmatch("ba单抽")
async def gacha_1(bot, ev: CQEvent):
    await check_jewel_num(bot, ev)
    jewel_limit.increase(ev.user_id, 150)

    gid = str(ev.group_id)
    gacha = Gacha(_blue_group_pool[gid])
    chara, hiishi = gacha.gacha_one(gacha.up_prob, gacha.s3_prob, gacha.s2_prob)
    silence_time = hiishi * 60

    res = f'{chara.icon.cqcode} {chara.name} {"★" * chara.star}'

    await silence(ev, silence_time)
    await bot.send(ev, res, at_sender=True)


@sv.on_fullmatch("ba十连")
async def gacha_10(bot, ev: CQEvent):
    SUPER_LUCKY_LINE = 170

    await check_jewel_num(bot, ev)
    jewel_limit.increase(ev.user_id, 1500)

    gid = str(ev.group_id)
    gacha = Gacha(_blue_group_pool[gid])
    result, hiishi = gacha.gacha_ten()
    silence_time = hiishi * 6 if hiishi < SUPER_LUCKY_LINE else hiishi * 60

    res1 = chara.gen_team_pic(result[:5], star_slot_verbose=False)
    res2 = chara.gen_team_pic(result[5:], star_slot_verbose=False)
    res = concat_pic([res1, res2])
    res = pic2b64(res)
    res = MessageSegment.image(res)
    result = [f'{c.name}{"★" * c.star}' for c in result]
    res1 = ' '.join(result[0:5])
    res2 = ' '.join(result[5:])
    res = f'{res}\n{res1}\n{res2}'
    # 纯文字版
    # result = [f'{c.name}{"★"*c.star}' for c in result]
    # res1 = ' '.join(result[0:5])
    # res2 = ' '.join(result[5:])
    # res = f'{res1}\n{res2}'

    if hiishi >= SUPER_LUCKY_LINE:
        await bot.send(ev, '有狗！')
    await bot.send(ev, f'{res}\n', at_sender=True)
    await silence(ev, silence_time)


@sv.on_fullmatch("ba来一井")
async def gacha_200(bot, ev: CQEvent):
    await check_tenjo_num(bot, ev)
    tenjo_limit.increase(ev.user_id)

    gid = str(ev.group_id)
    gacha = Gacha(_blue_group_pool[gid])
    result = gacha.gacha_tenjou()
    up = len(result['up'])
    s3 = len(result['s3'])
    s2 = len(result['s2'])
    s1 = len(result['s1'])

    res = [*(result['up']), *(result['s3'])]
    random.shuffle(res)
    lenth = len(res)
    if lenth <= 0:
        res = "竟...竟然没有3★？！"
    else:
        step = 4
        pics = []
        for i in range(0, lenth, step):
            j = min(lenth, i + step)
            pics.append(chara.gen_team_pic(res[i:j], star_slot_verbose=False))
        res = concat_pic(pics)
        res = pic2b64(res)
        res = MessageSegment.image(res)

    msg = [
        f"\n{res}",
        f"★★★×{up + s3} ★★×{s2} ★×{s1}",
        f"获得UP角色×{up}与神名文字×{50 * (up + s3) + 10 * s2 + s1}！\n第{result['first_up_pos']}抽首次获得up角色" if up else f"获得神名文字{50 * (up + s3) + 10 * s2 + s1}个！"
    ]

    if up == 0 and s3 == 0:
        msg.append("太惨了，咱们还是退款删游吧...")
    elif up == 0 and s3 > 7:
        msg.append("up呢？我的up呢？")
    elif up == 0 and s3 <= 3:
        msg.append("这位酋长，梦幻包考虑一下？")
    elif up == 0:
        msg.append("据说天井的概率只有24.5%")
    elif up <= 2:
        if result['first_up_pos'] < 40:
            msg.append("你的喜悦我收到了，滚去喂鲨鱼吧！")
        elif result['first_up_pos'] < 80:
            msg.append("已经可以了，您已经很欧了")
        elif result['first_up_pos'] > 120:
            msg.append("标 准 结 局")
        elif result['first_up_pos'] > 180:
            msg.append("补井还是不补井，这是一个问题...")
        else:
            msg.append("期望之内，亚洲水平")
    elif up == 3:
        msg.append("抽井母五一气呵成！")
    elif up >= 4:
        msg.append("UP角色一大堆！您是托吧？")

    await bot.send(ev, '\n'.join(msg), at_sender=True)
    silence_time = (100 * up + 50 * (up + s3) + 10 * s2 + s1) * 1
    await silence(ev, silence_time)


@sv.on_prefix('ba氪金')
async def kakin(bot, ev: CQEvent):
    if ev.user_id not in bot.config.SUPERUSERS:
        return
    count = 0
    for m in ev.message:
        if m.type == 'at' and m.data['qq'] != 'all':
            uid = int(m.data['qq'])
            jewel_limit.reset(uid)
            tenjo_limit.reset(uid)
            count += 1
    if count:
        await bot.send(ev, f"已经为{count}位用户充值完毕！谢谢惠顾～")
