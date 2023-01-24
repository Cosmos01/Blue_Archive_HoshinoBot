import json
import logging
import os
import re

import hoshino
from hoshino import priv, R, aiorequests
from nonebot import on_command, get_bot, scheduler

# 配置代理，例：{"http": "http://127.0.0.1:1080"}
proxy = {"http": ""}

chara_path = os.path.join(os.path.dirname(__file__), 'gacha', '_ba_data.json')
pool_path = os.path.join(os.path.dirname(__file__), 'gacha', 'config.json')

chara_url = "http://91.149.236.232:40000/Blue_Archive_HoshinoBot/gacha/_ba_data.json"
pool_url = "http://91.149.236.232:40000/Blue_Archive_HoshinoBot/gacha/config.json"
student_jp_url = "http://91.149.236.232:40000/SchaleDB/data/jp/students.min.json"
student_icon_base_url = "http://91.149.236.232:40000/SchaleDB/images/student/icon/"
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
            CollectionTexture = student["CollectionTexture"]
            img = await aiorequests.get(
                f'{student_icon_base_url}{CollectionTexture}.png',
                timeout=15,proxies=proxy)
            img_save_path = os.path.abspath(
                os.path.join(hoshino.config.RES_DIR, f'img/bluearchive/unit/icon_unit_{str(student["Id"])}.png'))
            img_cont = await img.content
            with open(img_save_path, 'wb') as f:
                f.write(img_cont)
    except:
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

        with open(pool_path, "w", encoding='utf8') as f:
            json.dump(local_pool, f, ensure_ascii=False)
        await update_icon()
        return f'日服:{str(local_pool["JP"]["up"])} fes:{str(local_pool["FES"]["up"])} 国际服:{str(local_pool["GLOBAL"]["up"])}'
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









#原bwiki获取
#
# async def get_img_data():
#     img_url = "https://wiki.biligame.com/bluearchive/api.php?action=parse&page=%E6%8A%BD%E5%8D%A1%E6%A8%A1%E6%8B%9F%E5%99%A8/src&format=json"
#     res = await aiorequests.get(img_url)
#     page_data = await res.json()
#     # revid = page_data["parse"]["revid"]  # 25957
#     text = page_data["parse"]["text"]["*"]
#     json_text = re.search(r"{.*?}", text).group()
#     img_data = json.loads(json_text)
#     return img_data
#
#
# # # 可能能当版本号
# # async def get_version():
# #     url = "https://wiki.biligame.com/bluearchive/api.php?action=parse&page=%E6%8A%BD%E5%8D%A1%E6%A8%A1%E6%8B%9F%E5%99%A8/src&format=json"
# #     res = await aiorequests.get(url)
# #     page_data = await res.json()
# #     revid = page_data["parse"]["revid"]  # 25957
# #     return revid
#
#
# async def get_up_data():
#     up_url = "https://wiki.biligame.com/bluearchive/gacha_config.json?action=raw&format=json"
#     res = await aiorequests.get(up_url)
#     up_data = await res.json()
#     pickup = []
#     if "pickup1" in up_data:
#         pickup.append(up_data["pickup1"])
#     if "pickup2" in up_data:
#         pickup.append(up_data["pickup2"])
#     return pickup
#
#
# async def get_student_base():
#     name_url = "https://wiki.biligame.com/bluearchive/Locales/zh-CN/student_name.json?action=raw&format=json"
#     id_url = "https://wiki.biligame.com/bluearchive/Base.json?action=raw&format=json"
#     res1 = await aiorequests.get(name_url)
#     student_name_data = await res1.json()
#     res2 = await aiorequests.get(id_url)
#     student_id_data = await res2.json()
#     student_base_data = {}
#     for student in student_id_data:
#         student_name_cn = student_name_data[student["name"]] if student["name"] in student_name_data else ""
#         student_base_data[str(student["id"])] = {"name": student["name"], "name_cn": student_name_cn}
#     return student_base_data
#
#
# async def get_student_info():
#     student_data = {}  # 最终角色数据
#     img_data = await get_img_data()
#     student_base_data = await get_student_base()  # {"1":{name:"xxx",name_cn:"xxx"},}
#     info_url = "https://wiki.biligame.com/bluearchive/CharacterExcelTable.json?action=raw&format=json"
#     res = await aiorequests.get(info_url)
#     student_info = await res.json()
#     for sid, data in student_base_data.items():
#         if data["name"] not in img_data:
#             continue  # 排除没有图片的
#         data["star"] = student_info[sid]["DefaultStarGrade"]  # 星级
#         data["standard"] = student_info[sid]["CollectionVisible"]  # 是否常驻
#         data["img_url"] = img_data[data["name"]]
#         img_path = f"bluearchive/unit/icon_unit_{sid}.png"
#         data["img_path"] = img_path
#         student_data[sid] = data
#     return student_data
#
#
# async def update_chara_data(student_info):
#     _ba_data = json.load(open(chara_path, encoding="utf-8"))
#     chara = _ba_data["CHARA_NAME"]
#     for sid, student in student_info.items():
#         if sid not in chara:
#             chara[sid] = [student["name"], student["name_cn"]]
#     _ba_data["CHARA_NAME"] = chara
#     json.dump(_ba_data, open(chara_path, 'w', encoding="utf-8"), ensure_ascii=False, indent=2)
#
#
# async def update_pool_data(student_info):
#     pool_config = json.load(open(pool_path, encoding="utf-8"))
#     pool = pool_config["JP"]
#     pick_up_jp = await get_up_data()
#     pick_up = []
#     star3 = []
#     star2 = []
#     star1 = []
#     for student in student_info.values():
#         if student["name"] in pick_up_jp:
#             pick_up.append(student["name_cn"])
#         if student["standard"]:
#             if student["star"] == 3:
#                 star3.append(student["name_cn"])
#             elif student["star"] == 2:
#                 star2.append(student["name_cn"])
#             elif student["star"] == 1:
#                 star1.append(student["name_cn"])
#     for name in pick_up:
#         star3.remove(name)
#     pool["up"] = pick_up
#     pool["star3"] = star3
#     pool["star2"] = star2
#     pool["star1"] = star1
#     pool_config["JP"] = pool
#     json.dump(pool_config, open(pool_path, 'w', encoding="utf-8"), ensure_ascii=False, indent=2)
#
#
# async def download_icon(student_info):
#     for student in student_info.values():
#         if not R.img(student["img_path"]).exist:
#             res = await aiorequests.get(student["img_url"])
#             if res.status_code == 200:
#                 with open(R.img(student["img_path"]).path, 'wb') as f:
#                     content = await res.content
#                     f.write(content)
#                     print(f'正在获取{student["name_cn"]}图片')
#
#
# async def update():
#     try:
#         pick_up = await get_up_data()
#         pick_up = str(pick_up)
#         if open(version_path).read() != pick_up:
#             stu = await get_student_info()
#             await update_chara_data(stu)
#             await update_pool_data(stu)
#             await download_icon(stu)
#             open(version_path, "w").write(pick_up)
#             return pick_up
#         else:
#             return 0
#     except:
#         return 2
#
#
# @on_command('ba更新卡池', only_to_me=False)
# async def update_pool_chat(session):
#     if not priv.check_priv(session.event, priv.ADMIN):
#         return
#     status = await update()
#     if status == 0:
#         await session.finish('已是最新版本')
#     elif status == 2:
#         await session.finish(f'发生错误')
#     else:
#         await session.finish(f'更新完成, 当前卡池版本:{status}')
#
#
# @scheduler.scheduled_job('cron', hour='17', minute='00')
# async def update_pool_sdj():
#     bot = get_bot()
#     master_id = hoshino.config.SUPERUSERS[0]
#     status = await update()
#     if status == 0:
#         return
#     elif status == 2:
#         msg = f'自动更新ba卡池时发生错误'
#         await bot.send_private_msg(user_id=master_id, message=msg)
