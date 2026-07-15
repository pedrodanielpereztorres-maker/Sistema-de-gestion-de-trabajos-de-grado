#!/usr/bin/env python3
"""Completa 500 estudiantes insertados con empresas y tutores asignados."""

import random
import sys
from pathlib import Path
from urllib.parse import urlparse

import psycopg2

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from rxconfig import URL_BASE_DATOS  # noqa: E402

COMPANY_NAMES = [
    "InnovaTech",
    "AgroPlus",
    "EducaLab",
    "LogiSoft",
    "GlobalFoods",
    "EcoEnergia",
    "MetaServicios",
    "BuildMax",
    "SaludVida",
    "TransaPro",
    "AquaNova",
    "TecnoSol",
    "GreenLine",
    "Urbania",
    "SmartWare",
    "MegaLogistics",
    "BioHealth",
    "CulturaLab",
    "DataConnect",
    "IntegraCorp",
]
COMPANY_CITIES = [
    "Valencia",
    "Barinas",
    "Maracaibo",
    "Puerto Ordaz",
    "Barquisimeto",
    "San Fernando",
    "Maturín",
    "Barcelona",
    "Ciudad Bolívar",
    "Cumana",
]
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
    "Daniel",
    "Victoria",
    "Julián",
    "Gabriela",
    "Sebastián",
    "Natalia",
    "Andrés",
    "Nicolás",
    "Laura",
    "Fernando",
    "Mariana",
    "Pablo",
    "Carolina",
    "Jorge",
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
    "Hernández",
    "Jiménez",
    "Sánchez",
    "Ramírez",
    "Torres",
    "Flores",
    "Rivera",
    "Castro",
    "Ortiz",
    "Ramos",
    "Ruiz",
    "Herrera",
    "Arias",
    "Medina",
    "Vargas",
    "Silva",
]
ACADEMIC_SPECIALTIES = [
    "Análisis de Datos",
    "Seguridad Informática",
    "Gestión de Proyectos",
    "Ingeniería de Software",
    "Redes y Telecomunicaciones",
    "Desarrollo Web",
    "Inteligencia Artificial",
    "Bases de Datos",
    "Sistemas Embebidos",
    "Arquitectura de Computadores",
]
PHONE_PREFIXES = ["0412", "0414", "0416", "0424", "0426"]


def get_connection():
    url = urlparse(URL_BASE_DATOS)
    return psycopg2.connect(
        dbname=url.path.lstrip("/"),
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
    )


def build_company_data(index: int):
    name = COMPANY_NAMES[index % len(COMPANY_NAMES)]
    city = COMPANY_CITIES[index % len(COMPANY_CITIES)]
    return (
        f"{name} {index + 1}",
        f"Calle {10 + index} de {city}",
        f"contacto{index + 1}@{name.lower()}.com",
        f"{PHONE_PREFIXES[index % len(PHONE_PREFIXES)]}{random.randint(1000000, 9999999)}",
        f"Empresa dedicada a soluciones de {name.lower()} y servicios profesionales.",
    )


def build_tutor_empresarial_data(index: int, company_id: int):
    nombre = random.choice(FIRST_NAMES)
    apellido = random.choice(LAST_NAMES)
    return (
        f"{nombre} {apellido}",
        (
            f"{nombre.lower()}."
            f"{apellido.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')}"
            f"@empresa{company_id}.com"
        ),
        f"{PHONE_PREFIXES[index % len(PHONE_PREFIXES)]}{random.randint(1000000, 9999999)}",
        company_id,
    )


def build_academic_tutor_data(index: int, carrera_id: int):
    nombre = random.choice(FIRST_NAMES)
    apellido = random.choice(LAST_NAMES)
    specialty = random.choice(ACADEMIC_SPECIALTIES)
    email = (
        f"{nombre.lower()}."
        f"{apellido.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')}"
        f"@tis.edu.vc"
    )
    phone = (
        f"{PHONE_PREFIXES[index % len(PHONE_PREFIXES)]}"
        f"{random.randint(1000000, 9999999)}"
    )
    cedula = str(50000000 + index)
    return nombre, apellido, email, phone, carrera_id, specialty, cedula


def main():
    random.seed(42)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM carrera WHERE esta_activa = TRUE ORDER BY id;")
    careers = [row[0] for row in cur.fetchall()]
    if not careers:
        raise SystemExit("No career records found.")

    cur.execute("SELECT id, nombre, correo, telefono FROM empresa ORDER BY id;")
    existing_companies = cur.fetchall()
    for company in existing_companies:
        company_id, name, correo, telefono = company
        if not correo or not telefono:
            updated_email = (
                correo or f"contacto{company_id}@{name.replace(' ', '').lower()}.com"
            )
            updated_phone = (
                telefono
                or f"{random.choice(PHONE_PREFIXES)}{random.randint(1000000, 9999999)}"
            )
            cur.execute(
                "UPDATE empresa SET correo=%s, telefono=%s WHERE id=%s;",
                (updated_email, updated_phone, company_id),
            )

    num_new_companies = max(0, 15 - len(existing_companies))
    company_ids = [row[0] for row in existing_companies]
    for i in range(num_new_companies):
        nombre, direccion, correo, telefono, descripcion = build_company_data(i)
        cur.execute(
            "INSERT INTO empresa (nombre, direccion, correo, telefono, descripcion) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
            (nombre, direccion, correo, telefono, descripcion),
        )
        company_ids.append(cur.fetchone()[0])

    # Crear tutores empresariales
    cur.execute("SELECT id FROM tutor_empresarial ORDER BY id;")
    existing_te = [row[0] for row in cur.fetchall()]
    tutor_emp_ids = existing_te.copy()
    needed_te = max(0, 50 - len(existing_te))
    for i in range(needed_te):
        company_id = random.choice(company_ids)
        nombre, correo, telefono, empresa_id = build_tutor_empresarial_data(
            i, company_id
        )
        cur.execute(
            "INSERT INTO tutor_empresarial (nombre, correo, telefono, empresa_id) VALUES (%s, %s, %s, %s) RETURNING id;",
            (nombre, correo, telefono, empresa_id),
        )
        tutor_emp_ids.append(cur.fetchone()[0])

    # Crear tutores académicos
    cur.execute("SELECT id FROM tutor_academico ORDER BY id;")
    academic_ids = [row[0] for row in cur.fetchall()]
    needed_academic = max(0, 30 - len(academic_ids))
    for i in range(needed_academic):
        carrera_id = random.choice(careers)
        nombre, apellido, correo, telefono, carrera_id, especialidad, cedula = (
            build_academic_tutor_data(i, carrera_id)
        )
        cur.execute(
            "INSERT INTO tutor_academico (usuario_id, cedula, nombre, apellido, correo, telefono, carrera_id, especialidad, esta_activo) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, TRUE) RETURNING id;",
            (cedula, nombre, apellido, correo, telefono, carrera_id, especialidad),
        )
        academic_ids.append(cur.fetchone()[0])

    # Assign tutors/companies to inserted students
    cur.execute(
        "SELECT id, cedula FROM estudiante WHERE cedula >= '60000000' ORDER BY id;"
    )
    students = cur.fetchall()
    if not students:
        raise SystemExit("No matching students found to update.")

    for student_id, cedula in students:
        tutor_academico_id = random.choice(academic_ids)
        tutor_empresarial_id = random.choice(tutor_emp_ids)
        cur.execute(
            "UPDATE estudiante SET tutor_academico_id=%s, tutor_empresarial_id=%s WHERE id=%s;",
            (tutor_academico_id, tutor_empresarial_id, student_id),
        )

    conn.commit()
    print(f"Updated {len(students)} students with company and tutor assignments.")
    print(f"Total companies: {len(company_ids)}")
    print(f"Total tutor_empresarial: {len(tutor_emp_ids)}")
    print(f"Total tutor_academico: {len(academic_ids)}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
