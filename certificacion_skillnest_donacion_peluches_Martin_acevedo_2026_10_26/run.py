from flask_app.config import create_app


app = create_app()


if __name__ == "__main__":
    print("Servidor Flask iniciado.")
    print("Abre http://127.0.0.1:5000/ en tu navegador.")
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
