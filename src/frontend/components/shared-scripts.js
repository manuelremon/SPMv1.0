/* ========== SHARED SCRIPTS FOR ALL PAGES ========== */

// Actualizar clase activa del navbar
function updateActiveNavItem(pageName) {
  // Remover clase active de todos los items
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active');
  });
  
  // Agregar clase active al item actual basado en el nombre de la página
  const currentPage = window.location.pathname.split('/').pop().replace('.html', '');
  document.querySelectorAll(`.nav-item`).forEach(item => {
    const href = item.getAttribute('href');
    if (href && href.includes(currentPage)) {
      item.classList.add('active');
    }
  });
}

// Cargar usuario desde sesión y actualizar sidebar
async function loadUserInfo() {
  try {
    const response = await fetch('/api/user/profile', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    
    if (response.ok) {
      const user = await response.json();
      const userAvatarSmall = document.getElementById('userAvatarSmall');
      const userNameSidebar = document.getElementById('userNameSidebar');
      const userRoleSidebar = document.getElementById('userRoleSidebar');
      
      if (userAvatarSmall) userAvatarSmall.textContent = user.nombre?.charAt(0).toUpperCase() || 'U';
      if (userNameSidebar) userNameSidebar.textContent = user.nombre || 'Usuario';
      if (userRoleSidebar) userRoleSidebar.textContent = user.rol || 'User';
      
      // Mostrar/ocultar sección admin
      const adminSection = document.getElementById('adminSection');
      const plannerSection = document.getElementById('plannerSection');
      if (adminSection) adminSection.classList.toggle('hidden', user.rol !== 'Admin');
      if (plannerSection) plannerSection.classList.toggle('hidden', user.rol !== 'Admin');
    }
  } catch (error) {
    console.error('Error loading user info:', error);
  }
}

// Logout handler
function setupLogout() {
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login.html';
    });
  }
}

// Setup notification badge
function setupNotificationBadge() {
  const notificationBtn = document.querySelector('.notification-btn');
  if (notificationBtn) {
    notificationBtn.addEventListener('click', () => {
      // Implementar drawer de notificaciones
      console.log('Mostrar notificaciones');
    });
  }
}

// Inicializar cuando el DOM está cargado
document.addEventListener('DOMContentLoaded', () => {
  updateActiveNavItem();
  loadUserInfo();
  setupLogout();
  setupNotificationBadge();
});

// Verificar autenticación
function checkAuth() {
  const token = localStorage.getItem('token');
  if (!token) {
    window.location.href = '/login.html';
  }
}

// Ejecutar verificación de autenticación al cargar
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', checkAuth);
} else {
  checkAuth();
}
