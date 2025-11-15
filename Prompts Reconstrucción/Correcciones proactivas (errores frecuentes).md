CSRF con cookies: no confíes solo en JWT HttpOnly; exige token en header.

CORS: si usas cookies, credentials: include + Access-Control-Allow-Credentials: true y origen explícito.

SQLite en prod: no; úsalo solo para dev/testing.

Validaciones: centraliza con Pydantic schemas; no valides en la vista.

Servicios: no pongas reglas de negocio en routes; ponlas en services.

Tests: crea fixtures de DB en memoria y tests por caso de uso.

Commits: pequeños, con diffs claros; PRs por módulo.