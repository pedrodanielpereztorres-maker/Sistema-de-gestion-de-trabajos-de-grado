import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sistema_gestion_trabajo_grado.estado.estado_dashboard import (  # noqa: E402
    EstadoDashboard,
)


class FakeCursor:
    def __init__(self, fetchone_responses=None, fetchall_responses=None):
        self.fetchone_responses = fetchone_responses or []
        self.fetchall_responses = fetchall_responses or []
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return self.fetchone_responses.pop(0) if self.fetchone_responses else None

    def fetchall(self):
        return self.fetchall_responses.pop(0) if self.fetchall_responses else []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class FakeConn:
    def __init__(self, cursor):
        self.cursor_obj = cursor
        self.closed = False

    def cursor(self):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def close(self):
        self.closed = True


class TestEstadoDashboard(unittest.TestCase):
    def test_cargar_dashboard_llena_valores_correctamente(self):
        estado = EstadoDashboard()
        fake_cursor = FakeCursor(
            fetchone_responses=[
                (504, 342, 162),  # resumen global
                (24,),  # total tesis
                (14, 10),  # públicas/privadas
            ],
            fetchall_responses=[
                [
                    ("Análisis de Sistemas", 161),
                    ("Electrónica", 172),
                    ("Administración Industrial", 171),
                ],
                [
                    ("V001", "Juan", "Pérez", "Análisis de Sistemas"),
                ],
                [
                    ("V002", "Ana", "Gómez", "Electrónica"),
                ],
            ],
        )
        fake_conn = FakeConn(fake_cursor)

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_dashboard.obtener_conexion",
            return_value=fake_conn,
        ):
            asyncio.run(estado.cargar_dashboard())

        self.assertEqual(estado.total_estudiantes, 504)
        self.assertEqual(estado.estudiantes_en_pasantia, 342)
        self.assertEqual(estado.estudiantes_sin_pasantia, 162)
        self.assertEqual(estado.total_trabajos_de_grado, 24)
        self.assertEqual(estado.trabajos_de_grado_publicos, 14)
        self.assertEqual(estado.trabajos_de_grado_privados, 10)

        self.assertEqual(len(estado.estudiantes_por_carrera), 3)
        self.assertEqual(estado.estudiantes_por_carrera[0].carrera, "Electrónica")
        self.assertEqual(estado.estudiantes_por_carrera[0].cantidad, 172)

        self.assertEqual(len(estado.lista_con_pasantia), 1)
        self.assertEqual(len(estado.lista_sin_pasantia), 1)

    def test_integridad_total_estudiantes_sumas(self):
        estado = EstadoDashboard()
        estado._total_estudiantes = 504
        estado._estudiantes_en_pasantia = 342
        estado._estudiantes_sin_pasantia = 162

        self.assertEqual(
            estado.total_estudiantes,
            estado.estudiantes_en_pasantia + estado.estudiantes_sin_pasantia,
        )


if __name__ == "__main__":
    unittest.main()
