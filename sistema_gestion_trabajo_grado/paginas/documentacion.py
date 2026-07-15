import reflex as rx

from ..componentes.encabezado import encabezado_pagina
from ..componentes.layout import layout_principal
from ..componentes.toast_viewer import toast_viewer
from ..estado.estado_autenticacion import EstadoAutenticacion
from ..estado.estado_documento import Documento, EstadoDocumento

COLOR_ICONO_PDF = "#EF4444"
COLOR_ICONO_WORD = "#3B82F6"
COLOR_ICONO_EXCEL = "#10B981"
COLOR_ICONO_GENERICO = "#6B7280"
COLOR_BORDE = "#4D5054"
DEGRADADO_ICONO = "linear-gradient(135deg, #6366F1 0%, #7C3AED 100%)"


def tarjeta_documento(doc: Documento) -> rx.Component:
    tipo = doc.tipo.lower()

    nombre_icono = rx.cond(
        tipo.contains("pdf"),
        "file-text",
        rx.cond(
            tipo.contains("doc"),
            "file-type-2",
            rx.cond(tipo.contains("xls"), "file-spreadsheet", "file"),
        ),
    )

    color_icono = rx.cond(
        tipo.contains("pdf"),
        COLOR_ICONO_PDF,
        rx.cond(
            tipo.contains("doc"),
            COLOR_ICONO_WORD,
            rx.cond(tipo.contains("xls"), COLOR_ICONO_EXCEL, COLOR_ICONO_GENERICO),
        ),
    )

    return rx.card(
        rx.flex(
            rx.hstack(
                rx.center(
                    rx.icon(nombre_icono, size=24, color=color_icono),
                    width="3rem",
                    height="3rem",
                    background=color_icono + "15",
                    border_radius="0.75rem",
                    border="1px solid " + color_icono + "30",
                ),
                rx.vstack(
                    rx.text(doc.titulo, weight="bold", size="3", color="#0F172A"),
                    rx.text(doc.descripcion, size="2", color="#1E293B", no_of_lines=2),
                    rx.hstack(
                        rx.badge(
                            doc.tipo.upper(),
                            variant="soft",
                            color_scheme="gray",
                            radius="full",
                            size="1",
                            style={
                                "color": "#1E293B",  # Texto oscuro
                                "background_color": "#F1F5F9",  # Fondo claro
                                "border": "1px solid #E2E8F0",
                                "font_weight": "bold",
                            },
                        ),
                        rx.text(
                            "• ", rx.text.span(doc.tamano), size="1", color="#475569"
                        ),
                        rx.text(
                            "• ",
                            rx.text.span(doc.fecha_subida),
                            size="1",
                            color="#475569",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                spacing="4",
                width="100%",
                align="center",
            ),
            rx.spacer(display=["none", "none", "block"]),
            rx.hstack(
                rx.cond(
                    tipo.contains("pdf"),
                    rx.link(
                        rx.icon_button(
                            rx.icon("eye", size=18),
                            variant="solid",
                            color_scheme="indigo",
                            size="2",
                            radius="full",
                            cursor="pointer",
                            title="Abrir documento",
                            _disabled={"opacity": "0.45", "cursor": "not-allowed"},
                        ),
                        href=rx.cond(doc.url != "", doc.url, "#"),
                        target="_blank",
                        rel="noopener noreferrer",
                        style={"display": "inline-flex"},
                    ),
                ),
                rx.icon_button(
                    rx.icon("download", size=18),
                    on_click=rx.cond(
                        doc.url != "",
                        rx.download(url=doc.url, filename=f"{doc.titulo}.{doc.tipo}"),
                        None,
                    ),
                    variant="solid",
                    color_scheme="blue",
                    size="2",
                    radius="full",
                    cursor="pointer",
                    title="Descargar documento",
                    _disabled={"opacity": "0.45", "cursor": "not-allowed"},
                ),
                rx.cond(
                    EstadoAutenticacion.rol_usuario == "administrador",
                    rx.hstack(
                        rx.icon_button(
                            rx.icon("pencil", size=16),
                            on_click=lambda: EstadoDocumento.preparar_edicion(doc),
                            variant="solid",
                            color_scheme="amber",
                            size="2",
                            radius="full",
                            cursor="pointer",
                            title="Editar",
                        ),
                        rx.icon_button(
                            rx.icon("trash-2", size=16),
                            on_click=lambda: EstadoDocumento.eliminar_documento(doc.id),
                            variant="solid",
                            color_scheme="red",
                            size="2",
                            radius="full",
                            cursor="pointer",
                            title="Eliminar",
                        ),
                        spacing="2",
                    ),
                ),
                spacing="2",
                align="center",
                width={"initial": "100%", "md": "auto"},
                justify={"initial": "end", "md": "start"},
                margin_top={"initial": "3", "md": "0"},
            ),
            direction={"initial": "column", "md": "row"},
            align={"initial": "start", "md": "center"},
            spacing="4",
            width="100%",
        ),
        width="100%",
        padding=["1.25rem", "1.25rem", "1rem"],
        background="white",
        border_radius="1rem",
        border=f"1px solid {COLOR_BORDE}",
        box_shadow="0 1px 3px rgba(0,0,0,0.05)",
        _hover={
            "border_color": "#6366F1",
            "transform": "translateY(-2px)",
            "box_shadow": "0 4px 6px -1px rgba(99,102,241,0.1)",
        },
        transition="all 0.2s ease",
        margin_bottom="0.75rem",
    )


def panel_administrador() -> rx.Component:
    return rx.cond(
        EstadoAutenticacion.rol_usuario == "administrador",
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("cloud-upload", size=20, color="#4F46E5"),
                    rx.text("Publicar Nuevo Documento", weight="bold", color="#4338CA"),
                    align="center",
                    spacing="2",
                    margin_bottom="2",
                ),
                rx.grid(
                    rx.vstack(
                        rx.text(
                            "Detalles del archivo",
                            size="2",
                            weight="bold",
                            color="black",
                        ),
                        rx.input(
                            placeholder="Título del documento...",
                            value=EstadoDocumento.titulo_nuevo,
                            on_change=EstadoDocumento.fijar_titulo_nuevo,
                            variant="classic",
                            radius="large",
                            width="100%",
                            style={
                                "background_color": "white",
                                "border": "1.5px solid #64748B",
                                "color": "black",
                                "& input": {
                                    "color": "black",
                                },
                                "font_weight": "bold",
                                "&::placeholder": {
                                    "color": "#94A3B8",
                                    "opacity": "0.85",
                                    "font_weight": "500",
                                    "letter_spacing": "0.01em",
                                },
                                "& input::placeholder": {
                                    "color": "#94A3B8",
                                    "opacity": "0.85",
                                    "font_weight": "500",
                                    "letter_spacing": "0.01em",
                                },
                            },
                        ),
                        rx.text_area(
                            placeholder="Descripción breve del contenido...",
                            value=EstadoDocumento.descripcion_nueva,
                            on_change=EstadoDocumento.fijar_descripcion_nueva,
                            variant="classic",
                            radius="large",
                            width="100%",
                            resize="vertical",
                            style={
                                "background_color": "white",
                                "border": f"1.5px solid {COLOR_BORDE}",
                                "color": "black",
                                "& textarea": {
                                    "color": "black",
                                },
                                "font_weight": "bold",
                                "&::placeholder": {
                                    "color": "#94A3B8",
                                    "opacity": "0.85",
                                    "font_weight": "500",
                                    "letter_spacing": "0.01em",
                                },
                                "& textarea::placeholder": {
                                    "color": "#94A3B8",
                                    "opacity": "0.85",
                                    "font_weight": "500",
                                    "letter_spacing": "0.01em",
                                },
                            },
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.cond(
                        rx.selected_files("upload_docs"),
                        rx.center(
                            rx.vstack(
                                rx.icon("file-check", size=40, color="#4F46E5"),
                                rx.foreach(
                                    rx.selected_files("upload_docs"),
                                    lambda f: rx.text(
                                        f,
                                        weight="bold",
                                        color="#1E293B",
                                        text_align="center",
                                        key=f,
                                    ),
                                ),
                                rx.button(
                                    "Cambiar archivo",
                                    on_click=rx.clear_selected_files("upload_docs"),
                                    variant="ghost",
                                    color_scheme="indigo",
                                    size="2",
                                    cursor="pointer",
                                ),
                                spacing="3",
                                align="center",
                                padding="1.875rem",
                                border="2px solid #4F46E5",
                                border_radius="0.75rem",
                                background="rgba(79,70,229,0.05)",
                                width="100%",
                                height="100%",
                            ),
                            width="100%",
                            height="100%",
                        ),
                        rx.upload(
                            rx.vstack(
                                rx.icon("upload", size=30, color="#475569"),
                                rx.text(
                                    "Arrastra archivos aquí o haz clic",
                                    color="#334155",
                                    weight="medium",
                                ),
                                rx.text(
                                    "Soporta PDF, Word, Excel",
                                    size="1",
                                    color="#475569",
                                ),
                                align="center",
                                spacing="2",
                            ),
                            id="upload_docs",
                            border="2px dashed #CBD5E1",
                            padding="1.875rem",
                            border_radius="0.75rem",
                            background="#F8FAFC",
                            width="100%",
                            height="100%",
                            max_files=1,
                            accept={
                                "application/pdf": [".pdf"],
                                "application/msword": [".doc"],
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
                                    ".docx"
                                ],
                                "application/vnd.ms-excel": [".xls", ".xlsx"],
                            },
                        ),
                    ),
                    columns="2",
                    spacing="6",
                    width="100%",
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.button(
                        "Cancelar",
                        on_click=EstadoDocumento.cancelar_publicacion,
                        variant="outline",
                        color_scheme="gray",
                        size="3",
                        radius="large",
                        style={
                            "border": "1.5px solid #94A3B8",
                            "font_weight": "bold",
                            "cursor": "pointer",
                        },
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon("send", size=16), rx.text("Publicar Documento")
                        ),
                        on_click=lambda: EstadoDocumento.publicar_documento(
                            rx.upload_files("upload_docs")
                        ),
                        size="3",
                        variant="solid",
                        color_scheme="indigo",
                        radius="large",
                        loading=EstadoDocumento.procesando,
                        style={
                            "font_weight": "bold",
                            "cursor": "pointer",
                            "padding_x": "1.5rem",
                        },
                    ),
                    width="100%",
                    padding_top="4",
                ),
                padding="1.5rem",
                background="white",
                border_radius="1rem",
                border=f"1px solid {COLOR_BORDE}",
                box_shadow="0 4px 6px -1px rgba(0,0,0,0.02)",
                width="100%",
            ),
            width="100%",
            margin_bottom="2rem",
        ),
    )


def modal_editar_documento() -> rx.Component:
    return rx.cond(
        EstadoDocumento.mostrar_modal_edicion,
        rx.box(
            rx.box(
                position="fixed",
                top="0",
                left="0",
                width="100vw",
                height="100vh",
                background="rgba(10,10,30,0.5)",
                backdrop_filter="blur(2px)",
                z_index="100",
                on_click=EstadoDocumento.cancelar_edicion,
            ),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.center(
                            rx.icon("pencil", size=20, color="white"),
                            width="2.5rem",
                            height="2.5rem",
                            border_radius="0.625rem",
                            background=DEGRADADO_ICONO,
                        ),
                        rx.text(
                            "Editar Documento", size="5", weight="bold", color="#1E293B"
                        ),
                        rx.spacer(),
                        rx.icon_button(
                            "x",
                            on_click=EstadoDocumento.cancelar_edicion,
                            variant="ghost",
                            color_scheme="gray",
                        ),
                        width="100%",
                        align="center",
                        margin_bottom="4",
                    ),
                    rx.text("Título", size="2", weight="bold", color="#1E293B"),
                    rx.input(
                        placeholder="Título del documento",
                        value=EstadoDocumento.titulo_edicion,
                        on_change=EstadoDocumento.fijar_titulo_edicion,
                        variant="classic",
                        width="100%",
                        style={
                            "background_color": "white",
                            "border": "1.5px solid #64748B",
                            "color": "black",
                            "& input": {
                                "color": "black",
                            },
                            "&::placeholder": {
                                "color": "#94A3B8",
                                "opacity": "0.85",
                                "font_weight": "500",
                                "letter_spacing": "0.01em",
                            },
                        },
                    ),
                    rx.text("Descripción", size="2", weight="bold", color="#1E293B"),
                    rx.text_area(
                        placeholder="Descripción breve del contenido",
                        value=EstadoDocumento.descripcion_edicion,
                        on_change=EstadoDocumento.fijar_descripcion_edicion,
                        variant="classic",
                        width="100%",
                        resize="vertical",
                        style={
                            "background_color": "white",
                            "border": "1.5px solid #64748B",
                            "color": "black",
                            "& textarea": {
                                "color": "black",
                            },
                            "&::placeholder": {
                                "color": "#94A3B8",
                                "opacity": "0.85",
                                "font_weight": "500",
                                "letter_spacing": "0.01em",
                            },
                        },
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancelar",
                            on_click=EstadoDocumento.cancelar_edicion,
                            variant="soft",
                            color_scheme="gray",
                        ),
                        rx.button(
                            "Guardar Cambios",
                            on_click=EstadoDocumento.guardar_edicion,
                            variant="solid",
                            color_scheme="indigo",
                        ),
                        spacing="3",
                        justify="end",
                        width="100%",
                        margin_top="6",
                    ),
                    width="100%",
                ),
                padding="1.5rem",
                background="white",
                border_radius="1rem",
                width="min(31.25rem, 90vw)",
                max_width="90vw",
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                z_index="200",
                box_shadow="0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)",
            ),
        ),
    )


def contenido_documentacion() -> rx.Component:
    """Contenido interno de la biblioteca de documentos."""
    return rx.vstack(
        encabezado_pagina("Biblioteca de Documentos", "", None),
        rx.text(
            "Repositorio oficial de formatos, guías y reglamentos de trabajos de grado.",
            color="#334155",
            margin_bottom="4",
        ),
        panel_administrador(),
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
                placeholder="Buscar documento por nombre o descripción...",
                value=EstadoDocumento.busqueda_documento,
                on_change=EstadoDocumento.fijar_busqueda_documento,
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
            # Barra ampliada para mejor visualización
            width=["100%", "100%", "50rem"],
            margin_bottom="0.5rem",
        ),
        rx.hstack(
            rx.heading("Archivos Disponibles", size="6", color="#1E293B"),
            rx.spacer(),
            rx.text(
                rx.text.span(EstadoDocumento.documentos_filtrados.length().to(str)),
                rx.text.span(" documentos"),
                size="2",
                color="#475569",
            ),
            width="100%",
            align="center",
            margin_bottom="4",
        ),
        rx.cond(
            EstadoDocumento.documentos_filtrados.length() > 0,
            rx.vstack(
                rx.foreach(EstadoDocumento.documentos_filtrados, tarjeta_documento),
                spacing="4",
                width="100%",
            ),
            rx.cond(
                EstadoDocumento.busqueda_documento != "",
                rx.vstack(
                    rx.icon("search-x", size=32, color="#94A3B8"),
                    rx.text(
                        'Sin resultados para "',
                        rx.text.span(EstadoDocumento.busqueda_documento),
                        '"',
                        color="#475569",
                        font_weight="600",
                    ),
                    rx.text(
                        "Intenta con otro término de búsqueda.",
                        color="#94A3B8",
                        font_size="0.8125rem",
                    ),
                    align="center",
                    spacing="2",
                    padding_y="2.5rem",
                ),
                rx.center(
                    rx.text("No hay documentos publicados aún.", color="#475569"),
                    padding="1.25rem",
                ),
            ),
        ),
        toast_viewer(),
        modal_editar_documento(),
        width="100%",
        padding=["1rem", "1.25rem", "1.5rem", "1.5rem"],
        max_width="75rem",
        spacing="5",
        on_mount=EstadoDocumento.cargar_documentos,
    )


def pagina_documentacion() -> rx.Component:
    return rx.theme(
        rx.cond(
            EstadoAutenticacion.usuario,
            layout_principal(contenido_documentacion()),
            rx.center(
                rx.spinner(),
                width="100vw",
                height="100vh",
                on_mount=EstadoAutenticacion.verificar_acceso,
            ),
        ),
        appearance="light",
        has_background=True,
    )
