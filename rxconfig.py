import os

import reflex as rx
from dotenv import load_dotenv
from reflex.plugins.sitemap import SitemapPlugin

load_dotenv()

USUARIO_BD = os.getenv("DB_USER")
CLAVE_BD = os.getenv("DB_PASSWORD")
HOST_BD = os.getenv("DB_HOST")
PUERTO_BD = os.getenv("DB_PORT")
NOMBRE_BD = os.getenv("DB_NAME")

URL_BASE_DATOS = (
    f"postgresql+psycopg2://{USUARIO_BD}:{CLAVE_BD}@{HOST_BD}:{PUERTO_BD}/{NOMBRE_BD}"
)
#API_URL = os.getenv("API_URL", "http://127.0.0.1:3000")

config = rx.Config(
    app_name="sistema_gestion_trabajo_grado",
    env=rx.Env.PROD,
    db_url=URL_BASE_DATOS,
    #api_url=API_URL,
    disable_plugins=[SitemapPlugin],
    show_built_with_reflex=False,
    # Esto ayuda al cliente a encontrar el servidor cuando se usa Nginx
)
