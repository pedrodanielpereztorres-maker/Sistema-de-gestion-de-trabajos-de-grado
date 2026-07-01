# SGT — Sistema de Gestión de Tesis y Pasantías
## IUTEPI — 2026

## Descripción
Sistema reactivo para la gestión administrativa de pasantías y trabajos de grado, desarrollado con Reflex y PostgreSQL.

## Requisitos previos
- Python 3.12+
- PostgreSQL 16+
- Node.js LTS (requerido por Reflex)

## Instalación
1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv .venv`
3. Activar entorno: `.venv\Scripts\activate` (Windows) o `source .venv/bin/activate` (Linux)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Copiar `.env.example` a `.env` y configurar con tus credenciales
6. Crear la base de datos en PostgreSQL: `CREATE DATABASE DB_TESIS;`
7. Ejecutar: `reflex run` (desarrollo) o `reflex run --env prod` (producción)

## Configuración inicial
El archivo `.env` NUNCA se comparte. Copiar `.env.example` y completarlo con las credenciales locales del servidor.

## Roles
- **Administrador**: acceso completo, solo desde PC/Laptop (bloqueo móvil activado).
- **Estudiante**: acceso a su perfil, documentación y tesis desde cualquier dispositivo.

## Estructura del proyecto
```
sistema_tesis/
├── estado/              # Lógica de negocio y cursores SQL
├── componentes/         # UI reusable (tablas, modales, etc.)
├── paginas/             # Vistas principales del sistema
├── database_manager.py  # Gestión de pool y esquema SQL
└── sistema_tesis.py     # Punto de entrada y rutas
```