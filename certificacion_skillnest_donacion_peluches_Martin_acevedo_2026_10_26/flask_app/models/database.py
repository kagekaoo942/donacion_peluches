from pathlib import Path

import mysql.connector
from flask import current_app, g


class Database:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, parameters=()):
        # Los controladores usan ? porque es una notación cómoda y conocida;
        # aquí la convertimos al formato %s que espera el conector de MySQL.
        cursor = self.connection.cursor(dictionary=True)
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
    if ssl_ca:
        options["ssl_ca"] = ssl_ca
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
    schema = Path(schema_file).read_text(encoding="utf-8")
    connection = mysql.connector.connect(
        **connection_options(host, port, user, password, ssl_ca=ssl_ca)
    )
    cursor = connection.cursor()
    try:
        for statement in schema.split(";"):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        connection.commit()
    finally:
        cursor.close()
        connection.close()
