// 思想会客厅 H5 前端逻辑（服务端额度版）
const API = window.API_BASE || '';
const FREE_QUOTA = 3;
const EN = window.NUWA_EN === true;
// 英文版：给 LLM 追加的指令（复用中文大师框架，但回答变英文）
const EN_INSTR = '\n\n[Respond in English, applying the thinker\'s cognitive framework. Keep the same depth and structure.]';
// 英文版：大师英文名映射（按 skills.json 的 name 键）
const EN_NAMES = {
  'charlie-munger': 'Charlie Munger', 'elon-musk': 'Elon Musk', 'richard-feynman': 'Richard Feynman',
  'zhang-yiming': 'Zhang Yiming', 'naval-ravikant': 'Naval Ravikant', 'steve-jobs': 'Steve Jobs',
  'kazuo-inamori': 'Kazuo Inamori', 'wang-yangming': 'Wang Yangming', 'socrates': 'Socrates',
  'warren-buffett': 'Warren Buffett', 'ray-dalio': 'Ray Dalio', 'confucius': 'Confucius',
  'friedrich-nietzsche': 'Friedrich Nietzsche', 'laozi': 'Laozi', 'marie-curie': 'Marie Curie',
  'daniel-kahneman': 'Daniel Kahneman', 'sun-tzu': 'Sun Tzu', 'jensen-huang': 'Jensen Huang',
  'coco-chanel': 'Coco Chanel', 'nassim-taleb': 'Nassim Taleb', 'sima-qian': 'Sima Qian',
  'sam-altman': 'Sam Altman', 'liqingzhao': 'Li Qingzhao', 'friedrich-hayek': 'Friedrich Hayek',
  'john-maynard-keynes': 'John Maynard Keynes',
};
const PKGS = [
  { id: 'all', name: '全解锁', en: 'All Access', price: 19.9, quota: 0, permanent: true },
  { id: 'lite', name: '轻会员', en: 'Lite', price: 9.9, quota: 3 },
  { id: 'deep', name: '深度对照', en: 'Deep Contrast', price: 29.9, quota: 10 },
  { id: 'master', name: '大师包', en: 'Master Pack', price: 99.0, quota: 40 },
];

const state = {
  persons: [],
  selected: new Set(),
  pkg: PKGS[0],
  pkgs: PKGS,
};

const $ = (s) => document.querySelector(s);
const personsEl = $('#persons');
const resultsEl = $('#results');
const quotaBar = $('#quotaBar');

// 页面错误可视化（便于排查）
window.onerror = (msg, src, line, col) => {
  const t = document.getElementById('toast');
  if (t) { t.hidden = false; t.textContent = '出错了：' + msg; }
  console.error('onerror', msg, src, line, col);
};

// 稳定的匿名用户标识（仅存本地，用于服务端关联额度）。
// localStorage 在隐私模式下可能抛错，做降级，保证不中断流程。
let _memUid = null;
function uid() {
  try {
    let id = localStorage.getItem('nuwa_uid');
    if (!id) { id = Math.random().toString(36).slice(2) + Date.now().toString(36); localStorage.setItem('nuwa_uid', id); }
    return id;
  } catch (e) {
    if (!_memUid) _memUid = Math.random().toString(36).slice(2) + Date.now().toString(36);
    return _memUid;
  }
}

async function refreshQuota() {
  const r = await fetch(API + '/api/me?uid=' + uid());
  const d = await r.json();
  state.pkgs = d.pkgs || state.pkgs;
  if (d.permanent) quotaBar.textContent = (EN ? 'All unlocked ✓' : '已全解锁 ✓');
  else quotaBar.textContent = (EN ? 'Free uses left: ' : '剩余次数：') + (d.remaining === undefined ? '…' : d.remaining);
  return d;
}

async function loadPersons() {
  const r = await fetch(API + '/api/persons');
  const d = await r.json();
  state.persons = d.persons || [];
  personsEl.innerHTML = '';
  const AVATAR_COLORS = ['#c0563b','#b07b2c','#5b8a72','#3f6fa3','#8a5a9e','#a6444f','#4a8c8c','#9c6b3f','#6b7bbf','#b5892f','#7a8450','#bd6a8a'];
  state.persons.forEach((p, i) => {
    const el = document.createElement('div');
    el.className = 'person';
    const nm = EN ? enNameOf(p.display_name) : p.display_name;
    const initial = (EN ? nm : nm.replace(/[·\s].*$/, '')).trim().charAt(0) || '?';
    el.innerHTML = '<span class="ava" style="background:' + AVATAR_COLORS[i % AVATAR_COLORS.length] + '">' + initial + '</span><span class="pn">' + nm + '</span>';
    el.onclick = () => {
      if (state.selected.has(p.name)) { state.selected.delete(p.name); el.classList.remove('on'); }
      else { if (state.selected.size >= 5) { toast(EN ? 'Max 5 at once' : '最多同时选 5 位'); return; } state.selected.add(p.name); el.classList.add('on'); }
    };
    personsEl.appendChild(el);
  });
  await refreshQuota();
}

function showPay() {
  $('#myUid').textContent = uid();
  const pkgEl = $('#pkg');
  pkgEl.innerHTML = '';
  state.pkgs.forEach(pk => {
    const o = document.createElement('div');
    o.className = 'opt' + (pk.id === state.pkg.id ? ' on' : '');
    const sub = pk.permanent ? (EN ? 'Unlimited' : '全解锁 · 任用') : (pk.quota + (EN ? ' uses' : '次'));
    o.innerHTML = (EN ? pk.en : pk.name) + '<small>¥' + pk.price + ' / ' + sub + '</small>';
    o.onclick = () => { state.pkg = pk; [...pkgEl.children].forEach(c => c.classList.remove('on')); o.classList.add('on'); };
    pkgEl.appendChild(o);
  });
  $('#payMask').hidden = false;
}

function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.hidden = false;
  clearTimeout(t._t); t._t = setTimeout(() => t.hidden = true, 1800);
}

async function ask() {
  const qRaw = $('#question').value.trim();
  if (state.selected.size === 0) { toast(EN ? 'Select at least one thinker' : '请先选择至少一位大师'); return; }
  if (!qRaw) { toast(EN ? 'Enter your question' : '请输入你的问题'); return; }
  const profile = getProfileText();
  if (!profile) {
    toast(EN ? 'Add your background first for a sharper answer (or just ask).' : '先完善下你的背景，大师回答会更准（也可以直接问）');
    const pb = document.getElementById('profileBlock'); if (pb) pb.scrollIntoView({ behavior: 'smooth' });
  }
  const q = EN ? (qRaw + EN_INSTR) : qRaw;

  const btn = $('#askBtn');
  btn.disabled = true; btn.textContent = EN ? 'Thinking…' : '思考中…';
  resultsEl.innerHTML = '<div class="loading">' + (EN ? 'The thinkers are reflecting…' : '正在请大师们思考…') + '</div>';

  try {
    let d;
    if (state.selected.size === 1) {
      const r = await fetch(API + '/api/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ uid: uid(), person: [...state.selected][0], question: q, profile }) });
      d = await r.json();
      if (d.error === 'QUOTA_EXCEEDED') { showPay(); return; }
      if (d.error) throw new Error(d.error);
      resultsEl.innerHTML = card(EN ? enNameOf(d.display_name) : d.display_name, d.answer);
    } else {
      const r = await fetch(API + '/api/compare', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ uid: uid(), persons: [...state.selected], question: q, profile }) });
      d = await r.json();
      if (d.error === 'QUOTA_EXCEEDED') { showPay(); return; }
      if (d.error) throw new Error(d.error);
      let html = '';
      d.answers.forEach(a => html += card(EN ? enNameOf(a.display_name) : a.display_name, a.answer));
      if (d.analysis) html += card(EN ? 'Synthesis' : '整合对比', d.analysis, true);
      resultsEl.innerHTML = html;
    }
    await refreshQuota();
  } catch (e) {
    resultsEl.innerHTML = '<div class="empty">出错了：' + e.message + '</div>';
  } finally {
    btn.disabled = false; btn.textContent = '提问';
  }
}

function card(name, ans, isAnalysis) {
  return '<div class="card' + (isAnalysis ? ' analysis' : '') + '"><h4>' + name + '</h4><div class="ans">' + escapeHtml(ans) + '</div></div>';
}
function escapeHtml(s) { return String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c])); }
// 英文版：从 "查理·芒格 Charlie Munger" 这类 display_name 中提取末尾英文部分
function enNameOf(disp) {
  if (!disp) return disp;
  const m = disp.match(/[A-Za-z][A-Za-z .'&-]*$/);
  return m ? m[0] : disp;
}

$('#askBtn').onclick = ask;
$('#closePay').onclick = () => $('#payMask').hidden = true;

// ——— 痛点问题池（从 /pains.json 动态加载，方便运营随时改文案；此处为兜底）———
let PAIN_POOL = [
  { label: '负债 30 万怎么翻身', q: '我背了 30 万负债，每月工资一到手就还债，看不到头。我该怎么规划，才能真正翻身？' },
  { label: '月薪 8 千该辞职吗', q: '我月薪 8 千，工作稳定但一眼望到头，心里一直有个想做的事。我该不该辞职去追？' },
  { label: '35 岁被裁怎么办', q: '我 35 岁刚被裁员，投了几十份简历没回音。是继续找工作，还是趁这个机会做点自己的事？' },
  { label: '存款为零还有救吗', q: '工作五六年存款为零，月薪不高花得不少。我想开始攒钱和搞副业，第一步该怎么做？' },
  { label: '该不该离婚', q: '这段婚姻让我很消耗，但孩子和现实让我不敢轻易决定。我到底该不该离？' },
  { label: '要不要回小城市', q: '在大城市漂着累但机会多，回小城市舒服但怕废掉。我该怎么选？' },
];
async function loadPains() {
  try {
    const r = await fetch(EN ? '/pains_en.json' : '/pains.json');
    if (r.ok) { const arr = await r.json(); if (Array.isArray(arr) && arr.length) PAIN_POOL = arr; }
  } catch (e) {}
  renderExamples();
}
// 拉取服务端痛点点击权重（用于自动加权）
let PAIN_WEIGHTS = {};
async function loadPainWeights() {
  try {
    const r = await fetch(API + '/api/pain-weights');
    if (r.ok) { const d = await r.json(); if (d.weights) PAIN_WEIGHTS = d.weights; }
  } catch (e) {}
  renderExamples();
}
// 按累计点击次数加权抽样：点得越多的示例被抽中概率越高
function weightedSample(arr, k) {
  const pool = arr.slice();
  const out = [];
  while (out.length < k && pool.length) {
    const w = pool.map(it => (PAIN_WEIGHTS[it.q] || 0) + 1);
    const total = w.reduce((a, b) => a + b, 0);
    let r = Math.random() * total, idx = 0;
    for (; idx < pool.length - 1; idx++) { r -= w[idx]; if (r <= 0) break; }
    out.push(pool[idx]); pool.splice(idx, 1);
  }
  return out;
}

function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) { const j = (Math.random() * (i + 1)) | 0; [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}

// ——— 痛点点击热度（本地 localStorage 记录，?stats 查看排名）———
function recordPainHit(q) {
  try {
    const s = JSON.parse(localStorage.getItem('nuwa_pain_hits') || '{}');
    s[q] = (s[q] || 0) + 1;
    localStorage.setItem('nuwa_pain_hits', JSON.stringify(s));
  } catch (e) {}
}
// 同时上报到服务端（用于后台聚合真实用户热度）
function sendPainHit(q) {
  try { fetch(API + '/api/pain-hit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ q }) }); } catch (e) {}
}
function showPainStats() {
  try {
    const s = JSON.parse(localStorage.getItem('nuwa_pain_hits') || '{}');
    const rows = Object.entries(s).sort((a, b) => b[1] - a[1]);
    if (!rows.length) { alert('还没有记录到任何点击。\n在首页点几个示例问题后，再访问本页 ?stats 即可看到排名。'); return; }
    const html = rows.map(([q, n], i) => (i + 1) + '. ' + n + ' 次 — ' + q).join('\n');
    alert('痛点示例点击排名（仅本机记录）:\n\n' + html);
  } catch (e) {}
}

function renderExamples() {
  const wrap = $('#exWrap');
  if (!wrap) return;
  wrap.innerHTML = '';
  weightedSample(PAIN_POOL, 6).forEach(item => {
    const s = document.createElement('span');
    s.textContent = item.label;
    s.onclick = () => { recordPainHit(item.q); sendPainHit(item.q); $('#question').value = item.q; $('#question').focus(); };
    wrap.appendChild(s);
  });
}

$('#reshuffle').onclick = renderExamples;
// 每 12 秒自动换一组（仅当用户还没开始打字，避免打断）
setInterval(() => { if (!$('#question').value.trim()) renderExamples(); }, 12000);

loadPersons();
renderExamples();   // 先用兜底池渲染，避免空白
loadPains();        // 拉取 /pains.json 后自动重渲染
loadPainWeights();  // 拉取服务端点击权重后自动重渲染
if (location.search.indexOf('stats') !== -1) showPainStats();

// ——— 用户画像（让大师的回答更针对你）———
const PF_FIELDS = ['pfGender', 'pfAge', 'pfJob', 'pfHobby', 'pfSkill', 'pfMore'];
const PF_KEY = 'nuwa_profile';
function setupProfile() {
  const block = document.getElementById('profileBlock');
  if (!block) return;
  if (EN) {
    const bd = document.getElementById('pfBadge'); if (bd) bd.textContent = 'saved';
    const labels = { pfGender: ['', 'Male', 'Female', 'Prefer not to say'], pfAge: 'Age', pfJob: 'Occupation', pfHobby: 'Interests', pfSkill: 'Strengths (optional)', pfMore: 'Anything else (optional): your situation, goals…' };
    for (const id in labels) {
      const e = document.getElementById(id); if (!e) continue;
      if (id === 'pfGender') e.innerHTML = labels[id].map(o => '<option>' + o + '</option>').join('');
      else e.placeholder = labels[id];
    }
  }
  try {
    const saved = JSON.parse(localStorage.getItem(PF_KEY) || 'null');
    if (saved) {
      PF_FIELDS.forEach(id => { const e = document.getElementById(id); if (e && saved[id] != null) e.value = saved[id]; });
      const badge = document.getElementById('pfBadge'); if (badge) badge.hidden = false;
    }
  } catch (e) {}
  const statusEl = document.getElementById('pfStatus');
  document.getElementById('pfSave').onclick = () => {
    const data = {};
    PF_FIELDS.forEach(id => { const e = document.getElementById(id); if (e) data[id] = e.value.trim(); });
    if (!PF_FIELDS.some(id => data[id])) {
      statusEl.textContent = EN ? 'Nothing entered yet.' : '还没填任何内容哦';
      statusEl.style.color = '#b00020'; return;
    }
    try { localStorage.setItem(PF_KEY, JSON.stringify(data)); } catch (e) {}
    const badge = document.getElementById('pfBadge'); if (badge) badge.hidden = false;
    statusEl.textContent = EN ? '✓ Profile saved' : '✓ 画像已保存';
    statusEl.style.color = '#6b8a5b';
  };
}
function getProfileText() {
  let data;
  try { data = JSON.parse(localStorage.getItem(PF_KEY) || 'null'); } catch (e) {}
  if (!data) return '';
  const labels = EN
    ? { pfGender: 'Gender', pfAge: 'Age', pfJob: 'Occupation', pfHobby: 'Interests', pfSkill: 'Strengths', pfMore: 'Note' }
    : { pfGender: '性别', pfAge: '年龄', pfJob: '职业', pfHobby: '兴趣', pfSkill: '特长', pfMore: '补充' };
  const lines = [];
  PF_FIELDS.forEach(id => { if (data[id]) lines.push((labels[id] || id) + (EN ? ': ' : '：') + data[id]); });
  if (!lines.length) return '';
  return (EN ? '[User Background]\n' : '【用户背景】\n') + lines.join('\n');
}

// 注入作者微信号（来自 config.js，避免硬编码写死在 HTML）
(function () {
  const wx = document.getElementById('authorWx');
  if (wx && window.AUTHOR_WECHAT) wx.textContent = window.AUTHOR_WECHAT;
})();
setupProfile();
