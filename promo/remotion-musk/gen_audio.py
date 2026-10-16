#!/usr/bin/env python3
# 生成 9 段配音(mp3) + beats.json(对话状态/时长) + qr.png，供 Remotion 渲染使用
import os, subprocess, json, qrcode

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, 'public'); os.makedirs(PUB, exist_ok=True)
SRC = os.path.join(HERE, 'src'); os.makedirs(SRC, exist_ok=True)

RATE = 240                       # say 语速(words/min)
PITCH = 32000 / 44100            # 伪男声：降调到 32kHz(AAC/mp3 合法采样率，保住音高)
PITCH_HZ = 32000
WRAP = 18                        # 气泡每行字数

def wrap(text, n=WRAP):
    lines, cur = [], ''
    for ch in text:
        if len(cur) >= n and ch in '，。、；：！？“”‘’—':
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur: lines.append(cur)
    # 兜底：超长行再硬切
    out = []
    for ln in lines:
        while len(ln) > n:
            out.append(ln[:n]); ln = ln[n:]
        out.append(ln)
    return out

BEATS = [
    ('title', 'host', '如果你的创业难题，能直接甩给马斯克，他会怎么回？我替你试了。'),
    ('you',   'you',  '成本一直降不下来，供应商说这已经是最低价了。'),
    ('musk',  'musk', '供应商说“最低价”？那是类比思维。第一性原理——拆到原材料和物理成本，火箭材料也只占售价一小部分。先算真实成本，再谈价。'),
    ('you',   'you',  '东西能做出来，但团队交付越来越慢。'),
    ('musk',  'musk', '大公司病。5 步工程法第一步是「删」。把一半需求直接删掉，别急着优化——你优化的要是没必要的零件，越优化越糟。'),
    ('you',   'you',  '很多人都说我这想法“不可能”。'),
    ('musk',  'musk', '物理定律是唯一真实约束，它不关心你的感受。先问“理论上最好能多好”，推到极限再逼近它。剩下的恐惧，多半是风险被高估了。'),
    ('cap',   'host', '……注意，他不是在复述金句，是真的拿物理和数学在推。'),
    ('end',   'host', '这套「用马斯克方式思考」的对话，nuwa-h5 上能跟 25 位大师聊。把你卡住的问题，直接甩给他。'),
]

out, state = [], []
for i, (btype, speaker, text) in enumerate(BEATS):
    aiff = os.path.join(PUB, f'beat{i}.aiff')
    mp3 = os.path.join(PUB, f'beat{i}.mp3')
    subprocess.run(['say', '-v', 'Ting-Ting', '-r', str(RATE), '-o', aiff, text], check=True)
    af = f'asetrate={PITCH_HZ},atempo={PITCH:.6f}'
    subprocess.run(['ffmpeg', '-y', '-i', aiff, '-af', af, mp3], check=True)
    os.remove(aiff)
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', mp3],
        capture_output=True, text=True).stdout.strip())
    messages = list(state)
    if btype in ('you', 'musk'):
        cur = {'speaker': btype, 'lines': wrap(text)}
        messages = list(state) + [cur]
        state.append(cur)
    out.append({'idx': i, 'type': btype, 'speaker': speaker, 'text': text,
                'audio': f'beat{i}.mp3', 'dur': round(dur, 2), 'messages': messages})

json.dump(out, open(os.path.join(SRC, 'beats.json'), 'w'), ensure_ascii=False, indent=1)

# 结尾二维码：深链直达马斯克对话
q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=18, border=4)
q.add_data('https://nuwa-h5.onrender.com/?thinker=elon-musk')
q.make_image(fill_color='#111111', back_color='white').convert('RGB').save(os.path.join(PUB, 'qr.png'))
print('wrote', len(out), 'beats + qr.png')
