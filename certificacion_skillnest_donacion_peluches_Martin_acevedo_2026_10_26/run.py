import os
import sys
from pathlib import Path

# Configurar el entorno de importaciones
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.chdir(PROJECT_DIR)

from flask_app.config import create_app

# Gunicorn en Render busca 'app' en este módulo
app = create_app()

# Iniciar servidor local
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    print(f"Servidor Flask iniciado en el puerto {port}.")
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
        use_reloader=False,
    )
