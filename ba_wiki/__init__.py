import hashlib
from hoshino import R, Service
from ..utils import *
from .raid_img import get_raid_img
from .student_info import get_student_info, get_student_list

sv = Service('ba_wiki', enable_on_default=True, visible=True, bundle='碧蓝档案攻略查询')

base_path = "bluearchive/wiki/"

arona_url = "https://arona.diyigemt.com/api/v2/image"
arona_img_url = "https://arona.cdn.diyigemt.com/image"
gamekee_url = "https://ba.gamekee.com/v1/content/detail/"

urls = {
    "cn_pools": "596691",
    "global_pools": "150045",
}


async def get_pools(server="cn"):
    url = gamekee_url + urls[server + "_pools"]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Game-Alias": "ba"}
    r = await aiorequests.get(url, headers=headers)
    data = await r.json()
    msgs = []
    try:
        thumb = data["data"]["thumb"]
        thumb_urls = thumb.split(",")
        for thumb_url in thumb_urls:
            img_url = "https:" + thumb_url.strip("")
            img_content = await get_img_content(img_url)
            msgs.append("\n" + img_content_to_cqcode(img_content))
        if len(thumb_urls) == 0:
            for thumb_url in data["data"]["thumb_list"]:
                img_url = "https:" + thumb_url
                img_content = await get_img_content(img_url)
                msgs.append("\n" + img_content_to_cqcode(img_content))
    except Exception as e:
        msgs.append("获取千里眼图片失败")
        logging.warning(e)
    return msgs


@sv.on_fullmatch(("国服千里眼", "国服未来视"))
async def send_pools_cn(bot, ev):
    server = "cn"
    msgs = await get_pools(server)
    for msg in msgs:
        await bot.send(ev, msg)


@sv.on_fullmatch(("国际服千里眼", "国际服未来视"))
async def send_pools_cn(bot, ev):
    server = "global"
    msgs = await get_pools(server)
    for msg in msgs:
        await bot.send(ev, msg)


def get_file_md5(file_path):
    with open(file_path, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()
        return md5


async def get_arona_img(name):
    msgs = []
    try:
        r = await aiorequests.get(arona_url, params={"name": name}, timeout=10)
        data = await r.json()
        if data["code"] != 200 and data["code"] != 101:
            msgs.append("请求错误: " + data["message"])
            logging.warning("请求错误: " + str(data))
            return msgs
        if "data" not in data or data["data"] is None or len(data["data"]) == 0:
            msgs.append("未找到相关内容")
            return msgs
        if len(data["data"]) > 1 or data["message"] == "Fuzzy Search":
            msgs = await get_arona_img(data["data"][0]["name"])
            if len(data["data"]) > 1:
                msg = "其他可能的查询结果："
                for item in data["data"][1:]:
                    msg += f'\n{item["name"]}'
                msgs.append(msg)
            return msgs

        msgs.append(f"查询结果：{data['data'][0]['name']}")
        path = data["data"][0]["content"]
        md5 = data["data"][0]["hash"]

        # 纯文本的情况(我也没遇到过)
        if data["data"][0] == "plain":
            msgs.append(path)
            return msgs

        flag = True
        if R.img(base_path + path).exist:
            local_md5 = get_file_md5(R.img(base_path + path).path)
            if local_md5 == md5:
                flag = False
        if flag:
            # 判断文件夹是否存在
            target_dir = os.path.dirname(R.img(base_path + path).path)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            # 获取和保存图片
            img_url = arona_img_url + path
            r = await aiorequests.get(img_url, timeout=10)
            img_cont = await r.content
            with open(R.img(base_path + path).path, 'wb') as f:
                f.write(img_cont)
        msgs.append(R.img(base_path + path).cqcode)
    except Exception as e:
        logging.warning(e)
        msgs.append("查询失败")
    return msgs


@sv.on_prefix(("ba攻略", "攻略查询", "/攻略"))
async def send_arona(bot, ev):
    cmd = ev.message.extract_plain_text().strip()
    if not cmd:
        await bot.send(ev, "请输入要查询的内容，如：ba攻略杂图")
        return
    msgs = await get_arona_img(cmd)
    for msg in msgs:
        await bot.send(ev, msg)


@sv.on_rex(r'([日国國美台])?[际際]?[服]?总力一图流')
async def raid_img(bot, ev):
    server_name = ev['match'].group(1)
    if server_name == "日" or server_name is None:
        server_name = "日"
    else:
        server_name = "國際"
    raid_data = await get_raid_img(server_name)
    if raid_data == "":
        await bot.send(ev, "获取图片失败")
        return
    await bot.send(ev, f'[CQ:image,file={raid_data}]')


@sv.on_prefix('ba查询')
async def send_student_info(bot, ev):
    nickname = ev.message.extract_plain_text()
    msgs = await get_student_info(nickname)
    if msgs is None:
        await bot.send(ev, "获取角色信息失败")
        return
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


@sv.on_fullmatch('ba角色列表')
async def send_student_list(bot, ev):
    msgs = await get_student_list()
    if msgs is None:
        await bot.send(ev, "获取角色列表失败")
        return
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


@sv.on_rex(r'^(?P<server>[日国Bb])?服?第?(?P<num>\d+)?期?(?P<type>(总力|大决))战?排名')
async def send_rank(bot, ev):
    server = ev['match'].group('server')
    if server is None:
        server = get_default_server(ev.group_id)
    num = ev['match'].group('num')
    rtype = ev['match'].group('type')
    if server == "国" or server == "cn":
        server = "cn"
    elif server == "B" or server == "b":
        server = "bili"
    else:
        server = "jp"
    if num is None:
        num = "last"
    if rtype == "总力":
        rtype = "raid"
    else:
        rtype = "eraid"
    if server != "jp" and rtype == "eraid":
        server = "jp"
    url = get_base_url() + f"rank/{server}/{rtype}/{num}.png"
    img = await get_img_content(url)
    if img is None:
        await bot.send(ev, "获取失败，请确认服务器和期数是否存在")
        return
    await bot.send(ev, img_content_to_cqcode(img))
