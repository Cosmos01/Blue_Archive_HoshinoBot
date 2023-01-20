import logging
from hoshino import aiorequests

async def get_img(server = "日"):
    if server == "國際":
        url = "http://91.149.236.232:40000/ba_raid_global.json"
    else:
        url = "http://91.149.236.232:40000/ba_raid_jp.json"
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


# 以下为本地获取方案,不能确保能够使用，可能需要修改
'''
import base64
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
mobileEmulation = {"userAgent":UA}
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('start-maximized')
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument('--disable-browser-side-navigation')
chrome_options.add_argument('enable-automation')
chrome_options.add_argument('--disable-infobars')
chrome_options.add_argument('enable-features=NetworkServiceInProcess')
chrome_options.add_experimental_option('mobileEmulation', mobileEmulation)

def img_gen(img):
    width, height = img.size
    draw = ImageDraw.Draw(img)
    draw.point((int(width / 2.5), int(height / 2.5)))
    buf = BytesIO()
    img = img.convert('RGB')
    img.save(buf, format='JPEG')
    img = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    return img

# 从巴哈姆特论坛获取总力攻略图，获取方式比较粗糙，可能会取错帖子。
# 实现方法：获取当前总力战top1的帖子的第二张图片。
# todo: 如果总力攻略贴固定，可以整理出每个总力对应帖子的url来获取图片

#仅http代理，示例：http://127.0.0.1:1080
proxy = "" 

async def get_raid_img(server="日"):
    driver = webdriver.Chrome(options=chrome_options)
    try:
        bbs_url = "https://forum.gamer.com.tw/B.php?bsn=38898&qt=2&subbsn=14"
        driver.get(bbs_url)
        pageData = driver.page_source
        soup = BeautifulSoup(pageData, "html.parser")
        articleUrl = ""
        for p in soup.find_all("p", "b-list__main__title is-highlight"):
            if server in p.text:
                articleUrl = "https://forum.gamer.com.tw/" + str(p.get("href"))
                break
        # articleUrl = "https://forum.gamer.com.tw/" + str(soup.find("p", "b-list__main__title is-highlight").get("href"))
        if articleUrl == "":
            driver.close()
            return ""
        driver.get(articleUrl)
        article = driver.page_source
        soup = BeautifulSoup(article, "html.parser").find("div", class_="c-post--manager")
        # 多了一个攻略图
        image_url1 = soup.find_all("a", "photoswipe-image")[1].get("href")
        async with aiohttp.request('GET', url=image_url1, allow_redirects=False, proxy=proxy) as resp:
            image_data = await resp.read()
        img = Image.open(BytesIO(image_data)).convert("RGBA")
        base64_str = img_gen(img)
        # 原一图流（懒得改别的地方，强行拼接了）
        if len(soup.find_all("a", "photoswipe-image")) > 2:
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
        driver.quit()
        return base64_str
    except Exception as e:
        print(e)
        driver.quit()
        return ""
        
'''
