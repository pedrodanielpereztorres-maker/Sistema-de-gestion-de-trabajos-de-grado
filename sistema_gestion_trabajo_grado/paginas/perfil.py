import logging
import re

import reflex as rx

from ..componentes.layout import layout_principal
from ..database_manager import obtener_conexion
from ..estado.estado_autenticacion import EncriptadorContrasena, EstadoAutenticacion

logger = logging.getLogger(__name__)


class EstadoPerfil(EstadoAutenticacion):
    """Estado para la gestión del perfil de usuario."""

    nombre_edit: str = ""
    apellido_edit: str = ""
    correo_edit: str = ""
    pass_nueva: str = ""
    pass_conf: str = ""

    tutor_nombre: str = "Pendiente"
    tutor_correo: str = "Pendiente"
    tutor_telefono: str = "Pendiente"
    tutor_empresa_nombre: str = "Pendiente"
    tutor_empresa_correo: str = "Pendiente"
    tutor_empresa_telefono: str = "Pendiente"
    empresa: str = "No asignada"
    empresa_direccion: str = "No asignada"
    fecha_inicio: str = "Pendiente"
    fecha_cierre: str = "Pendiente"

    def fijar_nombre_edit(self, val: str) -> None:
        self.nombre_edit = str(val or "")

    def fijar_apellido_edit(self, val: str) -> None:
        self.apellido_edit = str(val or "")

    def fijar_correo_edit(self, val: str) -> None:
        self.correo_edit = str(val or "")

    def fijar_pass_nueva(self, val: str) -> None:
        self.pass_nueva = str(val or "")

    def fijar_pass_conf(self, val: str) -> None:
        self.pass_conf = str(val or "")

    async def cargar_datos_iniciales(self):
        """Carga los datos del perfil y la información académica de forma centralizada."""
        if not self.usuario:
            return rx.redirect("/login")

        nombres = self.usuario.nombre_completo.split(" ")
        self.nombre_edit = nombres[0]
        self.apellido_edit = " ".join(nombres[1:]) if len(nombres) > 1 else ""
        self.correo_edit = self.usuario.correo

        if self.rol_usuario == "estudiante":
            conn = None
            try:
                conn = obtener_conexion()
                if conn is None:
                    logger.error(
                        "No hay conexión para cargar datos académicos de perfil."
                    )
                    return

                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            """
                            SELECT
                                ta.nombre || ' ' || ta.apellido, ta.correo, ta.telefono,
                                te.nombre, te.correo, te.telefono,
                                emp.nombre, emp.direccion,
                                e.periodo_inicio, e.periodo_cierre
                            FROM estudiante e
                            LEFT JOIN tutor_academico ta ON e.tutor_academico_id = ta.id
                            LEFT JOIN tutor_empresarial te ON e.tutor_empresarial_id = te.id
                            LEFT JOIN empresa emp ON te.empresa_id = emp.id
                            WHERE e.usuario_id = %s
                        """,
                            (self.usuario.id,),
                        )
                        res = cursor.fetchone()
                        if res:
                            self.tutor_nombre = res[0] or "Pendiente"
                            self.tutor_correo = res[1] or "Pendiente"
                            self.tutor_telefono = res[2] or "Pendiente"
                            self.tutor_empresa_nombre = res[3] or "Pendiente"
                            self.tutor_empresa_correo = res[4] or "Pendiente"
                            self.tutor_empresa_telefono = res[5] or "Pendiente"
                            self.empresa = res[6] or "Pendiente"
                            self.empresa_direccion = res[7] or "Pendiente"
                            self.fecha_inicio = (
                                res[8].strftime("%d/%m/%Y") if res[8] else "Pendiente"
                            )
                            self.fecha_cierre = (
                                res[9].strftime("%d/%m/%Y") if res[9] else "Pendiente"
                            )
            except Exception as e:
                logger.exception("Error al cargar datos académicos de perfil: %s", e)
            finally:
                if conn:
                    try:
                        conn.close()
                    except Exception:
                        pass

    async def actualizar_datos(self):
        """Actualiza los datos del usuario y la contraseña si corresponde."""
        nombre = self.nombre_edit.strip()
        apellido = self.apellido_edit.strip()
        correo = self.correo_edit.strip().lower()

        if not nombre or not apellido or not correo:
            return rx.toast.warning(
                "⚠️ Campos Obligatorios: Nombre, apellido y correo electrónico son requeridos para actualizar su perfil."
            )

        patron_correo = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron_correo, correo):
            return rx.toast.error(
                "✉️ Formato Inválido: La dirección de correo electrónico no cumple con un formato válido."
            )

        if self.pass_nueva or self.pass_conf:
            if self.pass_nueva != self.pass_conf:
                return rx.toast.error(
                    "🔒 Discrepancia de Clave: Las contraseñas ingresadas no coinciden. Por favor, verifíquelas."
                )
            if len(self.pass_nueva) < 8:
                return rx.toast.error(
                    "🔒 Clave Débil: La nueva contraseña debe tener al menos 8 caracteres de longitud por seguridad."
                )

        conn = None
        try:
            conn = obtener_conexion()
            if conn is None:
                return rx.toast.error(
                    "🔌 Sin Conexión: No se pudo establecer contacto con el servidor de base de datos."
                )

            with conn:
                with conn.cursor() as cursor:
                    if self.usuario is None or self.usuario.id is None:
                        return rx.toast.error(
                            "⚠️ Sesión Inválida: No se pudo identificar una sesión activa de usuario."
                        )

                    if self.pass_nueva:
                        nuevo_hash = EncriptadorContrasena.encriptar(self.pass_nueva)
                        cursor.execute(
                            """
                            UPDATE usuario
                            SET nombre = %s, apellido = %s, correo = %s, contrasena_hash = %s
                            WHERE id = %s;
                            """,
                            (nombre, apellido, correo, nuevo_hash, self.usuario.id),
                        )
                    else:
                        cursor.execute(
                            """
                            UPDATE usuario
                            SET nombre = %s, apellido = %s, correo = %s
                            WHERE id = %s;
                            """,
                            (nombre, apellido, correo, self.usuario.id),
                        )
                conn.commit()

            if self.usuario:
                self.usuario.nombre_completo = f"{nombre} {apellido}"
                self.usuario.correo = correo

            self.pass_nueva = ""
            self.pass_conf = ""
            return rx.toast.success(
                "🎉 Perfil Actualizado: Sus datos personales y de seguridad se han guardado con éxito."
            )

        except Exception as e:
            logger.exception("Error al actualizar el perfil: %s", e)
            return rx.toast.error(
                "💥 Error Crítico: Se presentó una falla interna al procesar la actualización del perfil."
            )
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass


def banner_perfil_usuario() -> rx.Component:
    """Genera una cabecera premium e interactiva con degradado y datos resumidos del usuario."""
    return rx.box(
        rx.hstack(
            rx.avatar(
                fallback=EstadoPerfil.inicial_usuario,
                size="7",
                color_scheme="indigo",
                style={
                    "border": "3px solid white",
                    "box_shadow": "0 4px 14px rgba(0,0,0,0.18)",
                    "flex_shrink": "0",
                },
            ),
            rx.vstack(
                rx.heading(
                    EstadoPerfil.nombre_usuario,
                    size="6",
                    color="white",
                    weight="bold",
                    style={
                        "overflow_wrap": "break-word",
                        "word_break": "break-word",
                        "width": "100%",
                    },
                ),
                rx.flex(
                    rx.badge(
                        EstadoPerfil.rol_usuario.to(str).upper(),
                        style={
                            "background": "rgba(255, 255, 255, 0.22)",
                            "color": "white",
                            "backdrop_filter": "blur(10px)",
                            "border": "1px solid rgba(255, 255, 255, 0.3)",
                            "font_weight": "800",
                            "padding_x": "12px",
                            "white_space": "nowrap",
                        },
                    ),
                    rx.badge(
                        EstadoPerfil.correo_edit,
                        style={
                            "background": "rgba(255, 255, 255, 0.12)",
                            "color": "rgba(255, 255, 255, 0.9)",
                            "backdrop_filter": "blur(10px)",
                            "border": "1px solid rgba(255, 255, 255, 0.15)",
                            "font_weight": "600",
                            "padding_x": "12px",
                            "overflow_wrap": "break-word",
                            "word_break": "break-all",
                            "max_width": "100%",
                        },
                    ),
                    wrap="wrap",
                    align="center",
                    width="100%",
                    style={"gap": "10px"},
                ),
                spacing="2",
                align_items="start",
                min_width="0",
                flex="1",
            ),
            spacing="4",
            align="center",
            width="100%",
        ),
        background="linear-gradient(135deg, #6366F1 0%, #4338CA 100%)",
        border_radius="1.5rem",
        padding="2.25rem",
        box_shadow="0 10px 30px -5px rgba(99, 102, 241, 0.35)",
        width="100%",
        overflow="hidden",
        margin_bottom="6",
    )


def tarjeta_detalle_academico(
    titulo: str, valor: str, icono: str, color: str
) -> rx.Component:
    """Componente reutilizable para presentar detalles con iconos y estilos refinados."""
    return rx.box(
        rx.hstack(
            rx.center(
                rx.icon(icono, size=16, color=color),
                width="2.125rem",
                height="2.125rem",
                background=f"{color}12",
                border_radius="8px",
            ),
            rx.vstack(
                rx.text(
                    titulo,
                    size="1",
                    font_weight="700",
                    color="#64748B",
                    text_transform="uppercase",
                    letter_spacing="0.05em",
                ),
                rx.text(valor, size="2", font_weight="600", color="#1E293B"),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        padding="0.75rem",
        background="#F8FAFC",
        border_radius="0.625rem",
        border="1px solid #F1F5F9",
        width="100%",
    )


def info_academica() -> rx.Component:
    """Sección visible solo para estudiantes con información de su pasantía estructurada premium."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("graduation-cap", size=22, color="#6366F1"),
                rx.heading(
                    "Información Académica", size="4", color="#0F172A", weight="bold"
                ),
                spacing="2",
                align="center",
            ),
            rx.divider(),
            rx.grid(
                tarjeta_detalle_academico(
                    "Tutor Académico",
                    EstadoPerfil.tutor_nombre,
                    "user-check",
                    "#6366F1",
                ),
                tarjeta_detalle_academico(
                    "Correo Tutor Acad.", EstadoPerfil.tutor_correo, "mail", "#6366F1"
                ),
                tarjeta_detalle_academico(
                    "Teléfono Tutor Acad.",
                    EstadoPerfil.tutor_telefono,
                    "phone",
                    "#6366F1",
                ),
                tarjeta_detalle_academico(
                    "Tutor Empresarial",
                    EstadoPerfil.tutor_empresa_nombre,
                    "user-check",
                    "#10B981",
                ),
                tarjeta_detalle_academico(
                    "Correo Tutor Emp.",
                    EstadoPerfil.tutor_empresa_correo,
                    "mail",
                    "#10B981",
                ),
                tarjeta_detalle_academico(
                    "Teléfono Tutor Emp.",
                    EstadoPerfil.tutor_empresa_telefono,
                    "phone",
                    "#10B981",
                ),
                columns={"initial": "1", "sm": "2"},
                spacing="3",
                width="100%",
            ),
            rx.divider(),
            rx.grid(
                tarjeta_detalle_academico(
                    "Empresa Asignada", EstadoPerfil.empresa, "building-2", "#0EA5E9"
                ),
                tarjeta_detalle_academico(
                    "Dirección Empresa",
                    EstadoPerfil.empresa_direccion,
                    "map-pin",
                    "#0EA5E9",
                ),
                tarjeta_detalle_academico(
                    "Fecha de Inicio",
                    EstadoPerfil.fecha_inicio,
                    "calendar-days",
                    "#10B981",
                ),
                tarjeta_detalle_academico(
                    "Fecha de Cierre",
                    EstadoPerfil.fecha_cierre,
                    "calendar-check",
                    "#F59E0B",
                ),
                columns={"initial": "1", "sm": "2"},
                spacing="3",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        style={
            "background": "#FFFFFF",
            "border": "1px solid #E2E8F0",
            "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
            "border_radius": "18px",
        },
        padding="1.5rem",
        width="100%",
    )


def info_mantenimiento_admin() -> rx.Component:
    """Componente que presenta directrices de administración si el usuario posee rol administrativo."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("shield-alert", size=22, color="#6366F1"),
                rx.heading(
                    "Políticas de Administración y Seguridad",
                    size="4",
                    color="#0F172A",
                    weight="bold",
                ),
                spacing="2",
                align="center",
            ),
            rx.divider(),
            rx.text(
                "Como Administrador del sistema ",
                rx.text.span("SGT", class_name="notranslate"),
                ", tu cuenta posee privilegios elevados para gestionar expedientes, ",
                "bóvedas de trabajos de grado e información de tutores académicos y empresariales.",
                size="2",
                color="#475569",
                line_height="1.6",
            ),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("key-round", size=18, color="#F59E0B"),
                        rx.text(
                            "Claves de Acceso Robustas",
                            font_weight="700",
                            size="2",
                            color="#1E293B",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Se recomienda cambiar tu contraseña periódicamente y utilizar combinaciones de letras, números y caracteres especiales.",
                        size="2",
                        color="#64748B",
                    ),
                    align_items="start",
                    spacing="1",
                ),
                padding="0.75rem",
                background="#FFFBEB",
                border_left="4px solid #F59E0B",
                border_radius="0.25rem",
                width="100%",
            ),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("file-lock-2", size=18, color="#10B981"),
                        rx.text(
                            "Privacidad de Datos",
                            font_weight="700",
                            size="2",
                            color="#1E293B",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    rx.text(
                        "Evite compartir capturas de pantalla de la bóveda o de estudiantes con datos sensibles. El sistema encripta los hashes y protege los logs.",
                        size="2",
                        color="#64748B",
                    ),
                    align_items="start",
                    spacing="1",
                ),
                padding="0.75rem",
                background="#ECFDF5",
                border_left="4px solid #10B981",
                border_radius="0.25rem",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        style={
            "background": "#FFFFFF",
            "border": "1px solid #E2E8F0",
            "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
            "border_radius": "18px",
        },
        padding="1.5rem",
        width="100%",
    )


def tarjeta_datos_personales() -> rx.Component:
    """Formulario premium para la actualización de datos personales del usuario."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("user", size=20, color="#6366F1"),
                rx.heading(
                    "Datos Personales", size="4", color="#0F172A", weight="bold"
                ),
                spacing="2",
                align="center",
            ),
            rx.text(
                "Actualiza la información básica vinculada a tu cuenta académica.",
                size="2",
                color="#64748B",
            ),
            rx.divider(),
            rx.vstack(
                rx.text("Nombre", size="2", font_weight="700", color="#334155"),
                rx.input(
                    placeholder="Nombre",
                    value=EstadoPerfil.nombre_edit,
                    on_change=EstadoPerfil.fijar_nombre_edit,
                    width="100%",
                    size="3",
                    variant="classic",
                    style={
                        "background": "white",
                        "border": "1.5px solid #CBD5E1",
                        "border_radius": "10px",
                        "font_weight": "600",
                        "&::placeholder": {
                            "color": "#94A3B8",
                            "opacity": "0.85",
                            "font_weight": "500",
                            "letter_spacing": "0.01em",
                        },
                    },
                    _focus={"border_color": "#6366F1"},
                ),
                width="100%",
                align="start",
                spacing="1",
            ),
            rx.vstack(
                rx.text("Apellido", size="2", font_weight="700", color="#334155"),
                rx.input(
                    placeholder="Apellido",
                    value=EstadoPerfil.apellido_edit,
                    on_change=EstadoPerfil.fijar_apellido_edit,
                    width="100%",
                    size="3",
                    variant="classic",
                    style={
                        "background": "white",
                        "border": "1.5px solid #CBD5E1",
                        "border_radius": "10px",
                        "font_weight": "600",
                        "&::placeholder": {
                            "color": "#94A3B8",
                            "opacity": "0.85",
                            "font_weight": "500",
                            "letter_spacing": "0.01em",
                        },
                    },
                    _focus={"border_color": "#6366F1"},
                ),
                width="100%",
                align="start",
                spacing="1",
            ),
            rx.vstack(
                rx.text(
                    "Correo Electrónico", size="2", font_weight="700", color="#334155"
                ),
                rx.input(
                    placeholder="ejemplo@correo.com",
                    value=EstadoPerfil.correo_edit,
                    on_change=EstadoPerfil.fijar_correo_edit,
                    width="100%",
                    size="3",
                    variant="classic",
                    style={
                        "background": "white",
                        "border": "1.5px solid #CBD5E1",
                        "border_radius": "10px",
                        "font_weight": "600",
                        "&::placeholder": {
                            "color": "#94A3B8",
                            "opacity": "0.85",
                            "font_weight": "500",
                            "letter_spacing": "0.01em",
                        },
                    },
                    _focus={"border_color": "#6366F1"},
                ),
                width="100%",
                align="start",
                spacing="1",
            ),
            rx.button(
                rx.hstack(
                    rx.icon("save", size=16), rx.text("Guardar Cambios", weight="bold")
                ),
                on_click=EstadoPerfil.actualizar_datos,
                width="100%",
                size="3",
                color_scheme="indigo",
                style={
                    "background": "linear-gradient(135deg, #6366F1 0%, #4338CA 100%)",
                    "color": "white",
                    "border_radius": "10px",
                    "box_shadow": "0 4px 12px rgba(99, 102, 241, 0.2)",
                    "cursor": "pointer",
                },
                _hover={
                    "box_shadow": "0 6px 16px rgba(99, 102, 241, 0.3)",
                },
            ),
            spacing="4",
            width="100%",
        ),
        style={
            "background": "#FFFFFF",
            "border": "1px solid #E2E8F0",
            "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
            "border_radius": "18px",
        },
        padding="1.5rem",
        width="100%",
    )


def tarjeta_seguridad() -> rx.Component:
    """Formulario premium para la actualización segura de contraseña."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("lock", size=20, color="#7C3AED"),
                rx.heading(
                    "Seguridad de la Cuenta", size="4", color="#0F172A", weight="bold"
                ),
                spacing="2",
                align="center",
            ),
            rx.text(
                "Mantén tu cuenta protegida actualizando tu contraseña con regularidad.",
                size="2",
                color="#64748B",
            ),
            rx.divider(),
            rx.vstack(
                rx.text(
                    "Nueva Contraseña", size="2", font_weight="700", color="#334155"
                ),
                rx.input(
                    type="password",
                    placeholder="••••••••",
                    value=EstadoPerfil.pass_nueva,
                    on_change=EstadoPerfil.fijar_pass_nueva,
                    width="100%",
                    size="3",
                    variant="classic",
                    style={
                        "background": "white",
                        "border": "1.5px solid #CBD5E1",
                        "border_radius": "10px",
                        "font_weight": "600",
                        "&::placeholder": {
                            "color": "#94A3B8",
                            "opacity": "0.85",
                            "font_weight": "500",
                            "letter_spacing": "0.01em",
                        },
                    },
                    _focus={"border_color": "#7C3AED"},
                ),
                width="100%",
                align="start",
                spacing="1",
            ),
            rx.vstack(
                rx.text(
                    "Confirmar Nueva Contraseña",
                    size="2",
                    font_weight="700",
                    color="#334155",
                ),
                rx.input(
                    type="password",
                    placeholder="••••••••",
                    value=EstadoPerfil.pass_conf,
                    on_change=EstadoPerfil.fijar_pass_conf,
                    width="100%",
                    size="3",
                    variant="classic",
                    style={
                        "background": "white",
                        "border": "1.5px solid #CBD5E1",
                        "border_radius": "10px",
                        "font_weight": "600",
                        "&::placeholder": {
                            "color": "#94A3B8",
                            "opacity": "0.85",
                            "font_weight": "500",
                            "letter_spacing": "0.01em",
                        },
                    },
                    _focus={"border_color": "#7C3AED"},
                ),
                width="100%",
                align="start",
                spacing="1",
            ),
            rx.button(
                rx.hstack(
                    rx.icon("key", size=16), rx.text("Actualizar Clave", weight="bold")
                ),
                on_click=EstadoPerfil.actualizar_datos,
                width="100%",
                size="3",
                variant="surface",
                color_scheme="violet",
                style={
                    "border_radius": "10px",
                    "cursor": "pointer",
                },
            ),
            spacing="4",
            width="100%",
        ),
        style={
            "background": "#FFFFFF",
            "border": "1px solid #E2E8F0",
            "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.05)",
            "border_radius": "18px",
        },
        padding="1.5rem",
        width="100%",
    )


def pagina_perfil() -> rx.Component:
    """Vista principal del perfil de usuario con formularios integrados y adaptados."""
    return layout_principal(
        rx.vstack(
            banner_perfil_usuario(),
            rx.grid(
                rx.cond(
                    EstadoPerfil.rol_usuario == "estudiante",
                    info_academica(),
                    info_mantenimiento_admin(),
                ),
                rx.vstack(
                    tarjeta_datos_personales(),
                    tarjeta_seguridad(),
                    spacing="6",
                    width="100%",
                ),
                columns={"initial": "1", "md": "1", "lg": "2"},
                spacing="6",
                width="100%",
            ),
            on_mount=EstadoPerfil.cargar_datos_iniciales,
            spacing="6",
            width="100%",
            max_width="96vw",
            margin="auto",
        )
    )
