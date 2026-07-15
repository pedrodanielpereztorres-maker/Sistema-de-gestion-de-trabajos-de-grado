#!/usr/bin/env python3
"""Inserta trabajos de grado públicos distribuidos por carrera.

Uso: ejecuta desde la raíz del proyecto.
Crea placeholders en `almacen_privado/trabajo_de_grado` y marca `es_publica=TRUE`.
"""
import os
import random
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import bcrypt
import psycopg2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rxconfig import URL_BASE_DATOS  # noqa: E402

OUTPUT_DIR = os.path.join("almacen_privado", "trabajo_de_grado")
TOTAL_PER_CARRERA = 30

FIRST_WORDS = [
    "Análisis",
    "Estudio",
    "Diseño",
    "Implementación",
    "Evaluación",
    "Propuesta",
    "Desarrollo",
    "Optimización",
]
SECOND_WORDS = [
    "de Sistemas",
    "de Redes",
    "de Seguridad",
    "de Aplicaciones",
    "de Datos",
    "de Procesos",
    "de Interfaces",
]


def get_connection():
    url = urlparse(URL_BASE_DATOS)
    return psycopg2.connect(
        dbname=url.path.lstrip("/"),
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
    )


def main():
    random.seed(2)
    start = time.time()
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, nombre FROM carrera WHERE esta_activa = TRUE ORDER BY id;")
        carreras = cur.fetchall()
        if not carreras:
            print("No hay carreras activas.")
            return

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        inserted = 0
        for carrera_id, carrera_nombre in carreras:
            for i in range(TOTAL_PER_CARRERA):
                try:
                    titulo = f"{random.choice(FIRST_WORDS)} {random.choice(SECOND_WORDS)} {i+1} - {carrera_nombre}"
                    ruta = f"trabajo_de_grado/public_{carrera_id}_{i+1}.pdf"

                    # Buscar un estudiante de la carrera; si no hay, crear uno mínimo
                    cur.execute(
                        "SELECT id FROM estudiante WHERE carrera_id = %s ORDER BY id LIMIT 1;",
                        (carrera_id,),
                    )
                    row = cur.fetchone()
                    if row:
                        estudiante_id = row[0]
                    else:
                        # crear usuario+estudiante mínimo
                        cedula = str(80000000 + carrera_id * 1000 + i)
                        nombre = f"Auto{carrera_id}{i}"
                        apellido = "Auto"
                        correo = f"auto_public_{carrera_id}_{i}@example.com"
                        password_hash = bcrypt.hashpw(
                            b"Password123!", bcrypt.gensalt()
                        ).decode("utf-8")
                        # rol estudiante
                        cur.execute("SELECT id FROM rol WHERE LOWER(nombre) = 'estudiante';")
                        rol_row = cur.fetchone()
                        if not rol_row:
                            raise SystemExit("No se encontró el rol 'Estudiante'.")
                        rol_id = rol_row[0]
                        cur.execute(
                            "INSERT INTO usuario (cedula, nombre, apellido, correo, contrasena_hash, rol_id, esta_activo) VALUES (%s,%s,%s,%s,%s,%s,TRUE) RETURNING id;",
                            (cedula, nombre, apellido, correo, password_hash, rol_id),
                        )
                        usuario_id = cur.fetchone()[0]
                        cur.execute(
                            "INSERT INTO estudiante (usuario_id, cedula, nombre, apellido, carrera_id, periodo_inicio, periodo_cierre, celular, esta_activo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,TRUE) RETURNING id;",
                            (usuario_id, cedula, nombre, apellido, carrera_id, date.today(), date.today(), '04120000000'),
                        )
                        estudiante_id = cur.fetchone()[0]

                    # Insertar trabajo
                    cur.execute(
                        "INSERT INTO trabajo_de_grado (titulo, es_publica, ruta_archivo, estudiante_id) VALUES (%s, TRUE, %s, %s) RETURNING id;",
                        (titulo, ruta, estudiante_id),
                    )
                    _ = cur.fetchone()[0]
                    conn.commit()

                    # crear archivo placeholder
                    filepath = os.path.join(OUTPUT_DIR, f"public_{carrera_id}_{i+1}.pdf")
                    try:
                        with open(filepath, "wb") as f:
                            f.write(b"%PDF-1.4\n%placeholder public\n")
                    except Exception as e:
                        print(f"Error creando archivo {filepath}: {e}")

                    inserted += 1
                except Exception as e:
                    conn.rollback()
                    print("Error insertando trabajo:", e)

        total_time = time.time() - start
        print(f"Insertados: {inserted} trabajos públicos. Tiempo: {total_time:.2f}s")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
