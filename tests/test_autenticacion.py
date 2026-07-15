import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sistema_gestion_trabajo_grado.estado.estado_autenticacion import (  # noqa: E402
    EncriptadorContrasena,
)


class TestAutenticacion(unittest.TestCase):

    def test_encriptar_y_verificar_password(self):
        texto_plano = "Prueba123!"
        hash_generado = EncriptadorContrasena.encriptar(texto_plano)

        self.assertTrue(EncriptadorContrasena.verificar(texto_plano, hash_generado))
        self.assertFalse(EncriptadorContrasena.verificar("otra123", hash_generado))

    def test_env_example_contiene_placeholders(self):
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


if __name__ == "__main__":
    unittest.main()
