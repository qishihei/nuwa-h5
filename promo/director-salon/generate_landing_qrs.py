#!/usr/bin/env python3
# 生成 25 位导演的「落地页深链」二维码：<LANDING>/?director=<name>
# 用途：替代原来直连 director-salon.onrender.com 的二维码，先落到即时静态页，避开冷启动。
import os, json, qrcode

HERE = os.path.dirname(os.path.abspath(__file__))
# h5/promo/director-salon/  ->  h5/directors/directors.json
DATA = os.path.normpath(os.path.join(HERE, '..', '..', 'directors', 'directors.json'))
OUT = os.path.join(HERE, 'landing_qrs')

# ↓↓↓ 改成你的静态落地页地址（GitHub Pages / Netlify / CF Pages 均可），不要以 / 结尾 ↓↓↓
LANDING = 'https://qishihei.github.io/nuwa-h5/promo/director-salon/landing'

def main():
    os.makedirs(OUT, exist_ok=True)
    directors = json.load(open(DATA, encoding='utf-8'))['directors']
    for d in directors:
        name = d.get('name')
        if not name: continue
        url = f'{LANDING}/?director={name}'
        q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=2)
        q.add_data(url); q.make(fit=True)
        q.make_image(fill_color='#111111', back_color='white').convert('RGB').save(
            os.path.join(OUT, f'{name}.png'))
    print(f'wrote {len(directors)} landing QRs -> {OUT}')
    print(f'landing base = {LANDING}')
    print('提示：若你的落地页地址不同，请改本脚本 LANDING 常量后重跑。')

if __name__ == '__main__':
    main()
