#!/usr/bin/env python3
# 生成「导演大师会客厅」每位导演的专属分享海报（带二维码，扫码直接进该导演对话）
# 用法: python3 make_director_posters.py [访问地址]
#   不传则使用 https://director-salon.onrender.com
# 产物: share/posters/<director-id>.png  (25 张，命名为导演 id，便于运营取用)
#        share/posters/index.html        (本地预览画廊，含二维码链接)

import io, os, re, sys, json, base64
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

BASE = sys.argv[1] if len(sys.argv) > 1 else 'https://director-salon.onrender.com'
HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, 'posters')
PORTRAITS = os.path.join(OUT, 'portraits')
os.makedirs(OUT, exist_ok=True)
os.makedirs(PORTRAITS, exist_ok=True)

CJK = '/System/Library/Fonts/PingFang.ttc'
EN  = '/System/Library/Fonts/Helvetica.ttc'
W, H = 750, 1334
TOP, MID, BOT = (43, 33, 24), (74, 56, 38), (43, 33, 24)
CREAM = (243, 233, 216, 255); GOLD = (233, 196, 106, 255)
SUB   = (243, 233, 216, 214); DIM = (243, 233, 216, 150)
BROWN = (43, 33, 24, 255)

def cn_name(disp):
    return re.split(r'(?=[A-Za-z])', disp or '')[0].strip() or disp

# ---------- 二维码 ----------
def qr_png(url, size=300):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(url); qr.make(fit=True)
    img = qr.make_image(fill_color='#2b2118', back_color='white').convert('RGBA')
    return img.resize((size, size))

# ---------- 字体 ----------
def font(path, size):
    try: return ImageFont.truetype(path, size)
    except Exception: return ImageFont.load_default()

def center(d, text, y, fnt, fill, spacing=0, cx=W//2):
    if spacing:
        total = sum(d.textlength(ch, font=fnt) + spacing for ch in text) - spacing
        x = cx - total / 2
        for ch in text:
            d.text((x, y), ch, font=fnt, fill=fill); x += d.textlength(ch, font=fnt) + spacing
    else:
        w = d.textlength(text, font=fnt); d.text((cx - w/2, y), text, font=fnt, fill=fill)

def fit_font(d, text, path, start, min_size, max_width, spacing=0):
    """自动缩小字号直到文本(含字距)不超过 max_width"""
    size = start
    while size > min_size:
        f = font(path, size)
        w = sum(d.textlength(ch, font=f) for ch in text) + spacing * max(0, len(text) - 1)
        if w <= max_width: return f, size
        size -= 2
    return font(path, min_size), min_size

def glow(img, cx, cy, r, color):
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for i in range(12, 0, -1):
        a = int(color[3] * (1 - i/12) * 0.5); rr = r * i / 12
        gd.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=color[:3] + (a,))
    return Image.alpha_composite(img, g.filter(ImageFilter.GaussianBlur(50)))

# ---------- 单张海报 ----------
def make_poster(director):
    name   = director['name']
    disp   = director.get('display_name', name)
    cn     = cn_name(disp)
    work   = director.get('work', '') or ''
    themes = director.get('themes') or []
    url    = f'{BASE}/?director={name}'

    base = Image.new('RGB', (W, H)); px = base.load()
    for y in range(H):
        t = y / (H - 1)
        cc = tuple(int(TOP[i] + (MID[i]-TOP[i])*(t/0.55)) for i in range(3)) if t < 0.55 else \
             tuple(int(MID[i] + (BOT[i]-MID[i])*((t-0.55)/0.45)) for i in range(3))
        for x in range(W): px[x, y] = cc
    img = base.convert('RGBA'); d = ImageDraw.Draw(img, 'RGBA')
    img = glow(img, W-90, 80, 380, (201, 161, 74, 140))
    img = glow(img, 60, H-160, 360, (192, 86, 59, 100))

    # 肖像淡背景：灰度 + 模糊 + 低透明度，垫在文字之下
    pf = os.path.join(PORTRAITS, name + '.jpg')
    if os.path.exists(pf):
        try:
            p = Image.open(pf).convert('L')
            p = ImageOps.fit(p, (W, H), method=Image.LANCZOS, bleed=0.0)
            p = p.filter(ImageFilter.GaussianBlur(10))
            pa = p.convert('RGBA'); pa.putalpha(34)
            img = Image.alpha_composite(img, pa)
        except Exception:
            pass

    d = ImageDraw.Draw(img, 'RGBA')
    cx = W // 2

    # 肖像：圆形金环头像（无图则自动跳过，仅保留淡背景）
    pf = os.path.join(PORTRAITS, name + '.jpg')
    if os.path.exists(pf):
        try:
            pr = 95                       # 肖像半径
            pcx, pcy = cx, 245            # 肖像圆心
            p = Image.open(pf).convert('RGB')
            p = ImageOps.fit(p, (pr*2, pr*2), method=Image.LANCZOS, centering=(0.5, 0.18))
            # 轻微降饱和，贴合复古底色
            p = Image.blend(p, ImageOps.grayscale(p).convert('RGB'), 0.25)
            mask = Image.new('L', (pr*2, pr*2), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, pr*2 - 1, pr*2 - 1], fill=255)
            img.paste(p, (pcx - pr, pcy - pr), mask)
            d.ellipse([pcx-pr-4, pcy-pr-4, pcx+pr+4, pcy+pr+4], outline=GOLD, width=5)
            d.ellipse([pcx-pr-9, pcy-pr-9, pcx+pr+9, pcy+pr+9], outline=(201, 161, 74, 90), width=2)
        except Exception:
            pass

    # 顶栏小标
    center(d, '导演大师会客厅', 70, font(CJK, 26), SUB, spacing=4)
    d.line([cx-90, 112, cx+90, 112], fill=GOLD, width=2)

    # 导演名（大字，长名自动缩号）
    nf, nsize = fit_font(d, cn, CJK, 78, 40, W - 80, spacing=10)
    center(d, cn, 415, nf, CREAM, spacing=10 if nsize >= 60 else 4)

    # 代表作（过长自动缩号，不再截断）
    if work:
        wf, _ = fit_font(d, '代表作  ' + work, CJK, 26, 16, W - 90)
        center(d, '代表作  ' + work, 505, wf, GOLD)

    # 招牌主题（最多 3 行，同样防溢出）
    ty = 560
    for th in themes[:3]:
        tf, _ = fit_font(d, th, CJK, 28, 18, W - 90)
        center(d, th, ty, tf, CREAM)
        ty += 46

    # 二维码卡片
    qrimg = qr_png(url, 280)
    card_y = 720
    d.rounded_rectangle([cx-200, card_y, cx+200, card_y+400], radius=28, fill=(250, 247, 241, 255))
    img.paste(qrimg, (cx-140, card_y+30))
    cap = '长按识别 · 与' + cn + '对话'
    cf, _ = fit_font(d, cap, CJK, 25, 15, 380)
    d.text((cx, card_y+336), cap, font=cf, fill=(107, 93, 74, 255), anchor='mm')

    # 底部
    center(d, '合作交流加微信：fuping394319746', 1250, font(CJK, 21), DIM)

    return img.convert('RGB'), url

# ---------- 整站总览海报（对齐 director-poster-zh 版式，全部文字自动缩号） ----------
def make_overview():
    url = BASE
    base = Image.new('RGB', (W, H)); px = base.load()
    for y in range(H):
        t = y / (H - 1)
        cc = tuple(int(TOP[i] + (MID[i]-TOP[i])*(t/0.55)) for i in range(3)) if t < 0.55 else \
             tuple(int(MID[i] + (BOT[i]-MID[i])*((t-0.55)/0.45)) for i in range(3))
        for x in range(W): px[x, y] = cc
    img = base.convert('RGBA')
    img = glow(img, W, 0, 420, (201, 161, 74, 150))
    img = glow(img, 0, H-140, 380, (192, 86, 59, 110))
    d = ImageDraw.Draw(img, 'RGBA')
    cx = W // 2

    # logo
    d.rounded_rectangle([cx-48, 70, cx+48, 166], radius=24, fill=(233, 196, 106, 255))
    d.rounded_rectangle([cx-48, 70, cx+48, 166], radius=24, fill=(192, 86, 59, 90))
    d.text((cx, 118), '导', font=font(CJK, 54), fill=BROWN, anchor='mm')

    title = '导演大师会客厅'
    tf, ts = fit_font(d, title, CJK, 62, 30, W - 100, spacing=8)
    center(d, title, 196, tf, CREAM, spacing=8 if ts >= 50 else 3)

    tagline = '让百年影史百位殿堂级导演，用招牌技法帮你拆解电影创作难题'
    gf, _ = fit_font(d, tagline, CJK, 24, 15, W - 70)
    center(d, tagline, 292, gf, SUB)

    m1 = '黑泽明 · 费里尼 · 希区柯克 · 王家卫 · 宫崎骏 · 塔可夫斯基'
    m2 = '库布里克 · 伯格曼 · 小津安二郎 · 戈达尔 · 李安 · 奉俊昊 …'
    for text, yy in ((m1, 380), (m2, 428)):
        mf, _ = fit_font(d, text, CJK, 24, 15, W - 70)
        center(d, text, yy, mf, GOLD)

    points = [
        '剧本卡壳、调度混乱、调色廉价、表演僵硬——说出你的创作难题',
        '多位导演同台，用各自招牌技法给你可落地的思路',
        '不是泛泛而谈，是能直接用到镜头前的实操框架',
    ]
    py = 510
    for p in points:
        pf, _ = fit_font(d, p, CJK, 24, 15, W - 140)
        d.text((60, py), '✦', font=font(CJK, 24), fill=GOLD)
        d.text((94, py), p, font=pf, fill=CREAM)
        py += 48

    qrimg = qr_png(url, 280)
    card_y = 770
    d.rounded_rectangle([cx-200, card_y, cx+200, card_y+380], radius=28, fill=(250, 247, 241, 255))
    img.paste(qrimg, (cx-140, card_y+28))
    cap = '长按识别二维码，立即体验'
    cf, _ = fit_font(d, cap, CJK, 23, 15, 380)
    d.text((cx, card_y+322), cap, font=cf, fill=(107, 93, 74, 255), anchor='mm')

    center(d, '合作交流加微信：fuping394319746', 1340, font(CJK, 21), DIM)
    return img.convert('RGB'), url

# ---------- 执行 ----------
data = json.load(open(os.path.join(HERE, '..', 'directors.json'), encoding='utf-8'))
directors = data['directors']
print(f'载入导演 {len(directors)} 位，开始生成海报 → {OUT}')
items = []

ovi, ourl = make_overview()
ofn = '00-总览.png'
ovi.save(os.path.join(OUT, ofn))
items.append(('总览 · 扫码进大厅', ourl, ofn))
print(f'  [ 总览 ] director-poster -> {os.path.join(OUT, ofn)}')

for i, dr in enumerate(directors, 1):
    img, url = make_poster(dr)
    fn = os.path.join(OUT, dr['name'] + '.png')
    img.save(fn)
    items.append((cn_name(dr.get('display_name', dr['name'])), url, os.path.basename(fn)))
    print(f'  [{i:2d}/{len(directors)}] {dr["name"]:22s} -> {fn}')

# 预览画廊
cards = '\n'.join(
    f'<div class="c"><img src="{fn}"><div class="meta"><b>{t}</b>'
    f'<code>{u}</code><a href="{u}" target="_blank">打开链接 ↗</a></div></div>'
    for t, u, fn in items
)
html = f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8">
<title>导演大师会客厅 · 海报预览</title><style>
body{{font-family:-apple-system,"PingFang SC",sans-serif;background:#1c1611;margin:0;padding:30px;color:#eee}}
h1{{font-size:24px;margin:0 0 6px}}p{{opacity:.6;margin:0 0 24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:22px}}
.c{{background:#2b2118;border-radius:16px;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.4)}}
.c img{{width:100%;display:block}}.meta{{padding:12px 14px}}.meta b{{font-size:18px}}
code{{display:block;font-size:11px;opacity:.5;margin:6px 0;word-break:break-all}}
a{{color:#e9c46a;font-size:13px;text-decoration:none}}</style></head>
<body><h1>导演大师会客厅 · 海报预览</h1>
<p>总览 1 张 + 导演专属 {len(directors)} 张 · 扫码即进入对应导演对话（深链 ?director=id）</p>
<div class="grid">{cards}</div></body></html>'''
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)
print('画廊 ->', os.path.join(OUT, 'index.html'))
