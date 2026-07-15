import asyncio
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, mock_open, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["PYTEST_CURRENT_TEST"] = "1"

from sistema_gestion_trabajo_grado.estado.estado_boveda import (  # noqa: E402
    EstadoBoveda,
)


class FakeCursor:
    def __init__(self, fetchall_responses=None, fetchone_responses=None):
        self.fetchall_responses = fetchall_responses or []
        self.fetchone_responses = fetchone_responses or []
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchall(self):
        return self.fetchall_responses.pop(0) if self.fetchall_responses else []

    def fetchone(self):
        return self.fetchone_responses.pop(0) if self.fetchone_responses else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class FakeConn:
    def __init__(self, cursor):
        self.cursor_obj = cursor
        self.committed = False
        self.closed = False

    def cursor(self):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.commit()
        return False

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


class FakeAuthState:
    def __init__(self, usuario_id=1, rol_usuario="estudiante", cedula="12345678"):
        self.usuario = type("U", (), {"id": usuario_id, "cedula": cedula})
        self.rol_usuario = rol_usuario


class FakeUploadFile:
    def __init__(self, filename, data):
        self.filename = filename
        self._data = data

    async def read(self):
        return self._data


class TestEstadoBoveda(unittest.TestCase):

    def test_lista_filtrada_filtra_por_carrera_y_busqueda(self):
        estado = EstadoBoveda()
        estado.lista_trabajos_de_grado = [
            {
                "id": 1,
                "carrera": "Sistemas",
                "titulo": "Trabajo de grado A",
                "nombre_estudiante": "Juan",
                "cedula_estudiante": "123",
            },
            {
                "id": 2,
                "carrera": "Administración",
                "titulo": "Gestión B",
                "nombre_estudiante": "Ana",
                "cedula_estudiante": "456",
            },
        ]
        estado.filtro_carrera = "Sistemas"
        estado.busqueda_dinamica = "trabajo de grado"

        resultado = estado.lista_filtrada

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["id"], 1)

    def test_trabajos_de_grado_visibles_muestra_privadas_solo_del_usuario(self):
        estado = EstadoBoveda()
        estado.lista_trabajos_de_grado = [
            {"id": 1, "publico": False, "usuario_id": 9},
            {"id": 2, "publico": False, "usuario_id": 1},
            {"id": 3, "publico": True, "usuario_id": 2},
        ]
        estado.usuario_actual_id = 1

        visibles = estado.trabajos_de_grado_visibles
        self.assertEqual({t["id"] for t in visibles}, {2, 3})

    def test_trabajos_de_grado_paginados_retorna_segmento_correcto(self):
        estado = EstadoBoveda()
        estado.lista_trabajos_de_grado = [
            {"id": i, "publico": True, "usuario_id": 1} for i in range(1, 10)
        ]
        estado.pagina_actual = 2
        estado.elementos_por_pagina = 3

        paginados = estado.trabajos_de_grado_paginados

        self.assertEqual([t["id"] for t in paginados], [4, 5, 6])

    def test_opciones_carreras_agrega_todas_las_carreras(self):
        estado = EstadoBoveda()
        estado.carreras_disponibles = ["Sistemas", "Derecho"]
        self.assertEqual(
            estado.opciones_carreras, ["Todas las carreras", "Sistemas", "Derecho"]
        )

    def test_balance_privacidad_trabajos_de_grado_calcuala_correctamente(self):
        estado = EstadoBoveda()
        estado.lista_trabajos_de_grado = [
            {"publico": True},
            {"publico": False},
            {"publico": False},
        ]
        balance = estado.balance_privacidad_trabajos_de_grado
        self.assertEqual(balance[0]["valor"], 1)
        self.assertEqual(balance[1]["valor"], 2)

    def test_generar_reporte_trabajos_de_grado_sin_datos_devuelve_warning(self):
        estado = EstadoBoveda()
        estado.lista_trabajos_de_grado = []
        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_boveda.rx.toast.warning",
            return_value="warning",
        ):
            self.assertEqual(estado.generar_reporte_trabajos_de_grado(), "warning")

    def test_abrir_modal_confirmacion_y_cerrar(self):
        estado = EstadoBoveda()
        estado.abrir_modal_confirmacion(5)
        self.assertTrue(estado.mostrar_modal_confirmacion)
        self.assertEqual(estado.trabajo_de_grado_id_a_eliminar, 5)

        estado.cerrar_modal_confirmacion()
        self.assertFalse(estado.mostrar_modal_confirmacion)
        self.assertEqual(estado.trabajo_de_grado_id_a_eliminar, 0)

    def test_buscar_estudiante_sin_cedula_devuelve_warning(self):
        estado = EstadoBoveda()
        estado.cedula_busqueda = ""
        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_boveda.rx.toast.warning",
            return_value="warning",
        ):
            resultado = asyncio.run(estado.buscar_estudiante())
        self.assertEqual(resultado, "warning")

    def test_confirmar_eliminacion_trabajo_de_grado_con_contrasena_invalida(self):
        estado = EstadoBoveda()
        estado.trabajo_de_grado_id_a_eliminar = 10
        estado.password_confirmacion = "wrongpass"

        fake_auth = FakeAuthState(usuario_id=1, rol_usuario="administrador")
        with patch.object(
            EstadoBoveda, "get_state", new=AsyncMock(return_value=fake_auth)
        ):
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_boveda.obtener_conexion",
                return_value=FakeConn(FakeCursor(fetchone_responses=[("hash",)])),
            ):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_boveda.EncriptadorContrasena.verificar",
                    return_value=False,
                ):
                    with patch(
                        "sistema_gestion_trabajo_grado.estado.estado_boveda.rx.toast.error",
                        return_value="error_pass",
                    ):
                        resultado = asyncio.run(
                            estado.confirmar_eliminacion_trabajo_de_grado()
                        )
        self.assertEqual(resultado, "error_pass")

    def test_confirmar_eliminacion_trabajo_de_grado_exitoso(self):
        estado = EstadoBoveda()
        estado.trabajo_de_grado_id_a_eliminar = 10
        estado.password_confirmacion = "correctpass"

        fake_auth = FakeAuthState(usuario_id=1, rol_usuario="administrador")
        with patch.object(
            EstadoBoveda, "get_state", new=AsyncMock(return_value=fake_auth)
        ):
            cursor = FakeCursor(fetchone_responses=[("hash",)])
            conn = FakeConn(cursor)
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_boveda.obtener_conexion",
                return_value=conn,
            ):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_boveda.EncriptadorContrasena.verificar",
                    return_value=True,
                ):
                    with patch(
                        "sistema_gestion_trabajo_grado.estado.estado_boveda.rx.toast.success",
                        return_value="success",
                    ):
                        with patch.object(
                            EstadoBoveda,
                            "cargar_trabajos_de_grado",
                            new=AsyncMock(return_value=None),
                        ):
                            resultado = asyncio.run(
                                estado.confirmar_eliminacion_trabajo_de_grado()
                            )
        self.assertEqual(resultado, "success")
        self.assertFalse(estado.mostrar_modal_confirmacion)

    def test_registrar_trabajo_de_grado_sin_permiso_devuelve_error(self):
        estado = EstadoBoveda()
        estado.cedula_busqueda = "12345678"
        estado.titulo_trabajo_de_grado = "Mi tesis"
        estado.nombre_encontrado = "Juan"
        estado.en_edicion = False

        fake_auth = FakeAuthState(usuario_id=2, rol_usuario="estudiante")
        with patch.object(
            EstadoBoveda, "get_state", new=AsyncMock(return_value=fake_auth)
        ):
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_boveda.rx.toast.error",
                return_value="error_perm",
            ):
                resultado = asyncio.run(
                    estado.registrar_trabajo_de_grado(
                        [FakeUploadFile("tesis.pdf", b"%PDF-1.4")]
                    )
                )
        self.assertEqual(resultado, "error_perm")

    def test_registrar_trabajo_de_grado_sin_estudiante_registrado(self):
        estado = EstadoBoveda()
        estado.cedula_busqueda = "12345678"
        estado.titulo_trabajo_de_grado = "Mi tesis"
        estado.nombre_encontrado = "Juan"

        fake_auth = FakeAuthState(usuario_id=1, rol_usuario="administrador")
        with patch.object(
            EstadoBoveda, "get_state", new=AsyncMock(return_value=fake_auth)
        ):
            conn = FakeConn(FakeCursor(fetchone_responses=[None]))
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_boveda.obtener_conexion",
                return_value=conn,
            ):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_boveda.rx.toast.error",
                    return_value="error_student",
                ):
                    resultado = asyncio.run(
                        estado.registrar_trabajo_de_grado(
                            [FakeUploadFile("tesis.pdf", b"%PDF-1.4")]
                        )
                    )
        self.assertEqual(resultado, "error_student")

    def test_registrar_trabajo_de_grado_exitoso_almacena_bd(self):
        estado = EstadoBoveda()
        estado.cedula_busqueda = "12345678"
        estado.titulo_trabajo_de_grado = "Mi tesis"
        estado.nombre_encontrado = "Juan"

        fake_auth = FakeAuthState(usuario_id=1, rol_usuario="administrador")
        with patch.object(
            EstadoBoveda, "get_state", new=AsyncMock(return_value=fake_auth)
        ):
            conn = FakeConn(FakeCursor(fetchone_responses=[[42]]))
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_boveda.obtener_conexion",
                return_value=conn,
            ):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_boveda.os.makedirs",
                    return_value=None,
                ):
                    with patch("builtins.open", mock_open()):
                        with patch(
                            "sistema_gestion_trabajo_grado.estado.estado_boveda.rx.toast.success",
                            return_value="success",
                        ):
                            with patch.object(
                                EstadoBoveda,
                                "cargar_trabajos_de_grado",
                                new=AsyncMock(return_value=None),
                            ):
                                resultado = asyncio.run(
                                    estado.registrar_trabajo_de_grado(
                                        [FakeUploadFile("tesis.pdf", b"%PDF-1.4")]
                                    )
                                )
        self.assertEqual(resultado, "success")
        self.assertTrue(conn.committed)


if __name__ == "__main__":
    unittest.main()
