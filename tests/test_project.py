import importlib
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import reflex as rx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

database_manager = importlib.import_module(
    "sistema_gestion_trabajo_grado.database_manager"
)


class TestProyecto(unittest.TestCase):

    def test_gitignore_ignora_env_y_no_env_example(self):
        contenido = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".env", contenido)
        self.assertIn(".env.local", contenido)
        self.assertIn("!.env.example", contenido)

    def test_env_example_existe_y_contiene_placeholders(self):
        archivo_ejemplo = ROOT / ".env.example"
        self.assertTrue(
            archivo_ejemplo.exists(),
            ".env.example debe existir en la raíz del proyecto",
        )

        contenido = archivo_ejemplo.read_text(encoding="utf-8")
        self.assertIn("DB_HOST=localhost", contenido)
        self.assertIn("DB_NAME=db_trabajo_grado", contenido)
        self.assertIn("DB_USER=postgres", contenido)
        self.assertIn("DB_PASSWORD=tu_contraseña_aqui", contenido)

    def test_rxconfig_lee_variables_del_entorno(self):
        os.environ["DB_HOST"] = "localhost"
        os.environ["DB_PORT"] = "5432"
        os.environ["DB_NAME"] = "db_trabajo_grado"
        os.environ["DB_USER"] = "postgres"
        os.environ["DB_PASSWORD"] = "secret123"

        import rxconfig

        importlib.reload(rxconfig)

        self.assertIn("postgres", rxconfig.URL_BASE_DATOS)
        self.assertIn("db_trabajo_grado", rxconfig.URL_BASE_DATOS)
        self.assertIn("localhost", rxconfig.URL_BASE_DATOS)

    def test_obtener_conexion_retorna_none_sin_db_url(self):
        # Forzar que no haya URL de BD en la configuración de Reflex
        original_get_config = rx.config.get_config
        rx.config.get_config = lambda: SimpleNamespace(db_url="")
        database_manager._motor = None
        try:
            self.assertIsNone(database_manager.obtener_conexion())
        finally:
            rx.config.get_config = original_get_config


if __name__ == "__main__":
    unittest.main()
