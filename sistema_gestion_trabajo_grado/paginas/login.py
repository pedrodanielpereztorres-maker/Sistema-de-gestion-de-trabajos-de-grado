import reflex as rx
from ..estado.estado_autenticacion import EstadoAutenticacion
from ..componentes.toast_viewer import toast_viewer

COLOR_FONDO_GLOBAL = "white"


def pagina_login() -> rx.Component:
    """Genera la vista de Login con un diseño extremadamente premium, moderno y pulido."""
    return rx.theme(
        rx.box(
            rx.center(
                rx.card(
                    rx.vstack(
                        # Logo institucional centrado (sin fondo blanco)
                        rx.center(
                            rx.image(
                                src="/iutepi.png",
                                alt="Logo IUTEPI",
                                width=["260px", "300px", "320px"],
                                height=["100px", "110px", "120px"],
                                object_fit="contain",
                                background="transparent",
                                style={"backgroundColor": "transparent"},
                            ),
                            width="100%",
                            margin_bottom="2",
                        ),
                        # Cabecera / Títulos
                        rx.vstack(
                            rx.heading(
                                "Acceso al Portal",
                                size="7",
                                align="center",
                                weight="bold",
                                color="#0F172A",
                            ),
                            rx.text(
                                "Ingresa tus credenciales para acceder a la plataforma ",
                                rx.text.span("SGT", class_name="notranslate"),
                                color="#64748B",
                                size="2",
                                text_align="center",
                                font_weight="500",
                            ),
                            spacing="1",
                            align="center",
                            width="100%",
                            margin_bottom="4",
                        ),
                        # Input: Usuario
                        rx.vstack(
                            rx.text(
                                "Correo Electrónico",
                                size="2",
                                weight="bold",
                                color="#1E293B",
                            ),
                            rx.input(
                                placeholder="ejemplo@correo.com",
                                value=EstadoAutenticacion.entrada_usuario,
                                on_change=EstadoAutenticacion.fijar_entrada_usuario,
                                custom_attrs={
                                    "autoComplete": "username",
                                    "name": "username",
                                },
                                width="100%",
                                variant="classic",
                                size="3",
                                style={
                                    "background": "white",
                                    "border": "1.5px solid #CBD5E1",
                                    "color": "black",
                                    "font_size": "14px",
                                    "font_weight": "500",
                                    "border_radius": "12px",
                                    "box_shadow": "inset 0 1px 2px rgba(0, 0, 0, 0.02)",
                                    "&::placeholder": {
                                        "color": "#94A3B8",
                                        "opacity": "0.85",
                                        "font_weight": "500",
                                        "letter_spacing": "0.01em",
                                    },
                                    "letter_spacing": "0.01em",
                                },
                                _focus={
                                    "border_color": "#6366F1",
                                    "box_shadow": "0 0 0 3px rgba(99, 102, 241, 0.15)",
                                    "outline": "none",
                                },
                                _hover={"border_color": "#94A3B8"},
                            ),
                            width="100%",
                            align_items="start",
                            spacing="1",
                        ),
                        # Input: Contraseña
                        rx.vstack(
                            rx.text(
                                "Contraseña", size="2", weight="bold", color="#1E293B"
                            ),
                            rx.box(
                                rx.input(
                                    placeholder="••••••••",
                                    type=rx.cond(
                                        EstadoAutenticacion.mostrar_contrasena,
                                        "text",
                                        "password",
                                    ),
                                    value=EstadoAutenticacion.entrada_contrasena,
                                    on_change=EstadoAutenticacion.fijar_entrada_contrasena,
                                    custom_attrs={
                                        "autoComplete": "current-password",
                                        "name": "current-password",
                                    },
                                    width="100%",
                                    variant="classic",
                                    size="3",
                                    style={
                                        "background": "white",
                                        "border": "1.5px solid #CBD5E1",
                                        "color": "black",
                                        "font_size": "14px",
                                        "font_weight": "500",
                                        "border_radius": "12px",
                                        "padding_right": "45px",
                                        "box_shadow": "inset 0 1px 2px rgba(0, 0, 0, 0.02)",
                                        "&::placeholder": {
                                            "color": "#94A3B8",
                                            "opacity": "0.85",
                                            "font_weight": "500",
                                            "letter_spacing": "0.01em",
                                        },
                                        "letter_spacing": "0.01em",
                                    },
                                    _focus={
                                        "border_color": "#6366F1",
                                        "box_shadow": "0 0 0 3px rgba(99, 102, 241, 0.15)",
                                        "outline": "none",
                                    },
                                    _hover={"border_color": "#94A3B8"},
                                ),
                                rx.icon_button(
                                    rx.icon(
                                        rx.cond(
                                            EstadoAutenticacion.mostrar_contrasena,
                                            "eye-off",
                                            "eye",
                                        ),
                                        size=18,
                                    ),
                                    on_click=EstadoAutenticacion.alternar_mostrar_contrasena,
                                    variant="ghost",
                                    color_scheme="gray",
                                    position="absolute",
                                    right="10px",
                                    top="0",
                                    height="100%",
                                    display="flex",
                                    align_items="center",
                                    z_index="10",
                                    cursor="pointer",
                                    _hover={
                                        "background": "transparent",
                                        "opacity": "0.7",
                                    },
                                ),
                                position="relative",
                                width="100%",
                            ),
                            width="100%",
                            align_items="start",
                            spacing="1",
                        ),
                        # Botón Iniciar Sesión con gradiente y sombra
                        rx.button(
                            rx.hstack(
                                rx.icon("log-in", size=18),
                                rx.text("Iniciar Sesión", weight="bold"),
                                spacing="2",
                                align="center",
                            ),
                            on_click=EstadoAutenticacion.iniciar_sesion,
                            width="100%",
                            size="3",
                            style={
                                "background": "linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)",
                                "color": "white",
                                "border_radius": "12px",
                                "box_shadow": "0 8px 20px rgba(99, 102, 241, 0.22)",
                                "cursor": "pointer",
                                "transition": "all 0.2s ease",
                                "margin_top": "12px",
                            },
                            _hover={
                                "box_shadow": "0 12px 28px rgba(99, 102, 241, 0.3)",
                                "transform": "translateY(-1px)",
                            },
                            _active={"transform": "translateY(0)"},
                        ),
                        toast_viewer(),
                        spacing="4",
                        width="100%",
                    ),
                    size="4",
                    width="100%",
                    max_width="420px",
                    style={
                        "background": "#FFFFFF",
                        "border-radius": "24px",
                        "box_shadow": "0 20px 40px -15px rgba(99, 102, 241, 0.12), 0 0 0 1px rgba(99, 102, 241, 0.04)",
                        "border": "1px solid #E2E8F0",
                        "padding": "32px",
                    },
                ),
                height="100vh",
            ),
            background="radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.05) 0%, rgba(255, 255, 255, 1) 90%)",
            width="100%",
            height="100vh",
            position="relative",
        ),
        appearance="light",
        has_background=True,
    )
