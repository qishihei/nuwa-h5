# 导演大师会客厅 · Render 部署指南

代码已就绪（零依赖 Node 服务，无需 `npm install`）。照下面在 Render 新建一个 Web Service 即可。

## 在 Render 新建服务

1. 登录 https://dashboard.render.com → **New +** → **Web Service**。
2. 连接 GitHub 仓库 `qishihei/nuwa-h5`（就是你之前 thinker 版同一个仓库）。
3. Service Name 建议填 `director-salon`——Render 网址就是 `https://<name>.onrender.com`，这样网址正好和 `share/` 里已生成海报的二维码一致，无需重生成。若名称被占用就随便起，之后重生成二维码即可。
4. Instance Type 选 **$0/month Free**（免费，15 分钟无访问休眠）；想不休眠再选 $7 Starter。
5. **关键**：Root Directory 填
   ```
   directors
   ```
   （GitHub 仓库根目录就是本地 `h5/`，仓库内的路径是 `directors`，**不要**带 `nuwa-skill/h5/` 前缀，否则找不到目录、构建失败。）
6. 运行环境：**Node**（选 18 或以上）。
7. Build Command：留空即可（或填 `npm install`，无害）。
8. Start Command：
   ```
   node server.js
   ```
9. 点 **Create Web Service**。

## 配置环境变量（重要）

服务建好后，进入该服务的 **Environment** 页，添加以下变量（不填则进入「演示模式」，只返回示例回答）：

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENAI_ENDPOINT` | 大模型兼容接口地址 | `https://api.deepseek.com/v1/chat/completions` |
| `OPENAI_API_KEY` | 接口密钥 | `sk-xxxx` |
| `OPENAI_MODEL` | 模型名 | `deepseek-chat` |
| `ADMIN_TOKEN` | 后台口令（默认 `nuwa-admin`，建议改） | `nuwa-admin` |
| `FREE_QUOTA` | 免费体验次数（默认 3） | `3` |

> 这些变量和 thinker 版一致。把 thinker 版 Render 后台里那几个值原样搬过来即可。

## 验证

部署完成后（免费版首次冷启动可能转圈 30~60 秒）：

- 中文版：`https://<你的服务名>.onrender.com/`
- 英文版：`https://<你的服务名>.onrender.com/en.html`
- 后台：`https://<你的服务名>.onrender.com/admin.html`（口令 = `ADMIN_TOKEN`）

进页面 → 选一位导演 → 免费问 3 次 → 应得到真实回答（非演示文本）。

## 部署后

把最终地址（`https://xxx.onrender.com`）发给开发同学，让他用
```
cd nuwa-skill/h5/directors/share && python3 make_posters.py https://xxx.onrender.com
```
重生成海报二维码（中文/英文各一份 HTML + PNG，二维码内嵌，直接可发）。
