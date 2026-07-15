import reflex as rx

from ..componentes.encabezado import encabezado_pagina
from ..componentes.layout import layout_principal
from ..componentes.modal_estudiante import modal_registrar_estudiante
from ..componentes.tabla_estudiantes import tabla_estudiantes
from ..componentes.toast_viewer import toast_viewer
from ..estado.estado_autenticacion import EstadoAutenticacion
from ..estado.estado_estudiante import EstadoEstudiante


def modal_seguridad_estudiante() -> rx.Component:
    """Modal de seguridad para confirmar la desactivación de un estudiante."""
    return rx.cond(
        EstadoEstudiante.mostrar_modal_confirmacion,
        rx.box(
            # Fondo oscuro
            rx.box(
                position="fixed",
                inset="0",
                background="rgba(10, 10, 30, 0.6)",
                backdrop_filter="blur(4px)",
                z_index="400",
                on_click=EstadoEstudiante.cerrar_modal_confirmacion,
            ),
            # Panel central
            rx.box(
                rx.vstack(
                    # Cabecera con icono de advertencia
                    rx.hstack(
                        rx.center(
                            rx.icon(
                                "triangle-alert",
                                size=22,
                                color="white",
                                stroke_width=2.5,
                            ),
                            width="46px",
                            height="46px",
                            border_radius="13px",
                            background="linear-gradient(135deg, #EF4444 0%, #B91C1C 100%)",
                            box_shadow="0 4px 12px rgba(239,68,68,0.30)",
                            flex_shrink="0",
                        ),
                        rx.vstack(
                            rx.text(
                                "Desactivar Estudiante",
                                size="4",
                                weight="bold",
                                color="#0F172A",
                            ),
                            rx.text(
                                "Esta acción es reversible desde el panel de mantenimiento.",
                                size="1",
                                color="#B91C1C",
                                font_weight="600",
                            ),
                            spacing="0",
                            align="start",
                        ),
                        width="100%",
                        align="center",
                        spacing="3",
                        padding_bottom="16px",
                        border_bottom="1px solid #E2E8F0",
                    ),
                    # Descripción
                    rx.text(
                        "Esta acción desactivará al estudiante y su cuenta de acceso al sistema. "
                        "Para confirmar, ingrese su contraseña de administrador.",
                        size="2",
                        color="#334155",
                        line_height="1.6",
                    ),
                    # Campo contraseña
                    rx.vstack(
                        rx.text(
                            "Contraseña de Administrador",
                            size="2",
                            weight="bold",
                            color="#1E293B",
                        ),
                        rx.input(
                            type="password",
                            placeholder="••••••••",
                            on_change=EstadoEstudiante.fijar_password_confirmacion,
                            width="100%",
                            variant="classic",
                            size="3",
                            style={
                                "border": "1.5px solid #CBD5E1",
                                "border_radius": "10px",
                                "font_weight": "500",
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
                        ),
                        width="100%",
                        spacing="2",
                        align="start",
                    ),
                    # Acciones
                    rx.hstack(
                        rx.button(
                            rx.hstack(
                                rx.icon("x", size=14),
                                rx.text("Cancelar", font_weight="700"),
                                spacing="1",
                                align="center",
                            ),
                            on_click=EstadoEstudiante.cerrar_modal_confirmacion,
                            variant="soft",
                            color_scheme="gray",
                            size="3",
                            style={
                                "border": "1.5px solid #CBD5E1",
                                "border_radius": "10px",
                                "cursor": "pointer",
                            },
                            _hover={"background_color": "#F1F5F9"},
                        ),
                        rx.button(
                            rx.hstack(
                                rx.icon("user-x", size=14),
                                rx.text("Desactivar Estudiante", font_weight="700"),
                                spacing="1",
                                align="center",
                            ),
                            on_click=EstadoEstudiante.confirmar_eliminacion_estudiante,
                            variant="solid",
                            color_scheme="red",
                            size="3",
                            style={
                                "border_radius": "10px",
                                "cursor": "pointer",
                                "background": "linear-gradient(135deg, #EF4444 0%, #B91C1C 100%)",
                                "box_shadow": "0 4px 12px rgba(239,68,68,0.20)",
                            },
                            _hover={
                                "box_shadow": "0 6px 18px rgba(239,68,68,0.30)",
                                "transform": "translateY(-1px)",
                            },
                        ),
                        width="100%",
                        justify="end",
                        spacing="3",
                        padding_top="4px",
                    ),
                    spacing="5",
                ),
                on_click=rx.stop_propagation,
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                background="white",
                padding="32px",
                border_radius="20px",
                width="460px",
                max_width="94vw",
                z_index="410",
                box_shadow="0 25px 50px -12px rgba(0,0,0,0.20)",
                border="1px solid #E2E8F0",
            ),
        ),
        rx.fragment(),
    )


def contenido_estudiantes() -> rx.Component:
    """Contenido interno de la gestión de estudiantes con pasantías profesionales."""
    return rx.vstack(
        encabezado_pagina(
            "Estudiantes en Pasantías Profesionales",
            "Añadir Estudiante",
            EstadoEstudiante.abrir_modal,
        ),
        tabla_estudiantes(),
        modal_registrar_estudiante(),
        modal_seguridad_estudiante(),
        toast_viewer(),
        padding=["16px", "20px", "24px", "24px"],
        width="100%",
        min_width="0",
        spacing="5",
        on_mount=EstadoEstudiante.cargar_estudiantes,
    )


def pagina_estudiantes() -> rx.Component:
    return rx.theme(
        rx.cond(
            EstadoAutenticacion.usuario,
            layout_principal(contenido_estudiantes()),
            rx.center(
                rx.spinner(size="3", color="indigo"),
                width="100vw",
                height="100vh",
                background_color="#F8F9FF",
                on_mount=EstadoAutenticacion.verificar_acceso,
            ),
        ),
        appearance="light",
        has_background=True,
    )
