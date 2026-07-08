#!/usr/bin/env python3
"""Inserta 50 trabajos de grado (tesis) sintéticos en la base de datos.

Comportamiento:
- Usa URL_BASE_DATOS desde `rxconfig` para conectar por psycopg2.
- Asegura que haya suficientes estudiantes; crea los que faltan.
- Inserta hasta 50 filas en `trabajo_de_grado`, una por estudiante sin trabajo.
- Crea archivos placeholder en `almacen_privado/trabajo_de_grado` para simular almacenamiento.
- Imprime métricas: intentos, insertados, saltados, errores, tiempo total.
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

# Asegurar que el directorio raíz del proyecto esté en sys.path cuando se ejecuta
# este script desde la carpeta `scripts/`.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rxconfig import URL_BASE_DATOS

OUTPUT_DIR = os.path.join("almacen_privado", "trabajo_de_grado")
TOTAL = 50

FIRST_NAMES = [
    "Alejandro",
    "Camila",
    "Diego",
    "Valentina",
    "Santiago",
    "Isabella",
    "Mateo",
    "María",
    "Lucas",
    "Sofía",
]
LAST_NAMES = [
    "González",
    "Rodríguez",
    "Pérez",
    "Martínez",
    "Gómez",
    "Díaz",
    "Fernández",
    "López",
]

START_CEDULA = 70000000
PASSWORD = "Password123!"


def get_connection():
    url = urlparse(URL_BASE_DATOS)
    return psycopg2.connect(
        dbname=url.path.lstrip("/"),
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
    )


def ensure_students(cursor, needed):
    cursor.execute("SELECT id, cedula FROM estudiante ORDER BY id;")
    existentes = cursor.fetchall()
    if len(existentes) >= needed:
        return [row[0] for row in existentes][:needed]

    # necesitamos crear más estudiantes
    cursor.execute("SELECT id FROM rol WHERE LOWER(nombre) = 'estudiante';")
    rol_row = cursor.fetchone()
    if not rol_row:
        raise SystemExit("No se encontró el rol 'Estudiante' en la base de datos.")
    rol_id = rol_row[0]

    cursor.execute("SELECT id FROM carrera WHERE esta_activa = TRUE ORDER BY id;")
    carreras = [row[0] for row in cursor.fetchall()]
    if not carreras:
        raise SystemExit("No se encontraron carreras activas en la base de datos.")

    cursor.execute(
        "SELECT id FROM tutor_academico WHERE esta_activo = TRUE ORDER BY id;"
    )
    tutores = [row[0] for row in cursor.fetchall()]

    created = []
    index = 0
    while len(existentes) + len(created) < needed:
        cedula = str(START_CEDULA + index)
        nombre = random.choice(FIRST_NAMES)
        apellido = random.choice(LAST_NAMES)
        correo = f"auto{cedula}@example.com"
        celular = f"0412{random.randint(1000000,9999999)}"

        cursor.execute(
            "SELECT 1 FROM usuario WHERE cedula = %s OR correo = %s;",
            (cedula, correo),
        )
        if cursor.fetchone():
            index += 1
            continue

        password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute(
            "INSERT INTO usuario (cedula, nombre, apellido, correo, contrasena_hash, rol_id, esta_activo) VALUES (%s,%s,%s,%s,%s,%s,TRUE) RETURNING id;",
            (cedula, nombre, apellido, correo, password_hash, rol_id),
        )
        usuario_id = cursor.fetchone()[0]
        carrera_id = random.choice(carreras)
        tutor_id = random.choice(tutores) if tutores else None

        cursor.execute(
            "INSERT INTO estudiante (usuario_id, cedula, nombre, apellido, carrera_id, tutor_academico_id, periodo_inicio, periodo_cierre, celular, esta_activo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,TRUE) RETURNING id;",
            (
                usuario_id,
                cedula,
                nombre,
                apellido,
                carrera_id,
                tutor_id,
                date.today(),
                date.today(),
                celular,
            ),
        )
        estudiante_id = cursor.fetchone()[0]
        created.append(estudiante_id)
        index += 1

    all_students = [row[0] for row in existentes] + created
    return all_students[:needed]


def main():
    random.seed(1)
    start = time.time()
    conn = get_connection()
    cur = conn.cursor()

    try:
        # obtener lista de estudiantes candidatos
        cur.execute("SELECT id FROM estudiante ORDER BY id;")
        rows = cur.fetchall()
        all_estudiantes = [r[0] for r in rows]
        estudiantes = ensure_students(cur, TOTAL)
        conn.commit()

        inserted = 0
        skipped = 0
        errors = []

        os.makedirs(OUTPUT_DIR, exist_ok=True)

        for i, estudiante_id in enumerate(estudiantes[:TOTAL]):
            try:
                # comprobar si ya existe trabajo_de_grado para el estudiante
                cur.execute("SELECT id FROM trabajo_de_grado WHERE estudiante_id = %s;", (estudiante_id,))
                if cur.fetchone():
                    skipped += 1
                    continue

                titulo = f"Tesis sintética {i+1}"
                ruta = f"trabajo_de_grado/placeholder_{i+1}.pdf"
                cur.execute(
                    "INSERT INTO trabajo_de_grado (titulo, es_publica, ruta_archivo, estudiante_id) VALUES (%s, %s, %s, %s) RETURNING id;",
                    (titulo, False, ruta, estudiante_id),
                )
                trabajo_id = cur.fetchone()[0]
                conn.commit()

                # crear archivo placeholder
                filepath = os.path.join(OUTPUT_DIR, f"placeholder_{i+1}.pdf")
                try:
                    with open(filepath, "wb") as f:
                        f.write(b"%PDF-1.4\n%placeholder\n")
                except Exception as e:
                    errors.append(f"Error creando archivo {filepath}: {e}")

                inserted += 1
            except Exception as e:
                conn.rollback()
                errors.append(str(e))

        total_time = time.time() - start
        print(f"Intentos: {TOTAL}, Insertados: {inserted}, Saltados: {skipped}, Errores: {len(errors)}, Tiempo: {total_time:.2f}s")
        if errors:
            print("Errores (muestra 10):", errors[:10])

        # report disk usage of folder
        total_bytes = 0
        total_files = 0
        for root, dirs, files in os.walk(OUTPUT_DIR):
            for name in files:
                total_files += 1
                try:
                    total_bytes += os.path.getsize(os.path.join(root, name))
                except Exception:
                    pass
        print(f"Archivos en {OUTPUT_DIR}: {total_files}, tamaño total: {total_bytes/1024:.1f} KB")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
