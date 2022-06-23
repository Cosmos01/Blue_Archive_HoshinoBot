import datetime
import base64
import json
import urllib
import urllib.request
import urllib.parse
import requests
import execjs
import os
from urllib.parse import quote
import tweepy
import hoshino
from hoshino.typing import CQEvent
from hoshino import aiorequests, priv

sv = hoshino.Service('ba_twitter', enable_on_default=False, visible=True, bundle='ba_twitter')
cfg_path = os.path.join(os.path.dirname(__file__), 'twitter.json')
rep1 = {"ブルアカ": "Blue Archive"}  # 在日语时替换，防止结合语境的奇奇怪怪翻译
rep2 = {"\n\n": "\n", "\r\n\r\n": "\r\n", "蓝色档案": "碧蓝档案", "Blue 存档": "碧蓝档案", "皮卡招募": "学生招募", "皮卡招聘": "学生招募","布鲁赤井部":"碧蓝档案"}  # 生草翻译强行替换，自行添加


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
    start_time = (datetime.datetime.utcnow() - datetime.timedelta(minutes=3.05)).isoformat("T")[:-4] + "Z"
    tweets = client.get_users_tweets(id=1237586987969687555, start_time=start_time,
                                     tweet_fields=['created_at', 'entities'], media_fields=["url", "preview_image_url"],
                                     expansions="attachments.media_keys", exclude=["retweets", "replies"])
    if not tweets.data:
        return msg_list

    media = {m["media_key"]: m for m in tweets.includes['media']} if "media" in tweets.includes else []
    for tweet in tweets.data:
        msg = ""
        text = str(tweet.text)
        for k, v in rep1.items():
            text = text.replace(k, v)
        text = Google().translate(text)  # 生草翻译，N114514可以注释此行
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


#下面是谷歌翻译相关内容
class Google():
    def __init__(self):
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
        self.url = 'http://translate.google.cn/translate_a/single'
        self.session = requests.Session()
        self.session.keep_alive = False

    def getTk(self, text):
        return self.get_ctx().call("TL", text)

    def get_ctx(self):
        ctx = execjs.compile(""" 
        function TL(a) { 
        var k = ""; 
        var b = 406644; 
        var b1 = 3293161072; 
        var jd = "."; 
        var $b = "+-a^+6"; 
        var Zb = "+-3^+b+-f"; 
        for (var e = [], f = 0, g = 0; g < a.length; g++) { 
            var m = a.charCodeAt(g); 
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023), 
            e[f++] = m >> 18 | 240, 
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224, 
            e[f++] = m >> 6 & 63 | 128), 
            e[f++] = m & 63 | 128) 
        } 
        a = b; 
        for (f = 0; f < e.length; f++) a += e[f], 
        a = RL(a, $b); 
        a = RL(a, Zb); 
        a ^= b1 || 0; 
        0 > a && (a = (a & 2147483647) + 2147483648); 
        a %= 1E6; 
        return a.toString() + jd + (a ^ b) 
    }; 
    function RL(a, b) { 
        var t = "a"; 
        var Yb = "+"; 
        for (var c = 0; c < b.length - 2; c += 3) { 
            var d = b.charAt(c + 2), 
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d), 
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d; 
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d 
        } 
        return a 
    } 
    """)
        return ctx

    def buildUrl(self,text,tk):
        baseUrl = 'http://translate.google.cn/translate_a/single'
        baseUrl += '?client=webapp&'  #这里client改成webapp后翻译的效果好一些 t翻译的比较差 ..
        baseUrl += 'sl=auto&'
        baseUrl += 'tl=zh-CN&'
        baseUrl += 'hl=ja&'
        baseUrl += 'dt=at&'
        baseUrl += 'dt=bd&'
        baseUrl += 'dt=ex&'
        baseUrl += 'dt=ld&'
        baseUrl += 'dt=md&'
        baseUrl += 'dt=qca&'
        baseUrl += 'dt=rw&'
        baseUrl += 'dt=rm&'
        baseUrl += 'dt=ss&'
        baseUrl += 'dt=t&'
        baseUrl += 'ie=UTF-8&'
        baseUrl += 'oe=UTF-8&'
        baseUrl += 'clearbtn=1&'
        baseUrl += 'otf=1&'
        baseUrl += 'pc=1&'
        baseUrl += 'srcrom=0&'
        baseUrl += 'ssel=0&'
        baseUrl += 'tsel=0&'
        baseUrl += 'kc=2&'
        baseUrl += 'tk=' + str(tk) + '&'
        content=urllib.parse.quote(text)
        baseUrl += 'q=' + content
        return baseUrl

    def getHtml(self, session, url, headers):
        try:
            html = session.get(url, headers=headers, timeout=5)
            return html.json()
        except Exception as e:
            return None

    def translate(self, text):
        tk = self.getTk(text)
        url = self.buildUrl(text, tk)
        result = self.getHtml(self.session, url, self.headers)
        if result != None:
            s=''
            for i in result[0]:
                if i[0]!=None:
                    s+=i[0]
            return s
        else:
            print('谷歌翻译失败 ')
            return text
