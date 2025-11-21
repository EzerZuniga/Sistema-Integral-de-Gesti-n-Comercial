#!/usr/bin/env python3
"""Prueba de conexión a MySQL usando PyMySQL.

Ejecuta este script desde el venv con las variables de entorno configuradas
(`APP_DB_HOST`, `APP_DB_PORT`, `APP_DB_USER`, `APP_DB_PASSWORD`, `APP_DB_NAME`).
"""
import os
import pymysql


def main():
    host = os.getenv("APP_DB_HOST", "127.0.0.1")
    port = int(os.getenv("APP_DB_PORT", "3306"))
    user = os.getenv("APP_DB_USER", "sistcom")
    pw = os.getenv("APP_DB_PASSWORD", "")
    db = os.getenv("APP_DB_NAME", "donarosa")

    print(f"Intentando conectar a MySQL: host={host} port={port} user={user} db={db}")
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=pw, database=db, connect_timeout=5)
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION();")
            ver = cur.fetchone()
            print("MySQL version:", ver)

            # Comprobar existencia de la tabla usuarios
            try:
                cur.execute("SELECT COUNT(*) FROM usuarios;")
                count = cur.fetchone()
                print("Conteo tabla usuarios:", count)
            except Exception as e:
                print("No se pudo consultar la tabla 'usuarios' (tal vez no existe):", e)

        conn.close()
        print("Conexión OK")
    except Exception as e:
        print("ERROR al conectar:", repr(e))


if __name__ == '__main__':
    main()
