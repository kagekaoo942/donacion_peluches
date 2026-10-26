import os
import sys
from pathlib import Path

# 1. Definir el directorio donde se encuentra este script
PROJECT_DIR = Path(__file__).resolve().parent

# 2. Configurar el entorno de importaciones
os.chdir(PROJECT_DIR)
sys.path.insert(0, str(PROJECT_DIR))

# 3. Importar 'app' (prueba con Opción A; si falla, usa Opción B)
from flask_app.config import app

# 4. Iniciar el servidor
if __name__ == "__main__":
    app.run(debug=True)