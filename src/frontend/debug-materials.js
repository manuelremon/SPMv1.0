// Debug script para investigar por qué no carga los materiales
console.log('=== DEBUG: Material Loading ===');

// 1. Verificar que el DOM esté listo
console.log('DOM Ready:', document.readyState);

// 2. Verificar que exista el select
const materialSelect = document.getElementById('materialSelect');
console.log('Material Select encontrado:', !!materialSelect);
console.log('Material Select options:', materialSelect?.options.length || 0);

// 3. Verificar que exista loadFormCatalogs
console.log('loadFormCatalogs existe:', typeof window.loadFormCatalogs);

// 4. Intentar cargar catálogos manualmente
console.log('Intentando cargar catálogos...');

window.loadFormCatalogs = async function() {
  try {
    console.log('[loadFormCatalogs] Iniciando...');
    
    // Load user access
    const accessResponse = await fetch('/api/auth/mi-acceso', {
      credentials: 'include',
      headers: { 'Accept': 'application/json' }
    });
    console.log('[loadFormCatalogs] Access response:', accessResponse.status);
    const accessData = await accessResponse.json();
    console.log('[loadFormCatalogs] Access data:', accessData);
    
    const centrosPermitidos = accessData.centros_permitidos || [];
    const almacenesPermitidos = accessData.almacenes_permitidos || [];
    
    // Store access info globally
    window.userAccess = {
      centros: centrosPermitidos,
      almacenes: almacenesPermitidos
    };
    
    const response = await fetch('/api/catalogos', {
      credentials: 'include',
      headers: { 'Accept': 'application/json' }
    });
    console.log('[loadFormCatalogs] Catalogs response:', response.status);
    const apiResponse = await response.json();
    console.log('[loadFormCatalogs] API Response:', apiResponse);
    
    const catalogs = apiResponse.data || apiResponse;
    console.log('[loadFormCatalogs] Catalogs:', catalogs);
    
    // Llenar selectores de centros y almacenes
    const centroSelect = document.getElementById('newReqCentro');
    const almacenSelect = document.getElementById('newReqAlmacen');
    
    console.log('[loadFormCatalogs] Centro select:', !!centroSelect);
    console.log('[loadFormCatalogs] Almacen select:', !!almacenSelect);
    console.log('[loadFormCatalogs] Materiales en catálogo:', catalogs.materiales?.length || 0);
    
    // Cargar materiales
    const materialSelect = document.getElementById('materialSelect');
    console.log('[loadFormCatalogs] Material select:', !!materialSelect);
    
    if (catalogs.materiales && materialSelect) {
      console.log('[loadFormCatalogs] Cargando', catalogs.materiales.length, 'materiales...');
      materialSelect.innerHTML = '<option value="">Seleccione un Material</option>';
      
      catalogs.materiales.forEach((m, idx) => {
        if (idx < 5) {
          console.log(`[loadFormCatalogs] Material ${idx}:`, m);
        }
        const opt = document.createElement('option');
        opt.value = JSON.stringify({ 
          id: m.id, 
          nombre: m.nombre, 
          precio: m.precio || 0,
          sap: m.sap || m.codigo || '',
          descripcion: m.descripcion || ''
        });
        opt.textContent = m.nombre;
        materialSelect.appendChild(opt);
      });
      
      console.log('[loadFormCatalogs] ✅ Materiales cargados:', materialSelect.options.length);
    } else {
      console.error('[loadFormCatalogs] ❌ No hay materiales o no existe el select');
    }
  } catch (e) {
    console.error('[loadFormCatalogs] Error:', e);
  }
};

// 5. Ejecutar y ver resultado
console.log('Ejecutando loadFormCatalogs...');
window.loadFormCatalogs();
