import datetime
import logging
import re
import requests
from bs4 import BeautifulSoup

dic = {"Schedule": "スケジュール掉落加倍", "School Exchange": "学园交流会掉落加倍",
       "Commissions": "特别依赖掉落加倍", "Bounty Hunts": "指名手配掉落加倍"}

def fmt_event(event_name,event_text,type=0):
    year = datetime.datetime.now().strftime('%Y')
    event_text = event_text.replace(" "," ") #wdnmd
    event_time = re.findall(r"(\d+/\d+) - (\d+/\d+)", event_text)[0]
    if type == 1:
        start_time = year + "/" + event_time[0] + " 17:00"
        end_time = year + "/" + event_time[1] + " 10:00"
    else:
        start_time = year + "/" + event_time[0] + " 03:00"
        end_time = year + "/" + event_time[1] + " 03:00"

    return {'title': event_name, 'start': start_time, 'end': end_time}


def get_event_jp_name(page_url):
    infoPageUrl = "https://bluearchive.wiki" + page_url
    event_name = ""
    try:
        pageData = requests.get(url=infoPageUrl, allow_redirects=False,timeout=10).text
        specialEvent = BeautifulSoup(pageData, "html.parser")
        names = specialEvent.find("table").find_all("tr")
        for tr in names:
            if "apanese name" in tr.text:
                event_name = BeautifulSoup(str(tr), "html.parser").find("td").text.strip()
                break
        return event_name
    except:
        return event_name


def extract_calendar_data(html_text):
    event_list = []
    soup = BeautifulSoup(html_text, "html.parser")
    gacha_div = soup.find("div", "fp-item-current-gacha")
    raid_div = soup.find("div", "fp-item-current-raid")
    updates_div = soup.find("div", "fp-item-recent-updates")

    #gacha
    pickups = gacha_div.find_all("p")
    if len(pickups) > 0:
        for pickup in pickups:
            if pickup.find("img") or not pickup.find("a"):
                continue
            try:
                event_name = "本期卡池: " + str(pickup.find("a").get("title")).strip()
                event_list.append(fmt_event(event_name, pickup.text, type=1))
            except Exception as e:
                logging.warning(e)
                continue

    #raid
    if raid_div.find("span", id="currentraid"):
        try:
            event_name = str(raid_div.find("a").get("title")).strip()+"总力战"
            event_list.append(fmt_event(event_name,raid_div.text))
        except Exception as e:
            print(e)
            pass

       
    #updates
    events = updates_div.find_all("li")
    if len(events) > 0:
        for event in events:
            try:
                event = BeautifulSoup(str(event), "html.parser")
                if len(event.text.strip()) < 4:  #有时候会冒出奇奇怪怪的测试内容,过滤一下
                    continue

                if event.find("img"):  #带图片的一般是各种活动
                    event_name = ""
                    if event.find("a"):
                        page_url = event.find("a").get("href").strip()
                        event_name = get_event_jp_name(page_url)
                    if event_name == "":
                        if event.find("a"):
                            event_name = event.find("a").get("title")
                        else:
                            event_name = event.text
                    event_list.append(fmt_event(event_name,event.text,type=1))
                else:
                    other_event = BeautifulSoup(str(event), "html.parser")
                    if other_event.find("a") == None:  #排除测试项
                        continue
                    event_name = other_event.find("a").get("title")
                    if "Exercise" in event_name:  #演习
                        event_name = "演习"
                        event_list.append(fmt_event(event_name,other_event.text))
                        continue
                    if event_name == "Missions":  #任务
                        if "Normal" in other_event.text:
                            event_name = "普通图掉落加倍"
                        elif "Hard" in other_event.text:
                            event_name = "困难图掉落加倍"
                        event_list.append(fmt_event(event_name,other_event.text))
                        continue
                    if event_name not in dic:  #其他特殊活动
                        page_url = other_event.find("a").get("href").strip()
                        event_name = get_event_jp_name(page_url)
                        if event_name == "":
                            event_name = other_event.find("a").get("title")
                        event_list.append(fmt_event(event_name,other_event.text,type=1))
                        continue
                    event_list.append(fmt_event(dic[event_name],other_event.text))
            except Exception as e:
                logging.warning(e)
                continue

    return event_list


def transform_enwiki_calendar(data):
    data = extract_calendar_data(data)
    return data


