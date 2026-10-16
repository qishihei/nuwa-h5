#!/usr/bin/env python3
# 本地生成「聊天录屏」式竖屏引流视频：模拟 nuwa-h5 与 AI 马斯克对话 + 中文配音 + 结尾二维码
# 依赖：ffmpeg(已装) / macOS say(已装) / Pillow / qrcode / numpy
import os, subprocess, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode

HERE = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(HERE, '_vid_tmp')
os.makedirs(TMP, exist_ok=True)
W, H = 1080, 1920
FPS = 25
RATE = 240  # say 语速(words/min)，默认~200；240≈1.2x，比 ffmpeg 提速更自然
FONT = '/System/Library/Fonts/Hiragino Sans GB.ttc'
def f(sz, idx=0): return ImageFont.truetype(FONT, sz, index=idx)

# ---------- 对话脚本 ----------
BEATS = [
    ('title', 'host',
     '如果你的创业难题，能直接甩给马斯克，他会怎么回？我替你试了。'),
    ('you', 'you', '成本一直降不下来，供应商说这已经是最低价了。'),
    ('musk', 'musk',
     '供应商说“最低价”？那是类比思维。第一性原理——拆到原材料和物理成本，火箭材料也只占售价一小部分。先算真实成本，再谈价。'),
    ('you', 'you', '东西能做出来，但团队交付越来越慢。'),
    ('musk', 'musk',
     '大公司病。5 步工程法第一步是「删」。把一半需求直接删掉，别急着优化——你优化的要是没必要的零件，越优化越糟。'),
    ('you', 'you', '很多人都说我这想法“不可能”。'),
    ('musk', 'musk',
     '物理定律是唯一真实约束，它不关心你的感受。先问“理论上最好能多好”，推到极限再逼近它。剩下的恐惧，多半是风险被高估了。'),
    ('cap', 'host',
     '……注意，他不是在复述金句，是真的拿物理和数学在推。'),
    ('end', 'host',
     '这套「用马斯克方式思考」的对话，nuwa-h5 上能跟 25 位大师聊。把你卡住的问题，直接甩给他。'),
]

# ---------- TTS ----------
def tts(text, voice, out_wav, pitch=None, rate=None):
    aiff = out_wav[:-4] + '.aiff'
    cmd = ['say', '-v', voice]
    if rate: cmd += ['-r', str(rate)]
    cmd += ['-o', aiff, text]
    subprocess.run(cmd, check=True)
    if pitch:
        # 离线无 rubberband/sox：asetrate 降采样率=降调+变慢，atempo 拉回语速
        # 关键：最终输出必须保持降后的采样率，否则 ffmpeg 重采样会把音高拉回女声
        af = f'asetrate=32000,atempo={pitch}'
        subprocess.run(['ffmpeg','-y','-i',aiff,'-af',af,out_wav], check=True)
    else:
        subprocess.run(['ffmpeg','-y','-i',aiff,out_wav], check=True)
    os.remove(aiff)

def dur(wav):
    return float(subprocess.run(['ffprobe','-v','error','-show_entries',
        'format=duration','-of','default=noprint_wrappers=1:nokey=1',wav],
        capture_output=True, text=True).stdout.strip())

VOICE_YOU = 'Ting-Ting'
VOICE_MUSK = 'Ting-Ting'
# 离线无男声：用统一降调模拟男声（同音高，避免重采样拉回女声）
# 目标采样率取 32000Hz（=44100×0.7256），是 AAC 合法采样率，可保住降调效果
PITCH = 32000 / 44100

# ---------- 文字换行 ----------
def wrap(text, font, max_w):
    d = ImageDraw.Draw(Image.new('RGB',(10,10)))
    lines, cur = [], ''
    for ch in text:
        if d.textlength(cur+ch, font=font) > max_w and cur:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur: lines.append(cur)
    return lines

# ---------- 渲染 ----------
BG = (14,14,16); PANEL = (22,22,26); BUB_YOU = (43,108,255); BUB_MUSK = (38,38,44)
TXT = (235,235,238); DIM = (150,150,156); ACCENT = (233,196,106)

def draw_chat(messages, newest=None):
    img = Image.new('RGB',(W,H),BG)
    d = ImageDraw.Draw(img,'RGBA')
    # 顶栏
    d.rounded_rectangle([40,70,W-40,200],radius=24,fill=PANEL)
    d.text((72,104),'nuwa-h5 · 思想会客厅',font=f(40),fill=TXT)
    d.text((W-72,112),'埃隆·马斯克',font=f(40),fill=ACCENT,anchor='ra')
    d.text((72,156),'AI 生成 · 灵感来自马斯克思维框架 · 非本人',font=f(26),fill=DIM)
    # 消息区
    px0,px1 = 60, W-60
    pad = 22; bw = 700
    y = 250
    for sp, lines in messages:
        if sp == 'musk':
            d.text((px0+pad, y),'埃隆·马斯克',font=f(27),fill=DIM); y += 40
            bx = px0+pad
        else:
            bx = px1-pad-bw
        lh = 46
        bh = len(lines)*lh + pad*2
        box = [bx, y, bx+bw, y+bh]
        fill = BUB_YOU if sp=='you' else BUB_MUSK
        d.rounded_rectangle(box, radius=22, fill=fill)
        for i,ln in enumerate(lines):
            tx = bx+pad if sp=='musk' else bx+pad
            d.text((tx, y+pad+i*lh), ln, font=f(33), fill=(255,255,255) if sp=='you' else TXT)
        y += bh + 34
    return img

def draw_card(title, sub, qr=False):
    img = Image.new('RGB',(W,H),BG)
    d = ImageDraw.Draw(img)
    tf = f(56)
    lines = wrap(title, tf, W-160)
    lh = 80
    total = len(lines)*lh
    y0 = 560 - total//2 + lh//2
    for i,ln in enumerate(lines):
        d.text((W//2, y0+i*lh), ln, font=tf, fill=TXT, anchor='mm')
    if sub:
        d.text((W//2, 560+total//2+70), sub, font=f(34), fill=DIM, anchor='mm', align='center')
    if qr:
        q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=18, border=4)
        q.add_data('https://nuwa-h5.onrender.com/?thinker=elon-musk')
        qm = q.make_image(fill_color='#111', back_color='white').convert('RGB')
        qm = qm.resize((360,360))
        img.paste(qm, ((W-360)//2, 1000))
        d.text((W//2, 1000-46),'扫码，把问题直接甩给马斯克',font=f(38),fill=ACCENT,anchor='mm')
        d.text((W//2, 1000+360+60),'nuwa-h5.onrender.com · 思想会客厅',font=f(30),fill=DIM,anchor='mm')
        d.text((W//2, 1000+360+120),'AI 生成演示，非真人言论，仅供娱乐',font=f(26),fill=DIM,anchor='mm')
    return img

def render_frame(beat_type, messages, text):
    if beat_type in ('title','cap'):
        return draw_card(text, None)
    if beat_type == 'end':
        return draw_card(text, None, qr=True)
    return draw_chat(messages)

# ---------- 生成 ----------
clips = []
state = []   # 已确定的对话气泡
for i,(btype, speaker, text) in enumerate(BEATS):
    wav = os.path.join(TMP, f'v{i}.wav')
    if speaker == 'musk':
        tts(text, VOICE_MUSK, wav, PITCH, RATE)
    else:
        tts(text, VOICE_YOU, wav, PITCH, RATE)
    dd = dur(wav)
    # 更新对话状态
    if btype in ('you','musk'):
        lines = wrap(text, f(33), 700-44)
        state.append((btype, lines))
    frame = render_frame(btype, state, text)
    fp = os.path.join(TMP, f'f{i}.png'); frame.save(fp)
    mp4 = os.path.join(TMP, f'c{i}.mp4')
    subprocess.run(['ffmpeg','-y','-loop','1','-i',fp,'-i',wav,
        '-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',
        '-t',str(dd+0.15),'-r',str(FPS), mp4], capture_output=True)
    clips.append(mp4)
    print(f'  [{i+1}/{len(BEATS)}] {btype:5s} {dd:.1f}s -> {mp4}')

with open(os.path.join(TMP,'list.txt'),'w') as lf:
    for c in clips: lf.write(f"file '{c}'\n")
out = os.path.join(HERE,'musk_chat_promo_male.mp4')
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',os.path.join(TMP,'list.txt'),
    '-c:v','libx264','-c:a','aac','-b:a','192k','-ar','32000','-pix_fmt','yuv420p', out], check=True)
print('OUTPUT ->', out)
