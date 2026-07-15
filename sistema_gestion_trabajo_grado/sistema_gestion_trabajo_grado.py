import os

import reflex as rx
import logging
from starlette.responses import FileResponse, PlainTextResponse
from starlette.staticfiles import StaticFiles

from .database_manager import inicializar_infraestructura
from .estado.estado_autenticacion import EstadoAutenticacion
from .estado.estado_boveda import EstadoBoveda
from .estado.estado_dashboard import EstadoDashboard
from .estado.estado_documento import EstadoDocumento
from .estado.estado_estudiante import EstadoEstudiante
from .paginas.boveda import pagina_boveda
from .paginas.documentacion import pagina_documentacion
from .paginas.estudiantes import pagina_estudiantes
from .paginas.inicio import pagina_inicio
from .paginas.login import pagina_login
from .paginas.mantenimiento import pagina_mantenimiento
from .paginas.perfil import EstadoPerfil, pagina_perfil
from .paginas.reportes import pagina_reportes

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
        EstadoBoveda.cargar_trabajos_de_grado,
        EstadoDocumento.cargar_documentos,
    ],
)
app.add_page(pagina_login, route="/login")
app.add_page(
    pagina_boveda,
    route="/boveda",
    on_load=[
        EstadoAutenticacion.verificar_sesion,
        EstadoBoveda.cargar_trabajos_de_grado,
    ],
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




def verificar_token_acceso(token: str) -> bool:
    if not token:
        return False
    if len(token) < 20:
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
            encontrado = cursor.fetchone() is not None
            if encontrado:
                try:
                    # Renovar expiración por inactividad: 1 hora desde ahora
                    cursor.execute(
                        "UPDATE sesion SET expira_en = NOW() + INTERVAL '1 hour' WHERE token = %s",
                        (token,),
                    )
                    conn.commit()
                except Exception:
                    # No fatal: si falla la renovación, seguimos considerando el token válido
                    pass
            return encontrado
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
    logging.info(
        "[servir_archivo_privado] method=%s url=%s cookies=%s cookie_header=%s",
        getattr(request, "method", "-"),
        getattr(request, "url", "-"),
        dict(getattr(request, "cookies", {})),
        request.headers.get("cookie"),
    )
    categoria = request.path_params.get("categoria", "")
    archivo = request.path_params.get("archivo", "")
    token = request.cookies.get("sts_token", "")
    logging.debug("[servir_archivo_privado] sts_token=%s", token)

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
        ruta_archivo,
        media_type="application/pdf",
        content_disposition_type="inline",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0", "Pragma": "no-cache"},
    )


def servir_pdf_publico(request):
    """Endpoint alternativo para servir PDFs sin validación de token (temporal)."""
    categoria = request.path_params.get("categoria", "")
    archivo = request.path_params.get("archivo", "")

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
        ruta_archivo,
        media_type="application/pdf",
        content_disposition_type="inline",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0", "Pragma": "no-cache"},
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
        "/almacen/{categoria}/{archivo:path}", servir_archivo_privado, methods=["GET", "POST"]
    )
    # Endpoint alternativo sin validación de token (temporal)
    app._api.add_route(
        "/almacen-publico/{categoria}/{archivo:path}", servir_pdf_publico, methods=["GET"]
    )
    app._api.add_route("/manifest.json", servir_manifest, methods=["GET"])
    app._api.add_route("/sw.js", servir_service_worker, methods=["GET"])
    # Log routes for debugging
    try:
        for route in app._api.routes:
            logging.info("RUTA REGISTRADA: %s %s", getattr(route, "path", str(route)), getattr(route, "methods", "-"))
    except Exception:
        pass
except Exception as e:
    import logging

    logging.error(f"No se pudo montar la ruta segura: {e}")
