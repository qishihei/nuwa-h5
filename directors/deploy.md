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

## 推荐模型（直接决定专家级专业度上限）

本服务只要求一个**兼容 OpenAI `/v1/chat/completions` 协议的接口**——所以任何暴露该协议的供应商都能用，关键是 `OPENAI_ENDPOINT` + `OPENAI_MODEL` + `OPENAI_API_KEY` 三项要配套。默认 `deepseek-chat` 是通用模型，偶有事实偏差；要对得起圈内挑剔的用户，建议换成以下之一：

| 优先级 | 模型 | `OPENAI_MODEL` 填 | `OPENAI_ENDPOINT` 填 | 说明 |
|------|------|------|------|------|
| ★★★ | DeepSeek R1（推理） | `deepseek-reasoner` | `https://api.deepseek.com/v1/chat/completions` | 默认最省事的一步升级，推理强、便宜；与现 key 同体系 |
| ★★★ | OpenAI GPT-4.1 | `gpt-4.1` | `https://api.openai.com/v1/chat/completions` | 综合知识/史实最稳，适合硬核影史问答 |
| ★★★ | OpenAI o3 | `o3` | `https://api.openai.com/v1/chat/completions` | 最强推理，复杂「手法/年表/影响」类长答首选 |
| ★★ | Claude（经网关） | `anthropic/claude-3.5-sonnet` 或 `anthropic/claude-3-opus` | `https://openrouter.ai/api/v1/chat/completions` | 风格贴合度、长文质感好；需走 OpenRouter 等 OpenAI 兼容网关 |
| ★★ | Gemini（经网关） | `google/gemini-2.0-pro` | `https://openrouter.ai/api/v1/chat/completions` | 多语、长上下文友好 |

**几点提醒：**
- 推理类模型（`deepseek-reasoner` / `o3`）对「为什么这样拍、受到谁影响、某个镜头怎么处理」这类深度问题明显更强，但回答更长、单次更慢、略贵。
- 换模型只改环境变量，**改完在 Environment 页点 Save Changes 会触发一次重新部署**，等它转圈结束即生效。
- `OPENAI_ENDPOINT` 必须与所选供应商一致：DeepSeek 用 `api.deepseek.com`，OpenAI 用 `api.openai.com`，走网关（Claude/Gemini 等）用 `openrouter.ai`。
- 想先在本地验证模型效果，把同样的三个变量 export 到环境变量后 `node server.js` 即可，不影响线上。

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
