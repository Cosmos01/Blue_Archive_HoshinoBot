import re
from hoshino import Service
from ..utils import get_default_server
from .support import search_support

sv = Service('arona_icu', enable_on_default=False, visible=True, bundle='什亭之匣')


@sv.on_prefix(('助战查询', '我要借'))
async def get_support(bot, ev):
    match_message = ev.message.extract_plain_text().strip()
    if not match_message:
        await bot.send(ev, '请指定角色名或昵称')
        return
    rs = re.match(
        r'^((?P<server>国|官|B|b|日|全球|港|澳|台|韩|亚|美)服)?(?P<atype>总力战|总力|演习|占领战|占领)?((?P<star>[1-5一二三四五])[星Xx*])?([专Ss](?P<weapon>[1234一二三四]))?(?P<nickname>\D+?)(?P<page>\d+)?$',
        match_message)
    table = str.maketrans('一二三四五', '12345')
    server = rs.group("server") if rs.group("server") else None
    star = int(rs.group("star").translate(table) if rs.group("star") else 0)
    weapon = int(rs.group("weapon").translate(table) if rs.group("weapon") else 0)
    nickname = rs.group("nickname")
    page = int(rs.group("page") if rs.group("page") else 1)
    atype = 2
    if rs.group("atype"):
        if rs.group("atype") in ["总力战", "总力"]:
            atype = 2
        elif rs.group("atype") in ["演习"]:
            atype = 15
        elif rs.group("atype") in ["占领战", "占领"]:
            atype = 3

    if server is None:
        server = get_default_server(ev.group_id)
    if server in ["国", "官", "cn"]:
        server = 1
    elif server in ["B", "b"]:
        server = 2
    elif server in ["日", "jp"]:
        server = 3
    elif server == "全球":
        server = 5
    elif server in ["港", "澳", "台"]:
        server = 6
    elif server == "韩":
        server = 7
    elif server == "亚":
        server = 8
    elif server == "美":
        server = 9
    else:
        server = 4

    msgs = await search_support(nickname, server=server, atype=atype, star=star, weapon=weapon, page=page)
    if len(msgs) == 1:
        await bot.send(ev, msgs[0])
    else:
        forward_msg = []
        for msg in msgs:
            forward_msg.append({
                "type": "node",
                "data": {
                    "name": "小冰",
                    "uin": "2854196306",
                    "content": msg
                }
            })
        await bot.send_group_forward_msg(group_id=ev.group_id, messages=forward_msg)






#user_data = {}

# def get_uid_server(uid):
#     if len(uid) != 7:
#         return 0
#     if uid[1] == "l" and uid[4] == "4":
#         return 1
#     if uid[1] == "6" and uid[4] == "9":
#         return 2
#     return 0

# def load_user_data():
#     path = os.path.join(os.path.dirname(__file__), 'user_data.json')
#     if not os.path.exists(path):
#         return
#     global user_data
#     try:
#         with open(path, encoding='utf8') as f:
#             user_data = json.load(f)
#     except Exception as e:
#         logging.error('读取数据失败')
#         logging.error(e)
#
#
# def save_user_data():
#     path = os.path.join(os.path.dirname(__file__), 'user_data.json')
#     try:
#         with open(path, 'w', encoding='utf8') as f:
#             json.dump(user_data, f, ensure_ascii=False, indent=2)
#     except Exception as e:
#         logging.error('保存数据失败')
#         logging.error(e)
#
#
# def get_default_server(uid):
#     if uid not in user_data or "friendCode" not in user_data[uid] or len(user_data[uid]["friendCode"]) == 0:
#         return 1
#     server = get_uid_server(user_data[uid]["friendCode"][0])
#     if server == 0:
#         return 1
#     return server
#
#
# @sv.on_prefix('绑定好友码')
# async def bind_friend_code(bot, ev):
#     friendCode = ev.message.extract_plain_text().strip()
#     if not friendCode:
#         await bot.send(ev, '请输入好友码')
#         return
#     if get_uid_server(friendCode) == 0:
#         await bot.send(ev, '好友码格式错误')
#         return
#
#     if str(ev.user_id) in user_data:
#         if friendCode in user_data[str(ev.user_id)]["friendCode"]:
#             await bot.send(ev, '已绑定该好友码')
#             return
#         else:
#             user_data[str(ev.user_id)]["friendCode"].append(friendCode)
#     else:
#         user_data[str(ev.user_id)] = {"friendCode": [friendCode]}
#     save_user_data()
#     await bot.send(ev, '绑定成功', at_sender=True)
#     return
#
#
# @sv.on_prefix('解绑好友码')
# async def unbind_friend_code(bot, ev):
#     friendCode = ev.message.extract_plain_text().strip()
#     if not friendCode:
#         await bot.send(ev, '请输入好友码')
#         return
#     if str(ev.user_id) not in user_data or "friendCode" not in user_data[str(ev.user_id)] or len(
#             user_data[str(ev.user_id)]["friendCode"]) == 0:
#         await bot.send(ev, '未绑定好友码')
#         return
#     if friendCode not in user_data[str(ev.user_id)]["friendCode"]:
#         await bot.send(ev, '未绑定该好友码')
#         return
#     user_data[str(ev.user_id)]["friendCode"].remove(friendCode)
#     save_user_data()
#     await bot.send(ev, '解绑成功', at_sender=True)
#     return
#
#
# @sv.on_prefix('查询好友码')
# async def query_friend_code(bot, ev):
#     user_id = 0
#     for msg_seg in ev.message:
#         if msg_seg.type == "at":
#             user_id = msg_seg.data["qq"]
#             break
#     if user_id == 0 or user_id == "all":
#         user_id = ev.user_id
#     if str(user_id) not in user_data or "friendCode" not in user_data[str(user_id)] or len(user_data[str(user_id)]["friendCode"]) == 0:
#         await bot.send(ev, '未绑定好友码')
#         return
#     code = []
#     bili_code = []
#     for friendCode in user_data[str(user_id)]["friendCode"]:
#         if get_uid_server(friendCode) == 1:
#             code.append(friendCode)
#         else:
#             bili_code.append(friendCode)
#     msg = ""
#     if len(code) > 0:
#         msg += "国服: " + "、".join(code) + "\n"
#     if len(bili_code) > 0:
#         msg += "B服: " + "、".join(bili_code)
#     await bot.send(ev, msg)

# @nonebot.on_startup
# async def startup():
#     load_user_data()


