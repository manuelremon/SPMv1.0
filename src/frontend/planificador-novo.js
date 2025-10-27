console.log('[planificador.js] Script cargado');

// Estado de la aplicación
const state = {
  currentPage: 1,
  itemsPerPage: 10,
  solicitudes: [],
  currentSolicitud: null,
  user: null,
  isPlanner: false
};

// Función para mostrar mensajes
function showMessage(msg, isSuccess = false) {
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
  console.log('[planificador.js] Esperando AuthAPI...');
  for (let i = 0; i < maxAttempts; i++) {
    if (window.AuthAPI && typeof window.AuthAPI.me === 'function') {
      console.log('[planificador.js] ✓ AuthAPI encontrado en intento', i);
      return;
    }
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error('AuthAPI no se cargó correctamente después de ' + (maxAttempts * 100) + 'ms');
}

// Verificar permisos de acceso
async function checkAccess() {
  try {
    await waitForAuthAPI();
    const user = await window.AuthAPI.me();
    state.user = user;
    
    console.log('[planificador.js] Usuario:', user.username, 'Rol:', user.rol);
    
    // Verificar si es Planificador o Administrador
    const rolesPermitidos = ['Planificador', 'Administrador', 'admin', 'planificador'];
    const tieneAcceso = rolesPermitidos.some(rol => 
      (user.rol || '').toLowerCase().includes(rol.toLowerCase())
    );
    
    if (!tieneAcceso) {
      console.error('[planificador.js] Acceso denegado: rol insuficiente', user.rol);
      showMessage('No tienes permiso para acceder a esta sección', false);
      setTimeout(() => {
        window.location.href = '/home.html';
      }, 2000);
      return false;
    }
    
    state.isPlanner = true;
    console.log('[planificador.js] ✓ Acceso permitido');
    return true;
  } catch (err) {
    console.error('[planificador.js] Error verificando acceso:', err);
    showMessage('Error al verificar permisos', false);
    return false;
  }
}

// Cargar solicitudes
async function loadSolicitudes() {
  try {
    console.log('[planificador.js] Cargando solicitudes...');
    
    const response = await fetch('/api/solicitudes?page=' + state.currentPage + '&per_page=' + state.itemsPerPage, {
      credentials: 'include',
      headers: { 'Accept': 'application/json' }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    state.solicitudes = data.solicitudes || data.data || [];
    
    console.log('[planificador.js] ✓ Solicitudes cargadas:', state.solicitudes.length);
    renderSolicitudes();
    updateStats();
  } catch (err) {
    console.error('[planificador.js] Error cargando solicitudes:', err);
    showMessage('Error al cargar solicitudes', false);
  }
}

// Renderizar tabla de solicitudes
function renderSolicitudes() {
  const tbody = document.querySelector('#solicitudesTable tbody');
  if (!tbody) return;
  
  if (state.solicitudes.length === 0) {
    tbody.innerHTML = `
      <tr class="empty-row">
        <td colspan="8" style="text-align: center; padding: 32px; color: var(--text-secondary);">
          No hay solicitudes para procesar
        </td>
      </tr>
    `;
    return;
  }
  
  tbody.innerHTML = state.solicitudes.map(sol => `
    <tr data-id="${sol.id}">
      <td>${sol.id}</td>
      <td>${sol.centro || '—'}</td>
      <td>${sol.sector || '—'}</td>
      <td><span class="badge badge--${(sol.criticidad || 'normal').toLowerCase()}">${sol.criticidad || 'Normal'}</span></td>
      <td>${sol.items_count || 0}</td>
      <td style="text-align: right;">$${(sol.total || 0).toLocaleString('es-AR', {minimumFractionDigits: 2})}</td>
      <td><span class="state state--${(sol.estado || 'pending').toLowerCase()}">${sol.estado || 'Pendiente'}</span></td>
      <td>
        <button type="button" class="btn-mini pri" data-action="view" data-id="${sol.id}">Ver</button>
      </td>
    </tr>
  `).join('');
  
  // Agregar event listeners
  tbody.querySelectorAll('[data-action="view"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = e.target.dataset.id;
      showDetail(id);
    });
  });
}

// Mostrar detalles de solicitud
async function showDetail(solicitudId) {
  try {
    console.log('[planificador.js] Mostrando detalles de solicitud:', solicitudId);
    
    const response = await fetch(`/api/solicitudes/${solicitudId}`, {
      credentials: 'include',
      headers: { 'Accept': 'application/json' }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    state.currentSolicitud = data;
    
    // Llenar panel de detalles
    document.getElementById('detailSolicitudId').textContent = `#${data.id}`;
    document.getElementById('detailCentro').textContent = data.centro || '—';
    document.getElementById('detailSector').textContent = data.sector || '—';
    document.getElementById('detailCriticidad').textContent = data.criticidad || '—';
    document.getElementById('detailEstado').textContent = data.estado || '—';
    
    // Llenar tabla de materiales
    const materialesBody = document.getElementById('detailMateriales');
    if (data.materiales && data.materiales.length > 0) {
      materialesBody.innerHTML = data.materiales.map(mat => `
        <tr>
          <td>${mat.nombre || mat.description || '—'}</td>
          <td>${mat.cantidad || 0}</td>
          <td>${mat.unidad || 'UN'}</td>
          <td>$${(mat.precio_unitario || 0).toFixed(2)}</td>
          <td>$${((mat.cantidad || 0) * (mat.precio_unitario || 0)).toFixed(2)}</td>
          <td>
            <button type="button" class="btn-mini ghost" data-action="substitute">Sustituir</button>
          </td>
        </tr>
      `).join('');
    } else {
      materialesBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 16px;">Sin materiales</td></tr>';
    }
    
    // Mostrar análisis de optimización
    showOptimizationAnalysis(data);
    
    // Mostrar panel
    document.getElementById('detailPanel').style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    console.error('[planificador.js] Error cargando detalles:', err);
    showMessage('Error al cargar detalles de solicitud', false);
  }
}

// Mostrar análisis de optimización
function showOptimizationAnalysis(solicitud) {
  const resultsDiv = document.getElementById('optimizationResults');
  
  // Análisis simulado (aquí se integraría con el motor de planificación)
  const analysis = {
    consolidationOpportunity: '3 proveedores pueden abastecer el 85% del pedido',
    costOptimization: 'Potencial de ahorro: 12% ($' + ((solicitud.total || 0) * 0.12).toFixed(2) + ')',
    leadTimeRisk: 'Criticidad Alta - Plazo: 5 días',
    alternativeItems: '2 ítems equivalentes disponibles con mejor precio'
  };
  
  resultsDiv.innerHTML = `
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
      <div style="padding: 12px; background: var(--bg-primary); border-left: 3px solid #3b82f6; border-radius: 4px;">
        <strong>🔗 Consolidación</strong>
        <p style="margin: 4px 0 0 0; font-size: 12px;">${analysis.consolidationOpportunity}</p>
      </div>
      <div style="padding: 12px; background: var(--bg-primary); border-left: 3px solid #10b981; border-radius: 4px;">
        <strong>💰 Ahorro</strong>
        <p style="margin: 4px 0 0 0; font-size: 12px;">${analysis.costOptimization}</p>
      </div>
      <div style="padding: 12px; background: var(--bg-primary); border-left: 3px solid #f59e0b; border-radius: 4px;">
        <strong>⏱️ Riesgo</strong>
        <p style="margin: 4px 0 0 0; font-size: 12px;">${analysis.leadTimeRisk}</p>
      </div>
      <div style="padding: 12px; background: var(--bg-primary); border-left: 3px solid #8b5cf6; border-radius: 4px;">
        <strong>🔄 Equivalentes</strong>
        <p style="margin: 4px 0 0 0; font-size: 12px;">${analysis.alternativeItems}</p>
      </div>
    </div>
  `;
}

// Actualizar estadísticas
function updateStats() {
  // Cargar estadísticas desde API
  fetch('/api/solicitudes/stats', {
    credentials: 'include',
    headers: { 'Accept': 'application/json' }
  })
  .then(r => r.json())
  .then(data => {
    document.getElementById('statPending').textContent = data.pending || 0;
    document.getElementById('statInProcess').textContent = data.in_process || 0;
    document.getElementById('statOptimized').textContent = data.optimized || 0;
    document.getElementById('statCompleted').textContent = data.completed || 0;
  })
  .catch(err => console.error('Error cargando stats:', err));
}

// Inicializar página
async function initPlanificadorPage() {
  console.log('[planificador.js] Inicializando página...');
  
  try {
    // Verificar acceso
    const hasAccess = await checkAccess();
    if (!hasAccess) return;
    
    // Cargar solicitudes
    await loadSolicitudes();
    
    // Configurar event listeners
    document.getElementById('btnRefresh').addEventListener('click', () => {
      state.currentPage = 1;
      loadSolicitudes();
    });
    
    document.getElementById('btnCloseDetail').addEventListener('click', () => {
      document.getElementById('detailPanel').style.display = 'none';
      state.currentSolicitud = null;
    });
    
    document.getElementById('btnPrevPage').addEventListener('click', () => {
      if (state.currentPage > 1) {
        state.currentPage--;
        loadSolicitudes();
      }
    });
    
    document.getElementById('btnNextPage').addEventListener('click', () => {
      state.currentPage++;
      loadSolicitudes();
    });
    
    document.getElementById('btnApplyOptimization').addEventListener('click', async () => {
      if (!state.currentSolicitud) return;
      
      try {
        showMessage('Aplicando optimización...', true);
        // Aquí se integraría con el motor de planificación
        await new Promise(r => setTimeout(r, 1000));
        showMessage('Optimización aplicada correctamente', true);
        document.getElementById('detailPanel').style.display = 'none';
        loadSolicitudes();
      } catch (err) {
        showMessage('Error al aplicar optimización', false);
      }
    });
    
    console.log('[planificador.js] ✓ Página inicializada correctamente');
  } catch (err) {
    console.error('[planificador.js] Error inicializando página:', err);
    showMessage('Error cargando la página', false);
  }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('[planificador.js] DOMContentLoaded disparado');
    initPlanificadorPage();
  });
} else {
  console.log('[planificador.js] DOM ya cargado, inicializando...');
  initPlanificadorPage();
}
