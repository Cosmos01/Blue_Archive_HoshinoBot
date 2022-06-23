from os import truncate
import re
from bs4 import BeautifulSoup
from html.parser import HTMLParser



def extract_calendar_data(html_text):
    event_list = []

    items = BeautifulSoup(html_text, "html.parser").find_all("div",class_="activity")
    for item in items:
        try:
            start_time = str(item.get("data-start")).replace("维护后","17:00")
            end_time = str(item.get("data-end")).replace("维护前","11:00")
            event_name = item.find("p",class_="activity__name").text

            event_list.append({
                'title': event_name,
                'start': start_time,
                'end': end_time,
            })
        except:
            continue
    return event_list


def transform_biliwiki_calendar(data):
    data = extract_calendar_data(data)
    return data


