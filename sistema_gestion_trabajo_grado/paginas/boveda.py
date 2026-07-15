import reflex as rx

from ..componentes.campo_texto import campo_texto
from ..componentes.encabezado import encabezado_pagina
from ..componentes.layout import layout_principal
from ..componentes.toast_viewer import toast_viewer
from ..estado.estado_autenticacion import EstadoAutenticacion
from ..estado.estado_boveda import EstadoBoveda

COLOR_PRIMARIO = "#6366F1"
COLOR_FONDO_GLOBAL = "#F8F9FF"
COLOR_PRIMARIO_OSCURO = "#4338CA"
COLOR_TEXTO_TITULO = "#0F172A"
COLOR_TEXTO_SUAVE = "#1E293B"
COLOR_TEXTO_MUY_SUAVE = "#334155"
COLOR_BORDE = "#E2E8F0"
DEGRADADO_ICONO = "linear-gradient(135deg, #6366F1 0%, #7C3AED 100%)"


def valor_a_string(v):
    try:
        if hasattr(v, "to"):
            return v.to(str)
    except Exception:
        pass
    try:
        if v is None:
            return "0"
        return str(v)
    except Exception:
        return ""


# ════════════════════════════════════════════════════════════
#  COMPONENTE: TARJETA DE TRABAJO DE GRADO
# ════════════════════════════════════════════════════════════


def tarjeta_trabajo_de_grado(tesis: rx.Var[dict]) -> rx.Component:
    """Card individual con datos de un trabajo de grado registrado."""

    # Avatar con gradiente moderno
    avatar = rx.center(
        rx.text(
            (tesis["nombre_estudiante"].to(str) + " " + tesis["apellido_estudiante"].to(str))[0],
            font_size={"initial": "1.4rem", "sm": "1.6rem"},
            font_weight="800",
            color="white",
            text_transform="uppercase"
        ),
        width={"initial": "3.5rem", "sm": "4rem"},
        height={"initial": "3.5rem", "sm": "4rem"},
        border_radius="1rem",
        background=DEGRADADO_ICONO,
        box_shadow="0 4px 12px rgba(99,102,241,0.3)",
        flex_shrink="0",
    )

    # Título con mejor tipografía
    titulo = rx.text(
        tesis["titulo"].to(str),
        font_size={"initial": "1rem", "sm": "1.1rem"},
        font_weight="700",
        color=COLOR_TEXTO_TITULO,
        line_height="1.4",
        no_of_lines=2,
        style={"whiteSpace": "normal"},
    )

    # Información del estudiante
    info_estudiante = rx.vstack(
        rx.hstack(
            rx.icon("user", size=16, color=COLOR_PRIMARIO),
            rx.text(
                tesis["nombre_estudiante"].to(str) + " " + tesis["apellido_estudiante"].to(str),
                font_size={"initial": "0.95rem", "sm": "1rem"},
                font_weight="600",
                color=COLOR_TEXTO_TITULO
            ),
            spacing="2",
            align="center"
        ),
        rx.hstack(
            rx.icon("calendar", size=14, color=COLOR_TEXTO_MUY_SUAVE),
            rx.text(
                rx.cond(tesis.get("fecha_registro_formateada") != "", tesis["fecha_registro_formateada"].to(str), ""),
                font_size="0.8rem",
                color=COLOR_TEXTO_MUY_SUAVE,
                font_weight="500"
            ),
            spacing="2",
            align="center"
        ),
        spacing="1",
        align="start"
    )

    # Badges de información
    badges_info = rx.hstack(
        rx.badge(
            tesis["carrera"].to(str),
            variant="soft",
            color_scheme="indigo",
            radius="full"
        ),
        rx.cond(
            tesis["publico"].to(bool),
            rx.badge("Pública", variant="soft", color_scheme="green", radius="full"),
            rx.badge("Privada", variant="soft", color_scheme="gray", radius="full")
        ),
        rx.badge("PDF", variant="solid", color_scheme="indigo", radius="full"),
        spacing="2",
        wrap="wrap"
    )

    # Información de tutores y empresa
    info_meta = rx.grid(
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("graduation-cap", size=16, color=COLOR_PRIMARIO),
                    rx.text("Tutor Académico", font_size="0.7rem", color=COLOR_TEXTO_MUY_SUAVE, font_weight="600", text_transform="uppercase"),
                    spacing="1",
                    align="center"
                ),
                rx.text(
                    tesis["tutor_academico"].to(str),
                    font_size="0.9rem",
                    font_weight="600",
                    color=COLOR_TEXTO_TITULO,
                    no_of_lines=1
                ),
                spacing="1",
                align="start"
            ),
            padding="1rem",
            background="rgba(99,102,241,0.05)",
            border_radius="0.75rem",
            border="1px solid rgba(99,102,241,0.1)"
        ),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("briefcase", size=16, color="#10B981"),
                    rx.text("Tutor Empresa", font_size="0.7rem", color=COLOR_TEXTO_MUY_SUAVE, font_weight="600", text_transform="uppercase"),
                    spacing="1",
                    align="center"
                ),
                rx.text(
                    tesis["tutor_empresa"].to(str),
                    font_size="0.9rem",
                    font_weight="600",
                    color=COLOR_TEXTO_TITULO,
                    no_of_lines=1
                ),
                spacing="1",
                align="start"
            ),
            padding="1rem",
            background="rgba(16,185,129,0.05)",
            border_radius="0.75rem",
            border="1px solid rgba(16,185,129,0.1)"
        ),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("building", size=16, color="#F59E0B"),
                    rx.text("Empresa", font_size="0.7rem", color=COLOR_TEXTO_MUY_SUAVE, font_weight="600", text_transform="uppercase"),
                    spacing="1",
                    align="center"
                ),
                rx.text(
                    tesis["nombre_empresa"].to(str),
                    font_size="0.9rem",
                    font_weight="600",
                    color=COLOR_TEXTO_TITULO,
                    no_of_lines=1
                ),
                spacing="1",
                align="start"
            ),
            padding="1rem",
            background="rgba(245,158,11,0.05)",
            border_radius="0.75rem",
            border="1px solid rgba(245,158,11,0.1)"
        ),
        columns={"initial": "1", "sm": "3"},
        spacing="3",
        width="100%"
    )

    # Botones de acción
    acciones = rx.cond(
        EstadoAutenticacion.rol_usuario == "administrador",
        # Layout para administrador: 3 botones en grid
        rx.grid(
                rx.link(
                    rx.button(
                        rx.hstack(
                            rx.icon("eye", size=16),
                            rx.text("Visualizar", font_weight="600", font_size="0.85rem"),
                            spacing="2",
                            align="center"
                        ),
                        variant="solid",
                        size="3",
                        color_scheme="indigo",
                        style={
                            "width": "100%",
                            "border_radius": "0.875rem",
                            "height": "2.5rem",
                            "background": "linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)",
                            "box_shadow": "0 4px 6px -1px rgba(99, 102, 241, 0.2)",
                            "transition": "all 0.2s ease"
                        },
                        _hover={
                            "background": "linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)",
                            "box_shadow": "0 6px 8px -1px rgba(99, 102, 241, 0.3)",
                            "transform": "translateY(-1px)"
                        }
                    ),
                    href=rx.cond(tesis["url"].to(str) != "", tesis["url"].to(str) + "#toolbar=0", "#"),
                    target="_blank",
                    rel="noopener noreferrer",
                    style={"text_decoration": "none", "width": "100%"}
                ),
            rx.button(
                rx.hstack(
                    rx.icon("download", size=16),
                    rx.text("Descargar", font_weight="600", font_size="0.85rem"),
                    spacing="2",
                    align="center"
                ),
                variant="solid",
                size="3",
                color_scheme="green",
                style={
                    "width": "100%",
                    "border_radius": "0.875rem",
                    "height": "2.5rem",
                    "background": "linear-gradient(135deg, #10B981 0%, #059669 100%)",
                    "box_shadow": "0 4px 6px -1px rgba(16, 185, 129, 0.2)",
                    "transition": "all 0.2s ease"
                },
                _hover={
                    "background": "linear-gradient(135deg, #059669 0%, #047857 100%)",
                    "box_shadow": "0 6px 8px -1px rgba(16, 185, 129, 0.3)",
                    "transform": "translateY(-1px)"
                },
                on_click=rx.download(url=tesis["url"].to(str), filename="TrabajoDeGrado_" + tesis["cedula_estudiante"].to(str) + ".pdf")
            ),
            rx.button(
                rx.hstack(
                    rx.icon("trash-2", size=16),
                    rx.text("Eliminar", font_weight="600", font_size="0.85rem"),
                    spacing="2",
                    align="center"
                ),
                variant="solid",
                size="3",
                color_scheme="red",
                style={
                    "width": "100%",
                    "border_radius": "0.875rem",
                    "height": "2.5rem",
                    "background": "linear-gradient(135deg, #EF4444 0%, #DC2626 100%)",
                    "box_shadow": "0 4px 6px -1px rgba(239, 68, 68, 0.2)",
                    "transition": "all 0.2s ease"
                },
                _hover={
                    "background": "linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)",
                    "box_shadow": "0 6px 8px -1px rgba(239, 68, 68, 0.3)",
                    "transform": "translateY(-1px)"
                },
                on_click=lambda: EstadoBoveda.abrir_modal_confirmacion(tesis["id"].to(int))
            ),
            columns={"initial": "1", "sm": "3"},
            spacing="3",
            width="100%"
        ),
        # Layout para estudiante: verificar si es su propio trabajo
        rx.cond(
            tesis["usuario_id"].to(int) == EstadoAutenticacion.usuario_id,
            # Es su propio trabajo: 3 botones (Visualizar, Editar, Eliminar)
            rx.grid(
                rx.link(
                    rx.button(
                        rx.hstack(
                            rx.icon("eye", size=16),
                            rx.text("Visualizar", font_weight="600", font_size="0.85rem"),
                            spacing="2",
                            align="center"
                        ),
                        variant="solid",
                        size="3",
                        color_scheme="indigo",
                        style={
                            "width": "100%",
                            "border_radius": "0.875rem",
                            "height": "2.5rem",
                            "background": "linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)",
                            "box_shadow": "0 4px 6px -1px rgba(99, 102, 241, 0.2)",
                            "transition": "all 0.2s ease"
                        },
                        _hover={
                            "background": "linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)",
                            "box_shadow": "0 6px 8px -1px rgba(99, 102, 241, 0.3)",
                            "transform": "translateY(-1px)"
                        }
                    ),
                    href=rx.cond(tesis["url"].to(str) != "", tesis["url"].to(str) + "#toolbar=0", "#"),
                    target="_blank",
                    rel="noopener noreferrer",
                    style={"text_decoration": "none"}
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("pencil", size=16),
                        rx.text("Editar", font_weight="600", font_size="0.85rem"),
                        spacing="2",
                        align="center"
                    ),
                    variant="solid",
                    size="3",
                    color_scheme="amber",
                    style={
                        "width": "100%",
                        "border_radius": "0.875rem",
                        "height": "2.5rem",
                        "background": "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)",
                        "box_shadow": "0 4px 6px -1px rgba(245, 158, 11, 0.2)",
                        "transition": "all 0.2s ease"
                    },
                    _hover={
                        "background": "linear-gradient(135deg, #D97706 0%, #B45309 100%)",
                        "box_shadow": "0 6px 8px -1px rgba(245, 158, 11, 0.3)",
                        "transform": "translateY(-1px)"
                    },
                    on_click=lambda: EstadoBoveda.abrir_modal_edicion(tesis["id"].to(int))
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("trash-2", size=16),
                        rx.text("Eliminar", font_weight="600", font_size="0.85rem"),
                        spacing="2",
                        align="center"
                    ),
                    variant="solid",
                    size="3",
                    color_scheme="red",
                    style={
                        "width": "100%",
                        "border_radius": "0.875rem",
                        "height": "2.5rem",
                        "background": "linear-gradient(135deg, #EF4444 0%, #DC2626 100%)",
                        "box_shadow": "0 4px 6px -1px rgba(239, 68, 68, 0.2)",
                        "transition": "all 0.2s ease"
                    },
                    _hover={
                        "background": "linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)",
                        "box_shadow": "0 6px 8px -1px rgba(239, 68, 68, 0.3)",
                        "transform": "translateY(-1px)"
                    },
                    on_click=lambda: EstadoBoveda.abrir_modal_confirmacion(tesis["id"].to(int))
                ),
                columns={"initial": "1", "sm": "3"},
                spacing="3",
                width="100%"
            ),
            # No es su trabajo: solo visualizar
            rx.link(
                rx.button(
                    rx.hstack(
                        rx.icon("eye", size=16),
                        rx.text("Visualizar", font_weight="600", font_size="0.9rem"),
                        spacing="2",
                        align="center"
                    ),
                    variant="solid",
                    size="3",
                    color_scheme="indigo",
                    style={
                        "width": "100%",
                        "border_radius": "0.875rem",
                        "height": "2.75rem",
                        "background": "linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)",
                        "box_shadow": "0 4px 6px -1px rgba(99, 102, 241, 0.2)",
                        "transition": "all 0.2s ease"
                    },
                    _hover={
                        "background": "linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)",
                        "box_shadow": "0 6px 8px -1px rgba(99, 102, 241, 0.3)",
                        "transform": "translateY(-1px)"
                    }
                ),
                href=rx.cond(tesis["url"].to(str) != "", tesis["url"].to(str) + "#toolbar=0", "#"),
                target="_blank",
                rel="noopener noreferrer",
                is_external=True,
                style={"text_decoration": "none"}
            )
        )
    )

    return rx.box(
        rx.vstack(
            # Header con avatar e información principal
            rx.hstack(
                avatar,
                rx.vstack(
                    info_estudiante,
                    titulo,
                    badges_info,
                    spacing="3",
                    width="100%",
                    align="start"
                ),
                spacing="4",
                align="start",
                width="100%"
            ),
            # Separador
            rx.box(
                height="1px",
                width="100%",
                background="linear-gradient(90deg, transparent, rgba(99,102,241,0.2), transparent)",
                margin_y="2"
            ),
            # Información de tutores y empresa
            info_meta,
            # Botones de acción
            acciones,
            spacing="4",
            width="100%",
            align="start"
        ),
        padding="1.5rem",
        border_radius="1.25rem",
        background="white",
        border="1px solid " + COLOR_BORDE,
        box_shadow="0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)",
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": "0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)",
            "border_color": COLOR_PRIMARIO
        },
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        style={"position": "relative", "overflow": "hidden"}
    )


def estado_vacio_boveda() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.center(
                rx.icon(
                    "book-open",
                    size=48,
                    color="rgba(99,102,241,0.35)",
                    stroke_width=1.3,
                ),
                width="6rem",
                height="6rem",
                border_radius="1.5rem",
                background="rgba(99,102,241,0.06)",
                border="0.09375rem dashed rgba(99,102,241,0.22)",
            ),
            rx.vstack(
                rx.text(
                    "La bóveda está vacía",
                    font_size="1.0625rem",
                    font_weight="700",
                    color="#334155",
                    text_align="center",
                ),
                rx.text(
                    "Registra el primer trabajo de grado usando el botón de arriba.",
                    font_size="0.84375rem",
                    color=COLOR_TEXTO_MUY_SUAVE,
                    text_align="center",
                ),
                spacing="1",
                align="center",
            ),
            width="100%",
            spacing="4",
            align="center",
            padding_bottom="0.625rem",
            direction={"initial": "column", "md": "row"},
        ),
        padding_y="5rem",
        width="100%",
    )


def seccion_modal(icono: str, titulo: str, *contenido, **estilos) -> rx.Component:
    # Definir valores por defecto y permitir sobrescritura desde **estilos
    # para evitar duplicidad
    estilos.setdefault("spacing", "4")
    estilos.setdefault("width", "100%")
    estilos.setdefault("padding", "1.375rem")
    estilos.setdefault("border_radius", "0.875rem")
    estilos.setdefault("background", "white")
    estilos.setdefault("border", f"0.09375rem solid {COLOR_BORDE}")
    estilos.setdefault("border_left", f"0.25rem solid {COLOR_PRIMARIO}")
    estilos.setdefault("box_shadow", "0 0.125rem 0.25rem rgba(0,0,0,0.02)")

    return rx.vstack(
        rx.hstack(
            rx.center(
                rx.icon(icono, size=13, stroke_width=2, color="white"),
                width="1.625rem",
                height="1.625rem",
                border_radius="0.4375rem",
                background=DEGRADADO_ICONO,
                flex_shrink="0",
            ),
            rx.text(
                titulo,
                font_size="0.6875rem",
                font_weight="700",
                color=COLOR_TEXTO_SUAVE,
                letter_spacing="0.07em",
                text_transform="uppercase",
            ),
            rx.box(
                flex="1",
                height="0.0625rem",
                background="linear-gradient(90deg, rgba(99,102,241,0.20), transparent)",
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        *contenido,
        **estilos,
    )


def modal_nuevo_trabajo_de_grado() -> rx.Component:
    return rx.cond(
        EstadoBoveda.mostrar_modal,
        rx.box(
            rx.box(
                position="fixed",
                top="0",
                left="0",
                width="100vw",
                height="100vh",
                background="rgba(10,10,30,0.55)",
                backdrop_filter="blur(0.1875rem)",
                z_index="100",
                on_click=EstadoBoveda.cerrar_modal,
            ),
            rx.center(
                rx.vstack(
                    rx.hstack(
                        rx.center(
                            rx.icon(
                                "book-plus", size=20, stroke_width=1.8, color="white"
                            ),
                            width="2.75rem",
                            height="2.75rem",
                            border_radius="0.8125rem",
                            background=DEGRADADO_ICONO,
                            box_shadow="0 0.25rem 0.875rem rgba(99,102,241,0.35)",
                            flex_shrink="0",
                        ),
                        rx.vstack(
                            rx.text(
                                rx.cond(
                                    EstadoBoveda.en_edicion,
                                    "Editar Trabajo de Grado",
                                    "Registrar Nuevo Trabajo de Grado",
                                ),
                                font_size="1.125rem",
                                font_weight="800",
                                color=COLOR_TEXTO_TITULO,
                                letter_spacing="-0.01875rem",
                            ),
                            rx.text(
                                rx.cond(
                                    EstadoBoveda.en_edicion,
                                    "Actualice la información del trabajo de grado.",
                                    "Ingrese la cédula para vincular al autor.",
                                ),
                                font_size="0.78125rem",
                                color=COLOR_TEXTO_SUAVE,
                            ),
                            spacing="0",
                            align="start",
                        ),
                        rx.spacer(),
                        rx.icon_button(
                            rx.icon("x", size=15, stroke_width=2),
                            variant="ghost",
                            color_scheme="gray",
                            size="2",
                            border_radius="0.5625rem",
                            cursor="pointer",
                            on_click=EstadoBoveda.cerrar_modal,
                            _hover={
                                "background": "rgba(239,68,68,0.10)",
                                "color": "#EF4444",
                            },
                            transition="all 0.15s ease",
                        ),
                        align="center",
                        spacing="4",
                        width="100%",
                        padding_bottom="1.125rem",
                        border_bottom="1px solid " + COLOR_BORDE,
                    ),
                    # ÁREA DESPLAZABLE DEL FORMULARIO
                    rx.vstack(
                        rx.flex(
                            rx.box(
                                rx.icon(
                                    "search",
                                    size=15,
                                    color="#475569",
                                    stroke_width=2,
                                    position="absolute",
                                    left="0.8125rem",
                                    top="50%",
                                    transform="translateY(-50%)",
                                    z_index="1",
                                    pointer_events="none",
                                ),
                                rx.input(
                                    on_change=EstadoBoveda.fijar_cedula_busqueda,
                                    value=EstadoBoveda.cedula_busqueda,
                                    placeholder="Cédula del estudiante...",
                                    size="3",
                                    variant="classic",
                                    width="100%",
                                    radius="large",
                                    style={
                                        "padding_left": "2.625rem",
                                        "padding_right": "0.625rem",
                                        "background_color": "white",
                                        "border": "0.09375rem solid #CBD5E1",
                                        "color": "black",
                                        "font_size": "0.84375rem",
                                        "font_weight": "bold",
                                        "&::placeholder": {
                                            "color": "#94A3B8",
                                            "opacity": "0.85",
                                            "font_weight": "500",
                                            "letter_spacing": "0.01em",
                                        },
                                    },
                                    _focus={
                                        "border_color": COLOR_PRIMARIO,
                                        "box_shadow": "0 0 0 0.1875rem rgba(99,102,241,0.15)",
                                        "outline": "none",
                                    },
                                    _hover={"border_color": "#A5B4FC"},
                                    transition="border-color 0.15s ease",
                                ),
                                position="relative",
                                flex="1",
                            ),
                            rx.button(
                                rx.icon("search", size=15, stroke_width=2),
                                rx.text("Buscar", font_weight="600"),
                                on_click=EstadoBoveda.buscar_estudiante,
                                size="3",
                                radius="large",
                                color_scheme="indigo",
                                cursor="pointer",
                                background=DEGRADADO_ICONO,
                                box_shadow="0 0.1875rem 0.625rem rgba(99,102,241,0.25)",
                                _hover={
                                    "box_shadow": "0 0.3125rem 1rem rgba(99,102,241,0.35)"
                                },
                                transition="all 0.15s ease",
                            ),
                            width="100%",
                            spacing="3",
                            align="center",
                            direction="row",
                        ),
                        rx.grid(
                            # COLUMNA IZQUIERDA: Datos del Estudiante
                            seccion_modal(
                                "user",
                                "Autor",
                                rx.vstack(
                                    campo_texto(
                                        "Nombre Completo",
                                        EstadoBoveda.nombre_encontrado
                                        + " "
                                        + EstadoBoveda.apellido_encontrado,
                                        None,
                                        solo_lectura=True,
                                    ),
                                    campo_texto(
                                        "Carrera",
                                        EstadoBoveda.carrera_encontrada,
                                        None,
                                        solo_lectura=True,
                                    ),
                                    campo_texto(
                                        "Tutor Académico",
                                        EstadoBoveda.tutor_academico_encontrado,
                                        None,
                                        solo_lectura=True,
                                    ),
                                    campo_texto(
                                        "Empresa",
                                        EstadoBoveda.empresa_encontrada,
                                        None,
                                        solo_lectura=True,
                                    ),
                                    spacing="3",
                                    width="100%",
                                ),
                                height="100%",
                            ),
                            # COLUMNA DERECHA: Detalles
                            seccion_modal(
                                "file-text",
                                "Trabajo de Grado",
                                rx.vstack(
                                    rx.text(
                                        "Título del Trabajo de Grado",
                                        font_size="0.8125rem",
                                        font_weight="600",
                                        color=COLOR_TEXTO_TITULO,
                                    ),
                                    rx.text_area(
                                        placeholder="Ingrese el título completo...",
                                        on_change=EstadoBoveda.fijar_titulo_trabajo_de_grado,
                                        value=EstadoBoveda.titulo_trabajo_de_grado,
                                        width="100%",
                                        style={
                                            "min_height": "7.8125rem",
                                            "border": "1.5px solid #CBD5E1",
                                            "font_size": "0.84375rem",
                                            "resize": "none",
                                            "color": "black",
                                            "&::placeholder": {
                                                "color": "#94A3B8",
                                                "opacity": "0.85",
                                                "font_weight": "500",
                                                "letter_spacing": "0.01em",
                                            },
                                        },
                                    ),
                                    rx.hstack(
                                        rx.checkbox(
                                            on_change=EstadoBoveda.fijar_hacer_publico,
                                            checked=EstadoBoveda.hacer_publico,
                                            color_scheme="indigo",
                                        ),
                                        rx.text(
                                            "Hacer pública en la biblioteca digital",
                                            font_size="0.8125rem",
                                            font_weight="600",
                                        ),
                                        align="center",
                                        spacing="2",
                                        padding="0.75rem",
                                        bg="rgba(99,102,241,0.04)",
                                        border_radius="0.625rem",
                                        width="100%",
                                    ),
                                    spacing="3",
                                    width="100%",
                                ),
                                height="100%",
                            ),
                            columns={"initial": "1", "lg": "2"},
                            spacing="4",
                            width="100%",
                        ),
                        seccion_modal(
                            "upload",
                            "Archivo del Trabajo de Grado",
                            rx.cond(
                                rx.selected_files("upload_trabajo_de_grado"),
                                rx.hstack(
                                    rx.center(
                                        rx.icon(
                                            "file-check", size=24, color=COLOR_PRIMARIO
                                        ),
                                        width="3rem",
                                        height="3rem",
                                        background="rgba(99,102,241,0.1)",
                                        border_radius="0.625rem",
                                    ),
                                    rx.vstack(
                                        rx.foreach(
                                            rx.selected_files(
                                                "upload_trabajo_de_grado"
                                            ),
                                            lambda f: rx.text(
                                                f,
                                                font_weight="bold",
                                                size="3",
                                                color=COLOR_TEXTO_TITULO,
                                                no_of_lines=1,
                                            ),
                                        ),
                                        rx.text(
                                            "Nuevo archivo listo para subir",
                                            size="2",
                                            color=COLOR_TEXTO_SUAVE,
                                        ),
                                        spacing="0",
                                        align="start",
                                    ),
                                    rx.spacer(),
                                    rx.button(
                                        rx.icon("trash-2", size=16),
                                        "Quitar",
                                        on_click=rx.clear_selected_files(
                                            "upload_trabajo_de_grado"
                                        ),
                                        color_scheme="red",
                                        variant="soft",
                                        size="2",
                                        cursor="pointer",
                                    ),
                                    width="100%",
                                    padding="1rem",
                                    border=f"1.5px solid {COLOR_PRIMARIO}",
                                    border_radius="0.75rem",
                                    background="rgba(99,102,241,0.03)",
                                    align="center",
                                ),
                                rx.upload(
                                    rx.cond(
                                        EstadoBoveda.en_edicion
                                        & (EstadoBoveda.ruta_archivo_actual != ""),
                                        rx.hstack(
                                            rx.center(
                                                rx.icon(
                                                    "file-text",
                                                    size=24,
                                                    color=COLOR_PRIMARIO,
                                                ),
                                                width="3rem",
                                                height="3rem",
                                                background="rgba(99,102,241,0.1)",
                                                border_radius="0.625rem",
                                            ),
                                            rx.vstack(
                                                rx.text(
                                                    EstadoBoveda.ruta_archivo_actual.split(
                                                        "/"
                                                    )[
                                                        -1
                                                    ],
                                                    font_weight="bold",
                                                    size="3",
                                                    color=COLOR_TEXTO_TITULO,
                                                    no_of_lines=1,
                                                ),
                                                rx.text(
                                                    "Archivo actual (Haz clic para cambiar)",
                                                    size="2",
                                                    color=COLOR_TEXTO_SUAVE,
                                                ),
                                                spacing="0",
                                                align="start",
                                                flex="1",
                                            ),
                                            rx.icon(
                                                "upload",
                                                size=18,
                                                color=COLOR_PRIMARIO,
                                                opacity=0.6,
                                            ),
                                            width="100%",
                                            align="center",
                                            spacing="3",
                                        ),
                                        rx.vstack(
                                            rx.icon(
                                                "file-up", size=24, color="#94A3B8"
                                            ),
                                            rx.text(
                                                "Arrastra el PDF del trabajo de grado o haz clic",
                                                color="#64748B",
                                                font_size="0.8125rem",
                                            ),
                                            align="center",
                                            spacing="2",
                                        ),
                                    ),
                                    id="upload_trabajo_de_grado",
                                    border="0.125rem dashed #CBD5E1",
                                    padding="1.25rem",
                                    border_radius="0.75rem",
                                    background="#F8FAFC",
                                    width="100%",
                                    max_files=1,
                                    accept={"application/pdf": [".pdf"]},
                                    _hover={
                                        "border_color": COLOR_PRIMARIO,
                                        "background": "rgba(99,102,241,0.02)",
                                    },
                                    transition="all 0.2s ease",
                                    cursor="pointer",
                                ),
                            ),
                        ),
                        spacing="5",
                        max_height="60vh",
                        overflow_y="auto",
                        padding_right="0.625rem",
                        style={
                            "&::-webkit-scrollbar": {"width": "0.375rem"},
                            "&::-webkit-scrollbar-thumb": {
                                "background": "#CBD5E1",
                                "border-radius": "0.625rem",
                            },
                        },
                        width="100%",
                    ),
                    rx.flex(
                        rx.button(
                            rx.icon("ban", size=14, stroke_width=1.8),
                            rx.text("Cancelar", font_weight="600"),
                            on_click=EstadoBoveda.cerrar_modal,
                            variant="soft",
                            color_scheme="gray",
                            size="3",
                            radius="large",
                            cursor="pointer",
                            flex={"initial": "1", "sm": "none"},
                            style={
                                "color": "#0F172A",
                                "background_color": "#F1F5F9",
                                "border": "1.5px solid #94A3B8",
                                "font_weight": "700",
                            },
                            _hover={"background_color": "#E2E8F0"},
                            transition="all 0.15s ease",
                        ),
                        rx.button(
                            rx.icon("check", size=14, stroke_width=2),
                            rx.text(
                                rx.cond(
                                    EstadoBoveda.en_edicion,
                                    "Guardar Cambios",
                                    "Registrar Trabajo de Grado",
                                ),
                                font_weight="700",
                            ),
                            on_click=lambda: EstadoBoveda.manejar_subida_trabajo_de_grado(
                                rx.upload_files("upload_trabajo_de_grado")
                            ),
                            size="3",
                            radius="large",
                            flex={"initial": "1", "sm": "none"},
                            color_scheme="indigo",
                            cursor="pointer",
                            loading=EstadoBoveda.procesando,
                            background=DEGRADADO_ICONO,
                            box_shadow="0 0.25rem 0.875rem rgba(99,102,241,0.28)",
                            _hover={
                                "box_shadow": "0 0.375rem 1.25rem rgba(99,102,241,0.40)",
                                "transform": "translateY(-1px)",
                            },
                            transition="all 0.15s ease",
                        ),
                        spacing="3",
                        width="100%",
                        flex_direction="row",  # Siempre uno al lado del otro
                        justify="between",  # Distribución perfecta en móvil
                        padding_top="1.125rem",
                        border_top=f"0.0625rem solid {COLOR_BORDE}",
                    ),
                    spacing="5",
                    width="100%",
                    padding_bottom="0.3125rem",
                ),
                on_click=rx.stop_propagation,
                style={
                    "background": "white",
                    "border-radius": "1.375rem",
                    "padding": "2rem",
                    "width": "min(52rem, 96vw)",
                    "max-width": "96vw",
                    "z-index": "200",
                    "border": f"0.0625rem solid {COLOR_BORDE}",
                    "box_shadow": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                    "margin-y": "2.5rem",
                },
            ),
            display="flex",
            align_items="start",
            justify_content="center",
            position="fixed",
            inset="0",
            z_index="200",
            overflow_y="auto",
        ),
    )


def modal_confirmar_eliminacion_trabajo_de_grado() -> rx.Component:
    """Modal de seguridad para confirmar la eliminación de un trabajo de grado."""
    return rx.cond(
        EstadoBoveda.mostrar_modal_confirmacion,
        rx.box(
            rx.box(
                position="fixed",
                inset="0",
                bg="rgba(10,10,30,0.6)",
                backdrop_filter="blur(4px)",
                z_index="300",
                on_click=EstadoBoveda.cerrar_modal_confirmacion,
            ),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.center(
                            rx.icon(
                                "triangle-alert",
                                size=22,
                                color="white",
                                stroke_width=2.5,
                            ),
                            width="2.75rem",
                            height="2.75rem",
                            border_radius="0.75rem",
                            background="linear-gradient(135deg, #EF4444 0%, #B91C1C 100%)",
                            box_shadow="0 0.25rem 0.75rem rgba(239,68,68,0.3)",
                        ),
                        rx.vstack(
                            rx.text(
                                "Confirmar Eliminación",
                                size="4",
                                weight="bold",
                                color="#0F172A",
                            ),
                            rx.text(
                                "Esta acción es irreversible",
                                size="1",
                                color="#B91C1C",
                                font_weight="700",
                            ),
                            spacing="0",
                            align="start",
                        ),
                        width="100%",
                        align="center",
                        border_bottom="1px solid #E2E8F0",
                        padding_bottom="1rem",
                    ),
                    rx.text(
                        "Por motivos de seguridad, debe ingresar su contraseña para confirmar que desea eliminar permanentemente este trabajo de grado.",
                        size="2",
                        color="#334155",
                        line_height="1.5",
                    ),
                    rx.vstack(
                        rx.text(
                            "Su Contraseña", size="2", weight="bold", color="#1E293B"
                        ),
                        rx.input(
                            type="password",
                            placeholder="••••••••",
                            on_change=EstadoBoveda.fijar_password_confirmacion,
                            width="100%",
                            variant="classic",
                            size="3",
                            style={
                                "border": "1.5px solid #64748B",
                                "font_weight": "bold",
                                "&::placeholder": {
                                    "color": "#94A3B8",
                                    "opacity": "0.85",
                                    "font_weight": "500",
                                    "letter_spacing": "0.01em",
                                },
                            },
                        ),
                        width="100%",
                        spacing="2",
                        align="start",
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancelar",
                            on_click=EstadoBoveda.cerrar_modal_confirmacion,
                            variant="soft",
                            color_scheme="gray",
                            size="3",
                            cursor="pointer",
                        ),
                        rx.button(
                            "Eliminar Definitivamente",
                            on_click=EstadoBoveda.confirmar_eliminacion_trabajo_de_grado,
                            variant="solid",
                            color_scheme="red",
                            size="3",
                            cursor="pointer",
                        ),
                        justify="end",
                        width="100%",
                        spacing="3",
                        padding_top="0.75rem",
                    ),
                    spacing="5",
                    width="100%",
                ),
                padding="2rem",
                background="white",
                border_radius="1.25rem",
                width="min(32rem, 94vw)",
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                z_index="310",
                box_shadow="0 25px 50px -12px rgba(0,0,0,0.25)",
            ),
        ),
    )


def contenido_boveda() -> rx.Component:
    """Contenido interno de la bóveda de Trabajo de Grado."""
    return rx.vstack(
        encabezado_pagina(
            "Bóveda de Trabajo de Grado",
            "Registrar Nuevo Trabajo de Grado",
            EstadoBoveda.abrir_modal,
        ),
        # Barra de búsqueda dinámica
        rx.box(
            rx.icon(
                "search",
                size=16,
                color="#64748B",
                position="absolute",
                left="0.875rem",
                top="50%",
                transform="translateY(-50%)",
                z_index="1",
            ),
            rx.input(
                placeholder="Buscar por título, estudiante o cédula...",
                value=EstadoBoveda.busqueda_dinamica,
                on_change=EstadoBoveda.fijar_busqueda_dinamica,
                size="3",
                radius="large",
                variant="classic",
                style={
                    "padding_left": "2.625rem",
                    "background_color": "white",
                    "border": "1.5px solid #94A3B8",
                    "color": "#0F172A",
                    "font_size": "0.9375rem",
                    "font_weight": "500",
                    "&::placeholder": {
                        "color": "#94A3B8",
                        "opacity": "0.85",
                        "font_weight": "500",
                        "letter_spacing": "0.01em",
                    },
                },
                _focus={"border_color": "#6366F1"},
                _hover={"border_color": "#6366F1"},
                width="100%",
            ),
            position="relative",
            width=["100%", "100%", "34rem"],
            margin_bottom="0.5rem",
        ),
        rx.flex(  # Contenido de filtros y búsqueda
            rx.select(
                EstadoBoveda.opciones_carreras,
                placeholder="Todas las carreras",
                value=EstadoBoveda.filtro_carrera,
                on_change=EstadoBoveda.fijar_filtro_carrera,
                size="3",
                width={"initial": "100%", "md": "15rem"},
                radius="large",
                variant="classic",
                style={
                    "background_color": "#F8FAFC",
                    "color": "#0F172A",
                    "border": "1.5px solid #64748B",
                    "font_size": "0.9375rem",
                    "font_weight": "600",
                    "cursor": "pointer",
                },
                _hover={"border_color": COLOR_PRIMARIO},
            ),
            rx.cond(
                (EstadoBoveda.busqueda_dinamica != "")
                | (EstadoBoveda.filtro_carrera != "")
                & (EstadoBoveda.filtro_carrera != "Todas las carreras"),
                rx.button(
                    rx.icon("rotate-ccw", size=14),
                    "Limpiar",
                    on_click=EstadoBoveda.limpiar_filtros,
                    variant="soft",
                    color_scheme="gray",
                    size="2",
                    cursor="pointer",
                ),
            ),
            rx.cond(
                EstadoAutenticacion.rol_usuario == "administrador",
                rx.button(
                    rx.icon("file-spreadsheet", size=14),
                    "Descargar Reporte",
                    on_click=EstadoBoveda.generar_reporte_trabajos_de_grado,
                    variant="soft",
                    color_scheme="green",
                    size="2",
                    cursor="pointer",
                ),
            ),
            rx.spacer(),
            rx.hstack(
                rx.center(
                    rx.icon(
                        "book-marked", size=14, color=COLOR_PRIMARIO, stroke_width=2
                    ),
                    width="1.75rem",
                    height="1.75rem",
                    border_radius="0.5rem",
                    background="white",
                    border=f"1px solid {COLOR_BORDE}",
                ),
                rx.vstack(
                    rx.heading(
                        valor_a_string(EstadoBoveda.total_trabajos_de_grado_count),
                        size="5",
                        weight="bold",
                        color=COLOR_TEXTO_SUAVE,
                    ),
                    rx.text(
                        rx.cond(
                            EstadoAutenticacion.rol_usuario == "administrador",
                            " resultados",
                            " disponibles",
                        ),
                        font_size="0.8125rem",
                        color=COLOR_TEXTO_SUAVE,
                    ),
                ),
                spacing="2",
                align="center",
            ),
            width="100%",
            spacing="4",
            align="center",
            padding_bottom="0.625rem",
            direction={"initial": "column", "md": "row"},
        ),
        rx.cond(
            EstadoBoveda.total_trabajos_de_grado_count == 0,
            estado_vacio_boveda(),
            rx.vstack(
                rx.grid(
                    rx.foreach(
                        EstadoBoveda.trabajos_de_grado_paginados,
                        tarjeta_trabajo_de_grado,
                    ),
                    columns={"initial": "1", "sm": "1", "md": "2", "lg": "2", "xl": "3"},
                    spacing={"initial": "3", "sm": "3", "md": "4", "lg": "4"},
                    width="100%",
                ),
                rx.cond(
                    EstadoBoveda.total_paginas > 1,
                    rx.box(
                        rx.hstack(
                            rx.button(
                                rx.icon("chevrons-left", size=14),
                                "Anterior",
                                on_click=EstadoBoveda.pagina_anterior,
                                variant="soft",
                                size="2",
                                disabled=EstadoBoveda.pagina_actual <= 1,
                                style={"border_radius": "999px", "padding": "0.55rem 0.95rem"},
                            ),
                            rx.hstack(
                                rx.foreach(
                                    EstadoBoveda.paginas_disponibles,
                                    lambda pagina: rx.button(
                                        valor_a_string(pagina),
                                        on_click=lambda pagina=pagina: EstadoBoveda.ir_a_pagina(pagina),
                                        variant=rx.cond(
                                            pagina == EstadoBoveda.pagina_actual,
                                            "solid",
                                            "soft",
                                        ),
                                        color_scheme=rx.cond(
                                            pagina == EstadoBoveda.pagina_actual,
                                            "indigo",
                                            "gray",
                                        ),
                                        size="2",
                                        style={"min_width": "2.2rem", "border_radius": "999px"},
                                    ),
                                ),
                                spacing="2",
                                wrap="wrap",
                            ),
                            rx.button(
                                "Siguiente",
                                rx.icon("chevrons-right", size=14),
                                on_click=EstadoBoveda.pagina_siguiente,
                                variant="solid",
                                size="2",
                                disabled=EstadoBoveda.pagina_actual >= EstadoBoveda.total_paginas,
                                style={"border_radius": "999px", "padding": "0.55rem 0.95rem"},
                            ),
                            justify="between",
                            width="100%",
                            align="center",
                            wrap="wrap",
                            spacing="3",
                        ),
                        padding="0.9rem 1rem",
                        border_radius="1rem",
                        background="rgba(248, 250, 252, 0.95)",
                        border="1px solid " + COLOR_BORDE,
                        width="100%",
                    ),
                ),
                width="100%",
                spacing="4",
            ),
        ),
        modal_nuevo_trabajo_de_grado(),
        modal_confirmar_eliminacion_trabajo_de_grado(),
        toast_viewer(),
        padding=["0.5rem", "0.75rem", "0.75rem", "0.75rem"],
        width="100%",
        spacing="3",
        align="start",
    )


def pagina_boveda() -> rx.Component:
    return rx.theme(
        rx.cond(
            EstadoAutenticacion.usuario,
            layout_principal(contenido_boveda()),
            rx.center(
                rx.spinner(size="3", color="indigo"),
                width="100vw",
                height="100vh",
                on_mount=[
                    EstadoAutenticacion.verificar_acceso,
                    EstadoBoveda.cargar_trabajos_de_grado,
                ],
            ),
        ),
        appearance="light",
        has_background=True,
    )
