from ..utils import get_json_data, get_student_id, get_config

config = get_config()
token = config["arona_icu_token"] if "arona_icu_token" in config and config["arona_icu_token"] != "" else None
base_api = config["arona_icu_api"] if "arona_icu_api" in config and config["arona_icu_api"] != "" else "https://api.arona.icu/"
proxy = config["arona_icu_proxy"] if "arona_icu_proxy" in config and config["arona_icu_proxy"] != "" else None
proxies = None
if proxy is not None:
    proxies = {"http": proxy, "https": proxy}


async def search_support(nickname: str, server: int = 1,atype: int = 2, star: int = 0, weapon: int = 0, page: int = 1):
    if token is None:
        return ["使用此功能前请先配置token"]
    headers = {"Authorization": "ba-token " + token}
    student_id = get_student_id(nickname)
    if student_id is None:
        return ["未找到该角色"]
    student_id = int(student_id)
    url = base_api + "api/friends/assist_query"
    data = {
            "page": page,
            "size": 20,
            "friend": 47,
            "starGrade": star,
            "server": server,
            "uniqueId": student_id,
            "level": 0,
            "sort": 1,
            "assistType": atype,
            "weaponLevel": 0,
            "weaponStarGrade": weapon,
            "publicSkillLevel": 0,
            "exSkillLevel": 5,
            "passiveSkillLevel": 0,
            "extraPassiveSkillLevel": 0
        }

    res = await get_json_data(url, data=data, headers=headers, proxies=proxies)
    if res is None:
        return ["查询失败，请检查网络环境"]
    if res["code"] != 200:
        return [res["message"]]
    if len(res["data"]["records"]) == 0:
        return ["未找到匹配结果"]
    data = res["data"]
    result = []
    for user in data["records"]:
        result.append(user["friendCode"])
        msg = ""
        for assist in user["assistInfoList"]:
            if assist["uniqueId"] != student_id:
                continue
            msg += f'{assist["level"]}级 '
            if assist["starGrade"] == 5 and assist["weaponStarGrade"] > 0:
                msg += f'专{assist["weaponStarGrade"]} '
            else:
                msg += f'{assist["starGrade"]}星 '
            # 好感
            msg += f'♡{assist["favorRank"]} '
            # 技能
            msg += str(assist["exSkillLevel"]) if assist["exSkillLevel"] < 5 else "m"
            msg += str(assist["publicSkillLevel"]) if assist["publicSkillLevel"] < 10 else "m"
            msg += str(assist["passiveSkillLevel"]) if assist["passiveSkillLevel"] < 10 else "m"
            msg += str(assist["extraPassiveSkillLevel"]) if assist["extraPassiveSkillLevel"] < 10 else "m"
            # 装备
            msg += " "
            for equipment in assist["equipment"]:
                msg += f'T{equipment["Tier"]}'
        result.append(msg)
    result.append(f'{data["totalData"]}条 {data["page"]}/{data["totalPages"]}页')
    return result
