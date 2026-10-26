import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(database, schema_file):
    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    schema_file = Path(schema_file)
    with sqlite3.connect(database) as db:
        db.executescript(schema_file.read_text(encoding="utf-8"))
