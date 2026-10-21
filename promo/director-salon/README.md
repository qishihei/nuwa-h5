# 冷启动优化：静态落地页 + 投放期保活

解决 Render 免费版冷启动带来的「扫码后先看 10–60 秒 Render 启动页」问题。

## 方案组成

| 文件 | 作用 |
|---|---|
| `landing/index.html` | 即时静态落地页。秒开，显示「正在唤醒导播室」加载动画，轮询 `/api/persons`，服务就绪后自动带 `?director=` 深链跳转进对话 |
| `landing/netlify.toml` | Netlify 静态托管配置（无构建） |
| `keep-warm.sh` | 投放期保活：周期性 ping 健康接口，让实例不休眠、避开冷启动 |
| `generate_landing_qrs.py` | 生成 25 位导演的「落地页 + `?director=`」二维码（地址可配置） |

## 生效路径（三步）

### 1. 部署落地页（二选一，都要「秒开、免冷启动」）

**路线 A · GitHub Pages**（需先开启，实测当前**未启用**，访问返回 `Site not found · GitHub Pages`）
1. 仓库 `qishihei/nuwa-h5` → **Settings** → **Pages** → Source 选 **Deploy from a branch** → Branch `main`、目录 `/ (root)` → Save。
2. 等 1–2 分钟，访问应返回页面而非 404：
   `https://qishihei.github.io/nuwa-h5/promo/director-salon/landing/?director=charlie-chaplin`
3. 若你的 Pages 源是 `/docs` 或 `gh-pages` 分支，路径会不同——以实际能打开的地址为准。

**路线 B · Netlify（最快，不用改仓库设置）**
- 把 `landing/` 整个文件夹拖到 <https://app.netlify.com/drop>，立刻得到 `https://<随机名>.netlify.app`。
- 或连接仓库：Base directory 填 `promo/director-salon/landing`，`netlify.toml` 已配好（publish `.`、无 build command）。

记下落地页地址 `<LANDING>`（不带结尾 `/`）。

### 2. 生成指向落地页的二维码

```bash
cd promo/director-salon
python3 generate_landing_qrs.py https://<你的落地页地址>
# 例：python3 generate_landing_qrs.py https://abc123.netlify.app
```
产出 `landing_qrs/<导演id>.png` 共 25 张。用它替换卡片/海报里的旧二维码，或直接把新图发出去。

### 3. 投放期间保活

```bash
./keep-warm.sh start     # 后台保活（日志 keep-warm.log）
./keep-warm.sh status
./keep-warm.sh stop      # 投放结束务必停
```

## ⚠️ 额度红线（务必看）

Render 免费额度是**账号级 750 实例小时/月**，账号下所有 Web 服务**共享**。
单个服务 24h 常驻 ≈ 730 小时/月。你有 nuwa-h5 / director-salon / thought-salon 多个服务，
**同时长期保活会超额度、当月被停**。因此保活脚本只在投放期开、结束即停。

**最省事的终极解**：把 `director-salon` 升级到 Render Starter（约 \$7/月）→ 常驻不休眠、
无冷启动，以上两样都不需要。引流场景建议直接升级。

## 技术说明

- 健康接口 `/api/persons` 在线时返回 JSON（服务端已开 CORS `*`），可被落地页跨域轮询；
  冷启动期该路径返回 Render 启动页 HTML（无 CORS），落地页据此判定「尚未真醒」。
- 落地页带 5 秒兜底「仍要进入 →」按钮：即使浏览器拦截轮询，用户也能手动进。
- `landing/index.html` 支持 `?app=` 覆盖目标服务地址，便于测试其它实例。
- 已实测：服务热态下 `/api/persons` 返回 `{"persons":[{"name":"charlie-chaplin",...`，
  深链参数为 `?director=<name>`（如 `charlie-chaplin`、`wong-kar-wai`）。
