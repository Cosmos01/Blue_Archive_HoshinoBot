import logging
from hoshino import aiorequests

async def get_img(server = "日"):
    if server == "國際":
        url = "http://45.86.70.253:40000/ba_raid_global.json"
    else:
        url = "http://45.86.70.253:40000/ba_raid_jp.json"
    try:
        res = await aiorequests.get(url,timeout=20)
        json_data = await res.json()
        return json_data["raid_img"]
    except:
        return None

async def get_raid_img(server):
    img = ""
    for i in range(6):
        img = await get_img(server)
        if img != None:
            break
        if i == 5:
            logging.warning("获取ba_raid数据失败,请检查是否有更新或提交issues")
            return None
    return img


# 以下为本地获取方案
'''
import base64
import aiohttp
from bs4 import BeautifulSoup

# 从巴哈姆特论坛获取总力攻略图，获取方式比较粗糙，可能会取错帖子。
# 实现方法：获取当前总力战top1的帖子的第二张图片。
# todo: 如果总力攻略贴固定，可以整理出每个总力对应帖子的url来获取图片

#仅http代理，示例：http://127.0.0.1:1080
proxy = "" 

async def get_raid_img(server="日"):
    try:
        bbs_url = "https://forum.gamer.com.tw/B.php?bsn=38898&qt=2&subbsn=14"
        async with aiohttp.request('GET', url=bbs_url, allow_redirects=False, proxy=proxy) as resp:
            pageData = await resp.text()
        soup = BeautifulSoup(pageData, "html.parser")
        articleUrl = ""
        for p in soup.find_all("p", "b-list__main__title is-highlight"):
            if server in p.text:
                articleUrl = "https://forum.gamer.com.tw/" + str(p.get("href"))
                break
        # articleUrl = "https://forum.gamer.com.tw/" + str(soup.find("p", "b-list__main__title is-highlight").get("href"))
        if articleUrl == "":
            return ""
        async with aiohttp.request('GET', url=articleUrl, allow_redirects=False, proxy=proxy) as resp:
            article = await resp.text()
        soup = BeautifulSoup(article, "html.parser").find("div", class_="c-post--manager")
        # 多了一个攻略图
        image_url1 = soup.find_all("a", "photoswipe-image")[1].get("href")
        async with aiohttp.request('GET', url=image_url1, allow_redirects=False, proxy=proxy) as resp:
            image_data = await resp.read()
        img = Image.open(BytesIO(image_data)).convert("RGBA")
        base64_str = img_gen(img)
        # 原一图流（懒得改别的地方，强行拼接了）
        image_url2 = soup.find_all("a", "photoswipe-image")[2].get("href")
        async with aiohttp.request('GET', url=image_url2, allow_redirects=False, proxy=proxy) as resp:
            image_data2 = await resp.read()
        img = Image.open(BytesIO(image_data2)).convert("RGBA")
        base64_str2 = img_gen(img)
        base64_str = f"{base64_str}][CQ:image,file={base64_str2}"
        # 两个服同时开的情况会有两个一图流
        if len(soup.find_all("a", "photoswipe-image")) > 3:
            image_url3 = soup.find_all("a", "photoswipe-image")[3].get("href")
            async with aiohttp.request('GET', url=image_url3, allow_redirects=False, proxy=proxy) as resp:
                image_data3 = await resp.read()
            img = Image.open(BytesIO(image_data3)).convert("RGBA")
            base64_str3 = img_gen(img)
            base64_str = f"{base64_str}][CQ:image,file={base64_str3}"
        return base64_str
    except Exception as e:
        print(e)
        return ""
        
'''
