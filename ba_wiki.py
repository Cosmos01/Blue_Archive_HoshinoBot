import base64
import hoshino
from hoshino import aiorequests

sv = hoshino.Service('ba_wiki', enable_on_default=True, visible=True, bundle='ba_wiki')


async def im2base64str(img_url):
    img = await aiorequests.get(img_url, timeout=5)
    img_cont = await img.content
    base64_str = f"base64://{base64.b64encode(img_cont).decode()}"
    return base64_str




base_url = "https://ba.gamekee.com/v1/content/detail/"
urls = {
    "cn_pools": "596691",
    "global_pools": "150045",
}


async def get_pools(server="cn"):
    url = base_url + urls[server + "_pools"]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Game-Alias": "ba"}
    r = await aiorequests.get(url, headers=headers)
    data = await r.json()
    msgs = []
    try:
        thumb = data["data"]["thumb"]
        thumb_urls = thumb.split(",")
        for thumb_url in thumb_urls:
            img_url = "https:" + thumb_url.strip("")
            b64img = await im2base64str(img_url)
            msgs.append(f"\n[CQ:image,file={b64img}]")
        if len(thumb_urls) == 0:
            for thumb_url in data["data"]["thumb_list"]:
                img_url = "https:" + thumb_url
                b64img = await im2base64str(img_url)
                msgs.append(f"\n[CQ:image,file={b64img}]")
    except Exception as e:
        msgs.append("获取千里眼图片失败")
        print(e)
    return msgs


@sv.on_suffix(("服千里眼", "服万里眼","服未来视"))
async def send_pools(bot, ev):
    server_name = ev.message.extract_plain_text().strip()
    if server_name == "国际":
        server = "global"
    elif server_name == "国":
        server = "cn"
    else:
        return

    msgs = await get_pools(server)
    for msg in msgs:
        await bot.send(ev, msg)
