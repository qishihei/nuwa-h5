#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成「1024 造物挑战」投稿封面图（16:10，1600x1000）。

视觉沿用现有海报的复古棕金风格，保证与卡片/海报是同一套识别。
用法: python3 make_covers.py
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
H5 = os.path.abspath(os.path.join(HERE, '..', '..'))
THOUGHT = os.path.join(H5, 'share', 'posters', 'portraits')
DIRECTOR = os.path.join(H5, 'directors', 'share', 'posters', 'portraits')
OUT = HERE
os.makedirs(OUT, exist_ok=True)

W, H = 1600, 1000
TOP, MID, BOT = (43, 33, 24), (74, 56, 38), (43, 33, 24)
CREAM = (243, 233, 216, 255)
GOLD = (233, 196, 106, 255)
SUB = (243, 233, 216, 216)
DIM = (243, 233, 216, 150)
CJK = '/System/Library/Fonts/PingFang.ttc'


def font(size, heavy=False):
    p = '/System/Library/Fonts/Helvetica.ttc' if False else CJK
    try:
        return ImageFont.truetype(p, size)
    except Exception:
        return ImageFont.load_default()


def fit_font(d, text, start, min_size, max_w, spacing=0):
    size = start
    while size > min_size:
        f = font(size)
        w = sum(d.textlength(ch, font=f) for ch in text) + spacing * max(0, len(text) - 1)
        if w <= max_w:
            return f, size
        size -= 2
    return font(min_size), min_size


def center(d, text, y, fnt, fill, spacing=0, cx=W // 2):
    total = sum(d.textlength(ch, font=fnt) for ch in text) + spacing * max(0, len(text) - 1)
    x = cx - total / 2
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + spacing


def gradient_bg():
    img = Image.new('RGB', (W, H), TOP)
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(TOP[0] + (MID[0] - TOP[0]) * (1 - abs(t - 0.25) * 2) * 0.9)
        g = int(TOP[1] + (MID[1] - TOP[1]) * (1 - abs(t - 0.25) * 2) * 0.9)
        b = int(TOP[2] + (MID[2] - TOP[2]) * (1 - abs(t - 0.25) * 2) * 0.9)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    return img


def avatar(path, r):
    """圆形头像：贴顶裁切，保证脸完整不被切掉。"""
    p = Image.open(path).convert('RGB')
    c = ImageOps.fit(p, (r * 2, r * 2), method=Image.LANCZOS, centering=(0.5, 0.13))
    mask = Image.new('L', (r * 2, r * 2), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, r * 2 - 1, r * 2 - 1], fill=255)
    out = Image.new('RGBA', (r * 2, r * 2), (0, 0, 0, 0))
    out.paste(c, (0, 0), mask)
    return out


def make_cover(title, sub, points, footer, ids, pdir, fn):
    img = gradient_bg()
    d = ImageDraw.Draw(img, 'RGBA')
    cx = W // 2

    # 顶部小标
    center(d, 'WorkBuddy · 1024 造物挑战 投稿作品', 88, font(26), DIM, spacing=3)
    d.line([cx - 120, 138, cx + 120, 138], fill=GOLD, width=2)

    # 主标题
    tf, ts = fit_font(d, title, 104, 60, W - 140, spacing=14)
    center(d, title, 190, tf, CREAM, spacing=14 if ts >= 90 else 6)

    # 副标题（金色，核心卖点）
    sf, _ = fit_font(d, sub, 46, 26, W - 120)
    center(d, sub, 330, sf, GOLD)

    # 头像行
    r = 112
    gap = 34
    n = len(ids)
    total = n * r * 2 + (n - 1) * gap
    x0 = cx - total // 2
    y = 440
    for i, tid in enumerate(ids):
        p = os.path.join(pdir, tid + '.jpg')
        if not os.path.exists(p):
            continue
        x = x0 + i * (r * 2 + gap)
        img.paste(avatar(p, r), (x, y), avatar(p, r))
        # 金色细环
        d.ellipse([x - 5, y - 5, x + r * 2 + 5, y + r * 2 + 5], outline=GOLD, width=3)

    # 卖点
    py = 720
    for pt in points:
        pf, _ = fit_font(d, pt, 30, 18, W - 200)
        d.text((cx - 12 - d.textlength(pt, font=pf) / 2 + 12, py), pt, font=pf, fill=CREAM)
        py += 52

    # 底部
    center(d, footer, 900, font(30), GOLD)
    center(d, '扫码即用 · 无需下载安装', 950, font(22), DIM)

    img.convert('RGB').save(fn)
    return fn


if __name__ == '__main__':
    f1 = make_cover(
        '思想会客厅',
        '25 位大师，同时回答你一个问题',
        ['负债 · 辞职 · 婚姻 · 35 岁危机——说出你的纠结',
         '孔子 / 芒格 / 马斯克 / 尼采…各自用自家的认知框架作答',
         '多大师答案并排对照 · 支持多轮深度追问'],
        '扫码，把纠结说给 25 位大师听',
        ['confucius', 'charlie-munger', 'steve-jobs', 'laozi'],
        THOUGHT, os.path.join(OUT, 'cover-thought.png'))
    f2 = make_cover(
        '导演会客厅',
        '25 位导演，用镜头语言帮你重看问题',
        ['镜头卡住 · 剧本停滞 · 风格拿不准——说出来',
         '诺兰 / 王家卫 / 库布里克 / 黑泽明…各用自己的电影语言作答',
         '专为短视频与影视创作者设计 · 支持多轮追问'],
        '扫码，和 25 位导演聊聊你的镜头',
        ['christopher-nolan', 'wong-kar-wai', 'stanley-kubrick', 'akira-kurosawa'],
        DIRECTOR, os.path.join(OUT, 'cover-director.png'))
    print('封面 ->', f1)
    print('封面 ->', f2)
