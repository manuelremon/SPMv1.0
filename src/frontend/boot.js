function leerCookie(name) {
  return document.cookie.split('; ').find(r => r.startsWith(name + '='))?.split('=')[1] || '';
}

async function login(username, password) {
  try {
    const data = await window.API.login({ username, password });
    window.location.href = '/home.html';
  } catch (e) {
    const errorEl = document.querySelector('#login-error');
    if (errorEl) {
      errorEl.textContent = e.message || 'Error de autenticación';
      errorEl.hidden = false;
    }
    alert(e.message || 'Error de autenticación');
  }
}

// Check if user is already authenticated on page load
async function checkAuthAndRedirect() {
  // Only run on login page (index.html)
  const isLoginPage = window.location.pathname === '/' ||
                      window.location.pathname === '/index.html' ||
                      window.location.pathname.endsWith('/');

  if (!isLoginPage) return;

  try {
    // Check if user is authenticated
    const user = await window.API.me();
    if (user && user.id_spm) {
      // User is authenticated, redirect to home
      window.location.href = '/home.html';
    }
  } catch (e) {
    // Not authenticated, stay on login page
    console.log('Not authenticated, showing login form');
  }
}

// Initialize login form
document.addEventListener('DOMContentLoaded', () => {
  // Check authentication first
  checkAuthAndRedirect();

  // Setup login form handler
  const form = document.querySelector('#login-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const username = document.querySelector('#username').value;
      const password = document.querySelector('#password').value;
      login(username, password);
    });
  }
});
