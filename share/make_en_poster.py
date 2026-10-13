from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 750, 1440
TOP, MID, BOT = (0x2b,0x21,0x18), (0x4a,0x38,0x26), (0x2b,0x21,0x18)

REG_PATHS = ['/System/Library/Fonts/Supplemental/Arial.ttf', '/Library/Fonts/Arial.ttf', '/System/Library/Fonts/Helvetica.ttc']
BOLD_PATHS = ['/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf', '/System/Library/Fonts/Helvetica.ttc']

def font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()

REG = lambda s: font(REG_PATHS, s)
BOLD = lambda s: font(BOLD_PATHS, s)

base = Image.new('RGB', (W, H))
px = base.load()
for y in range(H):
    t = y / (H - 1)
    if t < 0.55:
        f = t / 0.55; c = tuple(int(TOP[i] + (MID[i]-TOP[i])*f) for i in range(3))
    else:
        f = (t - 0.55) / 0.45; c = tuple(int(MID[i] + (BOT[i]-MID[i])*f) for i in range(3))
    for x in range(W):
        px[x, y] = c
img = base.convert('RGBA')
d = ImageDraw.Draw(img, 'RGBA')

def glow(cx, cy, r, color):
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    steps = 12
    for i in range(steps, 0, -1):
        a = int(color[3] * (1 - i/steps) * 0.5)
        rr = r * i / steps
        gd.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], fill=(color[0], color[1], color[2], a))
    return g.filter(ImageFilter.GaussianBlur(50))

img = Image.alpha_composite(img, glow(W, 0, 420, (201,161,74,150)))
img = Image.alpha_composite(img, glow(0, H-140, 380, (192,86,59,110)))
d = ImageDraw.Draw(img, 'RGBA')

CREAM = (243,233,216,255); GOLD = (233,196,106,255); SUB = (243,233,216,217); DIM = (243,233,216,154)
cx = W // 2

def center(text, y, fnt, fill):
    w = d.textlength(text, font=fnt)
    d.text((cx - w/2, y), text, font=fnt, fill=fill)

# logo
d.rounded_rectangle([cx-48, 70, cx+48, 166], radius=24, fill=(233,196,106,255))
d.rounded_rectangle([cx-48, 70, cx+48, 166], radius=24, fill=(192,86,59,90))
d.text((cx-22, 84), 'M', font=BOLD(56), fill=(43,33,24,255))

center('The Salon of Minds', 196, BOLD(58), CREAM)
center('25 great thinkers, each lending you their mental models', 286, REG(24), SUB)
center('Charlie Munger · Steve Jobs · Richard Feynman · Naval · Wang Yangming · Inamori', 372, REG(24), GOLD)
center('Buffett · Dalio · Nietzsche · Laozi · Sun Tzu · Taleb · Keynes …', 420, REG(24), GOLD)

pts = ['Debt, quitting, marriage, the 35-year-old crisis — name your knot',
       'Multiple masters answer at once, perspectives in collision',
       'Not platitudes — actionable thinking frameworks']
py = 500
for p in pts:
    d.text((60, py), '✦', font=REG(24), fill=GOLD)
    d.text((94, py), p, font=REG(24), fill=CREAM)
    py += 46

qr = Image.open('en-link-qr.png').convert('RGB').resize((280, 280))
card_y = 760
d.rounded_rectangle([cx-200, card_y, cx+200, card_y+380], radius=28, fill=(250,247,241,255))
img.paste(qr, (cx-140, card_y+28))
d.text((cx, card_y+322), 'Scan to enter · English version', font=REG(23), fill=(107,93,74,255), anchor='mm')

center('WeChat: fuping394319746', 1340, REG(21), DIM)

img.convert('RGB').save('en-poster.png')
print('saved en-poster.png')
