import asyncio
import logging
import reflex as rx
from dataclasses import dataclass
from typing import List
from pydantic import Field

from ..database_manager import obtener_conexion

logger = logging.getLogger(__name__)


@dataclass
class EstadisticaCarrera:
    carrera: str
    cantidad: int
    progreso: int


@dataclass
class EstudiantePasantia:
    cedula: str
    nombre: str
    apellido: str
    carrera: str


def _fetch_dashboard_data():
    conn = obtener_conexion()
    if conn is None:
        logger.error("No hay conexión para cargar métricas del dashboard.")
        return None

    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS total,
                        COUNT(*) FILTER (WHERE tutor_academico_id IS NOT NULL) AS con_pasantia,
                        COUNT(*) FILTER (WHERE tutor_academico_id IS NULL) AS sin_pasantia
                    FROM estudiante
                    WHERE esta_activo = TRUE
                    """
                )
                conteo_general = cursor.fetchone() or (0, 0, 0)
                total = int(conteo_general[0] or 0)
                con_pasantia = int(conteo_general[1] or 0)
                sin_pasantia = int(conteo_general[2] or 0)

                cursor.execute("SELECT COUNT(*) FROM trabajo_de_grado")
                total_tesis = int((cursor.fetchone() or (0,))[0] or 0)

                cursor.execute(
                    """
                    SELECT
                        COUNT(*) FILTER (WHERE es_publica = TRUE) AS publicas,
                        COUNT(*) FILTER (WHERE es_publica = FALSE) AS privadas
                    FROM trabajo_de_grado
                    """
                )
                publicas_privadas = cursor.fetchone() or (0, 0)
                publicas = int(publicas_privadas[0] or 0)
                privadas = int(publicas_privadas[1] or 0)

                cursor.execute(
                    """
                    SELECT c.nombre, COUNT(e.id) AS cantidad
                    FROM carrera c
                    LEFT JOIN estudiante e
                        ON e.carrera_id = c.id
                        AND e.esta_activo = TRUE
                    WHERE c.esta_activa = TRUE
                    GROUP BY c.nombre
                    ORDER BY cantidad DESC, c.nombre ASC
                    """
                )
                filas_carreras = cursor.fetchall() or []
                filas_carreras_ordenadas = sorted(
                    filas_carreras,
                    key=lambda fila: (int(fila[1] or 0), str(fila[0] or "")),
                    reverse=True,
                )
                max_cantidad = max((int(fila[1] or 0) for fila in filas_carreras_ordenadas), default=1)
                estudiantes_por_carrera = [
                    EstadisticaCarrera(
                        carrera=fila[0] or "Sin Carrera",
                        cantidad=int(fila[1] or 0),
                        progreso=int(round((int(fila[1] or 0) / max_cantidad) * 100)),
                    )
                    for fila in filas_carreras_ordenadas
                ]

                cursor.execute(
                    """
                    SELECT e.cedula, e.nombre, e.apellido, COALESCE(c.nombre, 'Sin Carrera')
                    FROM estudiante e
                    LEFT JOIN carrera c ON c.id = e.carrera_id
                    WHERE e.esta_activo = TRUE AND e.tutor_academico_id IS NOT NULL
                    ORDER BY e.id ASC
                    LIMIT 10
                    """
                )
                filas_con_pasantia = cursor.fetchall() or []
                lista_con_pasantia = [
                    EstudiantePasantia(
                        cedula=fila[0] or "",
                        nombre=fila[1] or "",
                        apellido=fila[2] or "",
                        carrera=fila[3] or "Sin Carrera",
                    )
                    for fila in filas_con_pasantia
                ]

                cursor.execute(
                    """
                    SELECT e.cedula, e.nombre, e.apellido, COALESCE(c.nombre, 'Sin Carrera')
                    FROM estudiante e
                    LEFT JOIN carrera c ON c.id = e.carrera_id
                    WHERE e.esta_activo = TRUE AND e.tutor_academico_id IS NULL
                    ORDER BY e.id ASC
                    LIMIT 10
                    """
                )
                filas_sin_pasantia = cursor.fetchall() or []
                lista_sin_pasantia = [
                    EstudiantePasantia(
                        cedula=fila[0] or "",
                        nombre=fila[1] or "",
                        apellido=fila[2] or "",
                        carrera=fila[3] or "Sin Carrera",
                    )
                    for fila in filas_sin_pasantia
                ]

        return {
            "total": total,
            "con_pasantia": con_pasantia,
            "sin_pasantia": sin_pasantia,
            "total_tesis": total_tesis,
            "publicas": publicas,
            "privadas": privadas,
            "estudiantes_por_carrera": estudiantes_por_carrera,
            "lista_con_pasantia": lista_con_pasantia,
            "lista_sin_pasantia": lista_sin_pasantia,
        }
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


class EstadoDashboard(rx.State):
    _total_estudiantes: int = 0
    _estudiantes_en_pasantia: int = 0
    _estudiantes_sin_pasantia: int = 0
    _total_tesis: int = 0
    tesis_publicas: int = 0
    tesis_privadas: int = 0
    estudiantes_por_carrera: List[EstadisticaCarrera] = []
    lista_con_pasantia: List[EstudiantePasantia] = []
    lista_sin_pasantia: List[EstudiantePasantia] = []

    @rx.var
    def total_estudiantes(self) -> int:
        return int(self._total_estudiantes)

    @rx.var
    def top_carreras(self) -> List[EstadisticaCarrera]:
        """Devuelve la lista de carreras ordenada por cantidad (descendente).

        Esto evita intentar ordenar una Var en la vista y permite usar
        `rx.foreach(EstadoDashboard.top_carreras, ...)`.
        """
        try:
            return sorted(self.estudiantes_por_carrera or [], key=lambda x: getattr(x, "cantidad", 0), reverse=True)
        except Exception:
            return self.estudiantes_por_carrera or []

    @rx.var
    def estudiantes_en_pasantia(self) -> int:
        return int(self._estudiantes_en_pasantia)

    @rx.var
    def estudiantes_sin_pasantia(self) -> int:
        return int(self._estudiantes_sin_pasantia)

    @rx.var
    def total_tesis(self) -> int:
        return int(self._total_tesis)

    async def cargar_dashboard(self) -> None:
        """Carga todas las métricas del dashboard usando SQL puro y datos frescos."""
        try:
            data = await asyncio.to_thread(_fetch_dashboard_data)
            if not data:
                return

            self.estudiantes_por_carrera = data["estudiantes_por_carrera"]
            self.lista_con_pasantia = data["lista_con_pasantia"]
            self.lista_sin_pasantia = data["lista_sin_pasantia"]
            self._total_estudiantes = data["total"]
            self._estudiantes_en_pasantia = data["con_pasantia"]
            self._estudiantes_sin_pasantia = data["sin_pasantia"]
            self._total_tesis = data["total_tesis"]
            self.tesis_publicas = data["publicas"]
            self.tesis_privadas = data["privadas"]
        except Exception as e:
            logger.exception("Error al cargar métricas del dashboard: %s", e)
