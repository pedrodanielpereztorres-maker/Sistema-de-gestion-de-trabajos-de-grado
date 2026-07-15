import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sistema_gestion_trabajo_grado.estado.estado_estudiante import EstadoEstudiante


class TestEstadoEstudianteFilters(unittest.TestCase):
    def test_estudiantes_filtrados_aplica_rango_de_fechas_de_cierre(self):
        estado = EstadoEstudiante()
        estado.lista_estudiantes = [
            SimpleNamespace(
                cedula="123",
                nombre="Ana",
                apellido="Pérez",
                carrera="Ingeniería",
                telefono_personal="",
                periodo_inicio="2024-01-01",
                periodo_cierre="2024-01-15",
                fecha_inicio_formateada="01/01/2024",
                fecha_cierre_formateada="15/01/2024",
                nombre_tutor="",
                carrera_tutor="",
                tutor_empresa="",
                nombre_empresa="",
                direccion_empresa="",
                correo_empresa="",
                telefono_empresa="",
                inicial="A",
            ),
            SimpleNamespace(
                cedula="456",
                nombre="Luis",
                apellido="Gómez",
                carrera="Ingeniería",
                telefono_personal="",
                periodo_inicio="2024-01-01",
                periodo_cierre="2024-02-15",
                fecha_inicio_formateada="01/01/2024",
                fecha_cierre_formateada="15/02/2024",
                nombre_tutor="",
                carrera_tutor="",
                tutor_empresa="",
                nombre_empresa="",
                direccion_empresa="",
                correo_empresa="",
                telefono_empresa="",
                inicial="L",
            ),
        ]
        estado.filtro_fecha_cierre_inicio = "2024-01-01"
        estado.filtro_fecha_cierre_fin = "2024-01-31"

        resultado = estado.estudiantes_filtrados

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["nombre"], "Ana")


if __name__ == "__main__":
    unittest.main()
