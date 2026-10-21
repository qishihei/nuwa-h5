# 冷启动优化：静态落地页 + 投放期保活

解决 Render 免费版冷启动带来的「扫码后先看 10–60 秒 Render 启动页」问题。

## 方案组成

| 文件 | 作用 |
|---|---|
| `landing/index.html` | 即时静态落地页。秒开，显示「正在唤醒导播室」品牌化加载动画，轮询 `/api/persons`，服务就绪后自动带 `?director=` 深链跳转进对话 |
| `keep-warm.sh` | 投放期保活：周期性 ping 健康接口，让实例不休眠、避开冷启动 |
| `generate_landing_qrs.py` | 把 25 位导演的落地二维码统一指向「静态落地页 + `?director=`」 |

## 生效路径（三步）

1. **部署落地页**（任选，秒开、免冷启动）
   - GitHub Pages：仓库 `qishihei/nuwa-h5` 开 Pages，访问
     `https://qishihei.github.io/nuwa-h5/promo/director-salon/landing/?director=charlie-chaplin`
   - 或 Netlify / Cloudflare Pages 拖 `landing/` 目录。记下落地页地址 `<LANDING>`。
2. **把二维码指向落地页**（替换原来直连 Render 的二维码）
   - 编辑本目录下 `generate_landing_qrs.py` 顶部 `LANDING` 常量为你的落地页地址，
     运行 `python3 generate_landing_qrs.py` → 生成 `landing_qrs/<id>.png`；
   - 用它替换卡片/海报里的旧二维码，或直接把新图发出去。
3. **投放期间保活**
   ```bash
   cd promo/director-salon
   ./keep-warm.sh start     # 后台保活
   ./keep-warm.sh status    # 看状态
   ./keep-warm.sh stop      # 投放结束务必停
   ```

## ⚠️ 额度红线（务必看）

Render 免费额度是**账号级 750 实例小时/月**，账号下所有 Web 服务**共享**。
单个服务 24h 常驻 ≈ 730 小时/月。你有 nuwa-h5 / director-salon / thought-salon 多个服务，
**同时长期保活会超额度、当月被停**。因此保活脚本只在投放期开、结束即停。

**更省事的终极解**：把 `director-salon` 升级到 Render Starter（约 \$7/月）→ 常驻不休眠、
无冷启动，以上两样都不需要。引流场景建议直接升级。

## 说明

- 健康接口 `/api/persons` 在线时返回 JSON（已开 CORS `*`），可被落地页跨域轮询；
  冷启动期该路径返回的是 Render 启动页 HTML，落地页据此判断「尚未真醒」。
- 落地页带 5 秒兜底「仍要进入 →」按钮：即使浏览器拦截了轮询，用户也能手动进。
- `landing/index.html` 支持 `?app=` 覆盖目标服务地址，便于测试其它实例。
