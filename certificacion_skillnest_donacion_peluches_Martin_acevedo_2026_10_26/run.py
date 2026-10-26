import os

from flask_app.config import create_app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    print("Servidor Flask iniciado.")
    print(f"Servidor Flask iniciado en el puerto {port}.")
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
        use_reloader=False,
    )
