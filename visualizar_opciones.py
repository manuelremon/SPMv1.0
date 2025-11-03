#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Visualizador de Opciones de Diseño - SPM v1.0
Muestra un resumen visual de las 10 propuestas
"""

opciones = [
    {
        "num": 1,
        "nombre": "MINIMALISTA AZUL PROFESSIONAL",
        "emoji": "💼",
        "color_primary": "#2563eb",
        "paleta": "Azul corporativo + Blanco",
        "modo": "Light Mode",
        "vibe": "Corporativo, serio, profesional",
        "para": "Finanzas, Seguros, B2B",
        "rating": "⭐⭐⭐⭐"
    },
    {
        "num": 2,
        "nombre": "TECH VERDOSO",
        "emoji": "🌱",
        "color_primary": "#059669",
        "paleta": "Verde esmeralda + Negro azulado",
        "modo": "Dark Mode",
        "vibe": "Moderno, sostenible, tech",
        "para": "Startups, Sostenibilidad",
        "rating": "⭐⭐⭐⭐⭐ 🏆 TOP 1"
    },
    {
        "num": 3,
        "nombre": "GRADIENT PREMIUM NARANJA",
        "emoji": "🔥",
        "color_primary": "#f97316",
        "paleta": "Naranja a Rojo + Negro caramelo",
        "modo": "Dark Mode",
        "vibe": "Energético, moderno, dinámico",
        "para": "E-commerce, Entregas, Contenido",
        "rating": "⭐⭐⭐⭐"
    },
    {
        "num": 4,
        "nombre": "MINIMALISTA GRIS CONTEMPORÁNEO",
        "emoji": "⚪",
        "color_primary": "#4b5563",
        "paleta": "Gris neutro + Blanco puro",
        "modo": "Light Mode",
        "vibe": "Minimalista, neutral, enfoque contenido",
        "para": "SaaS, B2B, Máxima legibilidad",
        "rating": "⭐⭐⭐⭐ 🏆 TOP 2"
    },
    {
        "num": 5,
        "nombre": "DARK CYAN TECH",
        "emoji": "🚀",
        "color_primary": "#06b6d4",
        "paleta": "Cyan + Negro profundo",
        "modo": "Dark Mode",
        "vibe": "Futurista, cyberpunk, innovador",
        "para": "Fintech, Dashboards, Startups",
        "rating": "⭐⭐⭐"
    },
    {
        "num": 6,
        "nombre": "WARM ELEGANCE MARRÓN",
        "emoji": "🏛️",
        "color_primary": "#92400e",
        "paleta": "Marrón dorado + Negro caramelo",
        "modo": "Dark Mode",
        "vibe": "Lujo, sofisticado, confianza",
        "para": "Banca privada, Seguros premium",
        "rating": "⭐⭐⭐⭐"
    },
    {
        "num": 7,
        "nombre": "NEON UNDERGROUND",
        "emoji": "💥",
        "color_primary": "#ec4899",
        "paleta": "Rosa neón + Negro puro",
        "modo": "Dark Mode",
        "vibe": "Atrevido, disruptivo, joven",
        "para": "Social, Creativo, Generacional",
        "rating": "⭐⭐⭐"
    },
    {
        "num": 8,
        "nombre": "INDIGO BUSINESS SERIOUS",
        "emoji": "🏢",
        "color_primary": "#4338ca",
        "paleta": "Índigo profundo + Negro",
        "modo": "Dark Mode",
        "vibe": "Empresarial, confiable, serio",
        "para": "Corporativo, Finanzas, Gobierno",
        "rating": "⭐⭐⭐⭐"
    },
    {
        "num": 9,
        "nombre": "DUAL LIGHT/DARK TOGGLE",
        "emoji": "🌓",
        "color_primary": "Azul dinámico",
        "paleta": "Adaptable + Usuario controla",
        "modo": "Ambos modos",
        "vibe": "Flexible, inclusivo, moderno",
        "para": "Universal, Todos los usuarios",
        "rating": "⭐⭐⭐⭐⭐ 🏆 TOP 3"
    },
    {
        "num": 10,
        "nombre": "GLASSMORPHISM FROSTED",
        "emoji": "🎨",
        "color_primary": "#8b5cf6",
        "paleta": "Púrpura + Vidrio translúcido",
        "modo": "Light Mode",
        "vibe": "Ultra-moderno, premium, wow",
        "para": "Creativo, Portafolios, Premium",
        "rating": "⭐⭐⭐⭐"
    }
]

print("\n" + "="*80)
print("🎨 10 OPCIONES DE REDISEÑO COMPLETO - SPM v1.0")
print("="*80 + "\n")

for opcion in opciones:
    print(f"{opcion['emoji']} OPCIÓN {opcion['num']}: {opcion['nombre']}")
    print(f"   Color Principal:  {opcion['color_primary']}")
    print(f"   Paleta:           {opcion['paleta']}")
    print(f"   Modo:             {opcion['modo']}")
    print(f"   Vibe:             {opcion['vibe']}")
    print(f"   Mejor para:       {opcion['para']}")
    print(f"   Rating:           {opcion['rating']}")
    print()

print("="*80)
print("🏆 TOP 3 RECOMENDACIONES PARA SPM")
print("="*80)
print("""
1️⃣  OPCIÓN 2: VERDE TECH (Esmeralda)
    ✅ Perfecto para "Solicitud de Materiales"
    ✅ Verde = Crecimiento & Confianza
    ✅ Dark Mode elegante
    ✅ Diferencia de competencia

2️⃣  OPCIÓN 4: GRIS MINIMALISTA
    ✅ Ultra-profesional
    ✅ Máxima legibilidad
    ✅ Light Mode limpio
    ✅ Atemporales

3️⃣  OPCIÓN 9: DUAL LIGHT/DARK
    ✅ Máxima flexibilidad
    ✅ Usuario elige su experiencia
    ✅ Respeta preferencias
    ✅ Tendencia actual
""")

print("="*80)
print("📋 ESPECIFICACIONES TÉCNICAS DISPONIBLES EN:")
print("   📄 PROPUESTAS_DISEÑO_10_OPCIONES.md")
print("="*80 + "\n")
