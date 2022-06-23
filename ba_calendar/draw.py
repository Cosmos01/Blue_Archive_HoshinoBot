from PIL import Image, ImageDraw, ImageFont
from .event import *
import os

item_height = 45

font_path = os.path.join(os.path.dirname(__file__), 'wqy-microhei.ttc')
font = ImageFont.truetype(font_path, int(item_height * 0.67))


color = [
    {'front': 'black', 'back': 'white'},
    {'front': 'white', 'back': 'ForestGreen'},
    {'front': 'white', 'back': 'DarkOrange'},
    {'front': 'white', 'back': 'BlueViolet'},
]

def create_image(item_number, title_len):
    width = int(item_height * title_len * 0.7)
    height = item_number * item_height
    im = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    return im

def draw_rec(im, color, x, y, w, h, r):
    draw = ImageDraw.Draw(im)
    draw.rectangle((x+r,y, x+w-r, y+h),fill=color)    
    draw.rectangle((x,y+r, x+w, y+h-r),fill=color)
    r = r * 2
    draw.ellipse((x,y,x+r,y+r),fill=color)    
    draw.ellipse((x+w-r,y,x+w,y+r),fill=color)    
    draw.ellipse((x,y+h-r,x+r,y+h),fill=color)    
    draw.ellipse((x+w-r,y+h-r,x+w,y+h),fill=color)

def draw_text(im, x, y, w, h, text, align, color):
    draw = ImageDraw.Draw(im)
    tw, th = draw.textsize(text, font=font)
    y = y + (h - th) / 2
    if align == 0: #居中
        x = x + (w - tw) / 2
    elif align == 1: #左对齐
        x = x + 5
    elif align == 2: #右对齐
        x = x + w - tw - 5
    draw.text((x, y), text, fill=color, font=font)

def draw_item(im, n, t, text, days):
    if t >= len(color):
        t = 1
    x = 0
    y = n * item_height

    width = im.width
    height = int(item_height * 0.95)

    draw_rec(im, color[t]['back'], x, y, width, height, int(item_height * 0.1))

    draw_text(im, x, y, width, height, text, 1, color[t]['front'])

    if days > 0:

        text1 = f'{days}天后结束'
    elif days < 0:
        text1 = f'{-days}天后开始'
    else:
        text1 = '即将结束'
    draw_text(im, x, y, width, height, text1, 2, color[t]['front'])

def draw_title(im, n, left = None, middle = None, right = None):
    x = 0
    y = n * item_height
    width = im.width
    height = int(item_height * 0.95)


    draw_rec(im, color[0]['back'], x, y, width, height, int(item_height * 0.1))
    if middle:
        draw_text(im, x, y, width, height, middle, 0, color[0]['front'])
    if left:
        draw_text(im, x, y, width, height, left, 1, color[0]['front'])
    if right:
        draw_text(im, x, y, width, height, right, 2, color[0]['front'])

