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

loadPersons();
