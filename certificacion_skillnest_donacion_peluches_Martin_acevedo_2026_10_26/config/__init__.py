import os
from pathlib import Path

from flask import Flask

from models.database import close_db, init_db


BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get(
            "FLASK_SECRET_KEY", "clave-local-solo-para-desarrollo"
        ),
        DATABASE=BASE_DIR / "BD" / "peluches.db",
        DATABASE_SCHEMA=BASE_DIR / "BD" / "schema.sql",
    )

    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db(app.config["DATABASE"], app.config["DATABASE_SCHEMA"])

    from controllers.routes import register_routes

    register_routes(app)
    return app
