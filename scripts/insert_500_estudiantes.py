#!/usr/bin/env python3
"""Inserta 500 estudiantes sintéticos en la base de datos del proyecto."""

import random
from datetime import date, timedelta
from urllib.parse import urlparse

import bcrypt
import psycopg2

from rxconfig import URL_BASE_DATOS

FIRST_NAMES = [
    "Alejandro", "Camila", "Diego", "Valentina", "Santiago", "Isabella",
    "Mateo", "María", "Lucas", "Sofía", "Daniel", "Victoria",
    "Julián", "Gabriela", "Sebastián", "Natalia", "Andrés", "Camila",
    "Nicolás", "Florencia", "José", "Laura", "Adrián", "Antonella",
    "Cristian", "Paula", "Fernando", "Lucía", "Manuel", "Elena"
]
LAST_NAMES = [
    "González", "Rodríguez", "Pérez", "Martínez", "Gómez", "Díaz",
    "Fernández", "López", "Hernández", "Jiménez", "Sánchez", "Ramírez",
    "Torres", "Flores", "Rivera", "Castro", "Ortiz", "Ramos",
    "Ruiz", "Vargas", "Mendoza", "Cruz", "Rojas", "Núñez",
    "Silva", "Guerrero", "Cárdenas", "Herrera", "Arias", "Navarro"
]

EMAIL_DOMAIN = "example.com"
START_CEDULA = 60000000
TOTAL_STUDENTS = 500
PASSWORD = "Password123!"
BATCH_SIZE = 100


def get_connection():
    url = urlparse(URL_BASE_DATOS)
    return psycopg2.connect(
        dbname=url.path.lstrip("/"),
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
    )


def build_student_data(index: int):
    cedula = str(START_CEDULA + index)
    nombre = random.choice(FIRST_NAMES)
    apellido = random.choice(LAST_NAMES)
    correo = f"estudiante{START_CEDULA + index}@{EMAIL_DOMAIN}"
    celular = f"0412{random.randint(1000000, 9999999)}"
    inicio = date(2025, 1, 1) + timedelta(days=random.randint(0, 365))
    cierre = inicio + timedelta(days=90 + random.randint(0, 60))
    return cedula, nombre, apellido, correo, celular, inicio, cierre


def main():
    random.seed(42)
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM rol WHERE LOWER(nombre) = 'estudiante';")
    rol_row = cursor.fetchone()
    if not rol_row:
        raise SystemExit("No se encontró el rol 'Estudiante' en la base de datos.")
    rol_id = rol_row[0]

    cursor.execute("SELECT id FROM carrera WHERE esta_activa = TRUE ORDER BY id;")
    carreras = [row[0] for row in cursor.fetchall()]
    if not carreras:
        raise SystemExit("No se encontraron carreras activas en la base de datos.")

    cursor.execute("SELECT id FROM tutor_academico WHERE esta_activo = TRUE ORDER BY id;")
    tutores_academicos = [row[0] for row in cursor.fetchall()]

    password_hash = bcrypt.hashpw(PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    inserted = 0
    for i in range(TOTAL_STUDENTS):
        cedula, nombre, apellido, correo, celular, inicio, cierre = build_student_data(i)
        carrera_id = random.choice(carreras)
        tutor_academico_id = random.choice(tutores_academicos) if tutores_academicos else None

        cursor.execute(
            "SELECT 1 FROM usuario WHERE cedula = %s OR correo = %s;",
            (cedula, correo),
        )
        if cursor.fetchone():
            print(f"Saltando estudiante existente {cedula} / {correo}")
            continue

        cursor.execute(
            "INSERT INTO usuario (cedula, nombre, apellido, correo, contrasena_hash, rol_id, esta_activo) VALUES (%s, %s, %s, %s, %s, %s, TRUE) RETURNING id;",
            (cedula, nombre, apellido, correo, password_hash, rol_id),
        )
        usuario_id = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO estudiante (usuario_id, cedula, nombre, apellido, carrera_id, tutor_academico_id, periodo_inicio, periodo_cierre, celular, esta_activo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE);",
            (
                usuario_id,
                cedula,
                nombre,
                apellido,
                carrera_id,
                tutor_academico_id,
                inicio,
                cierre,
                celular,
            ),
        )
        inserted += 1

        if inserted % BATCH_SIZE == 0:
            connection.commit()
            print(f"Insertados {inserted} estudiantes...")

    connection.commit()
    print(f"Inserción completada: {inserted} estudiantes agregados.")
    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()
