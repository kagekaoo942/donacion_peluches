import os
import sys
from pathlib import Path

# Directorio del proyecto Flask
PROJECT_DIR = (
    Path(__file__).resolve().parent
    / "certificacion_skillnest_donacion_peluches_Martin_acevedo_2026_10_26"
)

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

os.chdir(PROJECT_DIR)

from flask_app.config import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    print(f"Servidor Flask iniciado en el puerto {port}.")
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
        use_reloader=False,
    )
