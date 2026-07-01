import asyncio
import logging
import os
import reflex as rx
from datetime import date
from pydantic import BaseModel
from typing import List
from ..database_manager import obtener_conexion

logger = logging.getLogger(__name__)


class Documento(BaseModel):
    id: int = 0
    titulo: str = ""
    descripcion: str = ""
    fecha_subida: str = ""
    tipo: str = ""
    tamano_kb: int = 0
    tamano: str = "0 KB"
    url: str = ""


class EstadoDocumento(rx.State):
    lista_documentos: list[Documento] = []

    titulo_nuevo: str = ""
    descripcion_nueva: str = ""
    procesando: bool = False

    # Variable para el texto de búsqueda del usuario
    busqueda_documento: str = ""

    mostrar_modal_edicion: bool = False
    id_edicion: int = 0
    titulo_edicion: str = ""
    descripcion_edicion: str = ""

    async def cargar_documentos(self):
        """Carga la lista de documentos desde la base de datos."""
        def _fetch_documentos():
            conn = obtener_conexion()
            if conn is None:
                logger.error("Sin conexión para cargar documentos.")
                return []
            try:
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT id, titulo, descripcion, fecha_subida, tipo, tamano_kb, ruta_archivo 
                            FROM documento 
                            ORDER BY fecha_subida DESC;
                        """)
                        return cursor.fetchall()
            except Exception as exc:
                logger.exception("Error al cargar documentos: %s", exc)
                return []
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

        resultados = await asyncio.to_thread(_fetch_documentos)
        self.lista_documentos = [
            Documento(
                id=fila[0],
                titulo=fila[1],
                descripcion=fila[2],
                fecha_subida=fila[3].strftime("%d/%m/%Y") if fila[3] else "",
                tipo=fila[4],
                tamano_kb=fila[5] or 0,
                tamano=f"{fila[5]} KB" if fila[5] is not None else "0 KB",
                url=f"{rx.config.get_config().api_url}/almacen/{fila[6].lstrip('/')}" if fila[6] else ""
            ) for fila in resultados
        ]

    def fijar_titulo_nuevo(self, val: str) -> None:
        self.titulo_nuevo = val

    def fijar_descripcion_nueva(self, val: str) -> None:
        self.descripcion_nueva = val

    def fijar_busqueda_documento(self, valor: str) -> None:
        """Actualiza el texto de búsqueda de documentos."""
        self.busqueda_documento = valor

    @rx.var
    def documentos_filtrados(self) -> list[Documento]:
        """Retorna los documentos filtrados según la búsqueda activa."""
        if not self.busqueda_documento.strip():
            return self.lista_documentos

        texto = self.busqueda_documento.strip().lower()
        return [
            doc for doc in self.lista_documentos
            if (
                texto in doc.titulo.lower() or
                texto in doc.descripcion.lower()
            )
        ]

    async def publicar_documento(self, archivos: List[rx.UploadFile]):
        """Publica uno o varios documentos validando tipo (magic bytes), tamaño y sanitizando nombres.

        El flujo es: leer en memoria -> validar -> insertar registro en BD -> escribir archivo en disco.
        Si la escritura falla, se elimina el registro en BD para evitar inconsistencias.
        """
        if not self.titulo_nuevo:
            self.procesando = False
            return rx.toast.error("Debes ingresar un título para el documento.")

        TIPOS_PERMITIDOS = {
            "pdf": b"%PDF",
            "docx": b"PK\x03\x04",
            "doc": b"\xd0\xcf\x11\xe0",
            "xlsx": b"PK\x03\x04",
            "pptx": b"PK\x03\x04",
            "png": b"\x89PNG",
            "jpg": b"\xff\xd8\xff",
        }

        MAX_TAMANO_BYTES = 20 * 1024 * 1024  # 20MB

        self.procesando = True
        archivos_creados_bd_ids = []

        async def _insert_registro_documento(titulo: str, descripcion: str, extension: str, tamano_kb: int, ruta_bd: str):
            def _insert():
                conn2 = obtener_conexion()
                if conn2 is None:
                    return None
                try:
                    with conn2:
                        with conn2.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO documento (titulo, descripcion, tipo, tamano_kb, ruta_archivo)
                                VALUES (%s, %s, %s, %s, %s)
                                RETURNING id;
                            """, (
                                titulo,
                                descripcion,
                                extension, tamano_kb, ruta_bd
                            ))
                            nuevo_id = cursor.fetchone()[0]
                        conn2.commit()
                    return nuevo_id
                except Exception as exc:
                    logger.exception("Error al insertar documento en BD: %s", exc)
                    return None
                finally:
                    try:
                        conn2.close()
                    except Exception:
                        pass

            return await asyncio.to_thread(_insert)

        def _delete_registro_documento(documento_id: int):
            conn2 = obtener_conexion()
            if conn2 is None:
                return False
            try:
                with conn2:
                    with conn2.cursor() as c2:
                        c2.execute("DELETE FROM documento WHERE id = %s", (documento_id,))
                    conn2.commit()
                return True
            except Exception as exc:
                logger.exception("Fallo en limpieza de BD: %s", exc)
                return False
            finally:
                try:
                    conn2.close()
                except Exception:
                    pass

        try:
            for archivo in archivos:
                datos_subida = await archivo.read()
                if len(datos_subida) > MAX_TAMANO_BYTES:
                    return rx.toast.error(f"El archivo {archivo.filename} supera el límite de 20MB.")

                # Determinar extensión y validar
                extension = archivo.filename.split('.')[-1].lower() if '.' in archivo.filename else ""
                if extension not in TIPOS_PERMITIDOS:
                    return rx.toast.error(f"Tipo de archivo no permitido: {extension}")

                magic = TIPOS_PERMITIDOS[extension]
                if not datos_subida.startswith(magic):
                    return rx.toast.error(f"El archivo {archivo.filename} no cumple con los bytes mágicos esperados para .{extension}.")

                # Sanitizar nombre y preparar rutas
                import re as _re
                nombre_limpio = _re.sub(r"[^\w\.-]", "_", archivo.filename)
                nombre_final = f"doc_{date.today().isoformat()}_{nombre_limpio}"
                ruta_bd = f"documentos/{nombre_final}"
                ruta_destino = os.path.join("almacen_privado", "documentos", nombre_final)

                # Insertar registro en BD y obtener id
                nuevo_id = await _insert_registro_documento(
                    self.titulo_nuevo,
                    self.descripcion_nueva or "Sin descripción",
                    extension,
                    max(1, len(datos_subida) // 1024),
                    ruta_bd,
                )
                if nuevo_id is None:
                    return rx.toast.error("Error al guardar el registro del documento en la base de datos.")

                # Escribir archivo en disco; si falla, eliminar registro BD creado
                try:
                    os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                    with open(ruta_destino, "wb") as f:
                        f.write(datos_subida)
                    archivos_creados_bd_ids.append((nuevo_id, ruta_destino))
                except Exception as e:
                    logger.error("Error al escribir archivo en disco: %s", e)
                    await asyncio.to_thread(_delete_registro_documento, nuevo_id)
                    return rx.toast.error(f"Error al guardar el archivo {archivo.filename} en el servidor.")

            # Si llegamos aquí, todos los archivos se procesaron correctamente
            self.titulo_nuevo = ""
            self.descripcion_nueva = ""
            await self.cargar_documentos()
            return rx.toast.success("Documento(s) publicado(s) correctamente.")

        except Exception as e:
            # Limpieza general en caso de fallo inesperado
            def _cleanup_documento(documento_id: int):
                conn2 = obtener_conexion()
                if conn2 is None:
                    return False
                try:
                    with conn2:
                        with conn2.cursor() as c2:
                            c2.execute("DELETE FROM documento WHERE id = %s", (documento_id,))
                        conn2.commit()
                    return True
                except Exception as exc:
                    logger.exception("Fallo en limpieza de BD durante la publicación: %s", exc)
                    return False
                finally:
                    try:
                        conn2.close()
                    except Exception:
                        pass

            for (_id, ruta) in archivos_creados_bd_ids:
                try:
                    if os.path.exists(ruta):
                        os.remove(ruta)
                    await asyncio.to_thread(_cleanup_documento, _id)
                except Exception:
                    pass
            logger.exception("Error crítico al publicar documentos: %s", e)
            return rx.toast.error(f"Error al publicar el documento: {e}")
        finally:
            self.procesando = False

    def cancelar_publicacion(self):
        """Limpia los campos del formulario de publicación."""
        self.titulo_nuevo = ""
        self.descripcion_nueva = ""
        return rx.clear_selected_files("upload_docs")

    async def eliminar_documento(self, id_documento: int):
        def _delete_documento(documento_id: int):
            conn2 = obtener_conexion()
            if conn2 is None:
                return None
            try:
                with conn2:
                    with conn2.cursor() as cursor:
                        cursor.execute("SELECT ruta_archivo FROM documento WHERE id = %s;", (documento_id,))
                        res_archivo = cursor.fetchone()
                        cursor.execute("DELETE FROM documento WHERE id = %s;", (documento_id,))
                    conn2.commit()
                    return res_archivo[0] if res_archivo else None
            except Exception as exc:
                logger.exception("Error al eliminar documento: %s", exc)
                return None
            finally:
                try:
                    conn2.close()
                except Exception:
                    pass

        ruta_bd = await asyncio.to_thread(_delete_documento, id_documento)
        if ruta_bd is None:
            return rx.toast.error("Error al eliminar el documento.")

        if ruta_bd:
            ruta_fisica = os.path.join("almacen_privado", ruta_bd)
            if os.path.exists(ruta_fisica):
                try:
                    os.remove(ruta_fisica)
                except Exception:
                    logger.exception("Error al borrar archivo físico de documento: %s", ruta_fisica)

        await self.cargar_documentos()
        return rx.toast.success("Documento eliminado correctamente.")

    def preparar_edicion(self, documento_instancia: Documento):
        self.id_edicion = documento_instancia.id
        self.titulo_edicion = documento_instancia.titulo
        self.descripcion_edicion = documento_instancia.descripcion
        self.mostrar_modal_edicion = True

    def cancelar_edicion(self):
        self.mostrar_modal_edicion = False

    async def guardar_edicion(self):
        """Guarda los cambios realizados en el título y descripción de un documento."""
        if not self.titulo_edicion.strip():
            return rx.toast.error("El título del documento es obligatorio.")

        def _update_documento():
            conn2 = obtener_conexion()
            if conn2 is None:
                return False, "Error de conexión."
            try:
                with conn2:
                    with conn2.cursor() as cursor:
                        cursor.execute("""
                            UPDATE documento 
                            SET titulo = %s, descripcion = %s
                            WHERE id = %s;
                        """, (self.titulo_edicion, self.descripcion_edicion, self.id_edicion))
                    conn2.commit()
                return True, ""
            except Exception as exc:
                logger.exception("Error al actualizar documento: %s", exc)
                return False, str(exc)
            finally:
                try:
                    conn2.close()
                except Exception:
                    pass

        ok, mensaje = await asyncio.to_thread(_update_documento)
        if not ok:
            return rx.toast.error(f"Error al actualizar el documento: {mensaje}")

        await self.cargar_documentos()
        self.mostrar_modal_edicion = False
        return rx.toast.success("Documento actualizado correctamente.")

    def fijar_titulo_edicion(self, val: str) -> None: self.titulo_edicion = val
    def fijar_descripcion_edicion(self, val: str) -> None: self.descripcion_edicion = val

    @rx.var
    def total_documentos(self) -> int:
        return len(self.lista_documentos)
