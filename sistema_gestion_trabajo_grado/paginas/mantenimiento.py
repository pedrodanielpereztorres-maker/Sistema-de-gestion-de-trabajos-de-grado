import reflex as rx
from ..componentes.encabezado import encabezado_pagina
from ..componentes.campo_texto import campo_texto
from ..componentes.toast_viewer import toast_viewer

# Importar desde el componente base
from ..componentes.campo_texto import COLOR_TEXTO_BOLD
from ..estado.estado_autenticacion import EstadoAutenticacion
from ..componentes.layout import layout_principal
from ..estado.estado_mantenimiento import (
    EstadoMantenimiento,
    TutorAcademico,
    Rol,
    UsuarioSistema,
    Carrera,
)

COLOR_CABECERA_TABLA = "#F8FAFC"
COLOR_BORDE = "#CBD5E1"
COLOR_PRIMARIO = "#6366F1"
DEGRADADO_ICONO = "linear-gradient(135deg, #6366F1 0%, #7C3AED 100%)"
SOMBRA_CARD = "0 1px 3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04)"
SOMBRA_MODAL = "0 25px 50px -12px rgba(0,0,0,0.25)"
RADIO_CARD = "14px"


def contenedor_tabla(contenido: rx.Component) -> rx.Component:
    return rx.box(
        contenido,
        background="white",
        border=f"1px solid {COLOR_BORDE}",
        border_radius=RADIO_CARD,
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        overflow_x="auto",
        width="100%",
    )


def barra_herramientas(
    titulo: str,
    placeholder_busqueda: str,
    valor_busqueda: rx.Var,
    setter_busqueda,
    texto_boton: str,
    icono_boton: str,
    accion_boton,
) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(
                titulo,
                font_weight="800",
                color="#1E293B",
                font_size="18px",
                letter_spacing="-0.01em",
            ),
            rx.text(
                "Administración y gestión de registros",
                color="#334155",
                font_size="12px",
                font_weight="500",
            ),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.hstack(
            rx.box(
                rx.icon(
                    "search",
                    size=15,
                    color="#000000",
                    position="absolute",
                    left="12px",
                    top="50%",
                    transform="translateY(-50%)",
                    z_index="1",
                ),
                rx.input(
                    placeholder=placeholder_busqueda,
                    value=valor_busqueda,
                    on_change=setter_busqueda,
                    padding_left="2.25rem",
                    variant="classic",
                    width="100%",
                    max_width="24rem",
                    color=COLOR_TEXTO_BOLD,  # Texto del input en negro
                    radius="large",
                    background="white",
                    border=f"1px solid {COLOR_BORDE}",
                    style={
                        "background_color": "white",
                        "border": "1.5px solid #64748B",
                        "color": COLOR_TEXTO_BOLD,
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
                        "box_shadow": "0 0 0 3px rgba(99,102,241,0.15)",
                        "outline": "none",
                    },
                ),
                position="relative",
            ),
            rx.button(
                rx.hstack(
                    rx.icon(icono_boton, size=18),
                    rx.text(texto_boton, font_weight="600"),
                ),
                on_click=accion_boton,
                size="3",
                radius="large",
                background=DEGRADADO_ICONO,
                color="white",
                box_shadow="0 4px 12px rgba(99,102,241,0.25)",
                cursor="pointer",
                _hover={
                    "opacity": 0.9,
                    "transform": "translateY(-1px)",
                    "box_shadow": "0 6px 16px rgba(99,102,241,0.35)",
                },
                transition="all 0.2s",
            ),
            spacing="3",
            align="center",
        ),
        width="100%",
        align="center",
        margin_bottom="1.25rem",
        padding_bottom="1.25rem",
        border_bottom=f"1px solid {COLOR_BORDE}",
    )


def celda_cabecera(texto: str) -> rx.Component:
    return rx.table.column_header_cell(
        rx.text(
            texto,
            font_weight="700",
            font_size="11px",
            color="#475569",
            letter_spacing="0.05em",
        ),
        padding_y="1rem",
        padding_x="1.25rem",
        background="#F1F5F9",
        text_transform="uppercase",
        border_bottom=f"2px solid {COLOR_BORDE}",
    )


def celda_texto(texto: str, secundario: bool = False) -> rx.Component:
    return rx.table.cell(
        rx.text(
            texto,
            color="#1E293B" if not secundario else "#475569",
            font_weight="500",
            font_size="14px",
        ),
        padding_y="1rem",
        padding_x="1.25rem",
    )


def celda_simple(texto: str, bold: bool = False) -> rx.Component:
    return rx.table.cell(
        rx.text(
            texto,
            color="#0F172A",
            font_weight="700" if bold else "600",
            font_size="14px",
        ),
        padding_y="1rem",
        padding_x="1.25rem",
    )


def boton_accion(icono: str, color: str, accion, tooltip: str) -> rx.Component:
    return rx.icon_button(
        rx.icon(icono, size=16),
        on_click=accion,
        variant="solid",
        color_scheme=color,
        size="2",
        radius="full",
        cursor="pointer",
        title=tooltip,
    )


def fila_usuario(user: UsuarioSistema) -> rx.Component:
    return rx.table.row(
        # Columna: Perfil (Avatar + Nombre/Rol)
        rx.table.cell(
            rx.hstack(
                # Avatar circular con inicial (con extracción segura)
                rx.center(
                    rx.text(
                        user.nombre.to(str)[0],
                        color="white",
                        font_weight="bold",
                        font_size="14px",
                        text_transform="uppercase",
                    ),
                    width="2rem",
                    height="2rem",
                    border_radius="full",
                    flex_shrink="0",
                    background=rx.cond(
                        user.rol == "Administrador",
                        "#4F46E5",
                        "#059669",  # Colores un poco más intensos
                    ),
                ),
                # Texto: Nombre completo y Rol debajo
                rx.vstack(
                    rx.text(
                        user.nombre.to(str) + " " + user.apellido.to(str),
                        font_weight="600",
                        font_size="13px",
                        color="#0F172A",
                    ),
                    rx.text(user.rol, font_size="11px", color="#64748B"),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),
            padding_y="1rem",
            padding_x="1.25rem",
        ),
        # Columna: Correo
        celda_texto(user.correo),
        # Columna: Badge de Rol (Corregido el color gris)
        rx.table.cell(
            rx.badge(
                user.rol,
                # Usamos colores semánticos que Reflex traduce bien
                color_scheme=rx.cond(user.rol == "Administrador", "indigo", "green"),
                variant="soft",
                radius="full",
                size="2",
                style={
                    # Forzamos un color de texto más oscuro para legibilidad
                    "color": rx.cond(user.rol == "Administrador", "#3730A3", "#065F46"),
                    # Fondo un poco más saturado para que no parezca gris
                    "background_color": rx.cond(
                        user.rol == "Administrador", "#E0E7FF", "#D1FAE5"
                    ),
                    "font_weight": "bold",
                    "padding_x": "10px",
                },
            ),
            padding_y="1rem",
            padding_x="1.25rem",
        ),
        # Columna: Estado y Acciones
        rx.table.cell(
            rx.hstack(
                rx.badge(
                    rx.cond(user.esta_activo, "ACTIVO", "INACTIVO"),
                    color_scheme=rx.cond(user.esta_activo, "green", "gray"),
                    variant="soft",
                    radius="full",
                    font_weight="bold",
                ),
                rx.icon_button(
                    rx.icon(rx.cond(user.esta_activo, "lock", "unlock"), size=14),
                    on_click=lambda: EstadoMantenimiento.alternar_estado_usuario(
                        user.id
                    ),
                    variant="ghost",
                    color_scheme=rx.cond(user.esta_activo, "red", "green"),
                    size="2",
                    cursor=rx.cond(
                        EstadoAutenticacion.usuario_id == user.id,
                        "not-allowed",
                        "pointer",
                    ),
                    disabled=rx.cond(
                        EstadoAutenticacion.usuario_id == user.id, True, False
                    ),
                    title=rx.cond(
                        EstadoAutenticacion.usuario_id == user.id,
                        "No puedes desactivar tu propia cuenta",
                        rx.cond(
                            user.esta_activo, "Desactivar Cuenta", "Activar Cuenta"
                        ),
                    ),
                ),
                rx.icon_button(
                    rx.icon("trash-2", size=14),
                    on_click=lambda: EstadoMantenimiento.eliminar_usuario(user.id),
                    variant="ghost",
                    color_scheme="red",
                    size="2",
                    cursor=rx.cond(
                        EstadoAutenticacion.usuario_id == user.id,
                        "not-allowed",
                        "pointer",
                    ),
                    disabled=rx.cond(
                        EstadoAutenticacion.usuario_id == user.id, True, False
                    ),
                    title=rx.cond(
                        EstadoAutenticacion.usuario_id == user.id,
                        "No puedes eliminar tu propia cuenta",
                        "Eliminar Cuenta",
                    ),
                ),
                spacing="3",
                align="center",
            ),
            padding_y="1rem",
            padding_x="1.25rem",
        ),
        key=user.id,
        _hover={"background": "#F8FAFC"},
        transition="background 0.2s",
    )


def paginacion_tabla(
    pagina_actual, total_paginas, total_registros, anterior, siguiente, etiqueta: str
) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.button(
                rx.hstack(
                    rx.icon("chevron-left", size=15),
                    rx.text(
                        "Anterior", style={"font_size": "14px", "font_weight": "600"}
                    ),
                    spacing="1",
                    align="center",
                ),
                on_click=anterior,
                is_disabled=pagina_actual <= 1,
                variant="soft",
                color_scheme="gray",
                size="2",
                style={"border": f"1px solid {COLOR_BORDE}", "border_radius": "10px"},
                _hover={"background_color": "#E2E8F0"},
            ),
            rx.hstack(
                rx.text(
                    "Página ",
                    rx.text.span(
                        pagina_actual.to(str),
                        style={"font_weight": "800", "color": "#6366F1"},
                    ),
                    " de ",
                    rx.text.span(total_paginas.to(str), style={"font_weight": "800"}),
                    style={"font_size": "14px", "color": "#334155"},
                ),
                rx.badge(
                    total_registros.to(str) + " registros",
                    variant="soft",
                    color_scheme="indigo",
                    radius="full",
                    style={"font_size": "12px", "font_weight": "700"},
                ),
                spacing="3",
                align="center",
            ),
            rx.button(
                rx.hstack(
                    rx.text(
                        "Siguiente", style={"font_size": "14px", "font_weight": "600"}
                    ),
                    rx.icon("chevron-right", size=15),
                    spacing="1",
                    align="center",
                ),
                on_click=siguiente,
                is_disabled=pagina_actual >= total_paginas,
                variant="soft",
                color_scheme="indigo",
                size="2",
                style={"border": "1px solid #C7D2FE", "border_radius": "10px"},
                _hover={"background_color": "#EEF2FF"},
            ),
            justify="center",
            align="center",
            spacing="4",
            width="100%",
        ),
        padding="0.875rem 1.25rem",
        background="#F8FAFC",
        border_top=f"1px solid {COLOR_BORDE}",
        border_radius="0 0 16px 16px",
        width="100%",
    )


def contenido_usuarios() -> rx.Component:
    return rx.vstack(
        barra_herramientas(
            "Cuentas de Acceso",
            "Buscar usuario...",
            EstadoMantenimiento.busqueda_usuarios,
            EstadoMantenimiento.fijar_busqueda_usuarios,
            "Nuevo Usuario",
            "user-plus",
            EstadoMantenimiento.abrir_modal_usuario,
        ),
        contenedor_tabla(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        celda_cabecera("Usuario"),
                        celda_cabecera("Correo Electrónico"),
                        celda_cabecera("Rol Asignado"),
                        celda_cabecera("Estado / Acción"),
                    )
                ),
                rx.table.body(
                    rx.foreach(EstadoMantenimiento.usuarios_paginados, fila_usuario)
                ),
                variant="surface",
                width="100%",
            )
        ),
        paginacion_tabla(
            EstadoMantenimiento.usuarios_pagina_actual,
            EstadoMantenimiento.usuarios_total_paginas,
            EstadoMantenimiento.usuarios_total_registros,
            EstadoMantenimiento.usuarios_pagina_anterior,
            EstadoMantenimiento.usuarios_pagina_siguiente,
            "usuarios",
        ),
        width="100%",
    )


def fila_carrera(carrera: Carrera) -> rx.Component:
    return rx.table.row(
        celda_simple(carrera.nombre, bold=True),
        rx.table.cell(
            rx.badge(
                rx.cond(carrera.esta_activa, "ACTIVA", "INACTIVA"),
                color_scheme=rx.cond(carrera.esta_activa, "indigo", "gray"),
                variant="soft",
                radius="full",
                font_weight="bold",
            )
        ),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    rx.icon("pencil", size=16),
                    "Editar",
                    on_click=lambda: EstadoMantenimiento.abrir_modal_carrera(
                        True, carrera
                    ),
                    size="2",
                    variant="solid",
                    color_scheme="blue",
                ),
                rx.cond(
                    carrera.tiene_movimientos,
                    rx.button(
                        rx.icon(
                            rx.cond(carrera.esta_activa, "power-off", "power"), size=16
                        ),
                        rx.cond(carrera.esta_activa, "Desactivar", "Activar"),
                        on_click=lambda: EstadoMantenimiento.alternar_estado_carrera(
                            carrera.id
                        ),
                        size="2",
                        variant="solid",
                        color_scheme=rx.cond(carrera.esta_activa, "orange", "green"),
                        style={
                            "title": "Esta carrera tiene registros y solo puede desactivarse."
                        },
                    ),
                    rx.button(
                        rx.icon("trash-2", size=16),
                        "Eliminar",
                        on_click=lambda: EstadoMantenimiento.eliminar_carrera(
                            carrera.id
                        ),
                        size="2",
                        variant="solid",
                        color_scheme="red",
                    ),
                ),
                spacing="2",
            )
        ),
    )


def contenido_carreras() -> rx.Component:
    return rx.vstack(
        barra_herramientas(
            "Carreras Universitarias",
            "Buscar carrera...",
            EstadoMantenimiento.busqueda_carreras,
            EstadoMantenimiento.fijar_busqueda_carreras,
            "Nueva Carrera",
            "plus",
            lambda: EstadoMantenimiento.abrir_modal_carrera(),
        ),
        contenedor_tabla(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        celda_cabecera("Nombre"),
                        celda_cabecera("Tiene Registros"),
                        celda_cabecera("Acciones"),
                    )
                ),
                rx.table.body(
                    rx.foreach(EstadoMantenimiento.carreras_paginadas, fila_carrera)
                ),
                variant="surface",
                width="100%",
            )
        ),
        paginacion_tabla(
            EstadoMantenimiento.carreras_pagina_actual,
            EstadoMantenimiento.carreras_total_paginas,
            EstadoMantenimiento.carreras_total_registros,
            EstadoMantenimiento.carreras_pagina_anterior,
            EstadoMantenimiento.carreras_pagina_siguiente,
            "carreras",
        ),
        width="100%",
    )


def fila_tutor(tutor: TutorAcademico) -> rx.Component:
    return rx.table.row(
        celda_simple(tutor.nombre, bold=True),
        celda_simple(rx.cond(tutor.carrera, tutor.carrera, "Sin Carrera")),
        celda_simple(tutor.especialidad),
        celda_simple(tutor.correo),
        celda_simple(tutor.telefono),
        rx.table.cell(
            rx.badge(
                rx.cond(tutor.activo, "DISPONIBLE", "INACTIVO"),
                color_scheme=rx.cond(tutor.activo, "blue", "gray"),
                variant="soft",
                radius="full",
                size="2",
                style={
                    # Azul oscuro o Gris oscuro
                    "color": rx.cond(tutor.activo, "#1E40AF", "#1E293B"),
                    # Azul claro o Gris claro
                    "background_color": rx.cond(tutor.activo, "#DBEAFE", "#F1F5F9"),
                    "font_weight": "bold",
                    "padding_x": "10px",
                },
            )
        ),
        rx.table.cell(
            rx.hstack(
                # Botón Editar
                boton_accion(
                    "pencil",
                    "amber",
                    lambda: EstadoMantenimiento.abrir_modal_tutor(True, tutor),
                    "Editar",
                ),
                # Lógica: Si tiene movimientos -> Desactivar. Si no -> Eliminar.
                rx.cond(
                    tutor.tiene_movimientos,
                    # Caso: Tiene tesis (Solo desactivar)
                    rx.icon_button(
                        rx.icon(rx.cond(tutor.activo, "power-off", "power"), size=16),
                        on_click=lambda: EstadoMantenimiento.alternar_estado_tutor(
                            tutor.id
                        ),
                        variant="solid",
                        color_scheme=rx.cond(tutor.activo, "orange", "green"),
                        size="2",
                        radius="full",
                        cursor="pointer",
                        title=rx.cond(
                            tutor.activo, "Desactivar (Tiene historial)", "Reactivar"
                        ),
                    ),
                    # Caso: Limpio (Permite eliminar)
                    boton_accion(
                        "trash-2",
                        "red",
                        lambda: EstadoMantenimiento.eliminar_tutor(tutor.id),
                        "Eliminar Definitivamente",
                    ),
                ),
                spacing="2",
            )
        ),
        _hover={"background": "rgba(0,0,0,0.02)"},
        transition="background 0.15s",
    )


def contenido_tutores() -> rx.Component:
    return rx.vstack(
        barra_herramientas(
            "Tutores Académicos",
            "Buscar tutor...",
            EstadoMantenimiento.busqueda_tutores,
            EstadoMantenimiento.fijar_busqueda_tutores,
            "Nuevo Tutor",
            "user-plus",
            lambda: EstadoMantenimiento.abrir_modal_tutor(False, None),
        ),
        rx.box(
            rx.hstack(
                rx.icon("info", size=14, color="#3B82F6"),
                rx.text(
                    "Los tutores con tesis asignadas no pueden eliminarse, solo desactivarse.",
                    font_size="12px",
                    color="#3B82F6",
                ),
                align="center",
                spacing="2",
            ),
            padding="0.625rem 1rem",
            background="#EFF6FF",
            border="1px solid #BFDBFE",
            border_radius="0.625rem",
            width="100%",
            margin_bottom="1rem",
        ),
        contenedor_tabla(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        celda_cabecera("Nombre"),
                        celda_cabecera("Carrera"),
                        celda_cabecera("Especialidad"),
                        celda_cabecera("Correo"),
                        celda_cabecera("Teléfono"),
                        celda_cabecera("Estado"),
                        celda_cabecera("Acciones"),
                    )
                ),
                rx.table.body(
                    rx.foreach(EstadoMantenimiento.tutores_paginados, fila_tutor)
                ),
                variant="surface",
                width="100%",
            )
        ),
        paginacion_tabla(
            EstadoMantenimiento.tutores_pagina_actual,
            EstadoMantenimiento.tutores_total_paginas,
            EstadoMantenimiento.tutores_total_registros,
            EstadoMantenimiento.tutores_pagina_anterior,
            EstadoMantenimiento.tutores_pagina_siguiente,
            "tutores",
        ),
        width="100%",
    )


def fila_rol(rol: Rol) -> rx.Component:
    return rx.table.row(
        celda_texto(rol.nombre),
        celda_texto(rol.descripcion, secundario=True),
        rx.table.cell(
            rx.hstack(
                boton_accion(
                    "trash-2",
                    "red",
                    lambda: EstadoMantenimiento.abrir_confirmacion_rol(rol.id),
                    "Eliminar Rol",
                )
            ),
            padding_y="1rem",
            padding_x="1.25rem",
        ),
        _hover={"background": "rgba(0,0,0,0.02)"},
        transition="background 0.15s",
    )


def contenido_roles() -> rx.Component:
    return rx.vstack(
        barra_herramientas(
            "Roles y Permisos",
            "Buscar rol...",
            EstadoMantenimiento.busqueda_roles,
            EstadoMantenimiento.fijar_busqueda_roles,
            "Crear Rol",
            "shield-plus",
            EstadoMantenimiento.abrir_modal_rol,
        ),
        contenedor_tabla(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        celda_cabecera("Rol"),
                        celda_cabecera("Descripción"),
                        celda_cabecera("Acciones"),
                    )
                ),
                rx.table.body(
                    rx.foreach(EstadoMantenimiento.roles_paginados, fila_rol)
                ),
                variant="surface",
                width="100%",
            )
        ),
        paginacion_tabla(
            EstadoMantenimiento.roles_pagina_actual,
            EstadoMantenimiento.roles_total_paginas,
            EstadoMantenimiento.roles_total_registros,
            EstadoMantenimiento.roles_pagina_anterior,
            EstadoMantenimiento.roles_pagina_siguiente,
            "roles",
        ),
        width="100%",
        spacing="4",
    )


def cabecera_modal(
    titulo: str, subtitulo: str, icono: str, on_close: rx.EventHandler
) -> rx.Component:
    return rx.hstack(
        rx.center(
            rx.icon(icono, size=20, color="white"),
            width="2.75rem",
            height="2.75rem",
            border_radius="0.75rem",
            background=DEGRADADO_ICONO,
            box_shadow="0 4px 10px rgba(99,102,241,0.3)",
        ),
        rx.vstack(
            rx.text(titulo, font_size="18px", font_weight="800", color="#1E293B"),
            rx.text(subtitulo, font_size="13px", color="#334155"),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.icon_button(
            rx.icon("x", size=18),
            variant="ghost",
            color_scheme="gray",
            on_click=on_close,
            cursor="pointer",
        ),
        width="100%",
        align="center",
        margin_bottom="1.5rem",
        padding_bottom="1.25rem",
        border_bottom=f"1px solid {COLOR_BORDE}",
    )


def pie_modal(
    texto_guardar: str,
    accion_guardar: rx.EventHandler,
    accion_cancelar: rx.EventHandler,
) -> rx.Component:
    return rx.hstack(
        rx.button(
            "Cancelar",
            variant="soft",
            color_scheme="gray",
            on_click=accion_cancelar,
            radius="large",
        ),
        rx.button(
            texto_guardar,
            on_click=accion_guardar,
            radius="large",
            variant="solid",
            color_scheme="indigo",
            background=DEGRADADO_ICONO,
            box_shadow="0 4px 12px rgba(99,102,241,0.3)",
        ),
        justify="end",
        width="100%",
        margin_top="1.5rem",
        padding_top="1.25rem",
        border_top=f"1px solid {COLOR_BORDE}",
    )


def modal_usuario() -> rx.Component:
    return rx.cond(
        EstadoMantenimiento.modal_usuario_abierto,
        rx.box(
            rx.box(
                position="fixed",
                inset="0",
                bg="rgba(10,10,30,0.5)",
                backdrop_filter="blur(4px)",
                z_index="200",
                on_click=EstadoMantenimiento.cerrar_modal_usuario,
            ),
            rx.box(
                rx.vstack(
                    cabecera_modal(
                        "Nuevo Usuario",
                        "Registra un nuevo usuario en el sistema",
                        "user-plus",
                        EstadoMantenimiento.cerrar_modal_usuario,
                    ),
                    rx.grid(
                        campo_texto(
                            "Cédula de Identidad",
                            EstadoMantenimiento.u_cedula,
                            EstadoMantenimiento.fijar_u_cedula,
                        ),
                        columns="1",
                        width="100%",
                    ),
                    rx.grid(
                        campo_texto(
                            "Nombre",
                            EstadoMantenimiento.u_nombre,
                            EstadoMantenimiento.fijar_u_nombre,
                        ),
                        campo_texto(
                            "Apellido",
                            EstadoMantenimiento.u_apellido,
                            EstadoMantenimiento.fijar_u_apellido,
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    campo_texto(
                        "Correo",
                        EstadoMantenimiento.u_correo,
                        EstadoMantenimiento.fijar_u_correo,
                        tipo="email",
                    ),
                    rx.grid(
                        campo_texto(
                            "Contraseña",
                            EstadoMantenimiento.u_clave,
                            EstadoMantenimiento.fijar_u_clave,
                            tipo="password",
                        ),
                        rx.vstack(
                            rx.text(
                                "Rol Asignado",
                                font_size="13px",
                                font_weight="600",
                                color="#0F172A",
                            ),
                            rx.select(
                                EstadoMantenimiento.nombres_roles,
                                on_change=EstadoMantenimiento.fijar_u_rol,
                                width="100%",
                                radius="large",
                                size="3",
                                variant="classic",
                                color="black",
                                style={
                                    "background_color": "#F8FAFC",
                                    "border": "1.5px solid #64748B",
                                    "color": "#0F172A",
                                    "font_size": "15px",
                                    "font_weight": "600",
                                },
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    pie_modal(
                        "Crear Cuenta",
                        EstadoMantenimiento.guardar_usuario,
                        EstadoMantenimiento.cerrar_modal_usuario,
                    ),
                    width="100%",
                    spacing="5",
                ),
                padding="1.5rem",
                background="white",
                border_radius="1rem",
                box_shadow=SOMBRA_MODAL,
                width="100%",
                max_width="34rem",
                z_index="210",
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                on_click=rx.stop_propagation,
            ),
        ),
    )


def modal_carrera() -> rx.Component:
    return rx.cond(
        EstadoMantenimiento.modal_carrera_abierto,
        rx.box(
            rx.box(
                position="fixed",
                inset="0",
                bg="rgba(10,10,30,0.5)",
                backdrop_filter="blur(4px)",
                z_index="200",
                on_click=EstadoMantenimiento.cerrar_modal_carrera,
            ),
            rx.box(
                rx.vstack(
                    cabecera_modal(
                        rx.cond(
                            EstadoMantenimiento.c_en_edicion,
                            "Editar Carrera",
                            "Nueva Carrera",
                        ),
                        "Gestiona las carreras universitarias",
                        "graduation-cap",
                        EstadoMantenimiento.cerrar_modal_carrera,
                    ),
                    campo_texto(
                        "Nombre de la Carrera",
                        EstadoMantenimiento.c_nombre,
                        EstadoMantenimiento.fijar_c_nombre,
                    ),
                    pie_modal(
                        rx.cond(
                            EstadoMantenimiento.c_en_edicion,
                            "Guardar Cambios",
                            "Crear Carrera",
                        ),
                        EstadoMantenimiento.guardar_carrera,
                        EstadoMantenimiento.cerrar_modal_carrera,
                    ),
                    width="100%",
                    spacing="5",
                ),
                padding="1.5rem",
                background="white",
                border_radius="1rem",
                box_shadow=SOMBRA_MODAL,
                width="100%",
                max_width="28rem",
                z_index="210",
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                on_click=rx.stop_propagation,
            ),
        ),
    )


def modal_tutor() -> rx.Component:
    return rx.cond(
        EstadoMantenimiento.modal_tutor_abierto,
        rx.box(
            rx.box(
                position="fixed",
                inset="0",
                bg="rgba(10,10,30,0.5)",
                backdrop_filter="blur(4px)",
                z_index="200",
                on_click=EstadoMantenimiento.cerrar_modal_tutor,
            ),
            rx.box(
                rx.vstack(
                    cabecera_modal(
                        rx.cond(
                            EstadoMantenimiento.t_en_edicion,
                            "Editar Tutor",
                            "Nuevo Tutor",
                        ),
                        "Gestiona la información del personal académico",
                        "graduation-cap",
                        EstadoMantenimiento.cerrar_modal_tutor,
                    ),
                    rx.grid(
                        campo_texto(
                            "Cédula",
                            EstadoMantenimiento.t_cedula,
                            EstadoMantenimiento.fijar_t_cedula,
                            on_blur=EstadoMantenimiento.cargar_datos_usuario_tutor,
                        ),
                        campo_texto(
                            "Nombre Completo",
                            EstadoMantenimiento.t_nombre,
                            EstadoMantenimiento.fijar_t_nombre,
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    rx.grid(
                        campo_texto(
                            "Correo Electrónico",
                            EstadoMantenimiento.t_correo,
                            EstadoMantenimiento.fijar_t_correo,
                            tipo="email",
                        ),
                        campo_texto(
                            "Teléfono",
                            EstadoMantenimiento.t_telefono,
                            EstadoMantenimiento.fijar_t_telefono,
                            tipo="tel",
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text(
                                "Carrera",
                                font_size="13px",
                                font_weight="600",
                                color="#0F172A",
                            ),
                            rx.select(
                                EstadoMantenimiento.carreras_nombres,
                                on_change=EstadoMantenimiento.fijar_t_carrera,
                                value=EstadoMantenimiento.t_carrera,
                                placeholder="Seleccione una carrera",
                                width="100%",
                                radius="large",
                                size="3",
                                variant="classic",
                                color="black",
                                style={
                                    "background_color": "#F8FAFC",
                                    "border": "1.5px solid #64748B",
                                    "color": "#0F172A",
                                    "font_size": "15px",
                                    "font_weight": "600",
                                },
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        campo_texto(
                            "Especialidad",
                            EstadoMantenimiento.t_especialidad,
                            EstadoMantenimiento.fijar_t_especialidad,
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    pie_modal(
                        "Guardar Datos",
                        EstadoMantenimiento.guardar_tutor,
                        EstadoMantenimiento.cerrar_modal_tutor,
                    ),
                    width="100%",
                    spacing="5",
                ),
                padding="1.5rem",
                background="white",
                border_radius="1rem",
                box_shadow=SOMBRA_MODAL,
                width="100%",
                max_width="31.25rem",
                z_index="210",
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                on_click=rx.stop_propagation,
            ),
        ),
    )


def modal_rol() -> rx.Component:
    return rx.cond(
        EstadoMantenimiento.modal_rol_abierto,
        rx.box(
            rx.box(
                position="fixed",
                inset="0",
                bg="rgba(10,10,30,0.5)",
                backdrop_filter="blur(4px)",
                z_index="200",
                on_click=EstadoMantenimiento.cerrar_modal_rol,
            ),
            rx.box(
                rx.vstack(
                    cabecera_modal(
                        "Nuevo Rol",
                        "Define nuevos niveles de acceso",
                        "shield-check",
                        EstadoMantenimiento.cerrar_modal_rol,
                    ),
                    campo_texto(
                        "Nombre del Rol",
                        EstadoMantenimiento.r_nombre,
                        EstadoMantenimiento.fijar_r_nombre,
                    ),
                    campo_texto(
                        "Descripción",
                        EstadoMantenimiento.r_descripcion,
                        EstadoMantenimiento.fijar_r_descripcion,
                    ),
                    pie_modal(
                        "Guardar Rol",
                        EstadoMantenimiento.guardar_rol,
                        EstadoMantenimiento.cerrar_modal_rol,
                    ),
                    width="100%",
                    spacing="5",
                ),
                padding="1.5rem",
                background="white",
                border_radius="1rem",
                box_shadow=SOMBRA_MODAL,
                width="100%",
                max_width="28rem",
                z_index="210",
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                on_click=rx.stop_propagation,
            ),
        ),
    )


def modal_confirmar_eliminacion_rol() -> rx.Component:
    return rx.cond(
        EstadoMantenimiento.modal_confirmar_rol_abierto,
        rx.box(
            rx.box(
                position="fixed",
                inset="0",
                bg="rgba(10,10,30,0.5)",
                backdrop_filter="blur(4px)",
                z_index="200",
                on_click=EstadoMantenimiento.cerrar_confirmacion_rol,
            ),
            rx.box(
                rx.vstack(
                    cabecera_modal(
                        "Confirmar Eliminación",
                        "Esta acción requiere autorización",
                        "shield-alert",
                        EstadoMantenimiento.cerrar_confirmacion_rol,
                    ),
                    rx.text(
                        "Para eliminar este rol, confirme su contraseña de administrador:",
                        color="#334155",
                        font_size="13px",
                        font_weight="500",
                    ),
                    campo_texto(
                        "Contraseña del Administrador",
                        EstadoMantenimiento.password_confirmacion,
                        EstadoMantenimiento.fijar_password_confirmacion,
                        tipo="password",
                    ),
                    rx.hstack(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            on_click=EstadoMantenimiento.cerrar_confirmacion_rol,
                            radius="large",
                        ),
                        rx.button(
                            "Eliminar Definitivamente",
                            on_click=EstadoMantenimiento.confirmar_eliminar_rol,
                            radius="large",
                            variant="solid",
                            color_scheme="red",
                            box_shadow="0 4px 12px rgba(239,68,68,0.3)",
                        ),
                        justify="end",
                        width="100%",
                        margin_top="1.5rem",
                        padding_top="1.25rem",
                        border_top=f"1px solid {COLOR_BORDE}",
                    ),
                    width="100%",
                    spacing="5",
                ),
                padding="1.5rem",
                background="white",
                border_radius="1rem",
                box_shadow=SOMBRA_MODAL,
                width="100%",
                max_width="28rem",
                z_index="210",
                position="fixed",
                top="50%",
                left="50%",
                transform="translate(-50%, -50%)",
                on_click=rx.stop_propagation,
            ),
        ),
    )


def contenido_mantenimiento() -> rx.Component:
    """Contenido interno del panel de mantenimiento."""
    return rx.vstack(
        encabezado_pagina("Mantenimiento del Sistema", "", None),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger(
                    "Usuarios",
                    value="usuarios",
                    padding_x="1.25rem",
                    padding_y="0.625rem",
                    color="#334155",
                    _active={
                        "color": COLOR_PRIMARIO,
                        "background": "white",
                        "border_bottom": f"2px solid {COLOR_PRIMARIO}",
                        "font_weight": "700",
                    },
                ),
                rx.tabs.trigger(
                    "Tutores Académicos",
                    value="tutores",
                    padding_x="1.25rem",
                    padding_y="0.625rem",
                    color="#334155",
                    _active={
                        "color": COLOR_PRIMARIO,
                        "background": "white",
                        "border_bottom": f"2px solid {COLOR_PRIMARIO}",
                        "font_weight": "700",
                    },
                ),
                rx.tabs.trigger(
                    "Roles y Permisos",
                    value="roles",
                    padding_x="1.25rem",
                    padding_y="0.625rem",
                    color="#334155",
                    _active={
                        "color": COLOR_PRIMARIO,
                        "background": "white",
                        "border_bottom": f"2px solid {COLOR_PRIMARIO}",
                        "font_weight": "700",
                    },
                ),
                rx.tabs.trigger(
                    "Carreras",
                    value="carreras",
                    padding_x="1.25rem",
                    padding_y="0.625rem",
                    color="#334155",
                    _active={
                        "color": COLOR_PRIMARIO,
                        "background": "white",
                        "border_bottom": f"2px solid {COLOR_PRIMARIO}",
                        "font_weight": "700",
                    },
                ),
                background="transparent",
                border_bottom=f"2px solid {COLOR_BORDE}",
                width="100%",
            ),
            rx.box(
                rx.tabs.content(contenido_usuarios(), value="usuarios"),
                rx.tabs.content(contenido_tutores(), value="tutores"),
                rx.tabs.content(contenido_roles(), value="roles"),
                rx.tabs.content(contenido_carreras(), value="carreras"),
                padding_top="2rem",
                width="100%",
            ),
            margin_top="1.25rem",
            default_value="usuarios",
            width="100%",
        ),
        modal_usuario(),
        modal_tutor(),
        modal_rol(),
        modal_confirmar_eliminacion_rol(),
        toast_viewer(),
        modal_carrera(),
        width="100%",
        padding=["1.25rem", "1.75rem", "1.75rem", "2.25rem"],
        max_width="96vw",
        on_mount=EstadoMantenimiento.cargar_datos,
    )


def pagina_mantenimiento() -> rx.Component:
    return rx.theme(
        rx.cond(
            EstadoAutenticacion.rol_usuario == "administrador",
            layout_principal(contenido_mantenimiento()),
            rx.center(
                rx.vstack(
                    rx.icon("lock", size=48, color="#475569"),
                    rx.heading("Acceso Restringido", size="6", color="#1E293B"),
                    rx.text(
                        "Solo los administradores pueden ver esta página.",
                        color="#334155",
                    ),
                    rx.link(rx.button("Volver al Inicio"), href="/"),
                ),
                width="100vw",
                height="100vh",
                background_color="#F8F9FF",
            ),
        ),
        appearance="light",
        has_background=True,
    )
