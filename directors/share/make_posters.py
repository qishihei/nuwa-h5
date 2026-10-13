#!/usr/bin/env python3
# 生成「导演大师会客厅」中英文分享海报
# 用法: python3 make_posters.py [访问地址]
#   不传则使用占位地址 https://director-salon.onrender.com
# 产物(均内嵌二维码, 直接可用):
#   director-poster-zh.html / director-poster-zh.png  (中文版)
#   director-poster-en.html / director-poster-en.png  (英文版)

import io, sys, base64
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter

URL = sys.argv[1] if len(sys.argv) > 1 else 'https://director-salon.onrender.com'

CJK = '/System/Library/Fonts/PingFang.ttc'
EN  = '/System/Library/Fonts/Helvetica.ttc'

W, H = 750, 1440
TOP, MID, BOT = (43, 33, 24), (74, 56, 38), (43, 33, 24)

# ---------- 二维码 ----------
def qr_b64(url):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(url); qr.make(fit=True)
    img = qr.make_image(fill_color='#2b2118', back_color='white')
    buf = io.BytesIO(); img.save(buf, 'PNG')
    return base64.b64encode(buf.getvalue()).decode()

QR = qr_b64(URL)

# ---------- 内容 ----------
CONTENT = {
    'zh': {
        'logo': '导', 'title': '导演大师会客厅',
        'tagline': '让百年影史百位殿堂级导演，用招牌技法帮你拆解电影创作难题',
        'm1': '黑泽明 · 费里尼 · 希区柯克 · 王家卫 · 宫崎骏 · 塔可夫斯基',
        'm2': '库布里克 · 伯格曼 · 小津安二郎 · 戈达尔 · 李安 · 奉俊昊 …',
        'points': [
            '剧本卡壳、调度混乱、调色廉价、表演僵硬——说出你的创作难题',
            '多位导演同台，用各自招牌技法给你可落地的思路',
            '不是泛泛而谈，是能直接用到镜头前的实操框架',
        ],
        'qr_cap': '长按识别二维码，立即体验',
        'footer': '合作交流加微信：fuping394319746',
        'font': CJK,
    },
    'en': {
        'logo': 'D', 'title': "The Director's Salon",
        'tagline': "A century of cinema's master directors, solving your film-craft problems through their lenses",
        'm1': 'Kurosawa · Fellini · Hitchcock · Wong Kar-wai · Miyazaki · Tarkovsky',
        'm2': 'Kubrick · Bergman · Ozu · Godard · Ang Lee · Bong Joon-ho …',
        'points': [
            'Script stuck, blocking messy, grade looks cheap, actors stiff — name your craft problem',
            'Multiple directors answer at once, each through their own craft',
            "Not vague advice — a framework you can put on screen",
        ],
        'qr_cap': 'Scan to enter · English version',
        'footer': 'WeChat: fuping394319746',
        'font': EN,
    },
}

# ---------- HTML ----------
def make_html(c):
    masters = f'<b>{c["m1"].split(" · ")[0]}</b> · <b>{c["m1"].split(" · ")[1]}</b> · <b>{c["m1"].split(" · ")[2]}</b> · <b>{c["m1"].split(" · ")[3]}</b> · <b>{c["m1"].split(" · ")[4]}</b> · <b>{c["m1"].split(" · ")[5]}</b><br>{c["m2"]}'
    points = ''.join(f'<div>{p}</div>' for p in c['points'])
    return f'''<!DOCTYPE html>
<html lang={("zh" if c["font"]==CJK else "en")}>
<head><meta charset="UTF-8"><style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif; background:#2b2118; }}
  #poster {{ width:750px; height:1440px; position:relative; overflow:hidden;
    background:linear-gradient(160deg,#2b2118 0%,#4a3826 55%,#2b2118 100%); color:#f3e9d8;
    display:flex; flex-direction:column; align-items:center; padding:70px 60px 0; }}
  #poster::before {{ content:""; position:absolute; right:-120px; top:-120px; width:420px; height:420px;
    background:radial-gradient(circle,rgba(201,161,74,.28),transparent 70%); border-radius:50%; }}
  #poster::after {{ content:""; position:absolute; left:-140px; bottom:140px; width:380px; height:380px;
    background:radial-gradient(circle,rgba(192,86,59,.18),transparent 70%); border-radius:50%; }}
  .logo {{ width:96px; height:96px; border-radius:24px; display:flex; align-items:center; justify-content:center;
    background:linear-gradient(135deg,#e9c46a,#c0563b); color:#2b2118; font-size:54px; font-weight:800;
    box-shadow:0 12px 32px rgba(0,0,0,.35); z-index:1; }}
  h1 {{ font-size:64px; letter-spacing:6px; margin-top:36px; font-weight:700; z-index:1; }}
  .tagline {{ font-size:25px; opacity:.85; margin-top:20px; letter-spacing:1px; z-index:1; white-space:nowrap; }}
  .masters {{ margin-top:40px; font-size:24px; line-height:2; text-align:center; opacity:.92; z-index:1; }}
  .masters b {{ color:#e9c46a; font-weight:700; }}
  .points {{ margin-top:32px; z-index:1; }}
  .points div {{ font-size:25px; margin-bottom:14px; padding-left:34px; position:relative; opacity:.95; }}
  .points div::before {{ content:"✦"; position:absolute; left:0; color:#e9c46a; }}
  .qr-card {{ margin-top:40px; background:#faf7f1; border-radius:28px; padding:26px;
    box-shadow:0 18px 48px rgba(0,0,0,.4); text-align:center; z-index:1; }}
  .qr-card img {{ width:280px; height:280px; display:block; }}
  .qr-card p {{ color:#6b5d4a; font-size:23px; margin-top:12px; font-weight:600; }}
  .footer {{ margin-top:auto; padding:24px 0 46px; font-size:21px; opacity:.6; letter-spacing:1px; z-index:1; }}
</style></head>
<body>
<div id="poster">
  <div class="logo">{c['logo']}</div>
  <h1>{c['title']}</h1>
  <div class="tagline">{c['tagline']}</div>
  <div class="masters">{masters}</div>
  <div class="points">{points}</div>
  <div class="qr-card">
    <img src="data:image/png;base64,{QR}" alt="qr">
    <p>{c['qr_cap']}</p>
  </div>
  <div class="footer">{c['footer']}</div>
</div>
</body>
</html>'''

# ---------- PNG ----------
def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def make_png(c):
    f = lambda s: font(c['font'], s)
    base = Image.new('RGB', (W, H)); px = base.load()
    for y in range(H):
        t = y / (H - 1)
        cc = tuple(int(TOP[i] + (MID[i]-TOP[i])*(t/0.55)) for i in range(3)) if t < 0.55 else tuple(int(MID[i] + (BOT[i]-MID[i])*((t-0.55)/0.45)) for i in range(3))
        for x in range(W): px[x, y] = cc
    img = base.convert('RGBA'); d = ImageDraw.Draw(img, 'RGBA')

    def glow(cx, cy, r, color):
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        for i in range(12, 0, -1):
            a = int(color[3] * (1 - i/12) * 0.5); rr = r * i / 12
            gd.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=(color[0], color[1], color[2], a))
        return g.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, glow(W, 0, 420, (201, 161, 74, 150)))
    img = Image.alpha_composite(img, glow(0, H-140, 380, (192, 86, 59, 110)))
    d = ImageDraw.Draw(img, 'RGBA')
    CREAM = (243, 233, 216, 255); GOLD = (233, 196, 106, 255); SUB = (243, 233, 216, 217); DIM = (243, 233, 216, 154)
    cx = W // 2

    def center(text, y, fnt, fill, spacing=0):
        if spacing:
            total = sum(d.textlength(ch, font=fnt) + spacing for ch in text) - spacing
            x = cx - total / 2
            for ch in text:
                d.text((x, y), ch, font=fnt, fill=fill); x += d.textlength(ch, font=fnt) + spacing
        else:
            w = d.textlength(text, font=fnt); d.text((cx - w/2, y), text, font=fnt, fill=fill)

    # logo
    d.rounded_rectangle([cx-48, 70, cx+48, 166], radius=24, fill=(233, 196, 106, 255))
    d.rounded_rectangle([cx-48, 70, cx+48, 166], radius=24, fill=(192, 86, 59, 90))
    d.text((cx, 118), c['logo'], font=f(54), fill=(43, 33, 24, 255), anchor='mm')
    # title (中文加字距)
    center(c['title'], 196, f(62), CREAM, spacing=8 if c['font'] == CJK else 0)
    center(c['tagline'], 286, f(24), SUB)
    center(c['m1'], 372, f(24), GOLD)
    center(c['m2'], 420, f(24), GOLD)
    # points
    py = 500
    for p in c['points']:
        d.text((60, py), '✦', font=f(24), fill=GOLD)
        d.text((94, py), p, font=f(24), fill=CREAM)
        py += 46
    # qr
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(URL); qr.make(fit=True)
    qrimg = qr.make_image(fill_color='#2b2118', back_color='white').convert('RGBA').resize((280, 280))
    card_y = 760
    d.rounded_rectangle([cx-200, card_y, cx+200, card_y+380], radius=28, fill=(250, 247, 241, 255))
    img.paste(qrimg, (cx-140, card_y+28))
    d.text((cx, card_y+322), c['qr_cap'], font=f(23), fill=(107, 93, 74, 255), anchor='mm')
    center(c['footer'], 1340, f(21), DIM)
    return img.convert('RGB')

for lang, c in CONTENT.items():
    open(f'director-poster-{lang}.html', 'w').write(make_html(c))
    make_png(c).save(f'director-poster-{lang}.png')
    print(f'director-poster-{lang}.html / director-poster-{lang}.png  ->  {URL}')
