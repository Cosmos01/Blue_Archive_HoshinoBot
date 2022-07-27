import os
import json
import datetime
import aiohttp
import asyncio
import math

from .enwiki_calendar import transform_enwiki_calendar
from .schaledb_calendar import transform_schaledb_calendar
from .biliwiki_calendar import transform_biliwiki_calendar

# type 0普通 1 活动 2双倍 3 总力战

event_data = {
    'jp': [],
    'global': [],
}

event_updated = {
    'jp': '',
    'global':''
}

lock = {
    'jp': asyncio.Lock(),
    'global': asyncio.Lock(),
}


async def query_data(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()
    except:
        pass
    return None


async def load_event_enwiki():
    data = ''
    try:
        async with aiohttp.ClientSession() as session:
            # biliwiki: https://wiki.biligame.com/bluearchive/%E9%A6%96%E9%A1%B5
            # async with session.get('https://wiki.biligame.com/bluearchive/%E9%A6%96%E9%A1%B5') as resp:
            #     data = await resp.text('utf-8')
            #     data = transform_enwiki_calendar(data)
            async with session.get('https://bluearchive.wiki/wiki/Main_Page') as resp:
                data = await resp.text('utf-8')
                data = transform_enwiki_calendar(data)
    except:
        print('解析B站日程表失败')
        return 1
    if data:
        event_data['jp'] = []
        for item in data:
            start_time = datetime.datetime.strptime(item['start'], r"%Y/%m/%d %H:%M")
            end_time = datetime.datetime.strptime(item['end'], r"%Y/%m/%d %H:%M")
            event = {'title': item['title'], 'start': start_time, 'end': end_time, 'type': 1}
            if '倍' in event['title']:
                event['type'] = 2
            elif '总力战' in event['title'] or '演习' in event['title'] or '演習' in event['title']:
                event['type'] = 3
            event_data['jp'].append(event)
        return 0
    return 1

async def load_event_schaledb(server):
    data = ''
    try:
        data = transform_schaledb_calendar(server)
        if data == None:
            print('解析ba日程表失败')
            return 1
    except:
        print('解析ba日程表失败')
        return 1
    if data:
        if server == "jp":
            event_data['jp'] = []
        else:
            event_data['global'] = []
        for item in data:
            start_time = datetime.datetime.strptime(item['start'], r"%Y/%m/%d %H:%M")
            end_time = datetime.datetime.strptime(item['end'], r"%Y/%m/%d %H:%M")
            event = {'title': item['title'], 'start': start_time, 'end': end_time, 'type': 1}
            if '倍' in event['title']:
                event['type'] = 2
            elif '总力战' in event['title'] or '演习' in event['title'] or '演習' in event['title']:
                event['type'] = 3
            if server == "jp":
                event_data['jp'].append(event)
            else:
                event_data['global'].append(event)
        return 0
    return 1

async def load_event(server):
    if server == 'jp':
        return await load_event_enwiki()
        #return await load_event_schaledb("jp")
    if server != 'jp':  #反正就俩服
        return await load_event_schaledb("global")
    return 1


def get_ba_now(offset):
    ba_now = datetime.datetime.now()
    if ba_now.hour < 4:
        ba_now -= datetime.timedelta(days=1)
    ba_now = ba_now.replace(hour=18, minute=0, second=0, microsecond=0)  # 用晚6点做基准
    ba_now = ba_now + datetime.timedelta(days=offset)
    return ba_now


async def get_events(server, offset, days):
    events = []
    ba_now = datetime.datetime.now()
    if ba_now.hour < 4:
        ba_now -= datetime.timedelta(days=1)
    ba_now = ba_now.replace(hour=18, minute=0, second=0, microsecond=0)  # 用晚6点做基准

    await lock[server].acquire()
    try:
        t = ba_now.strftime('%y%m%d')
        if event_updated[server] != t:
            if await load_event(server) == 0:
                event_updated[server] = t
    finally:
        lock[server].release()

    start = ba_now + datetime.timedelta(days=offset)
    end = start + datetime.timedelta(days=days)
    end -= datetime.timedelta(hours=8)

    for event in event_data[server]:
        if end > event['start'] and start < event['end']:  # 在指定时间段内 已开始 且 未结束
            event['start_days'] = math.ceil((event['start'] - start) / datetime.timedelta(days=1))  # 还有几天开始
            event['left_days'] = math.floor((event['end'] - start) / datetime.timedelta(days=1))  # 还有几天结束
            events.append(event)
    events.sort(key=lambda item: item["type"] * 100 - item['left_days'], reverse=True)  # 按type从大到小 按剩余天数从小到大
    return events


if __name__ == '__main__':
    async def main():
        events = await get_events('jp', 0, 1)
        for event in events:
            print(event)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
