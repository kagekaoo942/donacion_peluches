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
load_env_file(BASE_DIR.parent / ".env")


def resolve_ssl_ca(host=""):
    ssl_ca_env = os.environ.get("MYSQL_SSL_CA", "").strip()
    if ssl_ca_env:
        ca_path = Path(ssl_ca_env)
        if not ca_path.is_absolute():
            ca_path = BASE_DIR / ca_path
        if ca_path.exists():
            return str(ca_path.resolve())
        # Revisar en la raíz
        if (BASE_DIR.parent / ssl_ca_env).exists():
            return str((BASE_DIR.parent / ssl_ca_env).resolve())
        # Revisar certificados del sistema en Linux (Render)
        if Path("/etc/ssl/certs/ca-certificates.crt").exists():
            return "/etc/ssl/certs/ca-certificates.crt"

    # Si estamos en localhost / 127.0.0.1 y no se especificó MYSQL_SSL_CA, no forzamos SSL
    if host in ("127.0.0.1", "localhost", ""):
        return None

    # Si es un host remoto (como TiDB Cloud en Render), usar el certificado del proyecto o del sistema
    default_ca = BASE_DIR / "certificados" / "isrgrootx1.pem"
    if default_ca.exists():
        return str(default_ca.resolve())

    if Path("/etc/ssl/certs/ca-certificates.crt").exists():
        return "/etc/ssl/certs/ca-certificates.crt"

    return None


def create_app():
    # Todas las rutas parten de la raíz del proyecto, no de la carpeta config.
    schema_path = Path(
        os.environ.get("DATABASE_SCHEMA_PATH", str(BASE_DIR / "BD" / "schema.sql"))
    )
    if not schema_path.is_absolute():
        schema_path = BASE_DIR / schema_path

    mysql_host = os.environ.get("MYSQL_HOST", "127.0.0.1")
    ssl_ca_path = resolve_ssl_ca(mysql_host)

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
        MYSQL_HOST=mysql_host,
        MYSQL_PORT=int(os.environ.get("MYSQL_PORT", "3306")),
        MYSQL_USER=os.environ.get("MYSQL_USER", "root"),
        MYSQL_PASSWORD=os.environ.get("MYSQL_PASSWORD", ""),
        MYSQL_DATABASE=os.environ.get("MYSQL_DATABASE", "peluches_donacion"),
        MYSQL_SSL_CA=ssl_ca_path,
    )

    app.teardown_appcontext(close_db)

    with app.app_context():
        # Al iniciar intentamos verificar/crear las tablas.
        # Envolviendo en try/except para que no impida arrancar a Gunicorn en Render
        # si la conexión a la base de datos remota tarda unos segundos en responder.
        try:
            init_db(
                app.config["DATABASE_SCHEMA"],
                app.config["MYSQL_HOST"],
                app.config["MYSQL_PORT"],
                app.config["MYSQL_USER"],
                app.config["MYSQL_PASSWORD"],
                app.config["MYSQL_DATABASE"],
                app.config["MYSQL_SSL_CA"],
            )
        except Exception as e:
            print(f"[ADVERTENCIA] No se pudo inicializar la base de datos durante el arranque: {e}")

    from flask_app.controllers.routes import register_routes

    register_routes(app)
    return app
