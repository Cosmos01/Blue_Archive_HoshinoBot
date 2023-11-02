import hoshino
from .utils import *

sv = hoshino.Service('ba_twitter', enable_on_default=False, visible=True, bundle='碧蓝档案日服推特')


async def get_tweets():
    res = ""
    url = get_base_url() + "/ba_twitter.json"
    json_data = await get_json_data(url)
    if json_data is None:
        logging.warning("获取ba推特数据失败,请检查是否有更新或提交issues")
        return None
    data_list = json_data["data"]
    msg_list = []
    for data in data_list:
        msg = ""
        msg += data["msg"]
        if len(data["imgs"]) > 0:
            for img in data["imgs"]:
                msg += f"[CQ:image,file={img}]"
        msg_list.append(msg)
    return msg_list


@sv.scheduled_job('interval', minutes=5)
async def send_tweet():
    bot = hoshino.get_bot()
    available_group = await sv.get_enable_groups()
    if len(available_group) == 0:
        return
    msg_list = await get_tweets()
    if msg_list is not None and len(msg_list) > 0:
        for group_id in available_group:
            for msg in msg_list:
                await bot.send_group_msg(group_id=int(group_id), message=msg)
