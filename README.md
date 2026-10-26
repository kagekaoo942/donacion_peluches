# donacion_peluches

## Despliegue en Render

El proyecto incluye [render.yaml](./render.yaml), que configura la instalación
de dependencias y el servidor Gunicorn. En Render, crea un servicio web desde
este repositorio y agrega estas variables en **Environment > Environment
Variables**:

```text
FLASK_SECRET_KEY=<una-clave-secreta-larga>
MYSQL_HOST=<host-de-TiDB>
MYSQL_PORT=4000
MYSQL_USER=<usuario-de-TiDB>
MYSQL_PASSWORD=<contraseña-de-TiDB>
MYSQL_DATABASE=peluches_donacion
MYSQL_SSL_CA=certificados/isrgrootx1.pem
DATABASE_SCHEMA_PATH=BD/schema.sql
```

La contraseña y la clave secreta deben agregarse únicamente en Render; no se
deben subir en `.env` ni escribir en `render.yaml`. El certificado CA no es una
contraseña y está incluido en el proyecto para permitir la conexión TLS con
TiDB Cloud.

El servicio queda accesible en la URL que Render asigne. Render proporciona
automáticamente la variable `PORT`, que ya utiliza la aplicación y Gunicorn.