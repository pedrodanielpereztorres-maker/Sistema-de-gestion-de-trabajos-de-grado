import reflex as rx


def toast_viewer() -> rx.Component:
    return rx.toast.provider(position="bottom-right")
