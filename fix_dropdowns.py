#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

# Read the file
with open('src/frontend/home.html', 'r', encoding='utf-8') as f:
    content = f.read()

# New implementation for loadFormCatalogs
new_function = '''    window.loadFormCatalogs = async function() {
        try {
            const accessRes = await fetch('/api/auth/mi-acceso', { credentials: 'include' });
            const access = await accessRes.json();
            const centrosPermitidos = access.centros_permitidos || [];
            const almacenesPermitidos = access.almacenes_permitidos || [];

            const catalogRes = await fetch('/api/catalogos');
            const catalogs = await catalogRes.json();

            // Get DOM elements
            const centroSelect = document.getElementById('newReqCentro');
            const almacenSelect = document.getElementById('newReqAlmacen');

            if (!centroSelect || !almacenSelect) {
                console.warn('Could not find Centro or Almacén dropdowns');
                return;
            }

            // Clear existing options (keep the first placeholder)
            while (centroSelect.options.length > 1) centroSelect.remove(1);
            while (almacenSelect.options.length > 1) almacenSelect.remove(1);

            // CENTROS: Separate into permitted and denied
            const centrosPermitidosList = [];
            const centrosNegadosList = [];

            catalogs.centros.forEach(c => {
                const hasAccess = centrosPermitidos.includes(c.id);
                const centro = { id: c.id, nombre: c.nombre, sector: c.sector, hasAccess };
                if (hasAccess) {
                    centrosPermitidosList.push(centro);
                } else {
                    centrosNegadosList.push(centro);
                }
            });

            // Add permitted centros FIRST with green open lock
            centrosPermitidosList.forEach(c => {
                const opt = document.createElement('option');
                opt.value = JSON.stringify(c);
                opt.textContent = `🟢 🔓 ${c.id} - ${c.nombre}`;
                centroSelect.appendChild(opt);
            });

            // Add denied centros AFTER with red closed lock
            centrosNegadosList.forEach(c => {
                const opt = document.createElement('option');
                opt.value = JSON.stringify(c);
                opt.textContent = `🔴 🔒 ${c.id} - ${c.nombre}`;
                centroSelect.appendChild(opt);
            });

            // ALMACENES: Separate into permitted and denied
            const almacenesPermitidosList = [];
            const almacenesNegadosList = [];

            catalogs.almacenes.forEach(a => {
                const hasAccess = almacenesPermitidos.includes(a.id);
                const almacen = { id: a.id, nombre: a.nombre, hasAccess };
                if (hasAccess) {
                    almacenesPermitidosList.push(almacen);
                } else {
                    almacenesNegadosList.push(almacen);
                }
            });

            // Add permitted almacenes FIRST with green open lock
            almacenesPermitidosList.forEach(a => {
                const opt = document.createElement('option');
                opt.value = JSON.stringify(a);
                opt.textContent = `🟢 🔓 ${a.id} - ${a.nombre}`;
                almacenSelect.appendChild(opt);
            });

            // Add denied almacenes AFTER with red closed lock
            almacenesNegadosList.forEach(a => {
                const opt = document.createElement('option');
                opt.value = JSON.stringify(a);
                opt.textContent = `🔴 🔒 ${a.id} - ${a.nombre}`;
                almacenSelect.appendChild(opt);
            });

            // Add change listeners with warnings
            centroSelect.addEventListener('change', (e) => {
                if (e.target.value) {
                    try {
                        const centro = JSON.parse(e.target.value);
                        if (!centro.hasAccess) {
                            showToast(`⚠️ No tienes acceso al Centro "${centro.nombre}"`, 'warning');
                        }
                        autoFillSector();
                    } catch (err) {
                        console.error('Error parsing centro:', err);
                    }
                }
            });

            almacenSelect.addEventListener('change', (e) => {
                if (e.target.value) {
                    try {
                        const almacen = JSON.parse(e.target.value);
                        if (!almacen.hasAccess) {
                            showToast(`⚠️ No tienes acceso al Almacén "${almacen.nombre}"`, 'warning');
                        }
                    } catch (err) {
                        console.error('Error parsing almacen:', err);
                    }
                }
            });

        } catch (err) {
            console.error('Error loading form catalogs:', err);
            showToast('Error cargando catálogos', 'error');
        }
    };'''

# Find and replace the entire loadFormCatalogs function
# Note: The function is assigned to window.loadFormCatalogs
start_idx = content.find('window.loadFormCatalogs = async function()')
if start_idx == -1:
    print("ERROR: Could not find loadFormCatalogs function")
else:
    # Find the closing brace
    brace_count = 0
    found_opening = False
    end_idx = start_idx
    
    for i in range(start_idx, len(content)):
        if content[i] == '{':
            found_opening = True
            brace_count += 1
        elif content[i] == '}' and found_opening:
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
    
    if end_idx > start_idx:
        print(f"Found function from {start_idx} to {end_idx}")
        print(f"Replacing {end_idx - start_idx} characters")
        
        # Replace the function
        new_content = content[:start_idx] + new_function + content[end_idx:]
        
        # Write back
        with open('src/frontend/home.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Successfully replaced loadFormCatalogs function!")
    else:
        print("ERROR: Could not find function closing brace")
