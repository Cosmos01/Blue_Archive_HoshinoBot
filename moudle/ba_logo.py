from math import radians, tan
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC_PATH = Path(__file__).parent / 'src'
FONT_PATH = SRC_PATH / 'Merged.otf'
HALO_PATH = SRC_PATH / 'halo.png'
CROSS_PATH = SRC_PATH / 'cross.png'


def draw_pic(front: str = 'アリス', back: str = 'Archive', dx: int = 76, dy: int = -7):
    # consts and calc
    fnt_size = 84
    pic_width = fnt_size * (front.__len__() + back.__len__() + 2)
    pic_height = fnt_size * 2 + 50
    # color
    blue = (18, 138, 250, 255)
    gray = (43, 43, 43, 255)
    white = (255, 255, 255, 255)
    # load src
    fnt_Hans = ImageFont.truetype(FONT_PATH.as_posix(), fnt_size)
    halo = Image.open(HALO_PATH).convert('RGBA')
    cross = Image.open(CROSS_PATH).convert('RGBA')
    # text tilt
    angle = 20
    dist = pic_height * tan(radians(angle))
    data = (1, tan(radians(angle)), -dist, 0, 1, 0)
    # polygon const
    mid: tuple[int, int] = (304, 144)
    offset: int = 12
    offset_2: int = 12
    polygon_xy = [
        (138, 428),
        (mid[0] - offset, mid[1] - offset),
        (mid[0] + offset, mid[1] + offset),
    ]
    polygon_xy_second = [
        (484, 222),
        (mid[0] - offset_2, mid[1] + offset_2),
        (mid[0] + offset_2, mid[1] - offset_2),
    ]
    # resize halo
    halo = halo.resize((250, 250), Image.BICUBIC)
    # predraw polygon on cross
    prepaint_pic = Image.new('RGBA', (500, 500), (255, 255, 255, 0))
    prepaint = ImageDraw.Draw(prepaint_pic)
    prepaint.polygon(polygon_xy, fill=white)
    prepaint.polygon(polygon_xy_second, fill=white)
    prepaint.bitmap((0, 0), cross, fill=blue)
    prepaint_pic = prepaint_pic.resize((250, 250), Image.BICUBIC)
    # predraw front text
    front_pic = Image.new('RGBA', (fnt_size * (front.__len__() + 2), fnt_size * 2), (255, 255, 255, 0))
    prepaint = ImageDraw.Draw(front_pic)
    prepaint.text((0, 0), front, font=fnt_Hans, fill=blue)
    front_pic = front_pic.transform(front_pic.size, Image.AFFINE, data, Image.BICUBIC)
    front_pic = front_pic.crop(front_pic.getbbox())
    # predraw back text
    back_pic = Image.new('RGBA', (fnt_size * (back.__len__() + 2), fnt_size * 2), (255, 255, 255, 0))
    prepaint = ImageDraw.Draw(back_pic)
    prepaint.text(
        (0, 0),
        back,
        font=fnt_Hans,
        fill=gray,
        stroke_width=5,
        stroke_fill=white,
    )
    back_pic = back_pic.transform(back_pic.size, Image.AFFINE, data, Image.BICUBIC)
    back_pic = back_pic.crop(back_pic.getbbox())
    # draw pic
    pic = Image.new('RGBA', (pic_width, pic_height), (255, 255, 255, 0))
    paint_board = ImageDraw.Draw(pic)
    pic.paste(front_pic, (10, fnt_size), front_pic)
    paint_board.bitmap((front_pic.size[0] - dx, dy), halo, fill=gray)
    pic.paste(back_pic, (front_pic.size[0], fnt_size - 6), back_pic)  # magic number dkw just -6
    pic.paste(prepaint_pic, (front_pic.size[0] - dx, dy), prepaint_pic)
    pic = pic.crop(pic.getbbox())
    # close pic
    front_pic.close()
    back_pic.close()
    halo.close()
    cross.close()
    prepaint_pic.close()
    # return
    return pic.convert('RGB')