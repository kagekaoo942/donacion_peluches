from pathlib import Path

import mysql.connector
from flask import current_app, g


class Database:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, parameters=()):
        # Los controladores usan ? porque es una notación cómoda y conocida;
        # aquí la convertimos al formato %s que espera el conector de MySQL.
        # buffered=True evita el error "InternalError: Unread result found" con fetchone()
        cursor = self.connection.cursor(dictionary=True, buffered=True)
        cursor.execute(query.replace("?", "%s"), parameters)
        return cursor

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()


def connection_options(host, port, user, password, database=None, ssl_ca=None):
    options = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
    }
    if database:
        options["database"] = database
    if ssl_ca and Path(ssl_ca).exists():
        options["ssl_ca"] = str(Path(ssl_ca).resolve())
        options["ssl_verify_cert"] = True
        options["ssl_verify_identity"] = True
    return options


def get_db():
    # Una conexión por petición evita abrir conexiones nuevas en cada consulta
    # y permite cerrarla de forma ordenada al terminar la petición.
    if "db" not in g:
        connection = mysql.connector.connect(
            **connection_options(
                current_app.config["MYSQL_HOST"],
                current_app.config["MYSQL_PORT"],
                current_app.config["MYSQL_USER"],
                current_app.config["MYSQL_PASSWORD"],
                current_app.config["MYSQL_DATABASE"],
                current_app.config["MYSQL_SSL_CA"],
            )
        )
        g.db = Database(connection)
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(schema_file, host, port, user, password, database, ssl_ca=None):
    # El esquema vive en un archivo SQL para que también pueda ejecutarse
    # directamente desde MySQL Workbench y no quede escondido en Python.
    schema_path = Path(schema_file)
    if not schema_path.exists():
        return
    schema = schema_path.read_text(encoding="utf-8")

    # Intentamos conectar directamente a la base de datos configurada
    try:
        connection = mysql.connector.connect(
            **connection_options(
                host, port, user, password, database=database, ssl_ca=ssl_ca
            )
        )
    except mysql.connector.Error as err:
        # Si la base de datos no existe (error 1049: Unknown database), intentar crearla
        if getattr(err, "errno", None) == 1049:
            admin_conn = mysql.connector.connect(
                **connection_options(host, port, user, password, ssl_ca=ssl_ca)
            )
            admin_cur = admin_conn.cursor()
            admin_cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
            admin_conn.commit()
            admin_cur.close()
            admin_conn.close()
            connection = mysql.connector.connect(
                **connection_options(
                    host, port, user, password, database=database, ssl_ca=ssl_ca
                )
            )
        else:
            raise err

    cursor = connection.cursor()
    try:
        for statement in schema.split(";"):
            statement = statement.strip()
            if not statement:
                continue
            upper_stmt = statement.upper()
            # Ignorar sentencias CREATE DATABASE o USE porque ya estamos conectados a la BD
            if upper_stmt.startswith("CREATE DATABASE") or upper_stmt.startswith("USE "):
                continue
            cursor.execute(statement)
        connection.commit()
    finally:
        cursor.close()
        connection.close()
