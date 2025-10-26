export async function ensureAuth({ redirectTo = '/index.html' } = {}) {
  try { await window.AuthAPI.me(); }
  catch { location.href = redirectTo; }
}
