import reflex as rx
COLOR_TEXTO_BOLD = "black"  # Negro puro para máximo contraste
COLOR_PLACEHOLDER = "#94A3B8" # Gris suave para máscaras de ejemplo


def campo_texto(
    label: str,
    valor,
    setter,
    tipo: str = "text",
    solo_lectura: bool | rx.Var[bool] = False,
    **props,
) -> rx.Component:
    # Extracción de placeholder o generación automática
    placeholder = props.pop("placeholder", f"Ingrese {label.lower()}")
    
    input_editable = rx.input(
        placeholder=placeholder,
        value=valor,
        on_change=setter,
        type=tipo,
        size="3",
        variant="classic",
        width="100%",
        radius="large",
        bg="white",
        color="black",
        style={
            "border": "1.5px solid #CBD5E1",
            "font_size": "13.5px",
            "font_weight": "bold",
            "&::placeholder": {
                                    "color": "#94A3B8",
                                    "opacity": "0.85",
                                    "font_weight": "500",
                                    "letter_spacing": "0.01em",
                                },
        },
        _focus={
            "border_color": "#3B82F6",
            "box_shadow":   "0 0 0 3px rgba(59,130,246,0.15)",
            "outline":      "none",
        },
        _hover={"border_color": "#60A5FA"},
        transition="border-color 0.15s ease, box-shadow 0.15s ease",
        **props,
    )

    input_solo_lectura = rx.box(
        rx.text(
            valor,
            font_size="13.5px",
            font_weight="600",
            color="#1E293B",
        ),
        width="100%",
        padding="10px 14px",
        background="#FFFFFF",
        border="1px solid #CBD5E1",
        border_radius="12px",
    )

    return rx.vstack(
        rx.text(
            label,
            font_size="13px",
            font_weight="700",
            color="#0F172A",
        ),
        rx.cond(solo_lectura, input_solo_lectura, input_editable),
        spacing="2",
        width="100%",
        align="start",
    )
