#!/usr/bin/env python3
# 生成 25 位导演的「落地页深链」二维码：<LANDING>/?director=<name>
# 用途：替代原来直连 director-salon.onrender.com 的二维码，先落到即时静态页，避开冷启动。
#
# 用法：
#   python3 generate_landing_qrs.py                      # 用下面 LANDING 默认值
#   python3 generate_landing_qrs.py https://xxx.netlify.app
#   LANDING_URL=https://xxx.netlify.app python3 generate_landing_qrs.py
import os, sys, json, qrcode

HERE = os.path.dirname(os.path.abspath(__file__))
# h5/promo/director-salon/  ->  h5/directors/directors.json
DATA = os.path.normpath(os.path.join(HERE, '..', '..', 'directors', 'directors.json'))
OUT = os.path.join(HERE, 'landing_qrs')

# ↓↓↓ 默认落地页地址（可被命令行参数 / 环境变量覆盖），不要以 / 结尾 ↓↓↓
# GitHub Pages 需先在仓库 Settings → Pages 启用（Deploy from a branch: main, /root）
LANDING = 'https://qishihei.github.io/nuwa-h5/promo/director-salon/landing'

def main():
    landing = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get('LANDING_URL') or LANDING).rstrip('/')
    os.makedirs(OUT, exist_ok=True)
    directors = json.load(open(DATA, encoding='utf-8'))['directors']
    for d in directors:
        name = d.get('name')
        if not name: continue
        url = f'{landing}/?director={name}'
        q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=2)
        q.add_data(url); q.make(fit=True)
        q.make_image(fill_color='#111111', back_color='white').convert('RGB').save(
            os.path.join(OUT, f'{name}.png'))
    print(f'wrote {len(directors)} landing QRs -> {OUT}')
    print(f'landing base = {landing}')
    print(f'验证示例：{landing}/?director=charlie-chaplin')

if __name__ == '__main__':
    main()
