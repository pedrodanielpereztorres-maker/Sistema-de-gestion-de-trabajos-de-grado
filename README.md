# SGT — Sistema de Gestión de Tesis y Pasantías
## IUTEPI — [Año actual]

## Descripción
Sistema de Gestión de Tesis y Pasantías del IUTEPI. Permite a los
administradores registrar estudiantes, asignar tutores y empresas, gestionar
tesis y generar reportes. Los estudiantes acceden desde cualquier dispositivo
para ver su información y perfil.

## Requisitos previos
- Python 3.12+
- PostgreSQL 16+
- Node.js LTS (requerido por Reflex)

## Instalación
1. Clonar el repositorio
2. Crear entorno virtual: `python -m venv .venv`
3. Activar entorno: `.venv\Scripts\activate` (Windows)
4. Instalar dependencias: `pip install -r requirements.txt`
5. Copiar `.env.example` a `.env` y configurar con tus credenciales locales
6. Crear la base de datos en PostgreSQL: `CREATE DATABASE DB_TESIS;`
7. Ejecutar: `reflex run` (desarrollo) o `reflex run --env prod` (producción)

## Configuración inicial
Copiar `.env.example` a `.env` y completar los valores con tus credenciales locales.

> El archivo `.env` debe permanecer únicamente en tu máquina local y **no debe subirse a Git ni compartirse en ningún paquete**.
> El archivo `.env.example` sí puede versionarse y sirve como plantilla para otros desarrolladores.

## Pruebas
Ejecutar las pruebas locales con:

```bash
env PYTHONPATH=. .venv/bin/python -m unittest discover -s tests
```

> El archivo `.env` con credenciales reales NUNCA se comparte ni se adjunta en un ZIP de entrega.
> Mantén `.env` solo en la máquina del servidor o en tu entorno de desarrollo local.

## Roles
- **Administrador**: acceso completo, solo desde PC/Laptop
- **Estudiante**: acceso a su perfil y tesis, desde cualquier dispositivo

## Estructura del proyecto
```
sistema_tesis/
├── rxconfig.py
├── .env
├── .gitignore
├── requirements.txt
└── sistema_tesis/
    ├── sistema_tesis.py
    ├── database_manager.py
    ├── estado/
    │   ├── estado_autenticacion.py
    │   ├── estado_boveda.py
    │   ├── estado_estudiante.py
    │   ├── estado_mantenimiento.py
    │   ├── estado_documento.py
    │   ├── estado_reportes.py
    │   └── estado_layout.py
    ├── componentes/
    │   ├── layout.py
    │   ├── barra_lateral.py
    │   ├── modal_estudiante.py
    │   ├── tabla_estudiantes.py
    │   ├── campo_texto.py
    │   └── toast_viewer.py
    └── paginas/
        ├── login.py, inicio.py, perfil.py
        ├── boveda.py, estudiantes.py
        ├── documentacion.py, mantenimiento.py, reportes.py
```