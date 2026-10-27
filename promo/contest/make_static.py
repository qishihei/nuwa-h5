#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把「思想会客厅 / 导演会客厅」打成可静态托管的发布包。

背景：WorkBuddy「1024 造物挑战」投稿表单第 06 项要求体验链接必须带 sharecode 参数，
而 sharecode 只有 app.workbuddy.host 才会发放 —— 那个域名只托管静态站。
本脚本把纯前端剥离出来，让它跨域去调仍在 Render 上的后端（后端已带 CORS: *）。

产出：
    promo/submit/thought-static/     → 思想会客厅静态包
    promo/submit/director-static/    → 导演会客厅静态包

用法：
    python3 make_static.py
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# ROOT = nuwa-skill/h5
SUBMIT = os.path.join(ROOT, 'promo', 'submit')

# 需要随包发布的静态资源（全部是根绝对路径引用，必须放在托管根目录）
ASSETS = [
    'index.html', 'en.html',
    'app.js', 'config.js', 'style.css',
    'html2canvas.min.js',
    'icon.png', 'icon.svg', 'manifest.webmanifest',
    'pains.json', 'pains_en.json',
    'site-qr.png', 'wechat_pay_qr.png',
]

JOBS = [
    {
        'key': 'thought',
        'src': os.path.join(ROOT, 'public'),
        'out': os.path.join(SUBMIT, 'thought-static'),
        'backend': 'https://nuwa-h5.onrender.com',
        'title': '思想会客厅',
    },
    {
        'key': 'director',
        'src': os.path.join(ROOT, 'directors', 'public'),
        'out': os.path.join(SUBMIT, 'director-static'),
        'backend': 'https://director-salon.onrender.com',
        'title': '导演会客厅',
    },
]

NOTE = """# {title} · 静态发布包

用于 WorkBuddy「1024 造物挑战」投稿，目的是拿到带 sharecode 的体验链接。

## 这包是什么

纯前端。**问答能力由后端提供**，后端仍在 Render（`{backend}`），所以：

- 发布前请确认后端是「热」的（否则首次打开要等冷启动）
  ```bash
  cd ../../thought-salon && ./keep-warm.sh status     # 思想线
  cd ../../director-salon && ./keep-warm.sh status    # 导演线
  ```
- 免费额度存在浏览器 localStorage，换浏览器/清缓存会重置

## 发布步骤（在 WorkBuddy 客户端）

1. 首页切「开发」模式 →「开发网站」
2. 把本文件夹**全部文件**交给它发布（**不要漏 `pains.json` 和图片**，否则痛点池和二维码会失效）
3. 拿到形如 `https://xxx.app.workbuddy.host/?sharecode=XXXXXXXXXX` 的链接
4. 用**无痕窗口**打开，走一遍：选人 → 提问 → 看到回答
5. 把这个链接填进投稿表单第 06 项

## 生成方式

```bash
cd ../../../promo/contest && python3 make_static.py
```
"""


def build(job):
    src, out = job['src'], job['out']
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    missing = []
    for name in ASSETS:
        p = os.path.join(src, name)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(out, name))
        else:
            missing.append(name)
    if missing:
        print(f"  ⚠ {job['title']} 缺少资源: {', '.join(missing)}")

    # 把 API_BASE 指向 Render 后端；同源部署时它是空字符串，静态站必须显式写全域名
    cfg = os.path.join(out, 'config.js')
    text = open(cfg, encoding='utf-8').read()
    new_text, n = re.subn(
        r"window\.API_BASE\s*=\s*''",
        "window.API_BASE = '%s'" % job['backend'],
        text,
    )
    if n == 0:
        # 兼容写成 "..." / 已有值的情况
        new_text, n = re.subn(
            r"window\.API_BASE\s*=\s*[^;]*;",
            "window.API_BASE = '%s';" % job['backend'],
            text,
        )
    open(cfg, 'w', encoding='utf-8').write(new_text)

    open(os.path.join(out, 'README.md'), 'w', encoding='utf-8').write(
        NOTE.format(title=job['title'], backend=job['backend'])
    )

    size = sum(
        os.path.getsize(os.path.join(out, f))
        for f in os.listdir(out)
        if os.path.isfile(os.path.join(out, f))
    )
    files = sorted(os.listdir(out))
    print(f"✅ {job['title']} → {out}")
    print(f"   文件 {len(files)} 个，{size/1024:.0f} KB，后端 {job['backend']}")
    print(f"   config.js: {[l for l in new_text.splitlines() if 'API_BASE' in l and not l.strip().startswith('//')]}")
    return missing


def main():
    print('=' * 60)
    print('生成静态发布包（供 WorkBuddy 发布拿 sharecode）')
    print('=' * 60)
    for job in JOBS:
        build(job)
    print('=' * 60)
    print('下一步：把 thought-static / director-static 各自在 WorkBuddy 里发布，')
    print('拿到 https://xxx.app.workbuddy.host/?sharecode=XXX 后填进投稿表单。')


if __name__ == '__main__':
    main()
