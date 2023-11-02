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
        return "http://124.223.25.80:40000/"


def img_to_base64str(img):
    io = BytesIO()
    img.save(io, 'png')
    base64_str = f"base64://{base64.b64encode(io.getvalue()).decode()}"
    return base64_str


def img_content_to_base64str(content):
    return f"base64://{base64.b64encode(content).decode()}"


def img_content_to_cqcode(content):
    return f"[CQ:image,file={img_content_to_base64str(content)}]"


async def get_json_data(url, proxies=None):
    for i in range(2):
        try:
            res = await aiorequests.get(url, timeout=15, proxies=proxies)
            if res.status_code == 200:
                data = await res.json()
                return data
        except Exception as e:
            logging.error(e)
            await asyncio.sleep(3)
            continue
    return None


async def get_img_content(url, proxies=None):
    for i in range(2):
        try:
            r = await aiorequests.get(url, timeout=15)
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


