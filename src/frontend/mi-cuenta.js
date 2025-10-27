console.log('[mi-cuenta.js] Script cargado');

// Función para mostrar mensajes
function showMessage(msg, isSuccess = false) {
  console.log('[TOAST]', msg, isSuccess ? 'SUCCESS' : 'ERROR');
  const container = document.getElementById('toasts');
  if (!container) {
    alert(msg);
    return;
  }
  
  const node = document.createElement('div');
  node.className = `toast ${isSuccess ? 'ok' : 'err'}`;
  node.textContent = msg;
  node.style.marginBottom = '8px';
  node.style.padding = '12px 16px';
  node.style.borderRadius = '6px';
  node.style.backgroundColor = isSuccess ? '#10b981' : '#ef4444';
  node.style.color = 'white';
  node.style.fontSize = '14px';
  container.appendChild(node);
  
  setTimeout(() => {
    node.style.opacity = '0';
    node.style.transition = 'opacity 0.3s ease';
    setTimeout(() => node.remove(), 300);
  }, 3000);
}

// Esperar a que AuthAPI esté disponible
async function waitForAuthAPI(maxAttempts = 50) {
  console.log('[mi-cuenta.js] Esperando AuthAPI...');
  for (let i = 0; i < maxAttempts; i++) {
    if (window.AuthAPI && typeof window.AuthAPI.me === 'function') {
      console.log('[mi-cuenta.js] ✓ AuthAPI encontrado en intento', i);
      return;
    }
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error('AuthAPI no se cargó correctamente después de ' + (maxAttempts * 100) + 'ms');
}

async function initAccountPage() {
  console.log('[mi-cuenta.js] Iniciando página de cuenta...');
  try {
    // Esperar AuthAPI
    await waitForAuthAPI();
    console.log('[mi-cuenta.js] ✓ AuthAPI disponible');
    
    // Cargar datos del usuario
    console.log('[mi-cuenta.js] Llamando a AuthAPI.me()...');
    const user = await window.AuthAPI.me();
    console.log('[mi-cuenta.js] ✓ Usuario cargado:', user.username);
    
    // Obtener elementos
    const usernameEl = document.querySelector('#username');
    const displayNameEl = document.querySelector('#display_name');
    const emailEl = document.querySelector('#email');
    
    console.log('[mi-cuenta.js] Elementos del DOM encontrados:', {
      username: !!usernameEl,
      display_name: !!displayNameEl,
      email: !!emailEl
    });
    
    // Llenar formulario
    if (usernameEl) {
      usernameEl.value = user.username || '';
      console.log('[mi-cuenta.js] ✓ Username llenado');
    }
    if (displayNameEl) {
      displayNameEl.value = user.display_name || '';
      console.log('[mi-cuenta.js] ✓ Display name llenado');
    }
    if (emailEl) {
      emailEl.value = user.email || '';
      console.log('[mi-cuenta.js] ✓ Email llenado');
    }

    // Formulario de perfil
    const profileForm = document.querySelector('#profileForm');
    if (profileForm) {
      console.log('[mi-cuenta.js] Configurando formulario de perfil...');
      profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('[mi-cuenta.js] Enviando cambios de perfil...');
        
        const display_name = displayNameEl.value.trim();
        const email = emailEl.value.trim();
        
        if (!display_name || !email) {
          showMessage('Por favor, completa todos los campos', false);
          return;
        }
        
        try {
          await window.AuthAPI.updateMe({ display_name, email });
          showMessage('Perfil actualizado correctamente', true);
          const statusEl = document.querySelector('#profileStatus');
          if (statusEl) {
            statusEl.textContent = 'Última actualización: ' + new Date().toLocaleString('es-ES');
          }
        } catch(err) { 
          console.error('[mi-cuenta.js] Error updating profile:', err);
          showMessage('Error: ' + (err.message || 'No se pudo actualizar el perfil'), false);
        }
      });
    }

    // Formulario de cambio de contraseña
    const passwordForm = document.querySelector('#passwordForm');
    if (passwordForm) {
      console.log('[mi-cuenta.js] Configurando formulario de contraseña...');
      passwordForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('[mi-cuenta.js] Enviando cambio de contraseña...');
        
        const current = document.querySelector('#current_pw').value;
        const newPw = document.querySelector('#new_pw').value;
        const newPw2 = document.querySelector('#new_pw2').value;
        
        if (!current || !newPw || !newPw2) {
          showMessage('Por favor, completa todos los campos', false);
          return;
        }
        
        if (newPw !== newPw2) {
          showMessage('Las contraseñas no coinciden', false);
          return;
        }
        
        if (newPw.length < 6) {
          showMessage('La contraseña debe tener al menos 6 caracteres', false);
          return;
        }
        
        try {
          await window.AuthAPI.changePassword(current, newPw);
          showMessage('Contraseña actualizada correctamente', true);
          const statusEl = document.querySelector('#passwordStatus');
          if (statusEl) {
            statusEl.textContent = 'Contraseña actualizada: ' + new Date().toLocaleString('es-ES');
          }
          e.target.reset();
        } catch(err) { 
          console.error('[mi-cuenta.js] Error changing password:', err);
          showMessage('Error: ' + (err.message || 'No se pudo cambiar la contraseña'), false);
        }
      });
    }
    
    console.log('[mi-cuenta.js] ✓ Página inicializada correctamente');
  } catch (err) {
    console.error('[mi-cuenta.js] Error inicializando página:', err);
    showMessage('Error cargando la página: ' + err.message, false);
  }
}

// Inicializar cuando el DOM esté listo
console.log('[mi-cuenta.js] Estado del DOM:', document.readyState);
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('[mi-cuenta.js] DOMContentLoaded disparado');
    initAccountPage();
  });
} else {
  console.log('[mi-cuenta.js] DOM ya cargado, inicializando...');
  initAccountPage();
}
