import base64
import importlib
import json
from io import BytesIO
import os
import pygtrie
import requests
from fuzzywuzzy import fuzz, process
from PIL import Image

import hoshino
from hoshino import R, log, sucmd, util
from hoshino.typing import CommandSession

logger = log.new_logger('chara', hoshino.config.DEBUG)
UNKNOWN = "1000"
UnavailableChara = {
}



try:
    _ba_data = json.load(open(os.path.join(os.path.dirname(__file__), '_ba_data.json'),encoding="utf-8"))
    gadget_star = R.img('bluearchive/gadget/star.png').open()
    gadget_star_dis = R.img('bluearchive/gadget/star_disabled.png').open()
    unknown_chara_icon = R.img(f'bluearchive/unit/icon_unit_{UNKNOWN}.png').open()
except Exception as e:
    logger.exception(e)



class Roster:

    def __init__(self):
        self._roster = pygtrie.CharTrie()
        self.update()

    def update(self):
        global _ba_data
        _ba_data = json.load(open(os.path.join(os.path.dirname(__file__), '_ba_data.json'), encoding="utf-8"))
        self._roster.clear()
        for idx, names in _ba_data["CHARA_NAME"].items():
            for n in names:
                n = util.normalize_str(n)
                if n not in self._roster:
                    self._roster[n] = idx
                else:
                    logger.warning(f'bluearchive.chara.Roster: 出现重名{n}于id{idx}与id{self._roster[n]}')
        self._all_name_list = self._roster.keys()

    def get_id(self, name):
        name = util.normalize_str(name)
        if name in self._roster:
            return self._roster[name]
        else:
            self.update()
        return self._roster[name] if name in self._roster else UNKNOWN

    def guess_id(self, name):
        """@return: id, name, score"""
        name, score = process.extractOne(name, self._all_name_list, processor=util.normalize_str)
        return self._roster[name], name, score

    def parse_team(self, namestr):
        """@return: List[ids], unknown_namestr"""
        namestr = util.normalize_str(namestr.strip())
        team = []
        unknown = []
        while namestr:
            item = self._roster.longest_prefix(namestr)
            if not item:
                unknown.append(namestr[0])
                namestr = namestr[1:].lstrip()
            else:
                team.append(item.value)
                namestr = namestr[len(item.key):].lstrip()
        return team, ''.join(unknown)


roster = Roster()


def name2id(name):
    return roster.get_id(name)


def fromid(id_, star=0):
    return Chara(id_, star)


def fromname(name, star=0):
    id_ = name2id(name)
    return Chara(id_, star)


def guess_id(name):
    """@return: id, name, score"""
    return roster.guess_id(name)


def is_npc(id_):
    if id_ in UnavailableChara:
        return True
    else:
        return not ((1000 < id_ < 1200) or (1700 < id_ < 1900))


def gen_team_pic(team, size=64, star_slot_verbose=True):
    num = len(team)
    des = Image.new('RGBA', (num * size, size), (255, 255, 255, 255))
    for i, chara in enumerate(team):
        src = chara.render_icon(size, star_slot_verbose)
        des.paste(src, (i * size, 0), src)
    return des


class Chara:

    def __init__(self, id_, star=0):
        self.id = id_
        self.star = star
        self.load_data()

    def load_data(self):
        try:
            global _ba_data
            _ba_data = json.load(open(os.path.join(os.path.dirname(__file__), '_ba_data.json'), encoding="utf-8"))
        except Exception as e:
            logger.exception(e)

    @property
    def name(self):
        return _ba_data["CHARA_NAME"][self.id][1] if self.id in _ba_data["CHARA_NAME"] else \
        _ba_data["CHARA_NAME"][UNKNOWN][0]


    @property
    def is_npc(self) -> bool:
        return is_npc(self.id)

    @property
    def icon(self):
        res = R.img(f'bluearchive/unit/icon_unit_{self.id}.png')
        if not res.exist:
            global _ba_data
            _ba_data = json.load(open(os.path.join(os.path.dirname(__file__), '_ba_data.json'), encoding="utf-8"))
            res = R.img(f'bluearchive/unit/icon_unit_{self.id}.png')
        if not res.exist:
            res = R.img(f'bluearchive/unit/icon_unit_{UNKNOWN}.png')
        return res

    def render_icon(self, size, star_slot_verbose=True) -> Image:
        try:
            pic = self.icon.open().convert('RGBA').resize((size, size), Image.LANCZOS)
        except FileNotFoundError:
            logger.error(f'File not found: {self.icon.path}')
            pic = unknown_chara_icon.convert('RGBA').resize((size, size), Image.LANCZOS)

        l = size // 6
        star_lap = round(l * 0.15)
        margin_x = (size - 6 * l) // 2
        margin_y = round(size * 0.05)
        if self.star:
            for i in range(5 if star_slot_verbose else min(self.star, 5)):
                a = i * (l - star_lap) + margin_x
                b = size - l - margin_y
                s = gadget_star if self.star > i else gadget_star_dis
                s = s.resize((l, l), Image.LANCZOS)
                pic.paste(s, (a, b, a + l, b + l), s)
        return pic

