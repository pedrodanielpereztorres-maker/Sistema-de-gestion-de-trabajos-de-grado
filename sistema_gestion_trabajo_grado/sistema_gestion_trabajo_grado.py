import os

from .paginas.perfil import pagina_perfil
import reflex as rx
from .paginas.inicio import pagina_inicio
from .paginas.login import pagina_login
from .paginas.boveda import pagina_boveda
from .paginas.estudiantes import pagina_estudiantes
from .paginas.documentacion import pagina_documentacion
from .paginas.mantenimiento import pagina_mantenimiento
from .paginas.reportes import pagina_reportes
from .database_manager import inicializar_infraestructura
from .estado.estado_autenticacion import EstadoAutenticacion
from .estado.estado_estudiante import EstadoEstudiante
from .estado.estado_boveda import EstadoBoveda
from .estado.estado_dashboard import EstadoDashboard
from .estado.estado_documento import EstadoDocumento
from .paginas.perfil import EstadoPerfil
from starlette.responses import FileResponse, PlainTextResponse
from starlette.staticfiles import StaticFiles

PWA_ASSETS_DIR = os.path.join(os.getcwd(), "assets", "iconos_sgtg_premium")

app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="indigo",
        gray_color="slate",
        radius="large",
        scaling="95%",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
    style={
        "font_family": "Inter, sans-serif",
    },
    html_lang="es",
    html_custom_attrs={
        "translate": "no",
    },
    head_components=[
        rx.el.meta(name="theme-color", content="#C9A84C"),
        rx.el.meta(name="apple-mobile-web-app-capable", content="yes"),
        rx.el.meta(
            name="apple-mobile-web-app-status-bar-style", content="black-translucent"
        ),
        rx.el.meta(name="apple-mobile-web-app-title", content="S.G.T.G."),
        rx.el.link(rel="manifest", href="/manifest.json"),
        rx.el.link(rel="icon", href="/iconos_sgtg_premium/favicon.ico", sizes="any"),
        rx.el.link(rel="shortcut icon", href="/iconos_sgtg_premium/favicon_32x32.png"),
        rx.el.link(
            rel="apple-touch-icon", href="/iconos_sgtg_premium/apple_touch_180x180.png"
        ),
        rx.el.script("""
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/sw.js').catch(function(error) {
                    console.warn('No se pudo registrar el service worker:', error);
                });
            });
        }
        """),
    ],
)

# Inicializar base de datos al arrancar
inicializar_infraestructura()

# Registrar rutas con protección de sesión. /login permanece pública.
app.add_page(
    pagina_inicio,
    route="/",
    on_load=[
        EstadoAutenticacion.verificar_sesion,
        EstadoEstudiante.cargar_estudiantes,
        EstadoDashboard.cargar_dashboard,
        EstadoPerfil.cargar_datos_iniciales,
        EstadoBoveda.cargar_tesis,
        EstadoDocumento.cargar_documentos,
    ],
)
app.add_page(pagina_login, route="/login")
app.add_page(
    pagina_boveda,
    route="/boveda",
    on_load=[EstadoAutenticacion.verificar_sesion, EstadoBoveda.cargar_tesis],
)
app.add_page(
    pagina_estudiantes,
    route="/estudiantes",
    on_load=[
        EstadoAutenticacion.verificar_sesion_admin,
        EstadoEstudiante.cargar_estudiantes,
    ],
)
app.add_page(
    pagina_documentacion,
    route="/documentacion",
    on_load=[EstadoAutenticacion.verificar_sesion, EstadoDocumento.cargar_documentos],
)
# Páginas solo para administradores
app.add_page(
    pagina_mantenimiento,
    route="/mantenimiento",
    on_load=EstadoAutenticacion.verificar_sesion_admin,
)
app.add_page(
    pagina_perfil,
    route="/perfil",
    on_load=[EstadoAutenticacion.verificar_sesion, EstadoPerfil.cargar_datos_iniciales],
)
app.add_page(
    pagina_reportes,
    route="/reportes",
    on_load=EstadoAutenticacion.verificar_sesion_admin,
)

# =====================================================================
# SERVIDOR DE ARCHIVOS PRIVADOS (Bóveda y Documentación)
# =====================================================================


def verificar_token_acceso(token: str) -> bool:
    if not token:
        return False
    conn = None
    try:
        from .database_manager import obtener_conexion

        conn = obtener_conexion()
        if conn is None:
            return False
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM sesion WHERE token = %s AND esta_activa = TRUE AND expira_en > NOW()",
                (token,),
            )
            return cursor.fetchone() is not None
    except Exception:
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def servir_archivo_privado(request):
    """Endpoint para servir documentos privados validando el token de sesión."""
    categoria = request.path_params.get("categoria", "")
    archivo = request.path_params.get("archivo", "")
    token = request.query_params.get("token", "") or request.cookies.get(
        "sts_token", ""
    )

    if not verificar_token_acceso(token):
        return PlainTextResponse(
            "Acceso Denegado: Sesión inválida o expirada.", status_code=401
        )

    if categoria not in ["trabajo_de_grado", "documentos"]:
        return PlainTextResponse(
            "Acceso Denegado: Categoría no permitida.", status_code=403
        )

    ruta_base = os.path.join(os.getcwd(), "almacen_privado", categoria)
    ruta_archivo = os.path.join(ruta_base, archivo)

    if not os.path.abspath(ruta_archivo).startswith(os.path.abspath(ruta_base)):
        return PlainTextResponse("Acceso Denegado.", status_code=403)

    if not os.path.exists(ruta_archivo):
        return PlainTextResponse("Archivo no encontrado.", status_code=404)

    return FileResponse(
        ruta_archivo, media_type="application/pdf", content_disposition_type="inline"
    )


def servir_manifest(request):
    """Sirve el manifiesto PWA desde la carpeta de iconos del branding."""
    return FileResponse(
        os.path.join(PWA_ASSETS_DIR, "manifest.json"),
        media_type="application/manifest+json",
    )


def servir_service_worker(request):
    """Sirve el service worker para habilitar la experiencia PWA."""
    return FileResponse(
        os.path.join(PWA_ASSETS_DIR, "sw.js"), media_type="application/javascript"
    )


# Agregamos las rutas directamente al servidor ASGI interno de Reflex
try:
    app._api.mount(
        "/iconos_sgtg_premium",
        StaticFiles(directory=PWA_ASSETS_DIR),
        name="iconos_sgtg_premium",
    )
    app._api.add_route(
        "/almacen/{categoria}/{archivo:path}", servir_archivo_privado, methods=["GET"]
    )
    app._api.add_route("/manifest.json", servir_manifest, methods=["GET"])
    app._api.add_route("/sw.js", servir_service_worker, methods=["GET"])
except Exception as e:
    import logging

    logging.error(f"No se pudo montar la ruta segura: {e}")
