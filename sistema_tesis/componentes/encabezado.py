import reflex as rx


def encabezado_pagina(titulo: str, boton_texto: str, boton_accion) -> rx.Component:
    return rx.flex(
        rx.vstack(
            rx.heading(
                titulo,
                size={"initial": "7", "sm": "8"},
                weight="bold",
                color="#0F172A",  # Slate 900 para máxima legibilidad
                letter_spacing="-0.02em"
            ),
            rx.text(
                "Panel de gestión y monitoreo académico",
                color="#1E293B",  # Slate 800 (Más oscuro)
                font_size="13px",
                font_weight="500"
            ),
            spacing="1",
            align="start",
        ),
        rx.spacer(),
        rx.cond(
            boton_texto != "",
            rx.button(
                rx.hstack(rx.icon("plus", size=18), rx.text(
                    boton_texto, font_weight="700")),
                on_click=boton_accion,
                size="3",
                variant="solid",
                color_scheme="indigo",
                style={"cursor": "pointer",
                       "box_shadow": "0 4px 12px rgba(99,102,241,0.3)"}
            ),
        ),
        width="100%",
        align={"initial": "start", "sm": "center"},
        justify="between",
        direction={"initial": "column", "sm": "row"},
        spacing={"initial": "4", "sm": "0"},
        padding_bottom="16px",
        border_bottom="1px solid #E2E8F0",
        margin_bottom="28px",
    )
