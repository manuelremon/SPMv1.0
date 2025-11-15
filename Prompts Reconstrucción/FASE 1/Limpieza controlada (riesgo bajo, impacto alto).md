Objetivo: bajar ruido y riesgos antes de crear v2.

Criterios de aceptación

Secret hardcodeado eliminado.

Rutas legacy marcadas (@legacy_endpoint).

Código desactivado removido o documentado.

Dependencias no usadas removidas.

.env.example presente; .env ignorado por git.

Acciones paso a paso

Crea rama chore/cleanup/baseline.

Añade .env.example y actualiza .gitignore para .env, *.db, logs/.

Busca y elimina/separa código muerto y dependencias sin uso.

Introduce @legacy_endpoint en rutas legacy; log + header.



Tarea: Limpieza inicial segura sin romper v1.
Ámbito: src/backend, Dockerfile, requirements*.txt, package.json.

Acciones:
1) Detecta secretos y bypass en código y Dockerfile (SPM_SECRET_KEY, AUTH_BYPASS). 
   - Reemplaza por lectura desde entorno.
   - Genera .env.example con claves: SPM_SECRET_KEY, FRONTEND_ORIGIN, DB_PATH, LOG_PATH, OLLAMA_ENDPOINT, MAX_CONTENT_LENGTH, JWT_ALG, JWT_TTL.
   - Añade/actualiza .gitignore para ignorar .env, *.db, logs/.

2) Marca rutas legacy con un decorator @legacy_endpoint (warning + header X-Legacy-Endpoint: true):
   - /api/users/me y /api/auth/usuarios/me.
   - Implementa el decorator en middleware/decorators.py.

3) Elimina código desactivado del AI assistant (archivos form_intelligence_*), 
   o muévelo a docs/_archive/ con una nota de por qué.

4) Remueve dependencias Python no usadas (scikit-learn, scipy) si no tienen referencias activas.
   - Actualiza requirements*.txt.

Devuélveme: 
- listado de cambios propuestos (archivo→acción).
- diffs por archivo (patch). 
- contenido de .env.example y .gitignore.
No apliques cambios destructivos sin diff.