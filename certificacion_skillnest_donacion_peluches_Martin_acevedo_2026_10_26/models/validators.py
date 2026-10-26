import re


def clean(value):
    return value.strip() if value else ""


def validate_person_data(form):
    nombre = clean(form.get("nombre"))
    apellido = clean(form.get("apellido"))
    email = clean(form.get("email")).lower()
    password = form.get("password", "")
    confirmar = form.get("confirmar", "")
    errors = []

    if len(nombre) < 2:
        errors.append("El nombre debe tener al menos 2 caracteres.")
    if len(apellido) < 2:
        errors.append("El apellido debe tener al menos 2 caracteres.")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        errors.append("El email debe tener un formato valido.")
    if len(password) < 7:
        errors.append("La contrasena debe tener al menos 7 caracteres.")
    if password != confirmar:
        errors.append("La contrasena y su confirmacion deben ser iguales.")
    return nombre, apellido, email, password, errors


def validate_toy_data(form):
    nombre = clean(form.get("nombre"))
    descripcion = clean(form.get("descripcion"))
    errors = []
    if len(nombre) < 2:
        errors.append("El nombre del peluche debe tener al menos 2 caracteres.")
    if not descripcion:
        errors.append("La descripcion no puede estar vacia.")
    return nombre, descripcion, errors
