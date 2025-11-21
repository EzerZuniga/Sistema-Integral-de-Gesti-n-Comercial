"""Listar usuarios desde la base de datos (SQLite o MySQL).

Uso (PowerShell):
  # Si quieres usar MySQL, exporta las variables de entorno antes:
  $env:APP_DB_TYPE = 'mysql'
  $env:APP_DB_HOST = 'localhost'
  $env:APP_DB_PORT = '3306'
  $env:APP_DB_USER = 'root'
  $env:APP_DB_PASSWORD = 'tu_password'
  $env:APP_DB_NAME = 'donarosa'

  & ".\.venv\Scripts\Activate.ps1"
  python scripts/list_users.py

Si usas SQLite (por defecto) solo ejecuta:
  python scripts/list_users.py
"""
import sqlite3
import os
from pathlib import Path

from config.environment import env

def list_sqlite_users(db_path: Path):
    if not db_path.exists():
        print(f"No existe {db_path}")
        return
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute('SELECT id, username, nombre, email, rol, activo, created_at FROM usuarios').fetchall()
    for r in rows:
        print(dict(r))
    con.close()

def list_mysql_users():
    try:
        import pymysql
        from pymysql.cursors import DictCursor
    except Exception as e:
        print('PyMySQL no está instalado. Instálalo con: pip install PyMySQL')
        return

    conn = pymysql.connect(host=env.mysql_host, port=env.mysql_port, user=env.mysql_user,
                           password=env.mysql_password, database=env.mysql_database,
                           cursorclass=DictCursor)
    cur = conn.cursor()
    cur.execute('SELECT id, username, nombre, email, rol, activo, created_at FROM usuarios')
    rows = cur.fetchall()
    for r in rows:
        print(r)
    conn.close()

def main():
    dbtype = os.getenv('APP_DB_TYPE', 'sqlite').lower()
    if dbtype == 'mysql':
        print('Usando MySQL:')
        list_mysql_users()
    else:
        print('Usando SQLite:')
        list_sqlite_users(env.database_path)

if __name__ == '__main__':
    main()
import sqlite3
import pathlib
from pathlib import Path
import sys

base = Path(__file__).parent.parent
db = base / 'data' / 'bodega.db'
if not db.exists():
    print('NO_DB')
    sys.exit(0)
con = sqlite3.connect(str(db))
con.row_factory = sqlite3.Row
cur = con.cursor()
print('USERS:')
for row in cur.execute('SELECT id, username, nombre, email, rol, activo FROM usuarios'):
    print(dict(row))
con.close()
