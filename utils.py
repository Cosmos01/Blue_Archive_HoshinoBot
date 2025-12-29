import asyncio
import json
import logging
import os
import base64
from io import BytesIO
from hoshino import aiorequests


def get_base_dir():
    return os.path.dirname(__file__)


def get_config():
    with open(os.path.join(get_base_dir(), 'config.json'), encoding='utf8') as f:
        config = json.load(f)
    return config


def get_base_url():
    try:
        config = get_config()
        return config["base_url"]
    except Exception as e:
        logging.error("配置获取失败，请检查插件目录下的config.json文件")
        logging.error(e)
        return "https://blue-archive.oss-cn-shanghai.aliyuncs.com/"


def img_to_base64str(img):
    io = BytesIO()
    img.save(io, 'png')
    base64_str = f"base64://{base64.b64encode(io.getvalue()).decode()}"
    return base64_str


def img_content_to_base64str(content):
    return f"base64://{base64.b64encode(content).decode()}"


def img_content_to_cqcode(content):
    return f"[CQ:image,file={img_content_to_base64str(content)}]"


async def get_json_data(url, data=None, headers=None, proxies=None):
    for i in range(2):
        try:
            if data is not None:
                res = await aiorequests.post(url, json=data, headers=headers, timeout=15, proxies=proxies)
            else:
                res = await aiorequests.get(url, headers=headers, timeout=15, proxies=proxies)
            if res.status_code == 200:
                data = await res.json()
                return data
        except Exception as e:
            logging.error(e)
            await asyncio.sleep(3)
            continue
    return None


async def get_img_content(url, headers=None, proxies=None):
    for i in range(2):
        try:
            r = await aiorequests.get(url, headers=headers, timeout=15)
            content = await r.content
            if r.status_code == 200:
                return content
        except Exception as e:
            logging.error(e)
            await asyncio.sleep(3)
            continue
    return None


def get_item(dic, key, value):
    for item in dic:
        if item[key] == value:
            return item
    return None


def get_default_server(gid):
    try:
        path = os.path.join(os.path.dirname(__file__), 'data.json')
        with open(path, encoding='utf8') as f:
            group_data = json.load(f)
    except Exception as e:
        logging.error(e)
        return "jp"
    if str(gid) not in group_data or len(group_data[str(gid)]["server_list"]) == 0:
        return "jp"
    server = group_data[str(gid)]["server_list"][0]
    if "jp" in server:
        return "jp"
    elif server == "cn":
        return "cn"
    elif "global" in server:
        return "global"
    return "jp"


def get_student_id(nickname):
    student_list = \
    json.load(open(os.path.join(os.path.dirname(__file__), 'gacha/_ba_data.json'), encoding="utf-8"))[
        "CHARA_NAME"]
    for student_id, student_names in student_list.items():
        if student_id == "1000":
            continue
        if nickname in student_names:
            return student_id
    return None
