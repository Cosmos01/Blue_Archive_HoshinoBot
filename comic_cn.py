# import os
# import json
# import base64
# import aiohttp
# import traceback
# import hoshino
# from bs4 import BeautifulSoup

# url = "https://wiki.biligame.com/bluearchive/%E7%A2%A7%E8%93%9D%E6%A1%A3%E6%A1%88%EF%BC%81"
# path = os.path.join(os.path.dirname(__file__), 'comic_cn.json')

# sv = hoshino.Service('ba_comic_cn', enable_on_default=False, visible=True, bundle='ba_comic_cn')

# def save_data(urls):
#     try:
#         with open(path, 'w', encoding='utf8') as f:
#             json.dump(urls, f, ensure_ascii=False, indent=2)
#     except:
#         traceback.print_exc()


# async def get_comic_url():
#     urls = []
#     async with aiohttp.request('GET', url=url, allow_redirects=False) as resp:
#         pageData = await resp.text()
#     divs = BeautifulSoup(pageData, "html.parser").select("div[class='section-list']")
#     for div in divs:
#         img_url = div.find_all("div", class_="popup-content")[-1].find("img").get("srcset").split(",")[1].replace("2x",
#                                                                                                                   "").strip()
#         urls.append(img_url)
#     return urls


# @sv.scheduled_job('cron', hour='*/1')
# async def send_comic():
#     updated = False
#     urls = await get_comic_url()
#     local_urls = json.load(open(path, 'r', encoding='utf8'))
#     for url in urls:
#         if url not in local_urls:
#             async with aiohttp.request('GET', url=url, allow_redirects=False) as resp:
#                 image_data = await resp.read()
#             base64_str = f"base64://{base64.b64encode(image_data).decode()}"
#             msg = f"[CQ:image,file={base64_str}]"
#             await sv.broadcast(msg, 'ba comic cn', 0.5)
#             updated = True
#     if updated:
#         save_data(urls)
