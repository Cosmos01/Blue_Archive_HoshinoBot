import re
import time


def extract_calendar_data(server, data):
    if server == "jp":
        flag = "日服"
    else:
        flag = "国际服"
    event_list = []
    for item in data:
        try:
            title = item["title"]
            if flag not in title:
                continue
            if "卡池" in title:
                title = title.replace(flag, "")
            else:
                title = re.sub(r'【.*?】', "", title)
            start_time = item["begin_at"]
            end_time = item["end_at"]

            event_name = title

            event_list.append({
                'title': event_name,
                'start': start_time,
                'end': end_time,
            })
        except:
            continue
    return event_list


def transform_gamekee_calendar(server, data):
    data = extract_calendar_data(server, data)
    return data

