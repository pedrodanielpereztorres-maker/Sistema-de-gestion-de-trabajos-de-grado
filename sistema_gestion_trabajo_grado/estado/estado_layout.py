import reflex as rx


class EstadoLayout(rx.State):
    """Controla la visibilidad del menú lateral en dispositivos móviles."""

    menu_abierto: bool = False

    def abrir_menu(self):
        self.menu_abierto = True

    def cerrar_menu(self):
        self.menu_abierto = False

    def alternar_menu(self):
        self.menu_abierto = not self.menu_abierto
