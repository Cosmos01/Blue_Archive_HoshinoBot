import datetime
import requests

common = "https://lonqie.github.io/SchaleDB/data/common.json"
localization = "https://lonqie.github.io/SchaleDB/data/cn/localization.json"
raids = "https://lonqie.github.io/SchaleDB/data/raids.min.json"
student_cn = "https://lonqie.github.io/SchaleDB/data/cn/students.min.json"
student_jp = "https://lonqie.github.io/SchaleDB/data/jp/students.min.json"

def get_item(dict,key,value):
    for item in dict:
        if item[key] == value:
            return item
    return None


def get_json_data(url):
    for i in range(3):
        try:
            res = requests.get(url,timeout=15)
            if res.status_code == 200:
                return res.json()
        except:
            continue
    return None

def extract_calendar_data(server):
    event_list = []

    common_data = get_json_data(common)
    student_data = get_json_data(student_cn)
    localization_data = get_json_data(localization)
    raid_data = get_json_data(raids)
    if common_data == None or student_data == None or localization_data == None or raid_data == None:
        return None


    if server == "jp":
        data = common_data["regions"][0]
    else:
        data = common_data["regions"][1]


    #gacha
    for gacha in data["current_gacha"]:
        characters = gacha["characters"]
        for character in characters:
            stu_info = get_item(student_data,"Id",character)
            title = "本期卡池: " + stu_info["Name"]
            start_time = datetime.datetime.fromtimestamp(gacha["start"]).strftime("%Y/%m/%d %H:%M")
            end_time = datetime.datetime.fromtimestamp(gacha["end"]).strftime("%Y/%m/%d %H:%M")
            event_list.append({'title': title, 'start': start_time, 'end': end_time})

    #event
    for event in data["current_events"]:
        event_rerun = ""
        event_id = event["event"]
        # 复刻活动似乎是在原id前面加上10
        if event_id > 1000:
            event_id = str(event_id)[2:]
            event_rerun = "(复刻)"
        event_name = localization_data["EventName"][str(event_id)] + event_rerun
        start_time = datetime.datetime.fromtimestamp(event["start"]).strftime("%Y/%m/%d %H:%M")
        end_time = datetime.datetime.fromtimestamp(event["end"]).strftime("%Y/%m/%d %H:%M")
        event_list.append({'title': event_name, 'start': start_time, 'end': end_time})

    #raid
    for raid in data["current_raid"]:
        raid_id = raid["raid"]
        title = ""
        #总力
        if raid_id < 999:
            raid_info = get_item(raid_data["Raid"], "Id", raid_id)
            if raid_info["NameCn"] != None:
                title = "总力战: " + raid_info["NameCn"]
            else:
                title = "总力战: " + raid_info["NameJp"] + f'({raid_info["PathName"]})'
            if "terrain" in raid:
                title = title + f'({raid["terrain"]})'
        #演习
        if raid_id > 999 and raid_id < 99999:
            dungeon_types = {"Shooting": "射击", "Defense": "防御", "Destruction": "突破"}
            raid_info = get_item(raid_data["TimeAttack"], "Id", raid_id)
            title = raid_info["DungeonType"]
            if raid_info["DungeonType"] in dungeon_types:
                title = dungeon_types[raid_info["DungeonType"]]
            title += "演习"
            if "Terrain" in raid_info:
                title = title + f'({raid_info["Terrain"]})'
        #世界boss
        if raid_id > 800000 and raid_id < 900000:
            raid_info = get_item(raid_data["WorldRaid"], "Id", raid_id)
            title = raid_info["NameJp"]
            if raid_info["NameCn"] != None:
                title = raid_info["NameCn"]

        if title != "":
            start_time = datetime.datetime.fromtimestamp(raid["start"]).strftime("%Y/%m/%d %H:%M")
            end_time = datetime.datetime.fromtimestamp(raid["end"]).strftime("%Y/%m/%d %H:%M")
            event_list.append({'title': title, 'start': start_time, 'end': end_time})
    return event_list


def transform_schaledb_calendar(server):
    data = extract_calendar_data(server)
    return data
