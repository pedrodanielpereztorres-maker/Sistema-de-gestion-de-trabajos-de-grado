import reflex as rx
from ..componentes.encabezado import encabezado_pagina
from ..componentes.layout import layout_principal
from ..estado.estado_autenticacion import EstadoAutenticacion
from ..estado.estado_reportes import EstadoReportes
from ..estado.estado_estudiante import EstadoEstudiante
from datetime import datetime

# Paleta de colores del sistema
C_PRIMARIO = "#6366F1"  # Indigo
C_EXITO = "#10B981"  # Emerald
C_ADVERTENCIA = "#F59E0B"  # Amber
C_INFO = "#3B82F6"  # Blue
C_OSCURO = "#0F172A"
C_CUERPO = "#334155"
C_BORDE = "#E2E8F0"
C_FONDO_CARD = "rgba(255,255,255,0.85)"


def valor_a_string(v):
    try:
        if hasattr(v, "to"):
            return v.to(str)
    except Exception:
        pass
    try:
        return str(v)
    except Exception:
        return "0"


# KPI Card premium
def kpi_card(
    titulo: str, valor, descripcion: str, icono: str, color: str, gradiente: str
) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icono, size=22, color="white"),
                    padding="0.625rem",
                    border_radius="0.75rem",
                    background=gradiente,
                    box_shadow=f"0 4px 15px {color}55",
                ),
                rx.spacer(),
                rx.badge(
                    "● ACTIVO",
                    font_size="0.56rem",
                    letter_spacing="0.08em",
                    color=color,
                    background=f"{color}18",
                    border=f"1px solid {color}33",
                    border_radius="full",
                    padding="0.125rem 0.5rem",
                    font_weight="700",
                ),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.text(
                    titulo,
                    size="1",
                    weight="medium",
                    color=C_CUERPO,
                    letter_spacing="0.04em",
                ),
                rx.text(
                    valor_a_string(valor),
                    font_size="2.4rem",
                    font_weight="800",
                    color=C_OSCURO,
                    line_height="1",
                ),
                rx.text(descripcion, size="1", color="#94A3B8"),
                spacing="1",
                align="start",
            ),
            # Línea de acento inferior
            rx.box(
                height="3px", width="100%", background=gradiente, border_radius="full"
            ),
            spacing="4",
            width="100%",
        ),
        padding="1.25rem 1.5rem",
        background=C_FONDO_CARD,
        border=f"1px solid {color}22",
        border_radius="16px",
        box_shadow="0 2px 16px rgba(0,0,0,0.06)",
        backdrop_filter="blur(10px)",
        transition="transform 0.2s ease, box_shadow 0.2s ease",
        _hover={
            "transform": "translateY(-3px)",
            "box_shadow": f"0 8px 28px {color}22",
        },
        width="100%",
    )


# Tarjeta de exportación premium
def tarjeta_exportacion(
    titulo: str,
    desc: str,
    icono: str,
    color: str,
    gradiente: str,
    accion_excel=None,
    accion_pdf=None,
) -> rx.Component:
    botones = []
    if accion_excel:
        botones.append(
            rx.button(
                rx.hstack(
                    rx.icon("file-spreadsheet", size=13),
                    rx.text("Excel", size="2", weight="medium"),
                    spacing="1",
                    align="center",
                ),
                on_click=accion_excel,
                cursor="pointer",
                flex="1",
                size="2",
                border_radius="8px",
                background="#ECFDF5",
                color="#065F46",
                border="1px solid #6EE7B7",
                _hover={"background": "#D1FAE5", "border_color": "#34D399"},
                font_weight="600",
            )
        )
    if accion_pdf:
        botones.append(
            rx.button(
                rx.hstack(
                    rx.icon("file-text", size=13),
                    rx.text("PDF", size="2", weight="medium"),
                    spacing="1",
                    align="center",
                ),
                on_click=accion_pdf,
                cursor="pointer",
                flex="1",
                size="2",
                border_radius="8px",
                background="#FFF1F2",
                color="#881337",
                border="1px solid #FECDD3",
                _hover={"background": "#FFE4E6", "border_color": "#FB7185"},
                font_weight="600",
            )
        )

    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon(icono, size=20, color="white"),
                    padding="0.625rem",
                    border_radius="10px",
                    background=gradiente,
                    box_shadow=f"0 4px 12px {color}44",
                ),
                rx.vstack(
                    rx.text(titulo, weight="bold", size="3", color=C_OSCURO),
                    rx.text(desc, size="1", color="#64748B", line_height="1.4"),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),
            rx.hstack(*botones, spacing="2", width="100%"),
            spacing="4",
            align="start",
            width="100%",
        ),
        padding="1.125rem 1.25rem",
        background=C_FONDO_CARD,
        border=f"1.5px solid {color}22",
        border_radius="0.875rem",
        box_shadow="0 2px 12px rgba(0,0,0,0.05)",
        backdrop_filter="blur(8px)",
        transition="transform 0.2s ease, box-shadow 0.2s ease",
        _hover={"transform": "translateY(-2px)", "box_shadow": f"0 6px 24px {color}20"},
        width="100%",
    )


# Sección con encabezado visual
def seccion_reporte(
    titulo: str, descripcion: str, icono: str, contenido: rx.Component
) -> rx.Component:
    return rx.box(
        # Header de la sección
        rx.hstack(
            rx.hstack(
                rx.box(
                    rx.icon(icono, size=18, color="white"),
                    padding="0.5rem",
                    border_radius="8px",
                    background="linear-gradient(135deg, #6366F1, #8B5CF6)",
                    box_shadow="0 4px 10px #6366F155",
                ),
                rx.vstack(
                    rx.text(titulo, weight="bold", size="4", color=C_OSCURO),
                    rx.text(descripcion, size="1", color="#64748B"),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),
            rx.spacer(),
            rx.badge(
                f"Corte: {datetime.now().strftime('%d/%m/%Y')}",
                variant="outline",
                color_scheme="indigo",
                size="1",
                border_radius="full",
            ),
            width="100%",
            align="center",
            padding="1rem 1.25rem",
            border_bottom=f"1px solid {C_BORDE}",
        ),
        # Contenido
        rx.box(
            contenido,
            padding="1.25rem",
        ),
        background=C_FONDO_CARD,
        border=f"1px solid {C_BORDE}",
        border_radius="16px",
        box_shadow="0 2px 16px rgba(0,0,0,0.05)",
        backdrop_filter="blur(10px)",
        overflow="hidden",
        width="100%",
    )


# Fila de carrera con barra de progreso estilizada
def fila_carrera(item) -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.box(
                width="0.5rem",
                height="0.5rem",
                border_radius="full",
                background="linear-gradient(135deg, #6366F1, #8B5CF6)",
            ),
            rx.text(item["nombre"], size="2", color=C_CUERPO, weight="medium"),
            spacing="2",
            align="center",
            flex="1",
        ),
        rx.box(
            rx.box(
                height="100%",
                width=f"{item['progreso']}%",
                background="linear-gradient(90deg, #6366F1, #8B5CF6)",
                border_radius="full",
                transition="width 0.6s ease",
            ),
            width="45%",
            height="6px",
            background="#EEF2FF",
            border_radius="full",
            overflow="hidden",
        ),
        rx.text(
            valor_a_string(item.get("cantidad")),
            weight="bold",
            size="2",
            color=C_PRIMARIO,
            width="1.75rem",
            text_align="right",
        ),
        width="100%",
        align="center",
        key=item["nombre"],
        padding_y="0.625rem",
        border_bottom=f"1px solid {C_BORDE}",
    )


# Fila de tutor en el ranking
def fila_tutor(item, idx) -> rx.Component:
    colores_medalla = ["#F59E0B", "#94A3B8", "#CD7F32"]
    color_medalla = colores_medalla[idx] if idx < 3 else "#6366F1"

    return rx.hstack(
        rx.box(
            rx.text(
                str(idx + 1),
                font_size="11px",
                font_weight="800",
                color="white",
            ),
            width="1.5rem",
            height="1.5rem",
            border_radius="full",
            background=color_medalla,
            display="flex",
            align_items="center",
            justify_content="center",
            flex_shrink="0",
        ),
        rx.text(item["nombre"], size="2", color=C_CUERPO, flex="1"),
        rx.badge(
            valor_a_string(item.get("cantidad")) + " alumnos",
            color_scheme="indigo",
            variant="soft",
            border_radius="full",
        ),
        width="100%",
        align="center",
        padding_y="0.625rem",
        border_bottom=f"1px solid {C_BORDE}",
        spacing="3",
    )


# Tarjeta empresa en el ranking
def tarjeta_empresa(item) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("building-2", size=16, color=C_PRIMARIO),
                    padding="0.375rem",
                    background="#EEF2FF",
                    border_radius="8px",
                ),
                rx.text(
                    item["nombre"],
                    weight="bold",
                    size="2",
                    color=C_OSCURO,
                    overflow="hidden",
                    text_overflow="ellipsis",
                    white_space="nowrap",
                    flex="1",
                ),
                width="100%",
                align="center",
                spacing="2",
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon("mail", size=11, color="#94A3B8"),
                    rx.text(
                        rx.cond(item["correo"], item["correo"], "Sin correo"),
                        size="1",
                        color="#64748B",
                        font_style=rx.cond(item["correo"], "normal", "italic"),
                        overflow="hidden",
                        text_overflow="ellipsis",
                        white_space="nowrap",
                    ),
                    spacing="1",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("phone", size=11, color="#94A3B8"),
                    rx.text(
                        rx.cond(item["telefono"], item["telefono"], "Sin teléfono"),
                        size="1",
                        color="#64748B",
                        font_style=rx.cond(item["telefono"], "normal", "italic"),
                    ),
                    spacing="1",
                    align="center",
                ),
                spacing="1",
                align="start",
                width="100%",
            ),
            rx.hstack(
                rx.box(
                    rx.hstack(
                        rx.icon("users", size=12, color=C_PRIMARIO),
                        rx.text(
                            valor_a_string(item.get("cantidad")) + " pasantes",
                            size="1",
                            weight="bold",
                            color=C_PRIMARIO,
                        ),
                        spacing="1",
                        align="center",
                    ),
                    background="#EEF2FF",
                    padding="0.25rem 0.625rem",
                    border_radius="full",
                ),
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        padding="1rem",
        background=C_FONDO_CARD,
        border=f"1px solid {C_BORDE}",
        border_radius="12px",
        box_shadow="0 2px 8px rgba(0,0,0,0.04)",
        transition="transform 0.15s ease, box-shadow 0.15s ease",
        _hover={
            "transform": "translateY(-2px)",
            "box_shadow": "0 6px 20px rgba(99,102,241,0.12)",
        },
    )


# Contenido principal de la página
def contenido_reportes() -> rx.Component:
    return rx.box(
        # Fondo con gradiente decorativo sutil
        rx.box(
            position="fixed",
            top="0",
            left="0",
            right="0",
            bottom="0",
            background="radial-gradient(ellipse at 20% 20%, #EEF2FF 0%, transparent 50%), radial-gradient(ellipse at 80% 80%, #F0FDF4 0%, transparent 50%)",
            pointer_events="none",
            z_index="-1",
        ),
        rx.vstack(
            # Encabezado de página
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("bar-chart-3", size=20, color="white"),
                            padding="0.5rem",
                            border_radius="10px",
                            background="linear-gradient(135deg, #6366F1, #8B5CF6)",
                        ),
                        rx.heading(
                            "Analítica y Reportes",
                            size="7",
                            weight="bold",
                            color=C_OSCURO,
                        ),
                        spacing="3",
                        align="center",
                    ),
                    rx.text(
                        "Panel centralizado de métricas, estadísticas y exportación de documentos institucionales",
                        size="2",
                        color="#64748B",
                    ),
                    spacing="2",
                    align="start",
                ),
                rx.spacer(),
                rx.badge(
                    rx.hstack(
                        rx.box(
                            width="0.375rem",
                            height="0.375rem",
                            border_radius="full",
                            background=C_EXITO,
                        ),
                        rx.text(
                            "Actualizado: ",
                            rx.text.span(datetime.now().strftime("%d/%m/%Y")),
                        ),
                        spacing="2",
                        align="center",
                    ),
                    variant="outline",
                    color_scheme="green",
                    size="2",
                    border_radius="full",
                    padding="0.375rem 0.875rem",
                ),
                width="100%",
                align="center",
                flex_wrap="wrap",
                gap="3",
            ),
            # KPI Cards
            rx.grid(
                kpi_card(
                    "Estudiantes Totales",
                    EstadoReportes.resumen_global.get("total_estudiantes"),
                    "Registrados y activos",
                    "users",
                    "#6366F1",
                    "linear-gradient(135deg, #6366F1, #8B5CF6)",
                ),
                kpi_card(
                    "En Pasantía",
                    EstadoReportes.resumen_global.get("con_pasantia"),
                    "Con tutor asignado",
                    "circle-check",
                    "#10B981",
                    "linear-gradient(135deg, #10B981, #059669)",
                ),
                kpi_card(
                    "Pendientes",
                    EstadoReportes.resumen_global.get("sin_pasantia"),
                    "Sin tutor asignado",
                    "clock",
                    "#F59E0B",
                    "linear-gradient(135deg, #F59E0B, #D97706)",
                ),
                kpi_card(
                    "Trabajos de Grado",
                    EstadoReportes.resumen_global.get("total_tesis"),
                    "En la bóveda académica",
                    "book-open",
                    "#3B82F6",
                    "linear-gradient(135deg, #3B82F6, #2563EB)",
                ),
                columns={"initial": "1", "sm": "2", "md": "4"},
                spacing="4",
                width="100%",
            ),
            # Centro de exportación
            seccion_reporte(
                "Centro de Exportación de Datos",
                "Genera reportes oficiales en formato Excel o PDF para trámites administrativos e institucionales.",
                "cloud-download",
                rx.grid(
                    tarjeta_exportacion(
                        "Empresas Aliadas",
                        "Listado detallado de entidades receptoras y su vinculación.",
                        "building",
                        "#10B981",
                        "linear-gradient(135deg, #10B981, #059669)",
                        accion_excel=EstadoReportes.exportar_empresas_excel,
                        accion_pdf=EstadoReportes.exportar_empresas_pdf,
                    ),
                    tarjeta_exportacion(
                        "Estudiantes",
                        "Estado actual, tutores y períodos de todos los alumnos.",
                        "graduation-cap",
                        "#6366F1",
                        "linear-gradient(135deg, #6366F1, #8B5CF6)",
                        accion_excel=EstadoEstudiante.generar_reporte_estudiantes,
                        accion_pdf=EstadoEstudiante.exportar_estudiantes_pdf,
                    ),
                    tarjeta_exportacion(
                        "Bóveda de Tesis",
                        "Registro completo de trabajos de grado del sistema.",
                        "library",
                        "#F59E0B",
                        "linear-gradient(135deg, #F59E0B, #D97706)",
                        accion_excel=EstadoReportes.exportar_tesis_excel,
                        accion_pdf=EstadoReportes.exportar_tesis_pdf,
                    ),
                    columns={"initial": "1", "sm": "2", "md": "3"},
                    spacing="4",
                    width="100%",
                ),
            ),
            # Carreras y Tutores
            rx.grid(
                seccion_reporte(
                    "Distribución por Carrera",
                    "Volumen de estudiantes activos por programa académico.",
                    "graduation-cap",
                    rx.vstack(
                        rx.foreach(
                            EstadoReportes.estadisticas_carreras,
                            fila_carrera,
                        ),
                        width="100%",
                        spacing="0",
                    ),
                ),
                seccion_reporte(
                    "Top 5 Tutores Académicos",
                    "Ranking por carga de tutorías en el período vigente.",
                    "user-check",
                    rx.vstack(
                        rx.foreach(
                            EstadoReportes.mejores_tutores,
                            lambda item: rx.hstack(
                                rx.center(
                                    rx.icon("user", size=13, color=C_PRIMARIO),
                                    width="1.75rem",
                                    height="1.75rem",
                                    background="#EEF2FF",
                                    border_radius="full",
                                    flex_shrink="0",
                                ),
                                rx.text(
                                    item["nombre"], size="2", color=C_CUERPO, flex="1"
                                ),
                                rx.badge(
                                    valor_a_string(item.get("cantidad")) + " alumnos",
                                    color_scheme="indigo",
                                    variant="soft",
                                    border_radius="full",
                                ),
                                width="100%",
                                align="center",
                                padding_y="0.625rem",
                                border_bottom=f"1px solid {C_BORDE}",
                                spacing="3",
                            ),
                        ),
                        width="100%",
                        spacing="0",
                    ),
                ),
                columns={"initial": "1", "lg": "2"},
                spacing="6",
                width="100%",
            ),
            # Ranking Empresarial
            seccion_reporte(
                "Ranking de Vinculación Empresarial",
                "Entidades receptoras ordenadas por número de pasantes activos asignados.",
                "building-2",
                rx.grid(
                    rx.foreach(EstadoReportes.mejores_empresas, tarjeta_empresa),
                    columns={"initial": "1", "sm": "2", "md": "3", "lg": "4"},
                    spacing="4",
                    width="100%",
                ),
            ),
            padding=["1rem", "1.25rem", "1.75rem", "1.75rem"],
            width="100%",
            spacing="6",
            max_width="96vw",
            margin="0 auto",
        ),
        width="100%",
        min_height="100vh",
    )


def pagina_reportes() -> rx.Component:
    return rx.theme(
        rx.cond(
            EstadoAutenticacion.rol_usuario == "administrador",
            layout_principal(
                rx.box(
                    contenido_reportes(),
                    on_mount=EstadoReportes.cargar_reportes,
                )
            ),
            rx.center(
                rx.vstack(
                    rx.icon("lock", size=48, color="#CBD5E1"),
                    rx.heading("Acceso Denegado", size="6", color="#0F172A"),
                    rx.text(
                        "No tienes permisos para acceder a este módulo.",
                        color="#64748B",
                    ),
                    spacing="4",
                    align="center",
                ),
                width="100vw",
                height="100vh",
            ),
        ),
        appearance="light",
        has_background=True,
    )
