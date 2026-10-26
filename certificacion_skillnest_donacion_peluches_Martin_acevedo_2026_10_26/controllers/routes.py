from functools import wraps

from flask import (
    Flask,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from models.database import get_db
from models.validators import clean, validate_person_data, validate_toy_data


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            flash("Debes iniciar sesion para ver esta pagina.", "error")
            return redirect(url_for("registro"))
        return view(*args, **kwargs)

    return wrapped_view


def register_routes(app: Flask):
    @app.before_request
    def load_logged_user():
        user_id = session.get("user_id")
        g.user = None
        if user_id is not None:
            g.user = get_db().execute(
                "SELECT id, nombre, apellido, email FROM usuarios WHERE id = ?",
                (user_id,),
            ).fetchone()
            if g.user is None:
                session.clear()

    @app.get("/")
    def inicio():
        return redirect(url_for("dashboard" if g.user else "registro"))

    @app.route("/registro", methods=["GET", "POST"])
    def registro():
        if request.method == "POST":
            if request.form.get("formulario") == "login":
                email = clean(request.form.get("email")).lower()
                password = request.form.get("password", "")
                user = get_db().execute(
                    "SELECT * FROM usuarios WHERE email = ?", (email,)
                ).fetchone()
                if user is None or not check_password_hash(
                    user["password"], password
                ):
                    flash("Email o contrasena incorrectos.", "error")
                else:
                    session.clear()
                    session["user_id"] = user["id"]
                    return redirect(url_for("dashboard"))
            else:
                nombre, apellido, email, password, errors = validate_person_data(
                    request.form
                )
                if get_db().execute(
                    "SELECT 1 FROM usuarios WHERE email = ?", (email,)
                ).fetchone():
                    errors.append("El email ya esta registrado.")
                if not errors:
                    db = get_db()
                    db.execute(
                        "INSERT INTO usuarios "
                        "(nombre, apellido, email, password) VALUES (?, ?, ?, ?)",
                        (nombre, apellido, email, generate_password_hash(password)),
                    )
                    db.commit()
                    flash("Registro exitoso. Ahora puedes iniciar sesion.", "success")
                    return redirect(url_for("registro"))
                for error in errors:
                    flash(error, "error")
        return render_template("registro.html")

    @app.get("/logout")
    def logout():
        session.clear()
        flash("Sesion cerrada.", "success")
        return redirect(url_for("registro"))

    @app.get("/dashboard")
    @login_required
    def dashboard():
        peluches = get_db().execute(
            """
            SELECT p.*, u.nombre AS donador_nombre, u.apellido AS donador_apellido,
                   a.nombre AS adoptante_nombre, a.apellido AS adoptante_apellido
            FROM peluches p
            JOIN usuarios u ON u.id = p.usuario_id
            LEFT JOIN usuarios a ON a.id = p.adoptado_por
            ORDER BY p.id DESC
            """
        ).fetchall()
        return render_template("dashboard.html", peluches=peluches)

    @app.route("/nueva", methods=["GET", "POST"])
    @login_required
    def nueva():
        form_data = {"nombre": "", "descripcion": ""}
        if request.method == "POST":
            form_data = {
                "nombre": request.form.get("nombre", ""),
                "descripcion": request.form.get("descripcion", ""),
            }
            nombre, descripcion, errors = validate_toy_data(request.form)
            if not errors:
                db = get_db()
                db.execute(
                    "INSERT INTO peluches (nombre, descripcion, usuario_id) "
                    "VALUES (?, ?, ?)",
                    (nombre, descripcion, g.user["id"]),
                )
                db.commit()
                flash("Peluche donado correctamente.", "success")
                return redirect(url_for("dashboard"))
            for error in errors:
                flash(error, "error")
        return render_template("nueva.html", form_data=form_data)

    @app.route("/editar/<int:peluche_id>", methods=["GET", "POST"])
    @login_required
    def editar(peluche_id):
        db = get_db()
        peluche = db.execute(
            "SELECT * FROM peluches WHERE id = ?", (peluche_id,)
        ).fetchone()
        if peluche is None:
            flash("El peluche no existe.", "error")
            return redirect(url_for("dashboard"))
        if peluche["usuario_id"] != g.user["id"]:
            flash("Solo el dueño puede editar este peluche.", "error")
            return redirect(url_for("dashboard"))
        form_data = {
            "nombre": peluche["nombre"],
            "descripcion": peluche["descripcion"],
        }
        if request.method == "POST":
            form_data = {
                "nombre": request.form.get("nombre", ""),
                "descripcion": request.form.get("descripcion", ""),
            }
            nombre, descripcion, errors = validate_toy_data(request.form)
            if not errors:
                db.execute(
                    "UPDATE peluches SET nombre = ?, descripcion = ? WHERE id = ?",
                    (nombre, descripcion, peluche_id),
                )
                db.commit()
                flash("Peluche actualizado correctamente.", "success")
                return redirect(url_for("dashboard"))
            for error in errors:
                flash(error, "error")
        return render_template("editar.html", peluche=peluche, form_data=form_data)

    @app.post("/borrar/<int:peluche_id>")
    @login_required
    def borrar(peluche_id):
        db = get_db()
        peluche = db.execute(
            "SELECT usuario_id FROM peluches WHERE id = ?", (peluche_id,)
        ).fetchone()
        if peluche is None:
            flash("El peluche no existe.", "error")
        elif peluche["usuario_id"] != g.user["id"]:
            flash("Solo el dueño puede borrar este peluche.", "error")
        else:
            db.execute("DELETE FROM peluches WHERE id = ?", (peluche_id,))
            db.commit()
            flash("Peluche borrado correctamente.", "success")
        return redirect(url_for("dashboard"))

    @app.post("/adoptar/<int:peluche_id>")
    @login_required
    def adoptar(peluche_id):
        db = get_db()
        peluche = db.execute(
            "SELECT usuario_id, adoptado_por FROM peluches WHERE id = ?",
            (peluche_id,),
        ).fetchone()
        if peluche is None:
            flash("El peluche no existe.", "error")
        elif peluche["adoptado_por"] is not None:
            flash("Este peluche ya fue adoptado.", "error")
        elif peluche["usuario_id"] == g.user["id"]:
            flash("No puedes adoptar un peluche que tu donaste.", "error")
        else:
            db.execute(
                "UPDATE peluches SET adoptado_por = ? WHERE id = ?",
                (g.user["id"], peluche_id),
            )
            db.commit()
            flash("Peluche adoptado correctamente.", "success")
        return redirect(url_for("dashboard"))

    @app.get("/ver/<int:peluche_id>")
    @login_required
    def ver(peluche_id):
        db = get_db()
        peluche = db.execute(
            """
            SELECT p.*, u.nombre AS donador_nombre, u.apellido AS donador_apellido,
                   a.nombre AS adoptante_nombre, a.apellido AS adoptante_apellido
            FROM peluches p
            JOIN usuarios u ON u.id = p.usuario_id
            LEFT JOIN usuarios a ON a.id = p.adoptado_por
            WHERE p.id = ?
            """,
            (peluche_id,),
        ).fetchone()
        if peluche is None:
            flash("El peluche no existe.", "error")
            return redirect(url_for("dashboard"))
        db.execute("UPDATE peluches SET visitas = visitas + 1 WHERE id = ?", (peluche_id,))
        db.commit()
        peluche = dict(peluche)
        peluche["visitas"] += 1
        return render_template("ver.html", peluche=peluche)
