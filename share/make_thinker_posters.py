#!/usr/bin/env python3
# 生成「思想会客厅」每位大师的专属分享海报（带二维码，扫码直接选中该大师）
# 用法: python3 make_thinker_posters.py [访问地址]
#   不传则使用腾讯 CloudBase 部署地址
# 产物: share/posters/<thinker-id>.png  (25 张 + 00-总览.png)
#        share/posters/index.html        (本地预览画廊)
# 肖像: share/posters/portraits/<id>.jpg (先跑 fetch_thinker_portraits.py；缺图自动跳过)

import os, re, sys, json
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

BASE = sys.argv[1] if len(sys.argv) > 1 else 'https://d6gnzuxxd50c83iaa-1502990614.tcloudbaseapp.com'
HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS_JSON = os.path.join(HERE, '..', 'skills.json')
OUT  = os.path.join(HERE, 'posters')
PORTRAITS = os.path.join(OUT, 'portraits')
os.makedirs(OUT, exist_ok=True)
os.makedirs(PORTRAITS, exist_ok=True)

CJK = '/System/Library/Fonts/PingFang.ttc'
W, H = 750, 1334
TOP, MID, BOT = (43, 33, 24), (74, 56, 38), (43, 33, 24)
CREAM = (243, 233, 216, 255); GOLD = (233, 196, 106, 255)
SUB   = (243, 233, 216, 214); DIM = (243, 233, 216, 150)
BROWN = (43, 33, 24, 255)

# id -> (代表作, 招牌主题 x3)
META = {
    'charlie-munger':      ('《穷查理宝典》', ['多元思维模型', '逆向思维', '能力圈与激励']),
    'elon-musk':           ('《硅谷钢铁侠》', ['第一性原理', '五步工程法', '垂直整合']),
    'richard-feynman':     ('《别闹了，费曼先生》', ['费曼学习法', '怀疑与可证伪', '坦诚不确定性']),
    'zhang-yiming':        ('微博与公开访谈', ['延迟满足', '信息效率', '平常心']),
    'naval-ravikant':      ('《纳瓦尔宝典》', ['特定知识', '无需许可的杠杆', '产品化自己']),
    'steve-jobs':          ('《史蒂夫·乔布斯传》', ['专注说不', '科技×人文', '端到端控制']),
    'kazuo-inamori':       ('《活法》', ['作为人何谓正确', '利他经营', '成功方程式']),
    'wang-yangming':       ('《传习录》', ['知行合一', '致良知', '事上磨练']),
    'socrates':            ('《申辩篇》', ['产婆术诘问', '未经省察的人生', '我知我无知']),
    'warren-buffett':      ('《致股东的信》', ['护城河', '安全边际', '长期复利']),
    'ray-dalio':           ('《原则》', ['极度求真', '痛苦+反思=进步', '把人生当机器']),
    'confucius':           ('《论语》', ['仁与恕', '因材施教', '中庸之道']),
    'friedrich-nietzsche': ('《查拉图斯特拉如是说》', ['权力意志', '成为你自己', 'amor fati 爱命运']),
    'laozi':               ('《道德经》', ['无为而治', '上善若水', '反者道之动']),
    'marie-curie':         ('《放射性论》', ['极致专注', '严谨实证', '淡泊名利']),
    'daniel-kahneman':     ('《思考，快与慢》', ['系统1与系统2', '锚定与框架效应', '前景理论']),
    'sun-tzu':             ('《孙子兵法》', ['知己知彼', '以正合以奇胜', '不战而屈人之兵']),
    'jensen-huang':        ('《英伟达之道》', ['加速计算', '平坦组织', '战略耐心']),
    'coco-chanel':         ('《香奈儿的态度》', ['极简优雅', '打破常规', '为自由而设计']),
    'nassim-taleb':        ('《反脆弱》', ['反脆弱', '黑天鹅思维', '否定法']),
    'sima-qian':           ('《史记》', ['究天人之际', '通古今之变', '成一家之言']),
    'sam-altman':          ('《如何创业》', ['复利与动量', '想大做小', '长期押注']),
    'liqingzhao':          ('《漱玉词》', ['易安体', '寻常语度入音律', '词别是一家']),
    'friedrich-hayek':     ('《通往奴役之路》', ['自发秩序', '知识分散', '价格信号']),
    'john-maynard-keynes': ('《就业、利息和货币通论》', ['有效需求', '动物精神', '预期与不确定性']),
}

def cn_name(disp):
    return re.split(r'(?=[A-Za-z])', disp or '')[0].strip() or disp

# ---------- 二维码 ----------
def qr_png(url, size=300):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(url); qr.make(fit=True)
    img = qr.make_image(fill_color='#2b2118', back_color='white').convert('RGBA')
    return img.resize((size, size))

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

def gradient_bg():
    base = Image.new('RGB', (W, H)); px = base.load()
    for y in range(H):
        t = y / (H - 1)
        cc = tuple(int(TOP[i] + (MID[i]-TOP[i])*(t/0.55)) for i in range(3)) if t < 0.55 else \
             tuple(int(MID[i] + (BOT[i]-MID[i])*((t-0.55)/0.45)) for i in range(3))
        for x in range(W): px[x, y] = cc
    return base.convert('RGBA')

# ---------- 单张海报 ----------
def make_poster(tid, disp):
    work, themes = META.get(tid, ('', []))
    cn = cn_name(disp)
    url = f'{BASE}/?thinker={tid}'

    img = gradient_bg()
    img = glow(img, W-90, 80, 380, (201, 161, 74, 140))
    img = glow(img, 60, H-160, 360, (192, 86, 59, 100))

    # 肖像淡背景：灰度 + 模糊 + 低透明度
    pf = os.path.join(PORTRAITS, tid + '.jpg')
    if os.path.exists(pf):
        try:
            p = Image.open(pf).convert('L')
            p = ImageOps.fit(p, (W, H), method=Image.LANCZOS)
            p = p.filter(ImageFilter.GaussianBlur(10))
            pa = p.convert('RGBA'); pa.putalpha(34)
            img = Image.alpha_composite(img, pa)
        except Exception:
            pass

    d = ImageDraw.Draw(img, 'RGBA')
    cx = W // 2

    # 肖像：圆形金环头像（顶部偏移裁剪，防切头；无图自动跳过）
    if os.path.exists(pf):
        try:
            pr = 95
            pcx, pcy = cx, 245
            p = Image.open(pf).convert('RGB')
            p = ImageOps.fit(p, (pr*2, pr*2), method=Image.LANCZOS, centering=(0.5, 0.18))
            p = Image.blend(p, ImageOps.grayscale(p).convert('RGB'), 0.25)
            mask = Image.new('L', (pr*2, pr*2), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, pr*2 - 1, pr*2 - 1], fill=255)
            img.paste(p, (pcx - pr, pcy - pr), mask)
            d.ellipse([pcx-pr-4, pcy-pr-4, pcx+pr+4, pcy+pr+4], outline=GOLD, width=5)
            d.ellipse([pcx-pr-9, pcy-pr-9, pcx+pr+9, pcy+pr+9], outline=(201, 161, 74, 90), width=2)
        except Exception:
            pass

    # 顶栏小标
    center(d, '思想会客厅', 70, font(CJK, 26), SUB, spacing=4)
    d.line([cx-90, 112, cx+90, 112], fill=GOLD, width=2)

    # 大师名（大字，长名自动缩号）
    nf, nsize = fit_font(d, cn, CJK, 78, 40, W - 80, spacing=10)
    center(d, cn, 415, nf, CREAM, spacing=10 if nsize >= 60 else 4)

    # 代表作
    if work:
        wf, _ = fit_font(d, '代表作  ' + work, CJK, 26, 16, W - 90)
        center(d, '代表作  ' + work, 505, wf, GOLD)

    # 招牌主题（最多 3 行）
    ty = 560
    for th in themes[:3]:
        tf, _ = fit_font(d, th, CJK, 28, 18, W - 90)
        center(d, th, ty, tf, CREAM)
        ty += 46

    # 二维码卡片（深链：扫码直接选中该大师）
    qrimg = qr_png(url, 280)
    card_y = 720
    d.rounded_rectangle([cx-200, card_y, cx+200, card_y+400], radius=28, fill=(250, 247, 241, 255))
    img.paste(qrimg, (cx-140, card_y+30))
    cap = '长按识别 · 与' + cn + '对话'
    cf, _ = fit_font(d, cap, CJK, 25, 15, 380)
    d.text((cx, card_y+336), cap, font=cf, fill=(107, 93, 74, 255), anchor='mm')

    # 底部
    center(d, '免费体验 3 次', 1180, font(CJK, 28), GOLD, spacing=3)
    center(d, '合作交流加微信：fuping394319746', 1270, font(CJK, 21), DIM)

    return img.convert('RGB'), url

# ---------- 总览海报 ----------
def make_overview():
    url = BASE
    img = gradient_bg()
    img = glow(img, W, 0, 420, (201, 161, 74, 150))
    img = glow(img, 0, H-140, 380, (192, 86, 59, 110))
    d = ImageDraw.Draw(img, 'RGBA')
    cx = W // 2

    d.rounded_rectangle([cx-48, 70, cx+48, 166], radius=24, fill=(233, 196, 106, 255))
    d.rounded_rectangle([cx-48, 70, cx+48, 166], radius=24, fill=(192, 86, 59, 90))
    d.text((cx, 118), '思', font=font(CJK, 54), fill=BROWN, anchor='mm')

    title = '思想会客厅'
    tf, ts = fit_font(d, title, CJK, 62, 30, W - 100, spacing=8)
    center(d, title, 196, tf, CREAM, spacing=8 if ts >= 50 else 3)

    tagline = '让 25 位顶尖思想家，用他们的认知框架帮你思考'
    gf, _ = fit_font(d, tagline, CJK, 24, 15, W - 70)
    center(d, tagline, 292, gf, SUB)

    m1 = '芒格 · 乔布斯 · 费曼 · 纳瓦尔 · 王阳明 · 稻盛和夫'
    m2 = '巴菲特 · 达利欧 · 尼采 · 老子 · 孙子 · 塔勒布 · 凯恩斯 …'
    for text, yy in ((m1, 380), (m2, 428)):
        mf, _ = fit_font(d, text, CJK, 24, 15, W - 70)
        center(d, text, yy, mf, GOLD)

    points = [
        '负债、辞职、婚姻、35 岁危机——说出你的纠结',
        '多位大师同时作答，观点碰撞对照',
        '不是鸡汤语录，是可执行的思考框架',
    ]
    py = 510
    for p in points:
        pf2, _ = fit_font(d, p, CJK, 24, 15, W - 140)
        d.text((60, py), '✦', font=font(CJK, 24), fill=GOLD)
        d.text((94, py), p, font=pf2, fill=CREAM)
        py += 48

    qrimg = qr_png(url, 280)
    card_y = 770
    d.rounded_rectangle([cx-200, card_y, cx+200, card_y+380], radius=28, fill=(250, 247, 241, 255))
    img.paste(qrimg, (cx-140, card_y+28))
    cap = '长按识别二维码，立即体验'
    cf, _ = fit_font(d, cap, CJK, 23, 15, 380)
    d.text((cx, card_y+322), cap, font=cf, fill=(107, 93, 74, 255), anchor='mm')

    center(d, '免费体验 3 次', 1200, font(CJK, 28), GOLD, spacing=3)
    center(d, '合作交流加微信：fuping394319746', 1360, font(CJK, 21), DIM)
    return img.convert('RGB'), url

# ---------- 执行 ----------
skills = json.load(open(SKILLS_JSON, encoding='utf-8'))['skills']
thinkers = [s for s in skills if s['name'] in META]
print(f'载入思想家 {len(thinkers)} 位，开始生成海报 → {OUT}')
items = []

ovi, ourl = make_overview()
ovi.save(os.path.join(OUT, '00-总览.png'))
items.append(('总览 · 扫码进大厅', ourl, '00-总览.png'))
print(f'  [ 总览 ] -> {os.path.join(OUT, "00-总览.png")}')

for i, s in enumerate(thinkers, 1):
    tid = s['name']
    img, url = make_poster(tid, s.get('display_name', tid))
    fn = os.path.join(OUT, tid + '.png')
    img.save(fn)
    items.append((cn_name(s.get('display_name', tid)), url, os.path.basename(fn)))
    print(f'  [{i:2d}/{len(thinkers)}] {tid:22s} -> {fn}')

# 预览画廊
cards = '\n'.join(
    f'<div class="c"><img src="{fn}"><div class="meta"><b>{t}</b>'
    f'<code>{u}</code><a href="{u}" target="_blank">打开链接 ↗</a></div></div>'
    for t, u, fn in items
)
html = f'''<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8">
<title>思想会客厅 · 海报预览</title><style>
body{{font-family:-apple-system,"PingFang SC",sans-serif;background:#1c1611;margin:0;padding:30px;color:#eee}}
h1{{font-size:24px;margin:0 0 6px}}p{{opacity:.6;margin:0 0 24px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:22px}}
.c{{background:#2b2118;border-radius:16px;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,.4)}}
.c img{{width:100%;display:block}}.meta{{padding:12px 14px}}.meta b{{font-size:18px}}
code{{display:block;font-size:11px;opacity:.5;margin:6px 0;word-break:break-all}}
a{{color:#e9c46a;font-size:13px;text-decoration:none}}</style></head>
<body><h1>思想会客厅 · 海报预览</h1>
<p>总览 1 张 + 大师专属 {len(thinkers)} 张 · 扫码即选中对应大师（深链 ?thinker=id）</p>
<div class="grid">{cards}</div></body></html>'''
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)
print('画廊 ->', os.path.join(OUT, 'index.html'))
