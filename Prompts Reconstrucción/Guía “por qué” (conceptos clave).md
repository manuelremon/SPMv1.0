App factory: te permite instanciar la app con diferentes configs (dev/test/prod) y facilita tests.

Capas (routes/services/schemas/models): separan responsabilidades, mejoran mantenibilidad y pruebas.

JWT + CSRF: JWT en cookie HttpOnly protege del XSS, pero no del CSRF; por eso el token sincronizado.

Adapter del planner: interfaz estable que desacopla algoritmos de la API; permite evolucionar planner sin romper rutas.

CI/CD: feedback temprano, evita que el repo se deteriore.

Docker: entorno idéntico en dev y prod; menos “works on my machine”.