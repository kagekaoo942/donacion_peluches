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


def get_db():
    # Una conexión por petición evita abrir conexiones nuevas en cada consulta
    # y permite cerrarla de forma ordenada al terminar la petición.
    if "db" not in g:
        connection = mysql.connector.connect(
            host=current_app.config["MYSQL_HOST"],
            port=current_app.config["MYSQL_PORT"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DATABASE"],
        )
        g.db = Database(connection)
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(schema_file, host, port, user, password, database):
    # El esquema vive en un archivo SQL para que también pueda ejecutarse
    # directamente desde MySQL Workbench y no quede escondido en Python.
    schema = Path(schema_file).read_text(encoding="utf-8")
    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
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
