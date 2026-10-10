// 思想会客厅 H5 前端逻辑（服务端额度版）
const FREE_QUOTA = 3;
const PKGS = [
  { id: 'lite', name: '轻会员', price: 9.9, quota: 3 },
  { id: 'deep', name: '深度对照', price: 29.9, quota: 10 },
  { id: 'master', name: '大师包', price: 99.0, quota: 40 },
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
  const r = await fetch('/api/me?uid=' + uid());
  const d = await r.json();
  state.pkgs = d.pkgs || state.pkgs;
  quotaBar.textContent = '剩余次数：' + (d.remaining === undefined ? '…' : d.remaining);
  return d;
}

async function loadPersons() {
  const r = await fetch('/api/persons');
  const d = await r.json();
  state.persons = d.persons || [];
  personsEl.innerHTML = '';
  state.persons.forEach(p => {
    const el = document.createElement('div');
    el.className = 'person';
    el.textContent = p.display_name;
    el.onclick = () => {
      if (state.selected.has(p.name)) { state.selected.delete(p.name); el.classList.remove('on'); }
      else { if (state.selected.size >= 5) { toast('最多同时选 5 位'); return; } state.selected.add(p.name); el.classList.add('on'); }
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
    o.innerHTML = pk.name + '<small>¥' + pk.price + ' / ' + pk.quota + '次</small>';
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
  const q = $('#question').value.trim();
  if (state.selected.size === 0) { toast('请先选择至少一位大师'); return; }
  if (!q) { toast('请输入你的问题'); return; }

  const btn = $('#askBtn');
  btn.disabled = true; btn.textContent = '思考中…';
  resultsEl.innerHTML = '<div class="loading">正在请大师们思考…</div>';

  try {
    let d;
    if (state.selected.size === 1) {
      const r = await fetch('/api/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ uid: uid(), person: [...state.selected][0], question: q }) });
      d = await r.json();
      if (d.error === 'QUOTA_EXCEEDED') { showPay(); return; }
      if (d.error) throw new Error(d.error);
      resultsEl.innerHTML = card(d.display_name, d.answer);
    } else {
      const r = await fetch('/api/compare', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ uid: uid(), persons: [...state.selected], question: q }) });
      d = await r.json();
      if (d.error === 'QUOTA_EXCEEDED') { showPay(); return; }
      if (d.error) throw new Error(d.error);
      let html = '';
      d.answers.forEach(a => html += card(a.display_name, a.answer));
      if (d.analysis) html += card('整合对比', d.analysis, true);
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

$('#askBtn').onclick = ask;
$('#closePay').onclick = () => $('#payMask').hidden = true;

// ——— 痛点问题池（常问高频问题，随机抽取展示）———
const PAIN_POOL = [
  { label: '负债 30 万怎么翻身', q: '我背了 30 万负债，每月工资一到手就还债，看不到头。我该怎么规划，才能真正翻身？' },
  { label: '月薪 8 千该辞职吗', q: '我月薪 8 千，工作稳定但一眼望到头，心里一直有个想做的事。我该不该辞职去追？' },
  { label: '35 岁被裁怎么办', q: '我 35 岁刚被裁员，投了几十份简历没回音。是继续找工作，还是趁这个机会做点自己的事？' },
  { label: '存款为零还有救吗', q: '工作五六年存款为零，月薪不高花得不少。我想开始攒钱和搞副业，第一步该怎么做？' },
  { label: '该不该离婚', q: '这段婚姻让我很消耗，但孩子和现实让我不敢轻易决定。我到底该不该离？' },
  { label: '要不要回小城市', q: '在大城市漂着累但机会多，回小城市舒服但怕废掉。我该怎么选？' },
  { label: '首付凑不齐买房吗', q: '我和对象工作几年，首付还差一截。现在到底该不该咬牙买房？' },
  { label: '副业值不值得做', q: '我下班做副业月入一两千，很累但能多攒点。要不要继续投入时间？' },
  { label: '被领导打压忍吗', q: '我在公司被领导针对、穿小鞋，活不好干。该忍、该走、还是该争？' },
  { label: '考研还是工作', q: '我大三，家里让考研，我自己想早点赚钱。我该怎么选？' },
  { label: '异地恋要不要分', q: '我和对象异地两年，感情还在但很消耗。要不要结束这段关系？' },
  { label: '创业亏 20 万回本', q: '我去年创业亏了 20 万，现在进退两难。怎么把坑填回来？' },
  { label: '父母催婚怎么顶', q: '我 28 了，父母天天催婚，我不想将就。怎么跟家里沟通？' },
  { label: '身体垮了拼还是躺', q: '我熬夜加班身体出了毛病，但害怕停下来没收入。该拼还是该躺？' },
  { label: '朋友借钱不还咋办', q: '一个好朋友欠我几万一直拖。要不要撕破脸要回来？' },
  { label: '孩子留学值不值', q: '孩子快上高中，纠结要不要送出去留学，费用高但想给他更好出路。' },
];

function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) { const j = (Math.random() * (i + 1)) | 0; [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}

function renderExamples() {
  const wrap = $('#exWrap');
  if (!wrap) return;
  wrap.innerHTML = '';
  shuffle(PAIN_POOL).slice(0, 6).forEach(item => {
    const s = document.createElement('span');
    s.textContent = item.label;
    s.onclick = () => { $('#question').value = item.q; $('#question').focus(); };
    wrap.appendChild(s);
  });
}

$('#reshuffle').onclick = renderExamples;
// 每 12 秒自动换一组（仅当用户还没开始打字，避免打断）
setInterval(() => { if (!$('#question').value.trim()) renderExamples(); }, 12000);

loadPersons();
