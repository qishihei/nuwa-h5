// 后台解锁页逻辑
const $ = (s) => document.querySelector(s);

function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.hidden = false;
  clearTimeout(t._t); t._t = setTimeout(() => t.hidden = true, 1800);
}

async function loadPkgs() {
  const r = await fetch('/api/me?uid=__init__');
  const d = await r.json();
  const sel = $('#pkg');
  sel.innerHTML = '';
  (d.pkgs || []).forEach(pk => {
    const o = document.createElement('option');
    o.value = pk.id; o.textContent = pk.permanent ? `${pk.name}（¥${pk.price} / 永久）` : `${pk.name}（¥${pk.price} / ${pk.quota}次）`;
    sel.appendChild(o);
  });
}

$('#queryBtn').onclick = async () => {
  const uid = $('#uid').value.trim();
  if (!uid) return toast('请输入用户 uid');
  const r = await fetch('/api/me?uid=' + encodeURIComponent(uid));
  const d = await r.json();
  $('#qResult').textContent = d.error ? ('错误：' + d.error) : (d.permanent ? '该用户已全解锁（永久，无限次）' : `当前剩余次数：${d.remaining}（免费已用 ${d.free_used}，已购 ${d.bonus}）`);
};

$('#unlockBtn').onclick = async () => {
  const token = $('#token').value.trim();
  const uid = $('#uid').value.trim();
  const pkg = $('#pkg').value;
  if (!token) return toast('请输入管理员口令');
  if (!uid) return toast('请输入用户 uid');
  const r = await fetch('/api/admin/unlock', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ admin_token: token, uid, pkg }),
  });
  const d = await r.json();
  if (d.error) { $('#uResult').textContent = '失败：' + d.error; return; }
  $('#uResult').textContent = d.permanent ? '已全解锁（永久，无限次）。' : `已解锁，增加 ${d.added} 次，当前剩余 ${d.remaining} 次。`;
  toast('解锁成功');
};

loadPkgs();
