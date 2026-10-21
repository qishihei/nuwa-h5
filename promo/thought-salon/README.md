# 思想会客厅海报 · 冷启动优化

针对 `share/make_thinker_posters.py` 生成的 25+1 张大师海报（扫码 → `nuwa-h5.onrender.com`）。

## 现状结论

- **深链：已处理**。海报二维码内容为 `{BASE}/?thinker=<id>`（如 `?thinker=jensen-huang`），
  应用端 `public/app.js` 认 `?thinker=` / `?t=`，扫码即选中该大师。
- **冷启动：本目录此前未覆盖**。扫码仍直连 Render，闲置 15 分钟后首次扫码会先看到
  10–60 秒的 Render 启动页。现补齐与导演沙龙同款的方案 ↓

## 三件套

| 文件 | 作用 |
|---|---|
| `landing/index.html` | 即时静态落地页（秒开）：「正在唤醒会客厅」动画 + 轮询 `/api/persons`，就绪后带 `?thinker=` 深链跳转 |
| `landing/netlify.toml` | Netlify 静态托管配置 |
| `keep-warm.sh` | 投放期保活（默认 ping `https://nuwa-h5.onrender.com/api/persons`） |

## 生效路径

> **当前已部署（思想会客厅）**：`https://peaceful-paletas-5880b5.netlify.app`（Netlify Drop）。
> ⚠️ 需在 Netlify 后台点过 **Make public** 才对匿名扫码可见；海报/卡片的二维码已按此地址重刷
> （`share/posters/`、`share/cards/`，并同步到 `promo/thought-salon/`）。

1. **部署落地页**（二选一）
   - Netlify：把 `landing/` 拖到 <https://app.netlify.com/drop> → 得到地址
   - GitHub Pages：仓库 Settings → Pages → Source `main` + `/ (root)`（实测当前未启用，需先开启）
2. **重刷海报二维码**（复用原海报脚本，把 BASE 换成落地页地址即可）：
   ```bash
   cd share
   python3 make_thinker_posters.py https://<你的落地页地址>
   ```
   产出 `share/posters/`：00-总览 + 25 张，二维码变为 `<落地页>/?thinker=<id>`。
   落地页会透传 `thinker` 参数，就绪后跳 `nuwa-h5.onrender.com/?thinker=<id>`。
3. **投放期间保活**：
   ```bash
   cd promo/thought-salon && ./keep-warm.sh start   # 结束务必 stop
   ```

## ⚠️ 额度红线

Render 免费额度是**账号级 750 实例小时/月**（所有服务共享）。
nuwa-h5 与 director-salon **不要同时长期保活**，只保活当期投放的那个；
根治方案仍是升级 Render Starter（约 \$7/月/服务）。
