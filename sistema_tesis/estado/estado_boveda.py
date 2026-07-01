import asyncio
import os
import csv
import io
import re
from datetime import date
from typing import List, Dict, Any
import logging
import reflex as rx
logger = logging.getLogger(__name__)
from ..database_manager import obtener_conexion
from .estado_autenticacion import EstadoAutenticacion, EncriptadorContrasena


class CountProxy:
    """Contenedor simple para exponer un método to_string() usado en la UI.

    Definido a nivel de módulo para que las anotaciones de tipos sean evaluables
    en tiempo de importación por reflex sin depender de referencias hacia la
    propia clase EstadoBoveda.
    """
    def __init__(self, value: int):
        self._value = value

    def to_string(self) -> str:
        return str(self._value)

class EstadoBoveda(rx.State):
    lista_tesis: list[Dict[str, Any]] = []
    carreras_disponibles: list[str] = []
    mostrar_modal: bool = False
    cedula_busqueda: str = ""
    titulo_tesis: str = ""
    procesando: bool = False
    busqueda_dinamica: str = ""
    filtro_carrera: str = ""
    nombre_encontrado: str = ""
    apellido_encontrado: str = ""
    carrera_encontrada: str = ""
    tutor_academico_encontrado: str = ""
    tutor_empresa_encontrado: str = ""
    empresa_encontrada: str = ""
    hacer_publico: bool = False
    trabajo_de_grado_en_edicion_id: int = 0
    en_edicion: bool = False
    ruta_archivo_actual: str = ""  # Para mostrar el archivo actual en edición
    usuario_actual_id: int = 0
    usuario_actual_rol: str = ""

    # Variables para seguridad en eliminación
    mostrar_modal_confirmacion: bool = False
    password_confirmacion: str = ""
    trabajo_de_grado_id_a_eliminar: int = 0

    async def cargar_tesis(self) -> None:
        estado_auth = await self.get_state(EstadoAutenticacion)
        self.usuario_actual_id = estado_auth.usuario.id if estado_auth.usuario else 0
        self.usuario_actual_rol = estado_auth.rol_usuario if estado_auth.usuario else ""

        consulta = """
            SELECT 
                t.id,
                e.cedula, e.nombre, e.apellido, c.nombre as carrera_nom,
                ta.nombre || ' ' || ta.apellido as tutor_acad,
                te.nombre as tutor_emp, emp.nombre as empresa_nom,
                t.titulo, t.es_publica, t.ruta_archivo, e.usuario_id
            FROM trabajo_de_grado t
            LEFT JOIN estudiante e ON t.estudiante_id = e.id
            LEFT JOIN carrera c ON e.carrera_id = c.id
            LEFT JOIN tutor_academico ta ON e.tutor_academico_id = ta.id
            LEFT JOIN tutor_empresarial te ON e.tutor_empresarial_id = te.id
            LEFT JOIN empresa emp ON te.empresa_id = emp.id
        """

        def _fetch_tesis():
            conn = obtener_conexion()
            if conn is None:
                logger.error("Sin conexión para cargar tesis.")
                return None
            try:
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute(consulta)
                        datos = cursor.fetchall()
                        cursor.execute("SELECT nombre FROM carrera WHERE esta_activa = TRUE ORDER BY nombre")
                        carreras = [r[0] for r in cursor.fetchall()]
                return datos, carreras
            except Exception as exc:
                logger.error("Error al cargar tesis: %s", exc, exc_info=True)
                return None
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

        resultado = await asyncio.to_thread(_fetch_tesis)
        if resultado is None:
            return rx.toast.error("Error al cargar tesis.")

        datos, carreras = resultado
        self.lista_tesis = [
            {
                "id": r[0],
                "cedula_estudiante": r[1], "nombre_estudiante": r[2],
                "apellido_estudiante": r[3], "carrera": r[4] or "Sin Carrera",
                "tutor_academico": r[5] or "No asignado",
                "tutor_empresa": r[6] or "No asignado",
                "nombre_empresa": r[7] or "N/A",
                "titulo": r[8], "publico": r[9],
                "url": f"{rx.config.get_config().api_url}/almacen/{r[10]}" if r[10] else "", "usuario_id": r[11]
            } for r in datos
        ]
        self.carreras_disponibles = carreras

    @rx.var
    def lista_filtrada(self) -> list[Dict[str, Any]]:
        resultado = self.lista_tesis
        if self.filtro_carrera and self.filtro_carrera != "Todas las carreras":
            resultado = [
                t for t in resultado
                if t["carrera"] == self.filtro_carrera
            ]
        if self.busqueda_dinamica:
            busqueda = self.busqueda_dinamica.lower()
            resultado = [
                t for t in resultado
                if (
                    busqueda in t["titulo"].lower() or
                    busqueda in t["nombre_estudiante"].lower() or
                    busqueda in t["cedula_estudiante"].lower()
                )
            ]
        return resultado

    @rx.var
    def tesis_visibles(self) -> list[Dict[str, Any]]:
        return [
            t for t in self.lista_filtrada
            if t["publico"] or (t.get("usuario_id") is not None and t.get("usuario_id") == self.usuario_actual_id)
        ]

    @rx.var
    def tesis_a_mostrar(self) -> list[Dict[str, Any]]:
        if self.usuario_actual_rol == "administrador":
            return self.lista_filtrada
        return self.tesis_visibles

    @rx.var
    def opciones_carreras(self) -> list[str]:
        return ["Todas las carreras"] + self.carreras_disponibles

    @rx.var
    def estudiante_encontrado(self) -> bool:
        return bool(self.nombre_encontrado)

    @rx.var
    def balance_privacidad_tesis(self) -> List[Dict[str, Any]]:
        """Retorna conteo de tesis públicas y privadas para mostrar en dashboard."""
        total = len(self.lista_tesis)
        publicas = sum(1 for t in self.lista_tesis if t.get("publico"))
        privadas = max(0, total - publicas)
        return [
            {"tipo": "Públicas", "color": "#10B981", "valor": publicas},
            {"tipo": "Privadas", "color": "#F59E0B", "valor": privadas},
        ]

    @rx.var
    def total_tesis_count(self) -> int:
        """Cantidad de tesis que se mostrarán según filtros y permisos."""
        # len() funciona sobre la lista devuelta por tesis_a_mostrar
        return len(self.tesis_a_mostrar)

    @rx.var
    def total_tesis_display(self) -> int:
        """Contenedor amigable para la UI."""
        return len(self.tesis_a_mostrar)

    @rx.var
    def detalles_estudiante_encontrado(self) -> Dict[str, str]:
        return {
            "Nombre Completo": f"{self.nombre_encontrado} {self.apellido_encontrado}",
            "Carrera": self.carrera_encontrada,
            "Tutor Académico": self.tutor_academico_encontrado,
            "Empresa": f"{self.empresa_encontrada} ({self.tutor_empresa_encontrado})"
        }

    def abrir_modal(self) -> None:
        self.mostrar_modal = True

    def limpiar_filtros(self) -> None:
        self.busqueda_dinamica = ""
        self.filtro_carrera = ""

    def cerrar_modal(self) -> None:
        self.mostrar_modal = False
        self.cedula_busqueda = ""
        self.titulo_tesis = ""
        self.hacer_publico = False
        self.nombre_encontrado = ""
        self.apellido_encontrado = ""
        self.carrera_encontrada = ""
        self.tutor_academico_encontrado = ""
        self.tesis_en_edicion_id = 0
        self.en_edicion = False
        self.ruta_archivo_actual = ""
        self.tutor_empresa_encontrado = ""
        self.empresa_encontrada = ""

    async def fijar_busqueda_dinamica(self, val: str) -> None:
        """Setter simple para la búsqueda dinámica en la UI. Recarga la lista de tesis."""
        try:
            self.busqueda_dinamica = val
        except Exception:
            self.busqueda_dinamica = str(val)
        await self.cargar_tesis()

    def fijar_cedula_busqueda(self, val: str) -> None:
        try:
            self.cedula_busqueda = val
        except Exception:
            self.cedula_busqueda = str(val)

    def fijar_titulo_tesis(self, val: str) -> None:
        try:
            self.titulo_tesis = val
        except Exception:
            self.titulo_tesis = str(val)

    def fijar_hacer_publico(self, val) -> None:
        # El valor puede venir como bool o Var
        try:
            self.hacer_publico = bool(val)
        except Exception:
            self.hacer_publico = str(val).lower() in ("1", "true", "yes")

    def fijar_password_confirmacion(self, val: str) -> None:
        try:
            self.password_confirmacion = val
        except Exception:
            self.password_confirmacion = str(val)

    async def fijar_filtro_carrera(self, val: str) -> None:
        try:
            self.filtro_carrera = val
        except Exception:
            self.filtro_carrera = str(val)
        await self.cargar_tesis()

    def generar_reporte_tesis(self):
        if not self.lista_tesis:
            return rx.toast.warning("No hay tesis registradas para exportar.")
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Cédula", "Nombre", "Apellido", "Carrera", "Tutor Académico", "Tutor Empresarial", "Empresa", "Título", "Pública"])
            for t in self.lista_tesis:
                writer.writerow([
                    t.get("id", ""), t.get("cedula_estudiante", ""), t.get("nombre_estudiante", ""),
                    t.get("apellido_estudiante", ""), t.get("carrera", ""), t.get("tutor_academico", ""),
                    t.get("tutor_empresa", ""), t.get("nombre_empresa", ""),
                    t.get("titulo", ""), "Sí" if t.get("publico", False) else "No",
                ])
            from datetime import datetime
            return rx.download(
                data=output.getvalue(),
                filename=f"reporte_boveda_{datetime.now().strftime('%d_%m_%Y')}.csv"
            )
        except Exception as e:
            logger.error("Error al generar reporte de tesis: %s", e, exc_info=True)
            return rx.toast.error(f"Error al generar reporte: {e}")

    def abrir_modal_confirmacion(self, trabajo_de_grado_id: int) -> None:
        """Abrir modal de confirmación para eliminar trabajo de grado definitivamente."""
        try:
            self.trabajo_de_grado_id_a_eliminar = int(trabajo_de_grado_id)
        except Exception:
            self.trabajo_de_grado_id_a_eliminar = trabajo_de_grado_id
        self.password_confirmacion = ""
        self.mostrar_modal_confirmacion = True

    def cerrar_modal_confirmacion(self) -> None:
        self.mostrar_modal_confirmacion = False
        self.password_confirmacion = ""
        self.trabajo_de_grado_id_a_eliminar = 0

    async def confirmar_eliminacion_trabajo_de_grado(self) -> rx.Component:
        """Elimina el trabajo de grado indicado por trabajo_de_grado_id_a_eliminar si existe.
        Requiere que el usuario ingrese correctamente su contraseña actual de inicio de sesión.
        """
        if not self.trabajo_de_grado_id_a_eliminar:
            return rx.toast.error("No hay trabajo de grado seleccionado para eliminar.")

        if not self.password_confirmacion:
            return rx.toast.error("Debe ingresar su contraseña para confirmar la eliminación.")

        estado_auth = await self.get_state(EstadoAutenticacion)
        if not estado_auth.usuario:
            return rx.toast.error("Sesión no válida o expirada.")

        def _delete_tesis(usuario_id: int, password: str, tesis_id: int):
            conn = obtener_conexion()
            if conn is None:
                return False, "Error de conexión al servidor de base de datos."
            try:
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT contrasena_hash FROM usuario WHERE id = %s", (usuario_id,))
                        resultado = cursor.fetchone()
                        if not resultado:
                            return False, "Usuario no registrado o inactivo."

                        hash_almacenado = resultado[0]
                        if not EncriptadorContrasena.verificar(password, hash_almacenado):
                            return False, "La contraseña ingresada es incorrecta."

                        cursor.execute("DELETE FROM trabajo_de_grado WHERE id = %s", (tesis_id,))
                    conn.commit()
                return True, ""
            except Exception as exc:
                try:
                    conn.rollback()
                except Exception:
                    pass
                logger.exception("Error al eliminar tesis: %s", exc)
                return False, str(exc)
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

        ok, mensaje = await asyncio.to_thread(_delete_tesis, estado_auth.usuario.id, self.password_confirmacion, self.trabajo_de_grado_id_a_eliminar)
        if not ok:
            return rx.toast.error(f"Error al eliminar el trabajo de grado: {mensaje}")

        await self.cargar_tesis()
        self.cerrar_modal_confirmacion()
        return rx.toast.success("Trabajo de grado eliminado permanentemente de la bóveda.")

    async def abrir_modal_edicion(self, trabajo_de_grado_id: int) -> rx.Component:
        self.en_edicion = True
        self.trabajo_de_grado_en_edicion_id = trabajo_de_grado_id
        trabajo_de_grado_a_editar = next(
            (t for t in self.lista_tesis if t["id"] == trabajo_de_grado_id), None)

        if trabajo_de_grado_a_editar:
            self.cedula_busqueda = trabajo_de_grado_a_editar["cedula_estudiante"]
            self.titulo_tesis = trabajo_de_grado_a_editar["titulo"]
            self.hacer_publico = trabajo_de_grado_a_editar["publico"]
            self.ruta_archivo_actual = trabajo_de_grado_a_editar["url"]
            await self.buscar_estudiante()
            self.mostrar_modal = True
        else:
            return rx.toast.error("No se encontró el trabajo de grado seleccionado.")

    async def buscar_estudiante(self) -> rx.Component:
        cedula = self.cedula_busqueda.strip()
        if not cedula:
            return rx.toast.warning("Ingrese una cédula válida.")

        consulta = """
                SELECT 
                    e.nombre, e.apellido, c.nombre as carrera_nom,
                    ta.nombre || ' ' || ta.apellido as tutor_acad,
                    emp.nombre as empresa_nom, te.nombre as tutor_emp
                FROM estudiante e
                LEFT JOIN carrera c ON e.carrera_id = c.id
                LEFT JOIN tutor_academico ta ON e.tutor_academico_id = ta.id
                LEFT JOIN tutor_empresarial te ON e.tutor_empresarial_id = te.id
                LEFT JOIN empresa emp ON te.empresa_id = emp.id
                WHERE e.cedula = %s AND e.esta_activo = TRUE
        """

        def _fetch_estudiante(cedula_val: str):
            conn = obtener_conexion()
            if conn is None:
                return None
            try:
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute(consulta, (cedula_val,))
                        return cursor.fetchone()
            except Exception as exc:
                logger.exception("Error en búsqueda de estudiante: %s", exc)
                return None
            finally:
                try:
                    conn.close()
                except Exception:
                    pass

        resultado = await asyncio.to_thread(_fetch_estudiante, cedula)
        if not resultado:
            return rx.toast.error("Estudiante no encontrado.")

        # Verificar si ya tiene tesis registrada y no estamos en modo edición
        if not self.en_edicion:
            tiene_tesis = any(t.get("cedula_estudiante") == cedula for t in self.lista_tesis)
            if tiene_tesis:
                self.nombre_encontrado = ""
                self.apellido_encontrado = ""
                return rx.toast.error("El estudiante ya posee un trabajo de grado registrado. Use el botón de editar.")

        self.nombre_encontrado, self.apellido_encontrado, self.carrera_encontrada, \
            self.tutor_academico_encontrado, self.empresa_encontrada, \
            self.tutor_empresa_encontrado = resultado

    async def manejar_subida_tesis(self, archivos: list[rx.UploadFile]):
        """Handler para on_drop: valida el formulario antes de registrar.
        Funciona tanto en móvil (on_drop) como en escritorio (botón).
        """
        if not self.cedula_busqueda.strip() or not self.nombre_encontrado:
            return rx.toast.warning("⚠️ Primero busca al estudiante con su cédula antes de subir el archivo.")
        if not self.titulo_tesis.strip():
            return rx.toast.warning("⚠️ Escribe el título de la tesis antes de subir el archivo.")
        return await self.registrar_tesis(archivos)

    async def registrar_tesis(self, archivos: list[rx.UploadFile]) -> rx.Component:

        estado_auth = await self.get_state(EstadoAutenticacion)
        es_admin = estado_auth.rol_usuario == "administrador"

        if not es_admin and self.cedula_busqueda != (estado_auth.usuario.cedula if estado_auth.usuario else ""):
            return rx.toast.error("No tienes permiso para registrar la tesis de otro estudiante.")

        if not self.cedula_busqueda.strip() or not self.titulo_tesis.strip() or not self.nombre_encontrado:
            return rx.toast.warning("Debe buscar un estudiante válido y proporcionar un título.")

        ruta_destino_final = None
        nombre_archivo_seguro = None
        datos_subida = None

        if archivos:
            # Leer bytes y validar magic bytes y tamaño antes de cualquier operación
            archivo = archivos[0]
            datos_subida = await archivo.read()
            MAX_TAMANO_BYTES = 50 * 1024 * 1024
            if len(datos_subida) > MAX_TAMANO_BYTES:
                return rx.toast.error("El archivo supera el límite de 50MB.")
            if not datos_subida.startswith(b"%PDF"):
                return rx.toast.error("El archivo no es un PDF válido.")

            # Sanitizar nombre para evitar path traversal
            extension = archivo.filename.split('.')[-1] if '.' in archivo.filename else 'pdf'
            nombre_original = f"trabajo_de_grado_{self.cedula_busqueda.strip()}.{extension}"
            nombre_archivo_seguro = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', nombre_original)
            ruta_destino = os.path.join("almacen_privado", "trabajo_de_grado", nombre_archivo_seguro)
            ruta_destino_final = f"trabajo_de_grado/{nombre_archivo_seguro}"
        elif self.en_edicion and self.ruta_archivo_actual:
            ruta_destino_final = self.ruta_archivo_actual.lstrip('/')
        else:
            return rx.toast.warning("Debe subir el archivo de la tesis.")

        self.procesando = True

        def _save_tesis(codigo_estudiante: str, titulo: str, publico: bool, ruta: str, en_edicion: bool, trabajo_de_grado_id: int):
            conn2 = obtener_conexion()
            if conn2 is None:
                return False, "Error de conexión al servidor."
            try:
                with conn2:
                    with conn2.cursor() as cursor:
                        cursor.execute("SELECT id FROM estudiante WHERE cedula = %s", (codigo_estudiante,))
                        resultado_estudiante = cursor.fetchone()
                        if not resultado_estudiante:
                            return False, "Error: El estudiante no está registrado."
                        id_estudiante = resultado_estudiante[0]

                        if en_edicion and trabajo_de_grado_id:
                            cursor.execute("""
                                UPDATE trabajo_de_grado
                                SET titulo = %s, es_publica = %s, ruta_archivo = %s, estudiante_id = %s
                                WHERE id = %s;
                            """, (titulo, publico, ruta, id_estudiante, trabajo_de_grado_id))
                        else:
                            cursor.execute("SELECT id FROM trabajo_de_grado WHERE estudiante_id = %s", (id_estudiante,))
                            if cursor.fetchone():
                                return False, "El estudiante ya posee un trabajo de grado registrado. Use el botón de editar."
                                
                            cursor.execute("""
                                INSERT INTO trabajo_de_grado (titulo, es_publica, ruta_archivo, estudiante_id)
                                VALUES (%s, %s, %s, %s);
                            """, (titulo, publico, ruta, id_estudiante))
                    conn2.commit()
                return True, ""
            except Exception as exc:
                try:
                    conn2.rollback()
                except Exception:
                    pass
                logger.exception("Error al registrar tesis en BD: %s", exc)
                return False, str(exc)
            finally:
                try:
                    conn2.close()
                except Exception:
                    pass

        ok, mensaje = await asyncio.to_thread(
            _save_tesis,
            self.cedula_busqueda.strip(),
            self.titulo_tesis,
            self.hacer_publico,
            ruta_destino_final,
            self.en_edicion,
            self.trabajo_de_grado_en_edicion_id,
        )

        if not ok:
            self.procesando = False
            return rx.toast.error(f"Error al registrar en base de datos: {mensaje}")

        if archivos and datos_subida is not None:
            try:
                os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                with open(ruta_destino, "wb") as f:
                    f.write(datos_subida)
            except Exception as e:
                logger.error("Error al escribir archivo de tesis tras commit: %s", e)
                self.procesando = False
                return rx.toast.warning("Tesis registrada en BD, pero hubo un error al guardar el archivo físico.")

        self.procesando = False
        self.cerrar_modal()
        await self.cargar_tesis()
        return rx.toast.success("Tesis procesada correctamente.")



    @rx.var
    def total_tesis(self) -> int:
        """Número total de tesis cargadas (activos)."""
        return len(self.lista_tesis)
