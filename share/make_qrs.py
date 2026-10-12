#!/usr/bin/env python3
# 重新生成思想会客厅文字版海报用的两个静态二维码，指向活的 Render 部署
# 用法: python3 make_qrs.py
import qrcode

URL = 'https://nuwa-h5.onrender.com'

def gen(fn, url, box=10, border=2):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=box, border=border)
    qr.add_data(url); qr.make(fit=True)
    img = qr.make_image(fill_color='#2b2118', back_color='white').convert('RGB')
    img.save(fn)
    print('生成', fn, '->', url)

gen('link-qr.png', URL)
gen('en-link-qr.png', URL)
print('完成（如需指向其他地址，改本脚本顶部 URL 即可）')
