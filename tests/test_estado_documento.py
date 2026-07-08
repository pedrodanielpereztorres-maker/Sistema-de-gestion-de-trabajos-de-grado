import sys
import unittest
import asyncio
import builtins
import os
from pathlib import Path
from unittest.mock import patch, mock_open

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["PYTEST_CURRENT_TEST"] = "1"

from sistema_gestion_trabajo_grado.estado.estado_documento import (
    EstadoDocumento,
    Documento,
)


class FakeUploadFile:
    def __init__(self, filename, data):
        self.filename = filename
        self._data = data

    async def read(self):
        return self._data


class FakeCursor:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchall(self):
        return []

    def fetchone(self):
        return self.responses.pop(0) if self.responses else None

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
        return False

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


class TestEstadoDocumento(unittest.TestCase):

    def test_documentos_filtrados_devuelve_resultados(self):
        doc1 = Documento(
            id=1,
            titulo="Informe final",
            descripcion="Resumen",
            fecha_subida="01/01/2024",
            tipo="pdf",
            tamano_kb=42,
            tamano="42 KB",
            url="/doc1",
        )
        doc2 = Documento(
            id=2,
            titulo="Plan de tesis",
            descripcion="Estructura",
            fecha_subida="02/01/2024",
            tipo="pdf",
            tamano_kb=10,
            tamano="10 KB",
            url="/doc2",
        )

        estado = EstadoDocumento()
        estado.lista_documentos = [doc1, doc2]
        estado.fijar_busqueda_documento("plan")

        filtrados = estado.documentos_filtrados

        self.assertEqual(len(filtrados), 1)
        self.assertEqual(filtrados[0].id, 2)

    def test_cancelar_publicacion_resetea_campos(self):
        estado = EstadoDocumento()
        estado.titulo_nuevo = "Título"
        estado.descripcion_nueva = "Desc"

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_documento.rx.clear_selected_files",
            return_value="clear_called",
        ):
            resultado = estado.cancelar_publicacion()

        self.assertEqual(resultado, "clear_called")
        self.assertEqual(estado.titulo_nuevo, "")
        self.assertEqual(estado.descripcion_nueva, "")

    def test_publicar_documento_sin_titulo_devuelve_error(self):
        estado = EstadoDocumento()
        archivo = FakeUploadFile("doc.pdf", b"%PDF-1.4")

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_documento.rx.toast.error",
            return_value="error_title",
        ):
            resultado = asyncio.run(estado.publicar_documento([archivo]))

        self.assertEqual(resultado, "error_title")

    def test_publicar_documento_extencion_no_permitida(self):
        estado = EstadoDocumento()
        estado.titulo_nuevo = "Informe"
        archivo = FakeUploadFile("archivo.exe", b"MZ...")

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_documento.rx.toast.error",
            return_value="error_type",
        ):
            resultado = asyncio.run(estado.publicar_documento([archivo]))

        self.assertEqual(resultado, "error_type")

    def test_publicar_documento_magic_bytes_incorrectos(self):
        estado = EstadoDocumento()
        estado.titulo_nuevo = "Informe"
        archivo = FakeUploadFile("archivo.pdf", b"GIF89a")

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_documento.rx.toast.error",
            return_value="error_magic",
        ):
            resultado = asyncio.run(estado.publicar_documento([archivo]))

        self.assertEqual(resultado, "error_magic")

    def test_publicar_documento_tamano_maximo_superado(self):
        estado = EstadoDocumento()
        estado.titulo_nuevo = "Informe"
        archivo = FakeUploadFile("archivo.pdf", b"%PDF" + b"A" * (20 * 1024 * 1024 + 1))

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_documento.rx.toast.error",
            return_value="error_size",
        ):
            resultado = asyncio.run(estado.publicar_documento([archivo]))

        self.assertEqual(resultado, "error_size")

    def test_publicar_documento_exitoso_inserta_bd_y_escribe_archivo(self):
        estado = EstadoDocumento()
        estado.titulo_nuevo = "Informe"
        estado.descripcion_nueva = "Descripción breve"
        archivo = FakeUploadFile("archivo.pdf", b"%PDF-1.4 ejemplo")

        cursor = FakeCursor(responses=[[1]])
        conn = FakeConn(cursor)

        async def dummy_cargar_documentos():
            return None

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_documento.obtener_conexion",
            return_value=conn,
        ):
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_documento.rx.toast.success",
                return_value="success",
            ):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_documento.os.makedirs",
                    return_value=None,
                ):
                    with patch("builtins.open", mock_open()):
                        with patch.object(
                            EstadoDocumento,
                            "cargar_documentos",
                            dummy_cargar_documentos,
                        ):
                            resultado = asyncio.run(
                                estado.publicar_documento([archivo])
                            )

        self.assertEqual(resultado, "success")
        self.assertEqual(estado.titulo_nuevo, "")
        self.assertEqual(estado.descripcion_nueva, "")
        self.assertTrue(conn.committed)


if __name__ == "__main__":
    unittest.main()
