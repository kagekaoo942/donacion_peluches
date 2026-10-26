import os
from pathlib import Path

from flask import Flask

from flask_app.models.database import close_db, init_db


BASE_DIR = Path(__file__).resolve().parent.parent.parent


def load_env_file(path):
    # Mantenemos el proyecto fácil de levantar: no obligamos a instalar otra
    # librería solo para leer unas pocas variables de configuración.
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        os.environ.setdefault(key, value)


load_env_file(BASE_DIR / ".env")


def create_app():
    # Todas las rutas parten de la raíz del proyecto, no de la carpeta config.
    # Así funciona igual desde VS Code, PowerShell o el lanzador de la raíz.
    schema_path = Path(
        os.environ.get("DATABASE_SCHEMA_PATH", str(BASE_DIR / "BD" / "schema.sql"))
    )
    if not schema_path.is_absolute():
        schema_path = BASE_DIR / schema_path

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get(
            "FLASK_SECRET_KEY", "clave-local-solo-para-desarrollo"
        ),
        DATABASE_SCHEMA=schema_path,
        MYSQL_HOST=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        MYSQL_PORT=int(os.environ.get("MYSQL_PORT", "3306")),
        MYSQL_USER=os.environ.get("MYSQL_USER", "root"),
        MYSQL_PASSWORD=os.environ.get("MYSQL_PASSWORD", ""),
        MYSQL_DATABASE=os.environ.get("MYSQL_DATABASE", "peluches_donacion"),
    )

    app.teardown_appcontext(close_db)

    with app.app_context():
        # Al iniciar comprobamos que la base y sus tablas estén disponibles
        # antes de aceptar peticiones de los formularios.
        init_db(
            app.config["DATABASE_SCHEMA"],
            app.config["MYSQL_HOST"],
            app.config["MYSQL_PORT"],
            app.config["MYSQL_USER"],
            app.config["MYSQL_PASSWORD"],
            app.config["MYSQL_DATABASE"],
        )

    from flask_app.controllers.routes import register_routes

    register_routes(app)
    return app
