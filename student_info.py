import base64
import json
import os
import re

import requests
from hoshino import R


students_url = "https://lonqie.github.io/SchaleDB/data/cn/students.json"
localization_cn_url = "https://lonqie.github.io/SchaleDB/data/cn/localization.json"
localization_jp_url = "https://lonqie.github.io/SchaleDB/data/jp/localization.json"
common_url = "https://lonqie.github.io/SchaleDB/data/common.json"

localization_cn_data = {}

def get_item(dict,key,value):
    for item in dict:
        if item[key] == value:
            return item
    return None

def get_student_id(student_list,nickname):
    for student_id,student_names in student_list.items():
        if nickname in student_names:
            return student_id
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

def fmt_desc(match):
    global localization_cn_data
    buffs = localization_cn_data["BuffName"]

    buff_types = {"b":"Buff_","d":"Debuff_","c":"CC_","s":"Special_"}
    if match.group(1) not in buff_types:
        return match.group()

    buff_name = buff_types[match.group(1)] + match.group(2)
    if buff_name not in buffs:
        return buff_name
    return buffs[buff_name]


parameters = []

def fmt_para(match):
    global parameters
    if parameters == []:
        return "UNKNOW"
    str = f'{parameters[int(match.group(1))-1][0]}({parameters[int(match.group(1))-1][-1]})'
    return str

def get_student_info(nickname):

    student_list = json.load(open(os.path.join(os.path.dirname(__file__), 'gacha/_ba_data.json'),encoding="utf-8"))["CHARA_NAME"]
    student_id = int(get_student_id(student_list,nickname))
    if student_id == None:
        return None

    global localization_cn_data
    common_data = get_json_data(common_url)
    student_data = get_json_data(students_url)
    localization_cn_data = get_json_data(localization_cn_url)
    localization_jp_data = get_json_data(localization_jp_url)
    if common_data == None or student_data == None or localization_cn_data == None or localization_jp_data == None:
        return

    msg_list = []

    base_info = get_item(student_data,"Id",student_id)

    #头像
    res = R.img(f'bluearchive/unit/icon_unit_{str(student_id)}.png')
    if not res.exist:
        try:
            img = requests.get(f'https://raw.githubusercontent.com/lonqie/SchaleDB/main/images/student/icon/Student_Portrait_{base_info["DevName"].strip()}_Collection.png',timeout=15).content
            base64_str = f"base64://{base64.b64encode(img).decode()}"
            res = f"[CQ:image,file={base64_str}]"
        except:
            res = R.img(f'bluearchive/unit/icon_unit_1000.png').cqcode
    else:
        res = res.cqcode
    msg_list.append(res)

    #名字
    names = base_info["FamilyName"] + base_info["PersonalName"] + "、"
    for name in student_list[str(student_id)]:
        names = names + name + "、"
    msg_list.append(names[:-1])

    #背景
    school = localization_cn_data["School"][base_info["School"]]
    school_jp = localization_jp_data["School"][base_info["School"]]
    club = localization_cn_data["Club"][base_info["Club"]]
    club_jp = localization_jp_data["Club"][base_info["Club"]]

    msg_list.append(f'学校:{school_jp}({school})\n社团:{club_jp}({club})\n'
                    f'{base_info["SchoolYear"]}  {base_info["CharacterAge"]}\n生日:{base_info["Birthday"]}')

    #属性
    bullet_types = {"Explosion":"爆破","Pierce":"穿甲","Mystic":"神秘"}
    equipment_types = {"Gloves":"手套","Bag":"包","Watch":"手表","Shoes":"鞋","Badge":"徽章",
                       "Necklace":"项链","Hat":"帽子","Hairpin":"发卡","Charm":"饰品"}
    equipments = ""
    for equipment in base_info["Equipment"]:
        equipments += (equipment_types[equipment] if equipment in equipment_types else equipment) + "、"

    adaptation = f'地形适应: 市街:{str(base_info["StreetBattleAdaptation"])} / 户外:{str(base_info["OutdoorBattleAdaptation"])} / 室内:{str(base_info["IndoorBattleAdaptation"])}\n'
    bullet_type = bullet_types[base_info["BulletType"]] if base_info["BulletType"] in bullet_types else base_info["BulletType"]


    type = f'攻击类型:{bullet_type}\n武器类型:{base_info["WeaponType"]}\n位置:{base_info["Position"]}\n' \
           f'装备:{equipments[:-1]}'


    msg_list.append(adaptation+type)

    #面板
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
    CriticalDamageRate = str(int(base_info["CriticalDamageRate"]/100))+"%"
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


    #技能
    global parameters
    skill_desc = ""
    skills = base_info["Skills"]
    for skill in skills:
        skill_desc += skill["SkillType"] + "\n"
        skill_desc += skill["Name"]
        if skill["SkillType"] == "ex":
            skill_desc += f' (Cost:{str(skill["Cost"][0])}→{str(skill["Cost"][-1])})'
        parameters = skill["Parameters"]
        desc = re.sub(r'<\?(\d+)>',fmt_para,skill["Desc"])
        desc = re.sub(r'<(\w):(\w+)>',fmt_desc,desc)
        skill_desc += "\n" + desc + "\n\n"

    msg_list.append(skill_desc)


    forward_msg = []
    for msg in msg_list:
        forward_msg.append({
        "type": "node",
        "data": {
            "name": "阿罗娜",
            "uin": "2854196306",
            "content": msg
        }
    })

    return forward_msg


if __name__ == '__main__':
    print(get_student_info("美咲"))
