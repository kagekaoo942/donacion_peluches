# Donación de Peluches - Certificación Skillnest

Aplicación web desarrollada con Flask y MySQL para el registro y adopción de peluches donados.

---

## 🚀 Despliegue en Render

El proyecto está configurado para desplegarse fácilmente en [Render](https://render.com) usando Gunicorn y una base de datos MySQL en la nube (como [TiDB Cloud Serverless](https://tidbcloud.com/) o similar).

### Pasos para desplegar:

1. Crea un **Nuevo Web Service** en Render conectado a tu repositorio en GitHub.
2. Render detectará automáticamente el archivo `render.yaml` o puedes configurar:
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --chdir certificacion_skillnest_donacion_peluches_Martin_acevedo_2026_10_26 --bind 0.0.0.0:$PORT run:app`
   - **Health Check Path:** `/registro`
3. Agrega las siguientes variables en la pestaña **Environment** de tu servicio en Render:

| Variable | Descripción / Ejemplo |
|---|---|
| `FLASK_SECRET_KEY` | Una cadena secreta segura (ej. `mi-clave-super-secreta-12345`) |
| `MYSQL_HOST` | Host de tu base de datos (ej. `gateway01.us-east-1.prod.aws.tidbcloud.com`) |
| `MYSQL_PORT` | Puerto de conexión (ej. `4000` para TiDB, o `3306` para MySQL estándar) |
| `MYSQL_USER` | Usuario de la base de datos |
| `MYSQL_PASSWORD` | Contraseña del usuario de la base de datos |
| `MYSQL_DATABASE` | Nombre de la base de datos (ej. `peluches_donacion` o `test`) |
| `MYSQL_SSL_CA` | *(Opcional)* `certificados/isrgrootx1.pem` (incluido en el proyecto) |

---

## 💻 Ejecución en local

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecuta el servidor de desarrollo:
   ```bash
   python run.py
   ```

3. Abre tu navegador en `http://localhost:5000/`.
