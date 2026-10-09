# 思想会客厅 · H5 版

把「天赋探索/思想会客厅」做成可直接在微信/浏览器打开的网页，免审核、无人数上限，变现路径最短。

## 本地运行
```bash
cd h5
node server.js          # 默认 http://localhost:3000
```
未配置 LLM 时自动进入「演示模式」（返回示例回答），方便先看整体流程。

## 接真实 LLM
```bash
OPENAI_ENDPOINT=https://你的端点/v1/chat/completions \
OPENAI_API_KEY=sk-xxx \
OPENAI_MODEL=deepseek-chat \
node server.js
```
（与云开发版用的同一套 OpenAI 兼容接口，环境变量名一致。）

## 部署（任选其一，拿到 HTTPS 域名后微信内可打开）
- **Render / Railway**：连 Git 仓库，Start 命令 `node h5/server.js`，设好上面 3 个环境变量。免费额度够首发。
- **任意云服务器**：`node h5/server.js` 或用 pm2 守护，前置 Nginx 反代 + HTTPS。
- 国内访问慢可换阿里云/腾讯云轻量 + 域名（需备案）。

## 与原小程序的关系
- 复用同一套 `skills/<人物>/SKILL.md` 认知框架与 LLM 逻辑。
- 当前额度/解锁为**前端原型**（localStorage），便于演示；正式变现时把 `/api/ask` 的扣减改到服务端（数据库）并接入支付回调即可。
- 收款码沿用 `public/wechat_pay_qr.png`，替换文件即换码。
