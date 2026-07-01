import reflex as rx
from ..estado.estado_autenticacion import EstadoAutenticacion
from ..estado.estado_estudiante import EstadoEstudiante
from ..estado.estado_boveda import EstadoBoveda
from ..estado.estado_dashboard import EstadoDashboard
from ..componentes.layout import layout_principal
from .perfil import EstadoPerfil

COLOR_PRIMARIO = "#6366F1"
COLOR_FONDO_GLOBAL = "white"
COLOR_TEXTO_BOLD = "#0F172A"
COLOR_TEXTO_BODY = "#1E293B"

# Helper: safely convert reactive or plain values to string for the UI
def valor_a_string(v):
    try:
        # If v is a Reflex Var-like object with .to, prefer reactive conversion
        if hasattr(v, "to"):
            return v.to(str)
    except Exception:
        pass
    try:
        return str(v)
    except Exception:
        return ""


def fila_estudiante_lista(estudiante) -> rx.Component:
    """Representa una fila de estudiante optimizada, interactiva y con transiciones hover."""
    # Soportar tanto dicts antiguos como objetos `EstudianteResumen`.
    if isinstance(estudiante, dict):
        nombre = estudiante.get("nombre", "")
        apellido = estudiante.get("apellido", "")
        carrera = estudiante.get("carrera", "")
        cedula = estudiante.get("cedula", "")
        # dicts contienen strings normales
        inicial = valor_a_string(nombre)[:1] or "E"
    else:
        nombre = getattr(estudiante, "nombre", "")
        apellido = getattr(estudiante, "apellido", "")
        carrera = getattr(estudiante, "carrera", "")
        cedula = getattr(estudiante, "cedula", "")
        # Priorizar campo precomputado `inicial` si existe
        inicial_attr = getattr(estudiante, "inicial", None)
        if hasattr(inicial_attr, "to"):
            inicial = rx.cond(inicial_attr != "", inicial_attr, "E")
        elif inicial_attr:
            inicial = str(inicial_attr)[:1]
        else:
            # Si `nombre` es reactivo, usar rx.cond sobre nombre.to(str)
            if hasattr(nombre, "to"):
                inicial = rx.cond(nombre.to(str) != "", nombre.to(str)[0], "E")
            else:
                inicial = valor_a_string(nombre)[:1] or "E"

    return rx.box(
        rx.hstack(
            rx.center(
                rx.text(
                    inicial,
                    color="white",
                    font_weight="bold",
                    font_size="0.75rem"
                ),
                width="2.25rem", height="2.25rem", border_radius="full",
                background="linear-gradient(135deg, #6366F1 0%, #4338CA 100%)",
                box_shadow="0 0.125rem 0.375rem rgba(99, 102, 241, 0.2)",
            ),
            rx.vstack(
                rx.text(
                    valor_a_string(nombre) + " " + valor_a_string(apellido),
                    font_size="0.875rem",
                    font_weight="700",
                    color=COLOR_TEXTO_BOLD,
                    style={"word_break": "break-word"}
                ),
                rx.text(
                    valor_a_string(carrera),
                    font_size="0.75rem",
                    color="#64748B",
                    font_weight="500",
                    style={"word_break": "break-word"}
                ),
                spacing="0",
                align="start"
            ),
            rx.spacer(),
            rx.badge(
                valor_a_string(cedula),
                variant="soft",
                color_scheme="gray",
                radius="medium",
                style={
                    "color": "#475569",
                    "background_color": "#F1F5F9",
                    "font_weight": "700",
                    "font_size": "0.75rem",
                }
            ),
            width="100%", align="center",
        ),
        padding="0.75rem 0.875rem",
        border_radius="0.75rem",
        background="white",
        border="1px solid #F1F5F9",
        margin_bottom="0.5rem",
        min_width="0",
        transition="transform 0.2s ease, box-shadow 0.2s ease",
        _hover={
            "transform": "translateX(0.25rem)",
            "box_shadow": "0 0.25rem 0.75rem rgba(0, 0, 0, 0.03)",
            "background": "#F8FAFC",
        },
        key=valor_a_string(cedula),
    )


def tarjeta_estadistica(titulo: str, valor: str, icono: str, color: str) -> rx.Component:
    """Tarjeta de estadísticas premium con degradado de color y animaciones hover."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.center(
                    rx.icon(icono, size=22, color="white"),
                    width="2.75rem",
                    height="2.75rem",
                    background=color,
                    border_radius="0.875rem",
                    box_shadow="0 0.5rem 1.5rem rgba(0, 0, 0, 0.08)"
                ),
                rx.spacer(),
                rx.badge(
                    "Actualizado", variant="soft", color_scheme="gray", radius="full",
                    style={
                        "color": "#1E293B",
                        "background_color": "#F1F5F9",
                        "font_weight": "bold",
                    }
                ),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.text(titulo, size="3", font_weight="700", color=COLOR_TEXTO_BODY),
                rx.text(valor, size="8", weight="bold", color=COLOR_TEXTO_BOLD, style={"background_color": "transparent", "line_height": "1.05"}),
                spacing="1",
                align="start",
            ),
            spacing="4",
            align="start",
        ),
        size="3",
        width="100%",
        style={
            "background": "#FFFFFF",
            "border": "1px solid #E5E7F0",
            "box_shadow": "0 0.875rem 2.5rem rgba(15, 23, 42, 0.06)",
            "transition": "transform 0.25s ease, box-shadow 0.25s ease",
            "cursor": "default",
            "border_radius": "1rem",
            "padding": "1.75rem",
            "min_width": "0",
        },
        _hover={
            "transform": "translateY(-3px)",
            "box_shadow": "0 18px 48px rgba(15, 23, 42, 0.08)",
            "border": "1px solid #C7D2FE",
        }
    )


def boton_accion_rapida(label: str, icono: str, color_scheme: str, on_click) -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.icon(icono, size=16),
            rx.text(label, weight="bold", color=COLOR_TEXTO_BOLD),
            spacing="3",
            align="center",
        ),
        width="100%",
        variant="soft",
        color_scheme=color_scheme,
        size="3",
        style={
            "display": "flex",
            "align_items": "center",
            "border_radius": "1rem",
            "padding": "1.125rem 1.375rem",
            "justify_content": "flex-start",
            "text_align": "left",
            "box_shadow": "0 0.5rem 1.5rem rgba(15, 23, 42, 0.06)",
        },
        _hover={
            "transform": "translateY(-2px)",
            "box_shadow": "0 14px 30px rgba(15, 23, 42, 0.08)",
            "background_color": "#EEF2FF",
        },
        on_click=on_click,
    )


def tarjeta_carrera(carrera, cantidad, progreso) -> rx.Component:
    valor_progreso = progreso.to(int) if hasattr(progreso, "to") else int(progreso)
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        valor_a_string(carrera),
                        size="3",
                        weight="bold",
                        color=COLOR_TEXTO_BOLD,
                        style={
                            "white_space": "normal",
                            "word_break": "break-word",
                            "overflow_wrap": "break-word",
                        }
                    ),
                    rx.text(f"{valor_a_string(cantidad)} estudiantes", size="2", color="#475569"),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                rx.badge(
                    f"{valor_progreso}%",
                    variant="solid",
                    color_scheme=rx.cond(valor_progreso >= 75, "green", rx.cond(valor_progreso >= 50, "orange", "red")),
                    radius="full",
                    style={"color": "white", "font_weight": "700", "padding": "0 1rem", "font_size": "0.8125rem"},
                ),
                align="start",
                spacing="5",
                width="100%",
            ),
            rx.progress(
                value=valor_progreso,
                width="100%",
                color_scheme=rx.cond(valor_progreso >= 75, "green", rx.cond(valor_progreso >= 50, "orange", "red")),
                style={
                    "height": "1rem",
                    "border_radius": "999px",
                    "background": "#E2E8F0",
                }
            ),
            rx.hstack(
                rx.text("Progreso de la carrera", size="1", color="#94A3B8"),
                rx.spacer(),
                rx.text(f"{valor_a_string(cantidad)} estudiantes", size="1", color="#64748B"),
            ),
            spacing="5",
            width="100%",
        ),
        size="3",
        style={
            "background": "#FFFFFF",
            "border": "1px solid #E5E7EB",
            "border_radius": "1.125rem",
            "box_shadow": "0 1rem 2.25rem rgba(15, 23, 42, 0.08)",
            "padding": "2rem",
            "min_height": "13.75rem",
            "min_width": "0",
            "transition": "transform 0.2s ease, box-shadow 0.2s ease",
        },
        _hover={
            "transform": "translateY(-3px)",
            "box_shadow": "0 20px 40px rgba(15, 23, 42, 0.12)",
            "border": "1px solid #C7D2FE",
        }
    )


def panel_carga_academica() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text("Carga Académica por Carrera", size="4", weight="bold", color=COLOR_TEXTO_BOLD),
                    rx.text("Las carreras con más estudiantes activos", size="2", color="#64748B", font_weight="500"),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.badge("Top 3", variant="soft", color_scheme="indigo", radius="full", style={"font_weight": "700"}),
                spacing="4",
                align="center",
                width="100%",
            ),
            rx.grid(
                rx.foreach(
                    EstadoDashboard.top_carreras,
                    lambda c, i: rx.cond(
                        i < 3,
                        tarjeta_carrera(c.carrera, c.cantidad, c.progreso),
                        rx.fragment()
                    )
                ),
                columns={"initial": "1", "md": "2", "xl": "3"},
                spacing="7",
                width="100%",
                min_width="0",
            ),
            rx.text(
                "Monitorea el volumen de estudiantes por carrera y prioriza los recursos académicos.",
                size="2", color="#475569", font_weight="500",
                style={"max_width": "48.75rem", "line_height": "1.8"}
            ),
            spacing="7",
            width="100%",
        ),
        size="3",
        style={
            "background": "#FFFFFF",
            "border": "1px solid #E2E8F0",
            "border_radius": "1rem",
            "box_shadow": "0 0.875rem 2.25rem rgba(15, 23, 42, 0.06)",
            "padding": "1.875rem",
            "width": "100%",
            "max_width": "100%",
            "min_width": "0",
        }
    )


def panel_boveda() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("archive", size=20, color=COLOR_PRIMARIO),
                rx.vstack(
                    rx.text("Estado de la Bóveda", size="4", weight="bold", color=COLOR_TEXTO_BOLD),
                    rx.text("Seguro, rápido y con control de privacidad", size="2", color="#64748B", font_weight="500"),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.badge("Privacidad", variant="soft", color_scheme="indigo", radius="full", style={"font_weight": "700"}),
                spacing="4",
                align="center",
            ),
            rx.grid(
                rx.card(
                    rx.vstack(
                        rx.text("Públicas", size="2", color="#475569", font_weight="700"),
                        rx.text(EstadoDashboard.tesis_publicas.to(str), size="5", weight="bold", color=COLOR_TEXTO_BOLD, style={"background_color": "transparent"}),
                        rx.text("Acceso abierto para la comunidad académica", size="1", color="#64748B", font_weight="500"),
                        spacing="3",
                        width="100%",
                    ),
                    size="3",
                    style={
                        "background": "#F0F9FF",
                        "border": "1px solid #D0E9FF",
                        "border_radius": "1.125rem",
                        "box_shadow": "0 0.75rem 2rem rgba(14,165,233,0.14)",
                        "padding": "1.75rem",
                        "min_width": "0",
                    }
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Privadas", size="2", color="#475569", font_weight="700"),
                        rx.text(EstadoDashboard.tesis_privadas.to(str), size="5", weight="bold", color=COLOR_TEXTO_BOLD, style={"background_color": "transparent"}),
                        rx.text("Documentos con acceso restringido", size="1", color="#64748B", font_weight="500"),
                        spacing="3",
                        width="100%",
                    ),
                    size="3",
                    style={
                        "background": "#FEF3C7",
                        "border": "1px solid #FDE68A",
                        "border_radius": "1.125rem",
                        "box_shadow": "0 0.75rem 2rem rgba(245,158,11,0.14)",
                        "padding": "1.75rem",
                        "min_width": "0",
                    }
                ),
                columns={"initial": "1", "lg": "2"},
                spacing="6",
                width="100%",
            ),
            rx.text(
                "Visualiza qué tan organizada está la bóveda y cuáles documentos están en público o privado.",
                size="2", color="#475569", font_weight="500",
                style={"max_width": "50rem", "line_height": "1.8"}
            ),
            spacing="6",
            width="100%",
        ),
        size="3",
        style={
            "background": "#FFFFFF",
            "border": "1px solid #E2E8F0",
            "border_radius": "1rem",
            "box_shadow": "0 0.875rem 2.25rem rgba(15, 23, 42, 0.06)",
            "padding": "1.875rem",
        }
    )


def panel_acciones() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text("Acciones de Gestión", size="4", weight="bold", color=COLOR_TEXTO_BOLD),
                    rx.text("Atajos de administración", size="1", color="#64748B"),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                width="100%",
                align="center",
            ),
            rx.grid(
                boton_accion_rapida("Inscribir Estudiante", "user-plus", "indigo", rx.redirect("/estudiantes")),
                boton_accion_rapida("Nuevo Trabajo de Grado", "book-plus", "violet", rx.redirect("/boveda")),
                boton_accion_rapida("Explorar Bóveda", "library", "indigo", rx.redirect("/boveda")),
                boton_accion_rapida("Subir Guía PDF", "file-up", "blue", rx.redirect("/documentacion")),
                boton_accion_rapida("Ver Documentación", "file-text", "blue", rx.redirect("/documentacion")),
                boton_accion_rapida("Reporte General", "file-down", "green", EstadoEstudiante.generar_reporte_estudiantes),
                columns={"initial": "1", "md": "2"},
                spacing="5",
                width="100%",
                min_width="0",
            ),
            spacing="5",
            width="100%",
        ),
        size="3",
        style={
            "background": "#FFFFFF",
            "border": "1px solid #E2E8F0",
            "border_radius": "1rem",
            "box_shadow": "0 0.875rem 2.125rem rgba(15, 23, 42, 0.06)",
            "padding": "1.875rem",
            "min_width": "0",
        }
    )


def tarjeta_info_estudiante(titulo: str, valor: str, icono: str, color: str) -> rx.Component:
    """Presenta bloques de información de estudiante en el dashboard con estilo refinado."""
    return rx.card(
        rx.hstack(
            rx.center(
                rx.icon(icono, size=20, color=color),
                width="2.5rem",
                height="2.5rem",
                background="white",
                border=f"1.5px solid {color}30",
                border_radius="0.625rem",
            ),
            rx.vstack(
                rx.text(titulo, size="1", font_weight="800",
                        color="#64748B", text_transform="uppercase", letter_spacing="0.05em"),
                rx.text(valor, size="3", weight="bold",
                        color=COLOR_TEXTO_BOLD),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        size="2",
        width="100%",
        style={
            "background": "#FFFFFF",
            "border": "1px solid #E2E8F0",
            "box_shadow": "0 0.125rem 0.25rem rgba(0, 0, 0, 0.02)",
            "border_radius": "0.75rem",
            "min_width": "0",
        }
    )


def encabezado_bienvenida() -> rx.Component:
    """Cabecera de bienvenida pulida y responsiva."""
    return rx.flex(
        rx.vstack(
            rx.heading(
                f"Bienvenido, {EstadoAutenticacion.nombre_usuario}",
                size={"initial": "7", "sm": "8"},
                weight="bold",
                color=COLOR_TEXTO_BOLD
            ),
            rx.text("Panel central de control y seguimiento académico",
                    color="#475569", size="3", font_weight="500"),
            spacing="1",
            align="start",
        ),
        rx.spacer(),
        rx.button(
            rx.icon("refresh-cw", size=16),
            rx.text("Sincronizar", weight="bold"),
            variant="soft",
            color_scheme="indigo",
            style={
                "color": "#312E81",
                "background_color": "#E0E7FF",
                "border": "1px solid #C7D2FE",
                "border_radius": "0.625rem",
                "cursor": "pointer",
            },
            _hover={"background_color": "#C7D2FE"},
            on_click=[EstadoEstudiante.cargar_estudiantes,
                      EstadoDashboard.cargar_dashboard,
                      EstadoBoveda.cargar_tesis]
        ),
        width="100%",
        align={"initial": "start", "sm": "center"},
        direction={"initial": "column", "sm": "row"},
        justify="between",
        spacing="4",
        margin_bottom="6",
    )


def panel_estudiante() -> rx.Component:
    """Información completa de la pasantía asignada al estudiante en el dashboard."""
    return rx.vstack(
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("graduation-cap", size=22, color=COLOR_PRIMARIO),
                    rx.text("Mi Información de Pasantía", size="4", weight="bold", color=COLOR_TEXTO_BOLD),
                    rx.spacer(),
                    rx.badge(
                        "En Curso", color_scheme="green", variant="soft", radius="full",
                        style={
                            "color": "#065F46",
                            "background_color": "#D1FAE5",
                            "font_weight": "800",
                            "padding_x": "0.75rem",
                        }
                    ),
                    width="100%", align="center", margin_bottom="4"
                ),
                rx.grid(
                    tarjeta_info_estudiante("Tutor Académico", EstadoPerfil.tutor_nombre, "user-check", "#6366F1"),
                    tarjeta_info_estudiante("Correo Tutor Acad.", EstadoPerfil.tutor_correo, "mail", "#8B5CF6"),
                    tarjeta_info_estudiante("Teléfono Tutor Acad.", EstadoPerfil.tutor_telefono, "phone", "#6366F1"),
                    tarjeta_info_estudiante("Tutor Empresarial", EstadoPerfil.tutor_empresa_nombre, "user-check", "#10B981"),
                    tarjeta_info_estudiante("Correo Tutor Emp.", EstadoPerfil.tutor_empresa_correo, "mail", "#10B981"),
                    tarjeta_info_estudiante("Teléfono Tutor Emp.", EstadoPerfil.tutor_empresa_telefono, "phone", "#10B981"),
                    tarjeta_info_estudiante("Empresa Asignada", EstadoPerfil.empresa, "building-2", "#0EA5E9"),
                    tarjeta_info_estudiante("Dirección Empresa", EstadoPerfil.empresa_direccion, "map-pin", "#0EA5E9"),
                    tarjeta_info_estudiante("Fecha de Inicio", EstadoPerfil.fecha_inicio, "calendar-days", "#10B981"),
                    tarjeta_info_estudiante("Fecha de Cierre", EstadoPerfil.fecha_cierre, "calendar-check", "#F59E0B"),
                    tarjeta_info_estudiante("Estado de Trámite", "Activo", "check-check", "#6366F1"),
                    columns={"initial": "1", "sm": "1", "md": "2", "lg": "3"},
                    spacing="4",
                    width="100%",
                ),
                width="100%",
            ),
            padding=["1.25rem", "1.5rem", "1.75rem"],
            background="white",
            border_radius="1.25rem",
            border="1px solid #E2E8F0",
            box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)",
            margin_bottom="6",
            width="100%",
            overflow_x="auto",
        ),
        width="100%",
    )


def panel_administrador() -> rx.Component:
    """Grilla con tarjetas de estadísticas rápidas para administración."""
    return rx.vstack(
        rx.grid(
            tarjeta_estadistica(
                "Total Estudiantes", EstadoDashboard.total_estudiantes.to(str), "users", "linear-gradient(135deg, #6366F1, #3B82F6)"
            ),
            tarjeta_estadistica(
                "En Pasantía", EstadoDashboard.estudiantes_en_pasantia.to(str), "graduation-cap", "linear-gradient(135deg, #10B981, #059669)"
            ),
            tarjeta_estadistica(
                "Sin Pasantía", EstadoDashboard.estudiantes_sin_pasantia.to(str), "user-minus", "linear-gradient(135deg, #F59E0B, #D97706)"
            ),
            tarjeta_estadistica(
                "Bóveda (Trabajo de grado)", EstadoDashboard.total_tesis.to(str), "library", "linear-gradient(135deg, #8B5CF6, #7C3AED)"
            ),
            columns={"initial": "1", "sm": "2", "md": "4"},
            spacing="5",
            width="100%",
            margin_bottom="6"
        ),
        width="100%",
    )


def pagina_inicio() -> rx.Component:
    """Página de inicio / Dashboard principal del SGT."""
    return rx.theme(
        rx.cond(
            EstadoAutenticacion.usuario,
            layout_principal(
                rx.vstack(
                    encabezado_bienvenida(),
                    rx.cond(
                        EstadoAutenticacion.rol_usuario == "estudiante",
                        panel_estudiante(),
                        rx.fragment()
                    ),
                    rx.cond(
                        EstadoAutenticacion.rol_usuario == "administrador",
                        panel_administrador(),
                        rx.fragment()
                    ),
                    rx.fragment(),
                    rx.cond(
                        EstadoAutenticacion.rol_usuario == "administrador",
                        rx.vstack(
                            panel_carga_academica(),
                            rx.grid(
                                panel_boveda(),
                                panel_acciones(),
                                columns={"initial": "1", "lg": "2"},
                                spacing="6",
                                width="100%",
                                min_width="0",
                            ),
                            spacing="6",
                            width="100%",
                        ),
                        rx.fragment()
                    ),
                    width="100%",
                    max_width={"initial": "100%", "xl": "100rem"},
                    margin_x="auto",
                    padding=["1.25rem", "1.75rem", "2.25rem", "2.25rem"],
                ),
            ),
            rx.center(
                rx.spinner(size="3", color="indigo"),
                width="100vw",
                height="100vh",
                background_color=COLOR_FONDO_GLOBAL,
                on_mount=[
                    EstadoAutenticacion.verificar_acceso,
                    EstadoEstudiante.cargar_estudiantes,
                    EstadoBoveda.cargar_tesis,
                    EstadoDashboard.cargar_dashboard,
                    EstadoPerfil.cargar_datos_iniciales,
                ],
            ),
        ),
        appearance="light",
        has_background=True,
    )
