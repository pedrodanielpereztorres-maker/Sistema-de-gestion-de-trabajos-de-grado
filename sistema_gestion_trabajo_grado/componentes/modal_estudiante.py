from .campo_texto import campo_texto
from ..estado.estado_estudiante import EstadoEstudiante
import reflex as rx

COLOR_PRIMARIO = "#6366F1"
COLOR_PRIMARIO_OSCURO = "#4338CA"
COLOR_TEXTO_TITULO = "#0F172A"
COLOR_TEXTO_SECCION = "#475569"
COLOR_BORDE_SECCION = "#E2E8F0"
DEGRADADO_ICONO = "linear-gradient(135deg, #6366F1 0%, #7C3AED 100%)"


def encabezado_seccion(icono: str, titulo: str) -> rx.Component:
    return rx.hstack(
        rx.center(
            rx.icon(icono, size=14, stroke_width=2, color="white"),
            width="1.75rem",
            height="1.75rem",
            border_radius="0.5rem",
            background=DEGRADADO_ICONO,
            flex_shrink="0",
        ),
        rx.text(
            titulo,
            font_size="12px",
            font_weight="700",
            color=COLOR_TEXTO_TITULO,
            letter_spacing="0.06em",
            text_transform="uppercase",
        ),
        rx.box(
            flex="1",
            height="1px",
            background="linear-gradient(90deg, rgba(99,102,241,0.20), transparent)",
        ),
        align="center",
        spacing="3",
        width="100%",
    )


def bloque_seccion(icono: str, titulo: str, *contenido) -> rx.Component:
    return rx.vstack(
        encabezado_seccion(icono, titulo),
        *contenido,
        spacing="4",
        width="100%",
        padding="1.25rem",
        border_radius="0.875rem",
        background="white",
        border=f"1.5px solid {COLOR_BORDE_SECCION}",
        border_left=f"4px solid {COLOR_PRIMARIO}",
        box_shadow="0 1px 3px rgba(0,0,0,0.04)",
    )


def selector_carrera() -> rx.Component:
    return rx.vstack(
        rx.text(
            "Carrera",
            font_size="13px",
            font_weight="600",
            color=COLOR_TEXTO_TITULO,
        ),
        rx.select(
            EstadoEstudiante.carreras_disponibles,
            value=EstadoEstudiante.carrera,
            placeholder="Selecciona una carrera",
            on_change=[
                EstadoEstudiante.fijar_carrera,
                EstadoEstudiante.cargar_tutores_por_carrera,
            ],
            size="3",
            width="100%",
            radius="large",
            variant="classic",
            style={
                "background_color": "#F8FAFC",
                "color": "#0F172A",
                "border": "1.5px solid #64748B",
                "font_size": "15px",
                "font_weight": "600",
            },
        ),
        spacing="2",
        width="100%",
        align="start",
    )


def capa_oscura() -> rx.Component:
    return rx.box(
        position="fixed",
        top="0",
        width="100vw",
        height="100vh",
        background="rgba(10, 10, 30, 0.55)",
        backdrop_filter="blur(4px)",
        z_index="100",
        on_click=EstadoEstudiante.cerrar_modal,
    )


def cabecera_modal() -> rx.Component:
    return rx.hstack(
        rx.center(
            rx.icon("user-plus", size=20, stroke_width=1.8, color="white"),
            width="2.75rem",
            height="2.75rem",
            border_radius="0.8125rem",
            background=DEGRADADO_ICONO,
            box_shadow="0 4px 14px rgba(99,102,241,0.35)",
            flex_shrink="0",
        ),
        rx.vstack(
            rx.text(
                rx.cond(
                    EstadoEstudiante.en_edicion,
                    "Editar Estudiante",
                    "Registrar Estudiante",
                ),
                font_size="19px",
                font_weight="800",
                color=COLOR_TEXTO_TITULO,
                letter_spacing="-0.3px",
                line_height="1.2",
            ),
            rx.text(
                "Completa todos los campos para añadir un nuevo estudiante.",
                font_size="12.5px",
                font_weight="400",
                color=COLOR_TEXTO_SECCION,
            ),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.icon_button(
            rx.icon("x", size=16, stroke_width=2),
            variant="ghost",
            color_scheme="gray",
            size="2",
            border_radius="0.625rem",
            cursor="pointer",
            on_click=EstadoEstudiante.cerrar_modal,
            _hover={
                "background": "rgba(239,68,68,0.10)",
                "color": "#EF4444",
            },
            transition="all 0.15s ease",
        ),
        align="center",
        spacing="4",
        width="100%",
        padding_bottom="1.25rem",
        border_bottom=f"1px solid {COLOR_BORDE_SECCION}",
    )


def pie_modal() -> rx.Component:
    return rx.hstack(
        rx.button(
            rx.icon("circle-x", size=15, stroke_width=1.8),
            rx.text("Cancelar", font_weight="600"),
            on_click=EstadoEstudiante.cerrar_modal,
            variant="soft",
            color_scheme="gray",
            size="3",
            radius="large",
            cursor="pointer",
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
            rx.icon("user-check", size=15, stroke_width=2),
            rx.text(
                rx.cond(
                    EstadoEstudiante.en_edicion,
                    "Guardar Cambios",
                    "Registrar Estudiante",
                ),
                font_weight="700",
            ),
            on_click=EstadoEstudiante.guardar_estudiante,
            size="3",
            radius="large",
            variant="solid",
            color_scheme="indigo",
            cursor="pointer",
            background=DEGRADADO_ICONO,
            box_shadow="0 4px 14px rgba(99,102,241,0.30)",
            _hover={
                "box_shadow": "0 6px 20px rgba(99,102,241,0.40)",
                "transform": "translateY(-1px)",
            },
            transition="all 0.15s ease",
        ),
        justify="end",
        spacing="3",
        width="100%",
        padding_top="1.25rem",
        border_top=f"1px solid {COLOR_BORDE_SECCION}",
    )


def modal_registrar_estudiante() -> rx.Component:
    return rx.cond(
        EstadoEstudiante.mostrar_modal,
        rx.box(
            capa_oscura(),
            rx.center(
                rx.box(
                    rx.vstack(
                        cabecera_modal(),
                        bloque_seccion(
                            "user",
                            "Información Personal",
                            rx.grid(
                                rx.vstack(
                                    rx.text(
                                        "Cédula de Identidad",
                                        font_size="13px",
                                        font_weight="600",
                                        color=COLOR_TEXTO_TITULO,
                                    ),
                                    rx.input(
                                        value=EstadoEstudiante.cedula,
                                        on_change=EstadoEstudiante.fijar_cedula,
                                        on_blur=EstadoEstudiante.cargar_datos_usuario,
                                        type="text",
                                        size="3",
                                        width="100%",
                                        radius="large",
                                        read_only=rx.cond(
                                            EstadoEstudiante.en_edicion, True, False
                                        ),
                                        style={
                                            "background": "#FFFFFF",
                                            "border": "1.5px solid #CBD5E1",
                                            "color": "#0F172A",
                                            "font_size": "13.5px",
                                            "font_weight": "bold",
                                            "cursor": rx.cond(
                                                EstadoEstudiante.en_edicion,
                                                "not-allowed",
                                                "text",
                                            ),
                                            "&::placeholder": {
                                                "color": "#94A3B8",
                                                "opacity": "0.85",
                                                "font_weight": "500",
                                                "letter_spacing": "0.01em",
                                            },
                                        },
                                        placeholder="Cédula de Identidad",  # Add placeholder for clarity
                                        _focus={
                                            "border_color": "#6366F1",
                                            "box_shadow": "0 0 0 3px rgba(99,102,241,0.15)",
                                            "outline": "none",
                                        },
                                        _hover={"border_color": "#A5B4FC"},
                                        transition="border-color 0.15s ease, box-shadow 0.15s ease",
                                    ),
                                    spacing="2",
                                    width="100%",
                                    align="start",
                                ),
                                campo_texto(
                                    "Nombres",
                                    EstadoEstudiante.nombre,
                                    EstadoEstudiante.fijar_nombre,
                                    solo_lectura=EstadoEstudiante.usuario_encontrado,
                                ),
                                campo_texto(
                                    "Apellidos",
                                    EstadoEstudiante.apellido,
                                    EstadoEstudiante.fijar_apellido,
                                    solo_lectura=EstadoEstudiante.usuario_encontrado,
                                ),
                                campo_texto(
                                    "Correo Estudiante",
                                    EstadoEstudiante.correo,
                                    EstadoEstudiante.fijar_correo,
                                    solo_lectura=EstadoEstudiante.usuario_encontrado,
                                    tipo="email",
                                ),
                                campo_texto(
                                    "Teléfono Estudiante",
                                    EstadoEstudiante.telefono_personal,
                                    EstadoEstudiante.fijar_telefono_personal,
                                ),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                        ),
                        bloque_seccion(
                            "graduation-cap",
                            "Detalles Académicos",
                            rx.grid(
                                selector_carrera(),
                                campo_texto(
                                    "Período de Inicio",
                                    EstadoEstudiante.periodo_inicio,
                                    EstadoEstudiante.fijar_periodo_inicio,
                                    solo_lectura=EstadoEstudiante.en_edicion,
                                    tipo="date",
                                ),
                                campo_texto(
                                    "Período de Cierre",
                                    EstadoEstudiante.periodo_cierre,
                                    EstadoEstudiante.fijar_periodo_cierre,
                                    tipo="date",
                                ),
                                columns="3",
                                spacing="4",
                                width="100%",
                            ),
                            rx.hstack(
                                rx.checkbox(
                                    checked=EstadoEstudiante.haciendo_trabajo_de_grado,
                                    on_change=EstadoEstudiante.fijar_haciendo_trabajo_de_grado,
                                    color_scheme="indigo",
                                ),
                                rx.text(
                                    "El estudiante está realizando Pasantías",
                                    font_weight="800",
                                    color="#0F172A",
                                    font_size="13.5px",
                                ),
                                spacing="2",
                                align="center",
                                padding_y="0.5rem",
                            ),
                            rx.cond(
                                EstadoEstudiante.haciendo_trabajo_de_grado,
                                rx.vstack(
                                    rx.text(
                                        "Seleccionar Tutor Académico",
                                        font_size="13px",
                                        font_weight="600",
                                        color=COLOR_TEXTO_TITULO,
                                    ),
                                    rx.select(
                                        EstadoEstudiante.tutores_disponibles,
                                        value=EstadoEstudiante.tutor_academico_seleccionado,
                                        placeholder="Selecciona un tutor académico",
                                        on_change=EstadoEstudiante.fijar_tutor_academico_seleccionado,
                                        size="3",
                                        width="100%",
                                        radius="large",
                                        variant="classic",
                                        style={
                                            "background_color": "#F8FAFC",
                                            "color": "#0F172A",
                                            "border": "1.5px solid #64748B",
                                            "font_size": "15px",
                                            "font_weight": "600",
                                        },
                                    ),
                                    spacing="2",
                                    width="100%",
                                    align="start",
                                ),
                            ),
                        ),
                        bloque_seccion(
                            "building-2",
                            "Empresa / Prácticas",
                            rx.grid(
                                campo_texto(
                                    "Nombre de la Empresa",
                                    EstadoEstudiante.nombre_empresa,
                                    EstadoEstudiante.fijar_nombre_empresa,
                                ),
                                campo_texto(
                                    "Dirección de la Empresa",
                                    EstadoEstudiante.direccion_empresa,
                                    EstadoEstudiante.fijar_direccion_empresa,
                                ),
                                campo_texto(
                                    "Tutor Empresarial",
                                    EstadoEstudiante.tutor_empresa,
                                    EstadoEstudiante.fijar_tutor_empresa,
                                ),
                                campo_texto(
                                    "Correo de Contacto",
                                    EstadoEstudiante.correo_empresa,
                                    EstadoEstudiante.fijar_correo_empresa,
                                    tipo="email",
                                ),
                                campo_texto(
                                    "Teléfono",
                                    EstadoEstudiante.telefono_empresa,
                                    EstadoEstudiante.fijar_telefono_empresa,
                                    tipo="tel",
                                ),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                        ),
                        pie_modal(),
                        spacing="5",
                        width="100%",
                        padding_bottom="0.625rem",
                    ),
                    on_click=rx.stop_propagation,
                    background="white",
                    border_radius="1.5rem",
                    padding="2.25rem",
                    width="100%",
                    max_width="96vw",
                    max_height="95vh",
                    overflow_y="auto",
                    border=f"1px solid {COLOR_BORDE_SECCION}",
                    box_shadow="0 25px 50px -12px rgba(0,0,0,0.25)",
                ),
                position="fixed",
                top="0",
                left="0",
                width="100vw",
                height="100vh",
                z_index="200",
            ),
            key="modal-registrar-estudiante",
        ),
    )
