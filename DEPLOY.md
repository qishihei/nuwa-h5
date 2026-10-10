# 思想会客厅 H5 · 部署指南

> 零依赖 Node 服务，前后端同域，适合 Render / Railway / 任意云服务器。

## 一、部署到 Render（推荐，免费起步）

> 本仓库已自带 `render.yaml`。最省事的做法：把本仓库连到 Render 并选择「Blueprint」方式，会自动按 `render.yaml` 建好 Web Service（`startCommand`、`NODE_VERSION`、默认环境变量都已配好）。你只需在 Render 控制台补填 3 个 secret 变量：`OPENAI_ENDPOINT`、`OPENAI_API_KEY`、`ADMIN_TOKEN`（**务必设为 `nh2026secret`**，否则后台 `admin.html` 登不进）。其余变量有默认值，不用改。部署成功后 `/api/persons` 健康检查通过即说明人物数据加载正常。

1. 把代码推到 GitHub / GitLab 等 Git 仓库。
2. Render 控制台 → **New → Web Service** → 连接仓库。
3. 关键设置：
   - **Root Directory**：若仓库根不是 `h5`，填 `nuwa-skill/h5`
   - **Runtime**：Node
   - **Build Command**：留空（零依赖，无需 `npm install`）
   - **Start Command**：`node server.js`
   - **Instance Type**：Free（起步够用）
4. 环境变量（Environment）：
   - `OPENAI_ENDPOINT`：如 `https://api.deepseek.com/v1/chat/completions`
   - `OPENAI_API_KEY`：你的 key
   - `OPENAI_MODEL`：如 `deepseek-chat`
   - `ADMIN_TOKEN`：后台口令，例如 `nh2026secret`（与后台登录一致）
   - `FREE_QUOTA`：免费次数，默认 `3`
   - `PORT`：不用设，Render 自动注入
5. Create Web Service，等部署完成，拿到 `https://xxx.onrender.com`。

## 二、上线前必做

- **收款码**：微信收款码截图命名 `wechat_pay_qr.png` 放进 `h5/public/`，重新部署即生效。
- **作者微信号**：`public/config.js` 的 `AUTHOR_WECHAT` 改成你的（当前已为 `fuping394319746`）。
- **海报二维码** `h5/share/link-qr.png`：需指向你的 Render 域名，部署后重新生成该二维码。
- **API 地址**：`public/config.js` 的 `API_BASE` 留空 `''`（前后端同域，最稳）。

## 三、解锁操作（模式二 · 一口价全解锁）

用户付款后：

1. 打开 `https://你的域名/admin.html`
2. 填管理口令（`ADMIN_TOKEN`）
3. 填用户发来的「用户ID」+ 选「全解锁 ¥19.9（永久）」
4. 点确认解锁 → 对方刷新页面即全部可用，只点一次。

套餐档位（`server.js` 的 `PKGS`）：

| 档 id | 名称 | 价 | 次数 |
|---|---|---|---|
| `all` | 全解锁 | ¥19.9 | 永久 |
| `lite` | 轻会员 | ¥9.9 | 3 次 |
| `deep` | 深度对照 | ¥29.9 | 10 次 |
| `master` | 大师包 | ¥99 | 40 次 |

> 用户端弹窗默认选中「全解锁 ¥19.9」。其余档位保留作为可选。

## 四、本地运行 / 调试

```bash
cd nuwa-skill/h5
node server.js          # http://localhost:3000
# 未配置 LLM 时自动进入「演示模式」，整体流程可跑通
```

改完代码后若本地已在跑旧进程，需重启：

```bash
lsof -ti:3000 | xargs kill -9
node server.js
```

## 五、注意事项

- **数据持久化**：`store.json` 存于 `h5/data/`，记录额度与解锁状态。Render 免费版临时磁盘在休眠/重启后可能清空，已解锁用户需重新发 ID 解锁。解决：给 Render 挂 **Persistent Disk**，或把存储换为外部 DB/Redis。
- **冷启动**：Render 免费实例会休眠，首次访问冷启动约数十秒，耐心等待或升级付费实例。
- **合规售卖**：若上闲鱼/拼多多等平台，建议包装成「资料 + 一次性兑换码」并做一码一用鉴权，避免链接被转发白嫖与平台合规风险。
