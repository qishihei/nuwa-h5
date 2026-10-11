// 思想会客厅 · H5 版零依赖 Node 服务
// 启动：node server.js  （可选环境变量 OPENAI_ENDPOINT / OPENAI_API_KEY / OPENAI_MODEL / PORT / FREE_QUOTA）
// 未配置 LLM 时自动进入「演示模式」，返回示例回答，方便先看整体流程。
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

// 极简 .env 加载（零依赖）：若存在 h5/.env 则注入 process.env
(function loadEnv() {
  const f = path.join(__dirname, '.env');
  if (!fs.existsSync(f)) return;
  fs.readFileSync(f, 'utf-8').split('\n').forEach(line => {
    const m = line.match(/^\s*([\w.-]+)\s*=\s*(.*)\s*$/);
    if (m && process.env[m[1]] === undefined) {
      process.env[m[1]] = m[2].replace(/^["']|["']$/g, '');
    }
  });
})();

const PORT = parseInt(process.env.PORT || '3000', 10);
const ROOT = __dirname;
const PUBLIC = path.join(ROOT, 'public');
const SKILLS_DIR = path.join(ROOT, 'skills');
const SKILLS_JSON = path.join(ROOT, 'skills.json');
const QR_PATH = path.join(PUBLIC, 'wechat_pay_qr.png');

const FREE_QUOTA = parseInt(process.env.FREE_QUOTA || '3', 10) || 3;
const ENDPOINT = process.env.OPENAI_ENDPOINT || '';
const API_KEY = process.env.OPENAI_API_KEY || '';
const MODEL = process.env.OPENAI_MODEL || 'deepseek-chat';
const CONFIGURED = !!(ENDPOINT && API_KEY);
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || 'nuwa-admin';
const PKGS = [
  { id: 'all', name: '全解锁', price: 19.9, quota: 0, permanent: true },
  { id: 'lite', name: '轻会员', price: 9.9, quota: 3 },
  { id: 'deep', name: '深度对照', price: 29.9, quota: 10 },
  { id: 'master', name: '大师包', price: 99.0, quota: 40 },
];

// ——— 技能加载 ———
function loadSkillsMeta() {
  try { return JSON.parse(fs.readFileSync(SKILLS_JSON, 'utf-8')); } catch (e) { return { skills: [] }; }
}
function skillText(name) {
  const p = path.join(SKILLS_DIR, name, 'SKILL.md');
  if (!fs.existsSync(p)) return null;
  return fs.readFileSync(p, 'utf-8');
}
const DISPLAY = {};
loadSkillsMeta().skills.forEach(s => { if (s.name) DISPLAY[s.name] = s.display_name || s.name; });

// ——— 服务端额度存储（零依赖，落盘到 data/store.json）———
const STORE_PATH = path.join(ROOT, 'data', 'store.json');
let store = (() => { try { return JSON.parse(fs.readFileSync(STORE_PATH, 'utf-8')); } catch (e) { return { users: {}, pains: {}, questions: [] }; } })();
function saveStore() { try { fs.mkdirSync(path.dirname(STORE_PATH), { recursive: true }); fs.writeFileSync(STORE_PATH, JSON.stringify(store, null, 2)); } catch (e) {} }
function ensureUser(uid) { if (!uid) return null; if (!store.users[uid]) store.users[uid] = { used: 0, bonus: 0, permanent: false }; return store.users[uid]; }
function remaining(uid) { const u = ensureUser(uid); if (!u) return 0; if (u.permanent) return -1; return Math.max(0, FREE_QUOTA - u.used) + (u.bonus || 0); }
function consume(uid) {
  const u = ensureUser(uid); if (!u) return null;
  if (u.permanent) return 'permanent';
  if (u.used < FREE_QUOTA) { u.used++; saveStore(); return 'free'; }
  if (u.bonus > 0) { u.bonus--; saveStore(); return 'bonus'; }
  return null;
}
function refund(uid, type) {
  const u = ensureUser(uid); if (!u || !type) return;
  if (type === 'free') u.used = Math.max(0, u.used - 1);
  else if (type === 'bonus') u.bonus = (u.bonus || 0) + 1;
  saveStore();
}
function addBonus(uid, n) { const u = ensureUser(uid); if (!u) return; u.bonus = (u.bonus || 0) + n; saveStore(); }
function recordPainHit(q) { if (!q) return; store.pains[q] = (store.pains[q] || 0) + 1; saveStore(); }
// 记录用户实际提问（示例点击或自填都算），供后台做内容选题分析
function recordQuestion(uid, q, type, meta) {
  if (!q) return;
  store.questions.push({ q, uid: uid || '', type, meta: meta || '', ts: Date.now() });
  if (store.questions.length > 2000) store.questions = store.questions.slice(-2000);
  saveStore();
}

// ——— LLM（OpenAI 兼容，核心 https，无第三方依赖）———
function callLLM(system, question, maxTokens) {
  return new Promise((resolve, reject) => {
    if (!CONFIGURED) { resolve(null); return; }
    const body = JSON.stringify({
      model: MODEL,
      messages: [{ role: 'system', content: system }, { role: 'user', content: question }],
      temperature: 0.7,
      max_tokens: maxTokens || 1400,
    });
    let u;
    try { u = new URL(ENDPOINT); } catch (e) { reject(e); return; }
    const options = {
      hostname: u.hostname,
      port: u.port || 443,
      path: u.pathname + u.search,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + API_KEY,
        'Content-Length': Buffer.byteLength(body),
      },
    };
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const j = JSON.parse(data);
          const txt = j.choices && j.choices[0] && j.choices[0].message && j.choices[0].message.content;
          if (txt) resolve(txt); else reject(new Error('LLM 返回为空'));
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}
function analyzeCompare(answers, question, profile, maxTokens) {
  const sys = ('你是对比分析师。下面给出了多位思想家对同一问题的框架性回答。'
    + '请用中文提炼，只输出以下结构、不要客套：\n'
    + '## 共识\n各方都认同的核心要点（3 条以内）。\n'
    + '## 分歧\n各方视角的关键差异（2–3 条）。\n'
    + '## 整合建议\n普通人该如何吸收这些视角、形成自己的行动（2–3 条）。');
  const user = (profile ? profile + '\n\n' : '') + '问题：' + question + '\n\n' + Object.entries(answers)
    .map(([p, a]) => '【' + (DISPLAY[p] || p) + '】\n' + a).join('\n\n');
  return callLLM(sys, user, maxTokens || 900);
}

// ——— 工具 ———
function sendJSON(res, code, obj) {
  res.writeHead(code, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(JSON.stringify(obj));
}
function readBody(req) {
  return new Promise((resolve) => {
    let d = '';
    req.on('data', c => d += c);
    req.on('end', () => resolve(d));
  });
}
const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'application/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.ico': 'image/x-icon' };
function serveStatic(res, fp) {
  const ext = path.extname(fp);
  res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream', 'Cache-Control': 'no-cache' });
  fs.createReadStream(fp).pipe(res);
}

// ——— 路由 ———
const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, 'http://localhost');
  const p = u.pathname;
  console.log('[req]', new Date().toLocaleTimeString(), req.method, req.url);
  try {
    if (req.method === 'OPTIONS') {
      res.writeHead(204, {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '86400',
      });
      return res.end();
    }
    if (p === '/api/persons') {
      const meta = loadSkillsMeta();
      const list = meta.skills.map(s => ({ name: s.name, display_name: s.display_name }));
      return sendJSON(res, 200, { persons: list, count: list.length, free_quota: FREE_QUOTA, configured: CONFIGURED });
    }

    if (p === '/api/me' && req.method === 'GET') {
      const uid = u.searchParams.get('uid') || '';
      if (!uid) return sendJSON(res, 400, { error: '缺少 uid' });
      const user = ensureUser(uid);
      return sendJSON(res, 200, { remaining: remaining(uid), permanent: !!user.permanent, free_used: user.used, bonus: user.bonus || 0, free_quota: FREE_QUOTA, pkgs: PKGS });
    }

    if (p === '/api/admin/unlock' && req.method === 'POST') {
      const body = JSON.parse(await readBody(req) || '{}');
      if (body.admin_token !== ADMIN_TOKEN) return sendJSON(res, 403, { error: 'forbidden' });
      const uid = body.uid || '';
      if (!uid) return sendJSON(res, 400, { error: '缺少 uid' });
      const pkg = PKGS.find(x => x.id === body.pkg) || PKGS[0];
      if (pkg.permanent) { const user = ensureUser(uid); user.permanent = true; saveStore(); }
      else addBonus(uid, pkg.quota);
      return sendJSON(res, 200, { remaining: remaining(uid), permanent: !!pkg.permanent, added: pkg.permanent ? '∞' : pkg.quota });
    }

    if (p === '/api/pain-hit' && req.method === 'POST') {
      const body = JSON.parse(await readBody(req) || '{}');
      const q = (body.q || '').trim();
      if (!q) return sendJSON(res, 400, { error: '缺少 q' });
      recordPainHit(q);
      return sendJSON(res, 200, { ok: true });
    }

    if (p === '/api/admin/pain-stats' && req.method === 'GET') {
      const tk = u.searchParams.get('admin_token') || '';
      if (tk !== ADMIN_TOKEN) return sendJSON(res, 403, { error: 'forbidden' });
      const rows = Object.entries(store.pains || {}).map(([q, n]) => ({ q, n })).sort((a, b) => b.n - a.n);
      return sendJSON(res, 200, { rows });
    }

    // 供前端做「热点自动加权」：返回各示例累计点击次数（无需口令）
    if (p === '/api/pain-weights' && req.method === 'GET') {
      return sendJSON(res, 200, { weights: store.pains || {} });
    }

    // 后台查看「用户真实提问」大数据（需口令）：含高频重复排名 + 最近记录
    if (p === '/api/admin/questions' && req.method === 'GET') {
      const tk = u.searchParams.get('admin_token') || '';
      if (tk !== ADMIN_TOKEN) return sendJSON(res, 403, { error: 'forbidden' });
      const all = store.questions || [];
      const counts = {};
      all.forEach(x => { counts[x.q] = (counts[x.q] || 0) + 1; });
      const top = Object.entries(counts).map(([q, n]) => ({ q, n })).sort((a, b) => b.n - a.n).slice(0, 30);
      const recent = all.slice(-50).reverse().map(x => ({ q: x.q, type: x.type, ts: x.ts }));
      return sendJSON(res, 200, { total: all.length, top, recent });
    }

    if (p === '/api/ask' && req.method === 'POST') {
      const body = JSON.parse(await readBody(req) || '{}');
      const uid = body.uid || '';
      const person = body.person;
      const question = (body.question || '').trim();
      const profile = (body.profile || '').trim();
      if (!uid) return sendJSON(res, 400, { error: '缺少用户标识' });
      const text = skillText(person);
      if (!text) return sendJSON(res, 400, { error: '未知人物' });
      if (!question) return sendJSON(res, 400, { error: '请输入问题' });
      const ct = consume(uid);
      if (!ct) return sendJSON(res, 402, { error: 'QUOTA_EXCEEDED', remaining: 0 });
      try {
        recordQuestion(uid, question, 'single', person);
        const fullQ = profile ? profile + '\n\n' + question : question;
        let ans = await callLLM(text, fullQ, 1400);
        if (ans === null) ans = `[演示模式 · 未配置 LLM]\n\n以 ${DISPLAY[person] || person} 的视角，关于「${question}」：\n这是示例回答。配置 OPENAI_ENDPOINT / OPENAI_API_KEY 后将返回真实回答。`;
        return sendJSON(res, 200, { person, display_name: DISPLAY[person] || person, answer: ans, remaining: remaining(uid) });
      } catch (e) {
        refund(uid, ct);
        return sendJSON(res, 500, { error: String(e.message || e) });
      }
    }

    if (p === '/api/compare' && req.method === 'POST') {
      const body = JSON.parse(await readBody(req) || '{}');
      const uid = body.uid || '';
      const persons = (body.persons || []).filter(Boolean).slice(0, 5);
      const question = (body.question || '').trim();
      const profile = (body.profile || '').trim();
      if (!uid) return sendJSON(res, 400, { error: '缺少用户标识' });
      if (!persons.length) return sendJSON(res, 400, { error: '请选择至少一位人物' });
      if (!question) return sendJSON(res, 400, { error: '请输入问题' });
      const ct = consume(uid);
      if (!ct) return sendJSON(res, 402, { error: 'QUOTA_EXCEEDED', remaining: 0 });
      try {
        recordQuestion(uid, question, 'compare', persons.join(','));
        const fullQ = profile ? profile + '\n\n' + question : question;
        const answers = {};
        await Promise.all(persons.map(async (person) => {
          const t = skillText(person);
          if (!t) { answers[person] = ''; return; }
          let a = await callLLM(t, fullQ, 900);
          if (a === null) a = `[演示模式] ${DISPLAY[person] || person} 关于「${question}」的示例回答。`;
          answers[person] = a;
        }));
        let analysis = '';
        if (CONFIGURED && Object.values(answers).some(Boolean)) {
          analysis = await analyzeCompare(answers, question, profile).catch(() => '');
        }
        return sendJSON(res, 200, {
          answers: persons.map(person => ({ person, display_name: DISPLAY[person] || person, answer: answers[person] })),
          analysis, remaining: remaining(uid),
        });
      } catch (e) {
        refund(uid, ct);
        return sendJSON(res, 500, { error: String(e.message || e) });
      }
    }

    if (p === '/pay-qr') {
      if (fs.existsSync(QR_PATH)) { res.writeHead(200, { 'Content-Type': 'image/png' }); fs.createReadStream(QR_PATH).pipe(res); return; }
      res.writeHead(404); res.end('no qr'); return;
    }

    if (p === '/' || p === '/index.html') { serveStatic(res, path.join(PUBLIC, 'index.html')); return; }
    if (p === '/favicon.ico') { res.writeHead(204); res.end(); return; }

    const fp = path.join(PUBLIC, p.replace(/^\//, ''));
    if (fs.existsSync(fp) && fs.statSync(fp).isFile()) { serveStatic(res, fp); return; }

    res.writeHead(404); res.end('not found');
  } catch (e) {
    sendJSON(res, 500, { error: String(e.message || e) });
  }
});

server.listen(PORT, () => {
  console.log('思想会客厅 H5 已启动: http://localhost:' + PORT);
  console.log(CONFIGURED ? 'LLM: 已配置（真实回答）' : 'LLM: 未配置（演示模式）');
});
