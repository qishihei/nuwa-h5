#!/usr/bin/env python3
# 生成思想会客厅中文文字版海报（对齐 share/poster.html 版式），内嵌 link-qr.png
# 用法: python3 make_zh_poster.py
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
CJK = '/System/Library/Fonts/PingFang.ttc'
W, H = 750, 1440
TOP, MID, BOT = (0x2b, 0x21, 0x18), (0x4a, 0x38, 0x26), (0x2b, 0x21, 0x18)

def font(p, s):
    try: return ImageFont.truetype(p, s)
    except Exception: return ImageFont.load_default()

def center(d, text, y, fnt, fill, cx=W//2):
    w = d.textlength(text, font=fnt)
    d.text((cx - w/2, y), text, font=fnt, fill=fill)

base = Image.new('RGB', (W, H)); px = base.load()
for y in range(H):
    t = y / (H - 1)
    if t < 0.55:
        f = t / 0.55; c = tuple(int(TOP[i] + (MID[i]-TOP[i])*f) for i in range(3))
    else:
        f = (t - 0.55) / 0.45; c = tuple(int(MID[i] + (BOT[i]-MID[i])*f) for i in range(3))
    for x in range(W): px[x, y] = c
img = base.convert('RGBA'); d = ImageDraw.Draw(img, 'RGBA')

def glow(cx, cy, r, color):
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for i in range(12, 0, -1):
        a = int(color[3] * (1 - i/12) * 0.5); rr = r * i / 12
        gd.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=color[:3] + (a,))
    return Image.alpha_composite(img, g.filter(ImageFilter.GaussianBlur(50)))

img = glow(W, 0, 420, (201, 161, 74, 150))
img = glow(0, H-140, 380, (192, 86, 59, 110))
d = ImageDraw.Draw(img, 'RGBA')

CREAM = (243, 233, 216, 255); GOLD = (233, 196, 106, 255); SUB = (243, 233, 216, 217); DIM = (243, 233, 216, 154)
cx = W // 2

# logo
d.rounded_rectangle([cx-48, 70, cx+48, 166], radius=24, fill=(233, 196, 106, 255))
d.rounded_rectangle([cx-48, 70, cx+48, 166], radius=24, fill=(192, 86, 59, 90))
d.text((cx, 118), '思', font=font(CJK, 54), fill=(43, 33, 24, 255), anchor='mm')

center(d, '思想会客厅', 196, font(CJK, 64), CREAM)
center(d, '让 25 位顶尖思想家，用他们的认知框架帮你思考', 286, font(CJK, 24), SUB)
center(d, '芒格 · 乔布斯 · 费曼 · 纳瓦尔 · 王阳明 · 稻盛和夫', 372, font(CJK, 24), GOLD)
center(d, '巴菲特 · 达利欧 · 尼采 · 老子 · 孙子 · 塔勒布 · 凯恩斯 …', 420, font(CJK, 24), GOLD)

pts = ['负债、辞职、婚姻、35 岁危机——说出你的纠结',
       '多位大师同时作答，观点碰撞对照',
       '不是鸡汤语录，是可执行的思考框架']
py = 500
for p in pts:
    d.text((60, py), '✦', font=font(CJK, 24), fill=GOLD)
    d.text((94, py), p, font=font(CJK, 24), fill=CREAM)
    py += 46

qr = Image.open(os.path.join(HERE, 'link-qr.png')).convert('RGB').resize((280, 280))
card_y = 760
d.rounded_rectangle([cx-200, card_y, cx+200, card_y+380], radius=28, fill=(250, 247, 241, 255))
img.paste(qr, (cx-140, card_y+28))
d.text((cx, card_y+322), '长按识别二维码，立即体验', font=font(CJK, 23), fill=(107, 93, 74, 255), anchor='mm')

center(d, '免费体验 3 次', 1200, font(CJK, 28), GOLD)
center(d, '合作交流加微信：fuping394319746', 1360, font(CJK, 21), DIM)

img.convert('RGB').save(os.path.join(HERE, 'poster.png'))
print('saved poster.png')
