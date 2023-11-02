import os
import re
from hoshino import R
from ..utils import *

base_url = get_base_url()
students_url = base_url + "/SchaleDB/data/cn/students.json"
localization_cn_url = base_url + "/SchaleDB/data/cn/localization.json"
localization_jp_url = base_url + "/SchaleDB/data/jp/localization.json"

localization_cn_data = {}


def get_student_id(student_list, nickname):
    for student_id, student_names in student_list.items():
        if nickname in student_names:
            return student_id
    return None


def fmt_desc(match):
    global localization_cn_data
    buffs = localization_cn_data["BuffName"]

    buff_types = {"b": "Buff_", "d": "Debuff_", "c": "CC_", "s": "Special_"}
    if match.group(1) not in buff_types:
        return match.group()

    buff_name = buff_types[match.group(1)] + match.group(2)
    if buff_name not in buffs:
        return buff_name
    return buffs[buff_name]


parameters = []


def fmt_para(match):
    str = "UNKNOW"
    try:
        global parameters
        if parameters == []:
            return str
        str = f'{parameters[int(match.group(1)) - 1][0]}({parameters[int(match.group(1)) - 1][-1]})'
        return str
    except Exception as e:
        print(e)
        return str


def fmt_para_ex(match):
    str = "UNKNOW"
    try:
        global parameters
        if not parameters:
            return str
        str = f'{parameters[int(match.group(1)) - 1][0]}({parameters[int(match.group(1)) - 1][4]})'
        return str
    except Exception as e:
        print(e)
        return str


async def get_student_list():
    msg_list = []
    student_list = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gacha/_ba_data.json'), encoding="utf-8"))[
        "CHARA_NAME"]
    for student_id, student_names in student_list.items():
        if student_id == "1000":
            continue
        # 头像
        img_path = R.img(f'bluearchive/unit/icon_unit_{str(student_id)}.png')
        if not img_path.exist:
            img_url = f'{base_url}/Blue_Archive_HoshinoBot/bluearchive/unit/icon_unit_{str(student_id)}.png'
            content = await get_img_content(img_url)
            if content is not None:
                with open(img_path.path, 'wb') as f:
                    f.write(content)
                res = img_content_to_cqcode(content)
            else:
                res = R.img(f'bluearchive/unit/icon_unit_1000.png').cqcode
        else:
            res = img_path.cqcode

        # 名字
        names = ""
        for name in student_list[str(student_id)]:
            names += name + "、"
        res = res + "\n" + names[:-1]
        msg_list.append(res)

    return msg_list


async def get_student_info(nickname):
    student_list = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gacha/_ba_data.json'), encoding="utf-8"))[
        "CHARA_NAME"]
    student_id = get_student_id(student_list, nickname)
    if student_id is None:
        return ["未找到该角色,使用“ba角色列表”命令查看所有角色"]
    student_id = int(student_id)

    global localization_cn_data
    student_data = await get_json_data(students_url)
    localization_cn_data = await get_json_data(localization_cn_url)
    localization_jp_data = await get_json_data(localization_jp_url)
    if student_data is None or localization_cn_data is None or localization_jp_data is None:
        return ["获取数据失败"]

    msg_list = []

    base_info = get_item(student_data, "Id", student_id)

    # 头像
    res = R.img(f'bluearchive/unit/icon_unit_{str(student_id)}.png')
    if not res.exist:
        try:
            img_content = await get_img_content(f'{base_url}/SchaleDB/images/student/icon/{base_info["CollectionTexture"]}.png')
            res = img_content_to_cqcode(img_content)
        except Exception as e:
            logging.warning("获取角色头像失败")
            logging.warning(e)
            res = R.img(f'bluearchive/unit/icon_unit_1000.png').cqcode
    else:
        res = res.cqcode
    msg_list.append(res)

    # 名字
    names = base_info["FamilyName"] + base_info["PersonalName"] + "、"
    for name in student_list[str(student_id)]:
        names = names + name + "、"
    msg_list.append(names[:-1])

    # 背景
    school = localization_cn_data["School"][base_info["School"]]
    school_jp = localization_jp_data["School"][base_info["School"]]
    club = localization_cn_data["Club"][base_info["Club"]]
    club_jp = localization_jp_data["Club"][base_info["Club"]]

    msg_list.append(f'学校:{school_jp}({school})\n社团:{club_jp}({club})\n'
                    f'{base_info["SchoolYear"]}  {base_info["CharacterAge"]}\n生日:{base_info["Birthday"]}')

    # 属性
    bullet_types = {"Explosion": "爆破", "Pierce": "穿甲", "Mystic": "神秘"}
    equipment_types = {"Gloves": "手套", "Bag": "包", "Watch": "手表", "Shoes": "鞋", "Badge": "徽章",
                       "Necklace": "项链", "Hat": "帽子", "Hairpin": "发卡", "Charm": "饰品"}
    armor_types = {"HeavyArmor": "重甲", "LightArmor": "轻甲", "Unarmed": "神秘甲"}
    equipments = ""
    for equipment in base_info["Equipment"]:
        equipments += (equipment_types[equipment] if equipment in equipment_types else equipment) + "、"

    adaptation = f'地形适应: 市街:{str(base_info["StreetBattleAdaptation"])} / 户外:{str(base_info["OutdoorBattleAdaptation"])} / 室内:{str(base_info["IndoorBattleAdaptation"])}\n'
    bullet_type = bullet_types[base_info["BulletType"]] if base_info["BulletType"] in bullet_types else base_info[
        "BulletType"]
    armor_type = armor_types[base_info["ArmorType"]] if base_info["ArmorType"] in armor_types else base_info[
        "ArmorType"]

    type = f'攻击类型: {bullet_type}\n护甲类型: {armor_type}\n武器类型: {base_info["WeaponType"]}\n位置: {base_info["Position"]}\n' \
           f'装备: {equipments[:-1]}'

    msg_list.append(adaptation + type)

    # 面板
    StabilityPoint = str(base_info["StabilityPoint"])
    AttackPower1 = str(base_info["AttackPower1"])
    AttackPower100 = str(base_info["AttackPower100"])
    MaxHP1 = str(base_info["MaxHP1"])
    MaxHP100 = str(base_info["MaxHP100"])
    DefensePower1 = str(base_info["DefensePower1"])
    DefensePower100 = str(base_info["DefensePower100"])
    HealPower1 = str(base_info["HealPower1"])
    HealPower100 = str(base_info["HealPower100"])
    DodgePoint = str(base_info["DodgePoint"])
    AccuracyPoint = str(base_info["AccuracyPoint"])
    CriticalPoint = str(base_info["CriticalPoint"])
    CriticalDamageRate = str(int(base_info["CriticalDamageRate"] / 100)) + "%"
    AmmoCount = str(base_info["AmmoCount"])
    AmmoCost = str(base_info["AmmoCost"])
    Range = str(base_info["Range"])
    RegenCost = str(base_info["RegenCost"])

    msg_list.append(f"HP:{MaxHP1}→{MaxHP100}		攻击:{AttackPower1}→{AttackPower100}\n"
                    f"防御:{DefensePower1}→{DefensePower100}		治愈:{HealPower1}→{HealPower100}\n"
                    f"闪避:{DodgePoint}		命中:{AccuracyPoint}\n"
                    f"暴击:{CriticalPoint}		暴伤:{CriticalDamageRate}\n"
                    f"弹药:{AmmoCount}		耗弹:{AmmoCost}\n"
                    f"安定:{StabilityPoint}		范围:{Range}\n"
                    f"回费:{RegenCost}\n")

    # 技能
    global parameters
    skill_desc = ""
    skills = base_info["Skills"]
    for skill in skills:
        if "Name" not in skill:
            continue
        skill_desc += skill["SkillType"] + "\n"
        skill_desc += skill["Name"]
        parameters = skill["Parameters"]
        if skill["SkillType"] == "ex":
            skill_desc += f' (Cost:{str(skill["Cost"][0])}→{str(skill["Cost"][-1])})'
            desc = re.sub(r'<\?(\d+)>', fmt_para_ex, skill["Desc"])
        else:
            desc = re.sub(r'<\?(\d+)>', fmt_para, skill["Desc"])
        desc = re.sub(r'<(\w):(\w+)>', fmt_desc, desc)
        skill_desc += "\n" + desc + "\n\n"

    msg_list.append(skill_desc)

    # 角评
    # 暂时停用该功能，使用arona api代替
    # img = R.img(f'bluearchive/info/info_{str(student_id)}.png')
    # if not img.exist:
    #     if not R.img(f'bluearchive/info/').exist:
    #         os.mkdir(R.img(f'bluearchive/info/').path)
    #     print("正在获取角评图片：" + str(student_id))
    #     try:
    #         r = await aiorequests.get(f'{base_url}/Blue_Archive_HoshinoBot/bluearchive/info/info_{str(student_id)}.png',
    #                                   timeout=20)
    #         content = await r.content
    #         if r.status_code == 200:
    #             with open(img.path, 'wb') as f:
    #                 f.write(content)
    #             base64_str = f"base64://{base64.b64encode(content).decode()}"
    #             res = f"[CQ:image,file={base64_str}]"
    #             msg_list.append(res)
    #         elif r.status_code == 404:
    #             msg_list.append(f'角评图片不存在')
    #     except Exception as e:
    #         msg_list.append(f'角评图片获取失败: {e}')
    #         pass
    # else:
    #     msg_list.append(img.cqcode)
    #     try:
    #         r = await aiorequests.head(
    #             f'{base_url}/Blue_Archive_HoshinoBot/bluearchive/info/info_{str(student_id)}.png', timeout=20)
    #         if "Last-Modified" in r.headers:
    #             last = r.headers.get("Last-Modified")
    #             if os.path.getmtime(img.path) < time.mktime(
    #                     time.strptime(last, "%a, %d %b %Y %H:%M:%S GMT")) + 8 * 60 * 60:
    #                 r = await aiorequests.get(
    #                     f'{base_url}/Blue_Archive_HoshinoBot/bluearchive/info/info_{str(student_id)}.png', timeout=20)
    #                 content = await r.content
    #                 if r.status_code == 200:
    #                     with open(img.path, 'wb') as f:
    #                         f.write(content)
    #         else:
    #             msg_list.append(f'角评图片更新出错: Last-Modified不存在')
    #     except Exception as e:
    #         msg_list.append(f'角评图片获取失败: {e}')
    #         pass

    return msg_list
