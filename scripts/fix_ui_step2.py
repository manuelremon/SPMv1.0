#!/usr/bin/env python3
"""
Script para rediseñar el Step 2 de la UI de forma limpia y profesional
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
target_file = PROJECT_ROOT / 'src' / 'frontend' / 'home.html'

# Leer el archivo
with target_file.open('r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar la sección de búsqueda y selección
# Esta es la SECCIÓN 1: SEARCH y SECTION 2: SELECT

# Encontrar la línea donde comienza el material input section
old_section = '''              <!-- SECTION 1: SEARCH -->
              <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                <h3 style="margin: 0 0 16px 0; color: #111827; font-size: 1rem; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                  <span style="font-size: 1.2em;">🔍</span> Buscar Material
                </h3>
                  
                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                    <div class="form-field">
                      <label for="materialSearchSAP" style="font-weight: 600; color: #1e40af;">'''

new_section = '''              <!-- SECTION 1: SEARCH -->
              <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                <h3 style="margin: 0 0 16px 0; color: #111827; font-size: 1rem; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                  <span style="font-size: 1.2em;">🔍</span> Buscar Material
                </h3>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                  <div class="form-field">
                    <label for="materialSearchSAP" style="font-weight: 500; color: #374151; font-size: 0.9rem;">Código SAP</label>
                    <input type="text" id="materialSearchSAP" placeholder="Ej: 1000000006" oninput="filterMaterials()" 
                           style="width: 100%; border: 1px solid #d1d5db; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px; box-sizing: border-box; font-family: inherit;">
                  </div>
                  <div class="form-field">
                    <label for="materialSearchDesc" style="font-weight: 500; color: #374151; font-size: 0.9rem;">Descripción</label>
                    <input type="text" id="materialSearchDesc" placeholder="Ej: TORNILLO, CABLE, SENSOR..." oninput="filterMaterials()" 
                           style="width: 100%; border: 1px solid #d1d5db; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px; box-sizing: border-box; font-family: inherit;">
                  </div>
                </div>
              </div>

              <!-- SECTION 2: SELECT & ADD -->
              <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                <h3 style="margin: 0 0 16px 0; color: #111827; font-size: 1rem; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                  <span style="font-size: 1.2em;">➕</span> Seleccionar y Agregar
                </h3>'''

if old_section in content:
    print("✓ Encontrada sección de búsqueda")
    content = content.replace(old_section, new_section)
    print("✓ Reemplazada sección de búsqueda")
else:
    print("✗ No encontrada sección de búsqueda (caracteres especiales?)")
    # Buscar una parte más pequeña
    if "SECTION 1: SEARCH" in content:
        print("  (pero encontré 'SECTION 1: SEARCH' en el archivo)")

# Ahora reemplazar el resto de inputs
old_inputs = '''Código SAP</label>
                      <input type="text" id="materialSearchSAP" placeholder="Ej: 1000000006" oninput="filterMaterials()" 
                             style="border: 2px solid #93c5fd; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px;">
                    </div>
                    <div class="form-field">
                      <label for="materialSearchDesc" style="font-weight: 600; color: #1e40af;">📝 Descripción o Nombre</label>
                      <input type="text" id="materialSearchDesc" placeholder="Ej: TORNILLO, CABLE, SENSOR..." oninput="filterMaterials()" 
                             style="border: 2px solid #93c5fd; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px;">
                    </div>
                  </div>
                </div>

                <!-- MATERIAL SELECTION SECTION -->
                <div style="margin-bottom: 20px;">
                  <h3 style="margin: 0 0 16px 0; color: #1e40af; font-size: 1.1rem; font-weight: 600;">✅ Seleccionar Material</h3>
                  
                  <div class="form-grid-materials" style="display: grid; grid-template-columns: 2fr 1fr 1fr auto auto; gap: 12px; align-items: flex-end;">
                    <div class="form-field">
                      <label for="materialSelect" style="font-weight: 600; color: #1e40af;">Material <span class="required">*</span></label>
                      <input type="search" id="materialSelect" list="materialsList" required 
                             placeholder="Selecciona de los resultados filtrados..." autocomplete="off"
                             style="border: 2px solid #3b82f6; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px; background: white;">
                      <datalist id="materialsList">
                        <!-- Populated by loadFormCatalogs() -->
                      </datalist>
                    </div>

                    <div class="form-field">
                      <label for="materialQuantity" style="font-weight: 600; color: #1e40af;">Cantidad <span class="required">*</span></label>
                      <input type="number" id="materialQuantity" min="1" placeholder="1" required
                             style="border: 2px solid #3b82f6; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px;">
                    </div>

                    <div class="form-field">
                      <label for="materialPrice" style="font-weight: 600; color: #1e40af;">Precio Unit. <span class="required">*</span></label>
                      <input type="number" id="materialPrice" min="0" step="0.01" placeholder="0.00" required
                             style="border: 2px solid #3b82f6; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px;">
                    </div>

                    <button type="button" class="btn btn-secondary" id="btnViewDescription" style="display: none; padding: 10px 14px; font-size: 0.9rem; white-space: nowrap;" onclick="showMaterialDescription()">
                      📖 Info
                    </button>

                    <button type="button" class="btn btn-success btn-add-material" onclick="addMaterialToList()" 
                            style="padding: 10px 16px; font-weight: 600; white-space: nowrap;">
                      ➕ Agregar
                    </button>'''

new_inputs = '''Código SAP</label>
                    <input type="text" id="materialSearchSAP" placeholder="Ej: 1000000006" oninput="filterMaterials()" 
                           style="width: 100%; border: 1px solid #d1d5db; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px; box-sizing: border-box; font-family: inherit;">
                  </div>
                  <div class="form-field">
                    <label for="materialSearchDesc" style="font-weight: 500; color: #374151; font-size: 0.9rem;">Descripción</label>
                    <input type="text" id="materialSearchDesc" placeholder="Ej: TORNILLO, CABLE, SENSOR..." oninput="filterMaterials()" 
                           style="width: 100%; border: 1px solid #d1d5db; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px; box-sizing: border-box; font-family: inherit;">
                  </div>
                </div>
              </div>

              <!-- SECTION 2: SELECT & ADD -->
              <div style="background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin-bottom: 24px;">
                <h3 style="margin: 0 0 16px 0; color: #111827; font-size: 1rem; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                  <span style="font-size: 1.2em;">➕</span> Seleccionar y Agregar
                </h3>
                
                <div style="display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 12px; align-items: flex-end;">
                  <div class="form-field">
                    <label for="materialSelect" style="font-weight: 500; color: #374151; font-size: 0.9rem;">Material <span style="color: #ef4444;">*</span></label>
                    <input type="search" id="materialSelect" list="materialsList" required 
                           placeholder="Selecciona de los resultados..." autocomplete="off"
                           style="width: 100%; border: 1px solid #d1d5db; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px; background: white; box-sizing: border-box; font-family: inherit;">
                    <datalist id="materialsList">
                      <!-- Populated by loadFormCatalogs() -->
                    </datalist>
                  </div>

                  <div class="form-field">
                    <label for="materialQuantity" style="font-weight: 500; color: #374151; font-size: 0.9rem;">Cantidad <span style="color: #ef4444;">*</span></label>
                    <input type="number" id="materialQuantity" min="1" placeholder="1" required
                           style="width: 100%; border: 1px solid #d1d5db; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px; box-sizing: border-box; font-family: inherit;">
                  </div>

                  <div class="form-field">
                    <label for="materialPrice" style="font-weight: 500; color: #374151; font-size: 0.9rem;">Precio <span style="color: #ef4444;">*</span></label>
                    <input type="number" id="materialPrice" min="0" step="0.01" placeholder="0.00" required
                           style="width: 100%; border: 1px solid #d1d5db; padding: 10px 12px; font-size: 0.95rem; border-radius: 6px; box-sizing: border-box; font-family: inherit;">
                  </div>

                  <button type="button" class="btn" id="btnViewDescription" style="display: none; padding: 10px 14px; font-size: 0.9rem; white-space: nowrap; background: #6b7280; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;" onclick="showMaterialDescription()">
                    📖 Ver Desc
                  </button>

                  <button type="button" class="btn" id="btnAddMaterial" style="padding: 10px 16px; font-size: 0.9rem; white-space: nowrap; background: #10b981; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; transition: background 0.2s;" onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10b981'" onclick="addMaterialToList()">
                    ➕ Agregar
                  </button>'''

if old_inputs in content:
    print("✓ Encontrados inputs de búsqueda y selección")
    content = content.replace(old_inputs, new_inputs)
    print("✓ Reemplazados inputs")
else:
    print("✗ No encontrados inputs (caracteres especiales?)")

# Guardar
with target_file.open('w', encoding='utf-8') as f:
    f.write(content)

print("✓ Archivo guardado")
