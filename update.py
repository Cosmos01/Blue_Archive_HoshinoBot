import json
import logging
import os
import re
import io
from io import BytesIO
from PIL import Image
import hoshino
from hoshino import priv, R, aiorequests
from nonebot import on_command, get_bot, scheduler

# 配置代理，例：{"http": "http://127.0.0.1:1080"}
proxy = {"http": ""}

chara_path = os.path.join(os.path.dirname(__file__), 'gacha', '_ba_data.json')
pool_path = os.path.join(os.path.dirname(__file__), 'gacha', 'config.json')

chara_url = "http://124.223.25.80:40000/Blue_Archive_HoshinoBot/gacha/_ba_data.json"
pool_url = "http://124.223.25.80:40000/Blue_Archive_HoshinoBot/gacha/config.json"
student_jp_url = "http://124.223.25.80:40000/SchaleDB/data/jp/students.min.json"
student_icon_base_url = "http://124.223.25.80:40000/SchaleDB/images/student/icon/"
# 通过git获取的url
# chara_url = "https://raw.githubusercontent.com/Cosmos01/Blue_Archive_HoshinoBot/main/gacha/_ba_data.json"
# pool_url = "https://raw.githubusercontent.com/Cosmos01/Blue_Archive_HoshinoBot/main/gacha/config.json"
# student_jp_url = "https://raw.githubusercontent.com/lonqie/SchaleDB/main/data/jp/students.min.json"
# student_icon_base_url = "https://raw.githubusercontent.com/lonqie/SchaleDB/main/images/student/icon/"

async def update_icon():
    try:
        student_res = await aiorequests.get(student_jp_url, timeout=15,proxies=proxy)
        students = await student_res.json()
        for student in students:
            if R.img(f'bluearchive/unit/icon_unit_{str(student["Id"])}.png').exist:
                continue
            print(f'检测到缺失角色图片：{student["DevName"]}，正在从SchaleDB下载图片')
            img = await aiorequests.get(
                f'{student_icon_base_url}{str(student["Id"])}.webp',
                timeout=15,proxies=proxy)
            img_save_path = os.path.abspath(
                os.path.join(hoshino.config.RES_DIR, f'img/bluearchive/unit/icon_unit_{str(student["Id"])}.png'))
            img_cont = await img.content
            byte_stream = BytesIO(img_cont) 
            roiImg = Image.open(byte_stream) 
            imgByteArr = io.BytesIO()
            roiImg.save(imgByteArr, format='PNG') 
            imgByteArr = imgByteArr.getvalue() 
            with open(img_save_path, 'wb') as f:
                f.write(imgByteArr)
    except Exception as e:
        logging.warning(e)
        return

async def update():
    try:
        chara_res = await aiorequests.get(chara_url,timeout=15,proxies=proxy)
        pool_res = await aiorequests.get(pool_url,timeout=15,proxies=proxy)
        chara = await chara_res.json()
        pool = await pool_res.json()
        local_pool = json.load(open(pool_path,encoding="utf-8"))

        with open(chara_path, "w", encoding='utf8') as f:
            json.dump(chara, f, ensure_ascii=False)

        local_pool["JP"] = pool["JP"]
        local_pool["FES"] = pool["FES"]
        local_pool["GLOBAL"] = pool["GLOBAL"]
        local_pool["CN"] = pool["CN"]
        
        with open(pool_path, "w", encoding='utf8') as f:
            json.dump(local_pool, f, ensure_ascii=False)
        await update_icon()
        return f'日服:{str(local_pool["JP"]["up"])} 国服:{str(local_pool["CN"]["up"])} fes:{str(local_pool["FES"]["up"])} 国际服:{str(local_pool["GLOBAL"]["up"])}'
    except Exception as e:
        logging.warning(e)
        return None

@on_command('ba更新卡池', only_to_me=False)
async def update_pool_chat(session):
    if not priv.check_priv(session.event, priv.ADMIN):
        return
    status = await update()
    if status == None:
        await session.finish(f'发生错误')
    else:
        await session.finish(f'更新完成, 当前卡池:{status}')

@scheduler.scheduled_job('cron', hour='17', minute='00')
async def update_pool_sdj():
    bot = get_bot()
    master_id = hoshino.config.SUPERUSERS[0]
    status = await update()
    if status == None:
        msg = f'自动更新ba卡池时发生错误'
        await bot.send_private_msg(user_id=master_id, message=msg)


