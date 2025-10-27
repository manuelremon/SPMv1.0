(function() {
function _readCookie(n){
  return document.cookie.split('; ').find(r=>r.startsWith(n+'='))?.split('=')[1] || '';
}
function _csrfHeaders(){
  const t = _readCookie('spm_csrf_token');
  return t ? {'X-CSRF-Token': t} : {};
}
// Cliente de API minimal. Intenta rutas comunes automáticamente.
const BASE =
  window.__API_BASE__ ||
  `${location.protocol}//${location.hostname}:${location.port}`;

const JSON_OPTS = { headers: { "Content-Type": "application/json" }, credentials: "include" };

async function xfetch(url, opts = {}) {
  const r = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
    body: JSON.stringify(opts.body || {}),
    credentials: 'include',
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    const msg = data?.message || data?.error || `HTTP ${r.status}`;
    const e = new Error(msg);
    e.status = r.status;
    e.data = data;
    throw e;
  }
  return data;
}

async function tryLogin(body) {
  // intenta /api/auth/login y /auth/login
  const paths = [
    `${BASE}/api/auth/login`,
    `${BASE}/auth/login`,
  ];
  let lastErr;
  for (const p of paths) {
    try {
      return await xfetch(p, { body, headers: _csrfHeaders() });
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr;
}

async function me() {
  const paths = [
    `${BASE}/api/auth/me`,
    `${BASE}/auth/me`,
  ];
  let lastErr;
  for (const p of paths) {
    try {
      const r = await fetch(p, { credentials: 'include' });
      if (r.ok) return await r.json();
      if (r.status !== 404) throw new Error(`HTTP ${r.status}`);
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr;
}

async function updateMe(data) {
  const r = await fetch(`${BASE}/api/users/me`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ..._csrfHeaders() },
    body: JSON.stringify(data),
    credentials: 'include',
  });
  if (!r.ok) throw new Error('update_failed');
  return await r.json();
}

async function changePassword(current, newPw) {
  const r = await fetch(`${BASE}/api/auth/me/cambiar-password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ..._csrfHeaders() },
    body: JSON.stringify({ current_password: current, new_password: newPw }),
    credentials: 'include',
  });
  if (!r.ok) throw new Error('change_failed');
  return await r.json();
}

const AuthAPI = {
  login: tryLogin,
  me,
  updateMe,
  changePassword,
  logout: async function() {
    const url = `${BASE}/api/auth/logout`;
    await xfetch(url, { headers: _csrfHeaders() });
  },
  files: {
    list(params = {}){
      const u = new URL(`${BASE}/api/files`);
      Object.keys(params).forEach(k => u.searchParams.set(k, params[k]));
      return fetch(u, { credentials: 'include' }).then(r => r.json());
    },
    query(params){ // {page, per_page, q, sort, order}
      const u = new URLSearchParams(params || {});
      this._qs = u.toString() ? `?${u.toString()}` : '';
      return this;
    },
    async upload(file) {
      const fd = new FormData();
      fd.append('file', file);
    const r = await fetch('/api/files', { method:'POST', body: fd, credentials:'include', headers: _csrfHeaders() });
      if (r.status === 201) return await r.json();
      if (r.ok) return await r.json(); // duplicate_of
      const err = await r.json().catch(()=>({error:'upload_failed'}));
      throw new Error(err.error || 'upload_failed');
    },
    downloadUrl(id){ return `/api/files/${id}`; },
    async remove(id){
    const r = await fetch(`/api/files/${id}`, { method:'DELETE', credentials:'include', headers: _csrfHeaders() });
      if (!r.ok) throw new Error('delete_failed');
      return true;
    }
  }
};

// Exponer para depuración
window.AuthAPI = AuthAPI;
})();
