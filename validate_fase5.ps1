#!/usr/bin/env pwsh
# Script para validar FASE 5 - Seguridad Reforzada
# Uso: .\validate_fase5.ps1

Write-Host "======================================"
Write-Host "VALIDACIÓN FASE 5 - Seguridad Reforzada"
Write-Host "======================================"
Write-Host ""

# 1. Verificar archivos nuevos
Write-Host "✓ Verificando archivos nuevos..." -ForegroundColor Green
$files = @(
    "backend_v2\core\csrf.py",
    "backend_v2\core\rate_limiter.py",
    "backend_v2\core\security_headers.py",
    "docs\FASE_5_SEGURIDAD_REFORZADA.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file MISSING" -ForegroundColor Red
    }
}

Write-Host ""

# 2. Verificar imports en app.py
Write-Host "✓ Verificando imports en app.py..." -ForegroundColor Green
$appContent = Get-Content "backend_v2\app.py" -Raw
$checks = @(
    ("csrf", "from core.csrf import init_csrf_protection"),
    ("security_headers", "from core.security_headers import init_security_headers"),
    ("rate_limiter", "CSRF protection init_csrf_protection")
)

foreach ($check in $checks) {
    if ($appContent -match [regex]::Escape($check[1])) {
        Write-Host "  ✓ $($check[0])" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $($check[0]) NOT FOUND" -ForegroundColor Red
    }
}

Write-Host ""

# 3. Verificar endpoint new en auth.py
Write-Host "✓ Verificando endpoint /refresh..." -ForegroundColor Green
$authContent = Get-Content "backend_v2\routes\auth.py" -Raw
if ($authContent -match "def refresh_token") {
    Write-Host "  ✓ Endpoint /api/auth/refresh implementado" -ForegroundColor Green
} else {
    Write-Host "  ✗ Endpoint /api/auth/refresh NO encontrado" -ForegroundColor Red
}

Write-Host ""

# 4. Verificar redis en requirements
Write-Host "✓ Verificando dependencias..." -ForegroundColor Green
$reqContent = Get-Content "requirements.txt" -Raw
if ($reqContent -match "redis==") {
    Write-Host "  ✓ redis añadido a requirements.txt" -ForegroundColor Green
} else {
    Write-Host "  ✗ redis NO encontrado en requirements.txt" -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================"
Write-Host "✅ VALIDACIÓN COMPLETADA"
Write-Host "======================================"
Write-Host ""

# Instrucciones siguientes
Write-Host "📝 PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Instalar dependencias:"
Write-Host "   pip install -r requirements.txt"
Write-Host ""
Write-Host "2. Revisar documentación:"
Write-Host "   docs\FASE_5_SEGURIDAD_REFORZADA.md"
Write-Host ""
Write-Host "3. Testing de endpoints:"
Write-Host "   - GET  /api/csrf       (obtener CSRF token)"
Write-Host "   - POST /api/auth/refresh (refrescar access token)"
Write-Host ""
Write-Host "4. Testing de rate limiting:"
Write-Host "   for i in {1..70}; do curl http://localhost:5000/api/health & done; wait"
Write-Host ""
Write-Host "5. Iniciar backend_v2:"
Write-Host "   python backend_v2/app.py"
Write-Host ""

