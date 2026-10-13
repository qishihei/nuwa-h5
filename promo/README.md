# 宣发引流素材总览

两版 H5 的宣发/引流海报统一放在本文件夹，便于一处找到、直接取用。

## 线上地址（解锁/体验入口）
- 思想会客厅（25 位大师）：https://nuwa-h5.onrender.com
- 导演会客厅版：https://director-salon.onrender.com
- 后台解锁（管理口令）：`https://nuwa-h5.onrender.com/admin.html` ｜ `https://director-salon.onrender.com/admin.html`

> Render 免费实例会休眠，首次打开可能要等几十秒冷启动。

## 文件夹结构
```
promo/
├── thought-salon/              # 思想会客厅版
│   ├── poster-zh.png           # 中文整站主海报（二维码→整站）
│   ├── poster-en.png           # 英文整站主海报
│   ├── 00-总览.png             # 25 位大师九宫格总览海报
│   ├── gallery.html            # 25 张单人海报画廊（网页预览）
│   └── thinkers/               # 25 张单人引流海报（按大师命名）
│       ├── charlie-munger.png
│       ├── confucius.png
│       └── ...（共 25 张）
│
└── director-salon/             # 导演会客厅版
    ├── poster-zh.png           # 中文整站主海报
    ├── poster-en.png           # 英文整站主海报
    ├── 00-总览.png             # 导演九宫格总览海报
    ├── gallery.html            # 25 张单人海报画廊
    └── directors/              # 25 张单人引流海报（按导演命名）
        ├── akira-kurosawa.png
        ├── wong-kar-wai.png
        └── ...（共 25 张）
```

## 取用建议
- **朋友圈/社群引流**：用 `poster-zh.png`（整站主海报，扫码进整站）。
- **单点人物种草**：从 `thinkers/` 或 `directors/` 取对应单人海报，每张二维码直达该人物的专属对话页。
- **九宫格晒图**：用 `00-总览.png` 或 `gallery.html` 截图拼图。

## 重新生成（源脚本位置，本文件夹为拷贝快照）
- 思想会客厅：`h5/share/make_zh_poster.py`、`make_en_poster.py`、`make_thinker_posters.py`
- 导演版：`h5/directors/share/make_posters.py`、`make_director_posters.py`

> 注意：本 `promo/` 为静态拷贝，重跑上述脚本后需手动再拷贝一次以保持同步。
