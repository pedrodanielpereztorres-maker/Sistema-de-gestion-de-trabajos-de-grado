import reflex as rx
from ..estado.estado_estudiante import EstadoEstudiante

# Valores rem fijos para tipografía y paddings

FS_HEADER = "0.75rem"  # cabeceras de columna
FS_BODY = "0.93rem"  # texto principal de celda
FS_SMALL = "0.78rem"  # texto secundario / badges
FS_BTN = "0.93rem"  # texto de botones

# Paddings fijos de celda
PAD_X = "0.75rem"
PAD_Y = "0.5rem"

# Constantes de diseño
COLOR_PRIMARIO = "#6366F1"
COLOR_VERDE = "#10B981"
COLOR_BORDE = "#E2E8F0"
COLOR_FONDO_FILA = "#F8FAFC"
GRAD_INDIGO = "linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)"


# Cabecera de columna
def celda_cabecera(texto: str, icono: str = "") -> rx.Component:
    """Cabecera con icono opcional. Nunca pasar icono vacío; usar celda_cabecera_simple en su lugar."""
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icono, size=14, color="#64748B"),
            rx.text(
                texto,
                style={
                    "font_size": FS_HEADER,
                    "font_weight": "700",
                    "color": "#475569",
                    "letter_spacing": "0.05em",
                    "text_transform": "uppercase",
                },
            ),
            spacing="1",
            align="center",
        ),
        style={"padding": f"{PAD_Y} {PAD_X}"},
        background="#F8FAFC",
        border_bottom=f"2px solid {COLOR_BORDE}",
        white_space="normal",
    )


def celda_cabecera_vacia() -> rx.Component:
    """Cabecera sin texto ni icono, para la columna del avatar."""
    return rx.table.column_header_cell(
        rx.box(),
        style={"padding": f"{PAD_Y} {PAD_X}"},
        background="#F8FAFC",
        border_bottom=f"2px solid {COLOR_BORDE}",
        width="3.25rem",
    )


# Fila de tabla
def fila_estudiante(estudiante) -> rx.Component:
    # Avatar con inicial
    inicial_cell = rx.table.cell(
        rx.center(
            rx.text(
                estudiante.inicial,
                style={
                    "font_size": "1rem",
                    "font_weight": "800",
                    "color": "white",
                    "text_transform": "uppercase",
                },
            ),
            width="2.375rem",
            height="2.375rem",
            border_radius="0.625rem",
            background=GRAD_INDIGO,
            box_shadow="0 2px 8px rgba(99,102,241,0.25)",
            flex_shrink="0",
        ),
        style={"padding": f"{PAD_Y} {PAD_X}"},
        white_space="normal",
    )

    # Nombre + cédula
    nombre_cell = rx.table.cell(
        rx.vstack(
            rx.hstack(
                rx.text(
                    estudiante.nombre,
                    style={
                        "font_size": "0.85rem",
                        "font_weight": "700",
                        "color": "#0F172A",
                        "white_space": "normal",
                    },
                    flex="1",
                ),
                rx.text(
                    estudiante.apellido,
                    style={
                        "font_size": "0.85rem",
                        "font_weight": "700",
                        "color": "#0F172A",
                        "white_space": "normal",
                    },
                    flex="1",
                ),
                spacing="1",
            ),
            rx.text(
                estudiante.cedula,
                style={
                    "font_size": "0.78rem",
                    "color": "#64748B",
                    "font_weight": "500",
                    "white_space": "normal",
                },
                flex="1",
            ),
            spacing="0",
            align="start",
        ),
        style={"padding": f"{PAD_Y} {PAD_X}"},
        white_space="normal",
    )

    # Badge de carrera
    carrera_cell = rx.table.cell(
        rx.badge(
            estudiante.carrera,
            variant="soft",
            color_scheme="indigo",
            radius="full",
            style={
                "font_size": "0.78rem",
                "font_weight": "700",
                "color": "#3730A3",
                "background_color": "#EEF2FF",
                "border": "1px solid #C7D2FE",
                "padding": "0.25rem 0.5rem",
            },
        ),
        style={"padding": f"{PAD_Y} {PAD_X}"},
        white_space="normal",
    )

    # Tutor académico + carrera
    tutor_cell = rx.table.cell(
        rx.cond(
            estudiante.nombre_tutor,
            rx.vstack(
                rx.hstack(
                    rx.icon("user-check", size=14, color=COLOR_VERDE),
                    rx.text(
                        estudiante.nombre_tutor,
                        style={
                            "font_size": "0.85rem",
                            "color": "#065F46",
                            "font_weight": "600",
                        },
                        flex="1",
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.text(
                    rx.cond(
                        estudiante.carrera_tutor,
                        estudiante.carrera_tutor,
                        "Carrera no asignada",
                    ),
                    style={
                        "font_size": "0.78rem",
                        "color": "#475569",
                        "font_weight": "500",
                        "white_space": "normal",
                    },
                    flex="1",
                ),
                spacing="1",
                align="start",
            ),
            rx.text("—", style={"color": "#CBD5E1", "font_size": FS_BODY}),
        ),
        py="2",
        px="1",
        white_space="normal",
    )

    # Botón empresa → tarjeta flotante
    empresa_cell = rx.table.cell(
        rx.cond(
            estudiante.nombre_empresa,
            rx.button(
                rx.hstack(
                    rx.icon("building-2", size=14),
                    rx.text(
                        estudiante.nombre_empresa,
                        style={
                            "font_size": "0.85rem",
                            "font_weight": "600",
                            "max_width": "10rem",
                            "white_space": "normal",
                        },
                        flex="1",
                    ),
                    spacing="1",
                    align="center",
                ),
                variant="soft",
                color_scheme="indigo",
                style={
                    "border_radius": "8px",
                    "cursor": "pointer",
                    "border": "1px solid #C7D2FE",
                    "background_color": "#EEF2FF",
                    "color": "#3730A3",
                    "transition": "all 0.18s ease",
                    "padding": "4px 8px",
                    "white_space": "normal",
                },
                _hover={"background_color": "#E0E7FF", "transform": "translateY(-1px)"},
                on_click=lambda _evt=None, e=estudiante: EstadoEstudiante.abrir_modal_empresa(
                    e.nombre_empresa,
                    e.direccion_empresa,
                    e.correo_empresa,
                    e.telefono_empresa,
                    e.tutor_empresa,
                ),
            ),
            rx.text("—", style={"color": "#CBD5E1", "font_size": FS_BODY}),
        ),
        style={"padding": f"{PAD_Y} {PAD_X}"},
    )

    # Fechas
    fecha_ini_cell = rx.table.cell(
        rx.hstack(
            rx.icon("calendar", size=14, color="#94A3B8"),
            rx.text(
                estudiante.fecha_inicio_formateada,
                style={
                    "font_size": "0.85rem",
                    "color": "#334155",
                    "font_weight": "500",
                    "white_space": "normal",
                },
            ),
            spacing="1",
            align="center",
        ),
        style={"padding": f"{PAD_Y} {PAD_X}"},
        white_space="normal",
    )

    fecha_fin_cell = rx.table.cell(
        rx.hstack(
            rx.icon("calendar-check", size=14, color=COLOR_VERDE),
            rx.text(
                estudiante.fecha_cierre_formateada,
                style={
                    "font_size": "0.85rem",
                    "color": "#065F46",
                    "font_weight": "500",
                    "white_space": "normal",
                },
            ),
            spacing="1",
            align="center",
        ),
        style={"padding": f"{PAD_Y} {PAD_X}"},
        white_space="normal",
    )

    # Botones Editar / Eliminar
    acciones_cell = rx.table.cell(
        rx.hstack(
            rx.button(
                rx.hstack(
                    rx.icon("pencil", size=14),
                    rx.text(
                        "Editar", style={"font_size": FS_BTN, "font_weight": "700"}
                    ),
                    spacing="1",
                    align="center",
                ),
                on_click=lambda _evt=None, e=estudiante: EstadoEstudiante.abrir_modal_edicion_estudiante(
                    e.cedula
                ),
                variant="soft",
                style={
                    "color": "#1E40AF",
                    "background_color": "#EFF6FF",
                    "border": "1px solid #BFDBFE",
                    "border_radius": "8px",
                    "cursor": "pointer",
                    "transition": "all 0.18s ease",
                    "padding": "6px 14px",
                },
                _hover={"background_color": "#DBEAFE", "transform": "translateY(-1px)"},
            ),
            rx.button(
                rx.hstack(
                    rx.icon("trash-2", size=14),
                    rx.text(
                        "Eliminar", style={"font_size": FS_BTN, "font_weight": "700"}
                    ),
                    spacing="1",
                    align="center",
                ),
                on_click=lambda _evt=None, e=estudiante: EstadoEstudiante.abrir_modal_confirmacion(
                    e.cedula
                ),
                variant="soft",
                style={
                    "color": "#991B1B",
                    "background_color": "#FEF2F2",
                    "border": "1px solid #FCA5A5",
                    "border_radius": "8px",
                    "cursor": "pointer",
                    "transition": "all 0.18s ease",
                    "padding": "6px 14px",
                },
                _hover={"background_color": "#FEE2E2", "transform": "translateY(-1px)"},
            ),
            spacing="2",
        ),
        style={"padding": f"{PAD_Y} {PAD_X}"},
    )

    return rx.table.row(
        inicial_cell,
        nombre_cell,
        carrera_cell,
        tutor_cell,
        empresa_cell,
        fecha_ini_cell,
        fecha_fin_cell,
        acciones_cell,
        key=rx.cond(
            getattr(estudiante, "cedula", None),
            estudiante.cedula,
            rx.cond(getattr(estudiante, "correo", None), estudiante.correo, ""),
        ),
        _hover={"background": "#F8FAFC"},
        transition="background 0.15s ease",
        border_bottom=f"1px solid {COLOR_BORDE}",
    )


# Tarjeta flotante de empresa (mejorada)
def tarjeta_empresa() -> rx.Component:
    def fila_dato(
        icono: str, etiqueta: str, valor, color_icono: str = "#6366F1"
    ) -> rx.Component:
        return rx.hstack(
            rx.center(
                rx.icon(icono, size=15, color=color_icono),
                width="1.75rem",
                height="1.75rem",
                border_radius="0.5rem",
                background="rgba(99,102,241,0.08)",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text(
                    etiqueta,
                    style={
                        "font_size": "0.72rem",
                        "font_weight": "700",
                        "color": "#64748B",
                        "text_transform": "uppercase",
                        "letter_spacing": "0.07em",
                    },
                ),
                rx.text(
                    rx.cond(valor, valor, "—"),
                    style={
                        "font_size": "0.93rem",
                        "font_weight": "600",
                        "color": "#0F172A",
                        "word_break": "break-word",
                    },
                ),
                spacing="0",
                align="start",
                flex="1",
            ),
            spacing="3",
            align="start",
            width="100%",
        )

    return rx.cond(
        EstadoEstudiante.empresa_modal_visible,
        rx.box(
            rx.box(
                position="fixed",
                inset="0",
                background="rgba(0,0,0,0.35)",
                backdrop_filter="blur(2px)",
                z_index="400",
                on_click=EstadoEstudiante.cerrar_modal_empresa,
            ),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.center(
                            rx.icon("building-2", size=20, color="white"),
                            width="2.75rem",
                            height="2.75rem",
                            border_radius="0.75rem",
                            background=GRAD_INDIGO,
                            box_shadow="0 4px 12px rgba(99,102,241,0.3)",
                            flex_shrink="0",
                        ),
                        rx.vstack(
                            rx.text(
                                "Ficha de Empresa",
                                style={
                                    "font_size": "1.05rem",
                                    "font_weight": "800",
                                    "color": "#0F172A",
                                    "letter_spacing": "-0.2px",
                                },
                            ),
                            rx.text(
                                "Información de contacto",
                                style={
                                    "font_size": "0.8rem",
                                    "color": "#64748B",
                                    "font_weight": "500",
                                },
                            ),
                            spacing="0",
                            align="start",
                        ),
                        rx.spacer(),
                        rx.icon_button(
                            rx.icon("x", size=15),
                            on_click=EstadoEstudiante.cerrar_modal_empresa,
                            variant="ghost",
                            color_scheme="gray",
                            size="2",
                            border_radius="9px",
                            cursor="pointer",
                            _hover={
                                "background": "rgba(239,68,68,0.08)",
                                "color": "#EF4444",
                            },
                        ),
                        width="100%",
                        align="center",
                        spacing="3",
                        padding_bottom="1rem",
                        border_bottom=f"1px solid {COLOR_BORDE}",
                    ),
                    rx.box(
                        rx.text(
                            rx.cond(
                                EstadoEstudiante.nombre_empresa,
                                EstadoEstudiante.nombre_empresa,
                                "—",
                            ),
                            style={
                                "font_size": "1.05rem",
                                "font_weight": "800",
                                "color": "#0F172A",
                                "text_align": "center",
                            },
                        ),
                        width="100%",
                        padding_y="0.75rem",
                        background="linear-gradient(135deg, rgba(99,102,241,0.05), rgba(139,92,246,0.04))",
                        border_radius="0.625rem",
                        border=f"1px solid {COLOR_BORDE}",
                        text_align="center",
                    ),
                    rx.vstack(
                        fila_dato(
                            "map-pin",
                            "Dirección",
                            EstadoEstudiante.direccion_empresa,
                            "#0EA5E9",
                        ),
                        fila_dato(
                            "mail",
                            "Correo Electrónico",
                            EstadoEstudiante.correo_empresa,
                            "#6366F1",
                        ),
                        fila_dato(
                            "phone",
                            "Teléfono",
                            EstadoEstudiante.telefono_empresa,
                            "#10B981",
                        ),
                        fila_dato(
                            "user-check",
                            "Tutor / Contacto",
                            EstadoEstudiante.tutor_empresa,
                            "#F59E0B",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon("x", size=14),
                            rx.text(
                                "Cerrar",
                                style={"font_weight": "700", "font_size": FS_BTN},
                            ),
                            spacing="1",
                            align="center",
                        ),
                        on_click=EstadoEstudiante.cerrar_modal_empresa,
                        width="100%",
                        size="2",
                        variant="soft",
                        color_scheme="gray",
                        style={
                            "border": f"1px solid {COLOR_BORDE}",
                            "border_radius": "10px",
                            "cursor": "pointer",
                            "margin_top": "4px",
                        },
                        _hover={"background_color": "#E2E8F0"},
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_click=rx.stop_propagation,
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                background="white",
                border_radius="1.25rem",
                padding="1.75rem",
                width="100%",
                max_width="38rem",
                z_index="410",
                box_shadow="0 25px 50px -12px rgba(0,0,0,0.20), 0 0 0 1px rgba(0,0,0,0.04)",
                border=f"1px solid {COLOR_BORDE}",
            ),
        ),
        rx.fragment(),
    )


# Tabla principal
def tabla_estudiantes() -> rx.Component:
    return rx.vstack(
        # Barra de búsqueda y filtros
        rx.box(
            rx.hstack(
                rx.box(
                    rx.icon(
                        "search",
                        size=16,
                        color="#64748B",
                        position="absolute",
                        left="14px",
                        top="50%",
                        transform="translateY(-50%)",
                        z_index="1",
                    ),
                    rx.input(
                        placeholder="Buscar por cédula, nombre o apellido...",
                        value=EstadoEstudiante.busqueda_dinamica,
                        on_change=EstadoEstudiante.fijar_busqueda_dinamica,
                        size="3",
                        variant="classic",
                        radius="large",
                        style={
                            "padding_left": "42px",
                            "background_color": "white",
                            "border": "1.5px solid #CBD5E1",
                            "color": "#0F172A",
                            "font_size": FS_BODY,
                            "&::placeholder": {
                                "color": "#94A3B8",
                                "opacity": "0.85",
                                "font_weight": "500",
                                "letter_spacing": "0.01em",
                            },
                        },
                        _focus={
                            "border_color": "#6366F1",
                            "box_shadow": "0 0 0 3px rgba(99,102,241,0.12)",
                        },
                        width="100%",
                    ),
                    position="relative",
                    flex="1",
                ),
                rx.select(
                    items=EstadoEstudiante.opciones_carreras,
                    value=EstadoEstudiante.filtro_carrera,
                    on_change=EstadoEstudiante.fijar_filtro_carrera,
                    placeholder="Todas las carreras",
                    size="3",
                    variant="classic",
                    radius="large",
                    style={
                        "background_color": "white",
                        "border": "1.5px solid #CBD5E1",
                        "color": "#0F172A",
                        "font_size": FS_BODY,
                        "cursor": "pointer",
                    },
                    _hover={"border_color": "#6366F1"},
                ),
                rx.cond(
                    (EstadoEstudiante.filtro_carrera != "")
                    | (EstadoEstudiante.busqueda_dinamica != ""),
                    rx.button(
                        rx.icon("rotate-ccw", size=14),
                        "Limpiar filtro",
                        variant="soft",
                        color_scheme="gray",
                        size="3",
                        on_click=EstadoEstudiante.limpiar_filtros,
                        style={
                            "border_radius": "0.75rem",
                            "font_weight": "700",
                        },
                    ),
                ),
                spacing="3",
                width="100%",
                align="center",
            ),
            padding="0.75rem 1rem",
            background="white",
            border_bottom=f"1px solid {COLOR_BORDE}",
            border_radius="1rem 1rem 0 0",
            width="100%",
            max_width="100%",
        ),
        # Tabla
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        celda_cabecera_vacia(),
                        celda_cabecera("Estudiante", "user"),
                        celda_cabecera("Carrera", "graduation-cap"),
                        celda_cabecera("Tutor Académico", "user-check"),
                        celda_cabecera("Empresa", "building-2"),
                        celda_cabecera("Inicio", "calendar"),
                        celda_cabecera("Cierre", "calendar-check"),
                        celda_cabecera("Acciones", "settings-2"),
                    )
                ),
                rx.table.body(
                    rx.foreach(EstadoEstudiante.estudiantes_filtrados, fila_estudiante)
                ),
                variant="ghost",
                width="100%",
                max_width="100%",
                # Font base para toda la tabla desde rem
                style={"font_size": FS_BODY, "table-layout": "auto"},
            ),
            width="100%",
            max_width="100%",
            overflow_x="hidden",
            background="white",
            style={
                "&::-webkit-scrollbar": {"height": "6px"},
                "&::-webkit-scrollbar-thumb": {
                    "background": "#CBD5E1",
                    "border_radius": "6px",
                },
            },
        ),
        # Paginación
        rx.box(
            rx.hstack(
                rx.button(
                    rx.hstack(
                        rx.icon("chevron-left", size=15),
                        rx.text(
                            "Anterior",
                            style={"font_size": FS_BTN, "font_weight": "600"},
                        ),
                        spacing="1",
                        align="center",
                    ),
                    on_click=EstadoEstudiante.pagina_anterior,
                    is_disabled=EstadoEstudiante.pagina_actual <= 1,
                    variant="soft",
                    color_scheme="gray",
                    size="2",
                    style={
                        "border": f"1px solid {COLOR_BORDE}",
                        "border_radius": "9px",
                    },
                    _hover={"background_color": "#E2E8F0"},
                ),
                rx.hstack(
                    rx.text(
                        "Página ",
                        rx.text.span(
                            EstadoEstudiante.pagina_actual.to(str),
                            style={"font_weight": "800", "color": "#6366F1"},
                        ),
                        " de ",
                        rx.text.span(
                            EstadoEstudiante.total_paginas.to(str),
                            style={"font_weight": "800"},
                        ),
                        style={"font_size": FS_BTN, "color": "#334155"},
                    ),
                    rx.badge(
                        EstadoEstudiante.total_registros.to(str) + " estudiantes",
                        variant="soft",
                        color_scheme="indigo",
                        radius="full",
                        style={"font_size": FS_SMALL, "font_weight": "700"},
                    ),
                    spacing="3",
                    align="center",
                ),
                rx.button(
                    rx.hstack(
                        rx.text(
                            "Siguiente",
                            style={"font_size": FS_BTN, "font_weight": "600"},
                        ),
                        rx.icon("chevron-right", size=15),
                        spacing="1",
                        align="center",
                    ),
                    on_click=EstadoEstudiante.pagina_siguiente,
                    is_disabled=EstadoEstudiante.pagina_actual
                    >= EstadoEstudiante.total_paginas,
                    variant="soft",
                    color_scheme="indigo",
                    size="2",
                    style={"border": "1px solid #C7D2FE", "border_radius": "9px"},
                    _hover={"background_color": "#EEF2FF"},
                ),
                justify="center",
                align="center",
                spacing="4",
                width="100%",
            ),
            padding="0.5rem 1rem",
            background=COLOR_FONDO_FILA,
            border_top=f"1px solid {COLOR_BORDE}",
            border_radius="0 0 16px 16px",
            width="100%",
            max_width="100%",
        ),
        # Tarjeta flotante de empresa
        tarjeta_empresa(),
        width="100%",
        max_width="100%",
        flex="1",
        flex_grow="1",
        min_width="0",
        background="white",
        border_radius="1rem",
        border=f"1px solid {COLOR_BORDE}",
        box_shadow="0 4px 6px -1px rgba(0,0,0,0.04)",
        overflow="visible",
        spacing="0",
    )
