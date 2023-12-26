import re
import time

def extract_calendar_data(server, data):
    if server == "jp":
        flag = "日服"
    elif server == "cn":
        flag = "国服"
    else:
        flag = "国际服"
    event_list = []
    for item in data:
        try:
            title = item["title"]
            start_time = item["begin_at"]
            end_time = item["end_at"]
            if flag not in item["pub_area"]:
                continue
            if "卡池" in title:
                title = title.replace(flag, "")
            elif "维护" in title:
                st = time.strftime("%m-%d %H:%M", time.localtime(start_time))
                et = time.strftime("%H:%M", time.localtime(end_time))
                title = title.replace(flag, "") + st + " ~ " + et
            else:
                title = re.sub(r'【.*?】', "", title)


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
