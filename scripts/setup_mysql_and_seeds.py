#!/usr/bin/env python3
"""Crear base de datos MySQL, tabla `usuarios` y seeds (admin / trabajador).

Uso:
  - Configura variables de entorno para la sesión (APP_DB_HOST, APP_DB_PORT, APP_DB_USER,
    APP_DB_PASSWORD, APP_DB_NAME) o usa `root` si lo prefieres para la creación.
  - Ejecuta desde el venv: `python scripts/setup_mysql_and_seeds.py`

El script **NO** sobrescribe usuarios existentes: solo crea la BD/tabla si no existen
y añade los seeds solo si `username` no está presente.
"""
import os
import sys
import pymysql
from datetime import datetime

try:
    # Importar el método de hashing del proyecto
    from core.security import security
except Exception:
    security = None


def get_env(name, default=None):
    return os.getenv(name, default)


def create_database_if_needed(conn, db_name):
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    conn.commit()


def create_table_if_needed(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(150) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                nombre VARCHAR(255),
                email VARCHAR(255),
                rol VARCHAR(50),
                activo TINYINT(1) DEFAULT 1,
                created_at DATETIME
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
    conn.commit()


def user_exists(conn, username):
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM usuarios WHERE username=%s", (username,))
        r = cur.fetchone()
        return (r[0] if r else 0) > 0


def insert_user(conn, username, plain_password, nombre, email, rol='trabajador'):
    if security is None:
        raise RuntimeError("No se pudo importar el módulo de seguridad del proyecto. Ejecuta desde la raíz del proyecto.")
    password_hash = security.hash_password(plain_password)
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO usuarios (username, password_hash, nombre, email, rol, activo, created_at) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (username, password_hash, nombre, email, rol, 1, created_at)
        )
    conn.commit()


def main():
    db_type = get_env('APP_DB_TYPE', 'mysql')
    if db_type.lower() != 'mysql':
        print('APP_DB_TYPE no es "mysql". Ajusta las variables de entorno para usar MySQL.')
        sys.exit(1)

    host = get_env('APP_DB_HOST', '127.0.0.1')
    port = int(get_env('APP_DB_PORT', '3306'))
    user = get_env('APP_DB_USER', 'root')
    pw = get_env('APP_DB_PASSWORD', '')
    db = get_env('APP_DB_NAME', 'donarosa')

    print(f"Conectando a MySQL server {host}:{port} como {user} (no a la BD todavía)...")
    try:
        conn0 = pymysql.connect(host=host, port=port, user=user, password=pw, autocommit=True)
    except Exception as e:
        print('ERROR conectando al servidor MySQL:', repr(e))
        sys.exit(2)

    try:
        create_database_if_needed(conn0, db)
        print(f"Base de datos '{db}' creada o ya existente.")
    finally:
        conn0.close()

    print(f"Conectando a la base de datos '{db}'...")
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=pw, database=db, autocommit=True)
    except Exception as e:
        print('ERROR conectando a la BD:', repr(e))
        sys.exit(3)

    try:
        create_table_if_needed(conn)
        print("Tabla 'usuarios' creada o ya existente.")

        # Seeds
        seeds = [
            ('admin', 'admin123', 'Administrador', 'admin@example.com', 'admin'),
            ('trabajador', 'trabajador123', 'Trabajador', 'trabajador@example.com', 'trabajador')
        ]

        for username, pwd, nombre, email, rol in seeds:
            if user_exists(conn, username):
                print(f"Usuario '{username}' ya existe. Se omite.")
            else:
                insert_user(conn, username, pwd, nombre, email, rol)
                print(f"Usuario seed '{username}' creado.")

        print('Seeds aplicados (si no existían).')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
