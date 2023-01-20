import logging
import hoshino
from hoshino import aiorequests

sv = hoshino.Service('ba_twitter', enable_on_default=False, visible=True, bundle='ba_twitter')

async def get_tweets():
    try:
        res = await aiorequests.get("http://91.149.236.232:40000/ba_twitter.json",timeout=20)
        return res
    except:
        return None

async def get_msgs():
    res = ""
    for i in range(6):
        res = await get_tweets()
        if res != None:
            break
        if i == 5:
            logging.warning("获取ba推特数据失败,请检查是否有更新或提交issues")
            return None
    json_data = await res.json()
    data_list = json_data["data"]
    msg_list = []
    for data in data_list:
        msg = ""
        msg += data["msg"]
        if len(data["imgs"]) > 0:
            for img in data["imgs"]:
                msg += f"[CQ:image,file={img}]"
        msg_list.append(msg)
    return msg_list

#顶不住了，改五分钟
@sv.scheduled_job('cron', minute='*/5')
async def send_tweet():
    bot = hoshino.get_bot()
    available_group = await sv.get_enable_groups()
    msg_list = await get_msgs()
    if msg_list != None and len(msg_list) > 0:
        for group_id in available_group:
            for msg in msg_list:
                await bot.send_group_msg(group_id=int(group_id), message=msg)




# 以下为本地获取推特方案
'''
import datetime
import base64
import json
from pygtrans import Translate
import os
import tweepy
import hoshino
from hoshino import aiorequests

sv = hoshino.Service('ba_twitter', enable_on_default=False, visible=True, bundle='ba_twitter')
cfg_path = os.path.join(os.path.dirname(__file__), 'twitter.json')
rep1 = {"ブルアカ": "Blue Archive"}  # 在日语时替换，防止结合语境的奇奇怪怪翻译
rep2 = {"\n\n": "\n", "\r\n\r\n": "\r\n", "蓝色档案": "碧蓝档案", "blue存档": "碧蓝档案", "Blue 存档": "碧蓝档案", "皮卡招募": "学生招募", "皮卡招聘": "学生招募","布鲁赤井部":"碧蓝档案"}  # 生草翻译强行替换，自行添加


def get_client(cfg):
    # 推特api密钥，自行获取填写
    bearer_token = cfg["bearer_token"]
    consumer_key = cfg["consumer_key"]
    consumer_secret = cfg["consumer_secret"]
    access_token = cfg["access_token"]
    access_token_secret = cfg["access_token_secret"]

    client = tweepy.Client(bearer_token=bearer_token,
                           access_token=access_token,
                           access_token_secret=access_token_secret,
                           consumer_key=consumer_key,
                           consumer_secret=consumer_secret)
    return client


async def im2base64str(img_url):
    img = await aiorequests.get(img_url)
    img_cont = await img.content
    base64_str = f"base64://{base64.b64encode(img_cont).decode()}"
    return base64_str


async def get_tweets(client):
    msg_list = []
    start_time = (datetime.datetime.utcnow() - datetime.timedelta(minutes=3.02)).isoformat("T")[:-4] + "Z"
    tweets = client.get_users_tweets(id=1237586987969687555, start_time=start_time,
                                     tweet_fields=['created_at', 'entities'], media_fields=["url", "preview_image_url"],
                                     expansions="attachments.media_keys", exclude=["retweets", "replies"])
    if not tweets.data:
        return msg_list

    media = {m["media_key"]: m for m in tweets.includes['media']} if "media" in tweets.includes else []
    for tweet in tweets.data:
        msg = ""
        text = str(tweet.text)
        # 替换文本
        for k, v in rep1.items():
            text = text.replace(k, v)
        # 生草翻译，N114514可以注释这三行
        res = Translate().translate(text,source="ja",fmt="text")
        if res != None:
            text = res.translatedText
        # 替换文本
        for k, v in rep2.items():
            text = text.replace(k, v)
        msg = msg + text
        include_img = False
        if 'attachments' in tweet.data and 'media_keys' in tweet.data['attachments']:
            media_keys = tweet.data['attachments']['media_keys']
            for media_key in media_keys:
                if media[media_key].url and media[media_key].type == "photo":
                    b64img = await im2base64str(media[media_key].url)
                    msg = msg + f"\n[CQ:image,file={b64img}]"
                    include_img = True
                if media[media_key].preview_image_url:
                    b64img = await im2base64str(media[media_key].preview_image_url)
                    msg = msg + f"\n[CQ:image,file={b64img}]"
                    include_img = True
        if not include_img and "urls" in tweet.entities:  # 实在没图片了拿来凑数
            for url in tweet.entities['urls']:
                if 'images' in url:
                    b64img = await im2base64str(url['images'][0]['url'])
                    msg = msg + f"\n[CQ:image,file={b64img}]"
        msg_list.append(msg)
    return msg_list


@sv.scheduled_job('cron', minute='*/3')
async def send_tweet():
    bot = hoshino.get_bot()
    if os.path.exists(cfg_path):
        cfg = json.load(open(cfg_path, 'r', encoding="utf-8"))
    else:
        return
    available_group = await sv.get_enable_groups()
    client = get_client(cfg)
    msg_list = await get_tweets(client)
    if len(msg_list) > 0:
        for group_id in available_group:
            for msg in msg_list:
                await bot.send_group_msg(group_id=int(group_id), message=msg)

'''
