from flask import Flask, render_template, request, redirect, url_for, session, abort

import mysql.connector
import os
from jinja2 import TemplateNotFound
import hashlib

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "8so138bs28d32s4wz3872s8ou6oqwo74368o283" 


# Conexión a la BD
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  
    database="evaluaciones"
)

@app.route('/')
def index():
    return render_template('index.html')

# Para redireccionar urls dentro de la página
@app.route('/<folder>/<page>')
@app.route('/<folder>/<page>/')   # con o sin slash final
def serve_page(folder, page):
    template = f"{folder}/{page}.html"
    try:
        return render_template(template)
    except TemplateNotFound:
        app.logger.debug(f"Template not found: templates/{template}")
        abort(404)

# Funciones para redirigir según tipo de usuario en el login

@app.route('/alumnxs/inicio')
def alumnxs_inicio():
    return render_template('alumnxs/inicio-alumnxs.html')

@app.route('/teachers/inicio')
def teachers_inicio():
    return render_template('teachers/inicio-teachers.html')

@app.route('/admin/inicio')
def admin_inicio():
    return render_template('admin/inicio-admin.html')

# Función para logear usuarios
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        uname = request.form.get('uname', '').strip()
        psw = request.form.get('psw', '')

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, name, password, role FROM user WHERE matricula = %s", (uname,))
        user = cursor.fetchone()
        cursor.close()

        # Validar usuario
        if not user or hashlib.md5(psw.encode()).hexdigest() != user['password']:
            error = "Usuario o contraseña incorrectos"
            return render_template('alumnxs/login-alumnxs.html', error=error)

        # Login OK
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_role'] = user['role']

        role = user['role'].strip().lower()
        if role == 'alumnx':
            return redirect(url_for('alumnxs_inicio'))
        elif role == 'docente':
            return redirect(url_for('teachers_inicio'))
        elif role == 'admin':
            return redirect(url_for('admin_inicio'))

    # GET request
    return render_template('alumnxs/login-alumnxs.html', error=error)


# Función consulta la base de datos para ver qué encuestas están activas y cuáles ya contestó el alumno
@app.route('/alumnxs/inicio-alumnxs', methods=['GET'])
def encuestas_alumnx():
    error = None

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT f.id, f.title, f.description, f.id_docente, f.id_materia, f.start_at, f.end_at, f.active FROM form f WHERE f.active = 1 AND ((f.id_materia IS NOT NULL AND EXISTS (SELECT 1 FROM alumnx_materia am WHERE am.id_alumnx = %s AND am.id_course = f.id_materia)) OR (f.id_docente IS NOT NULL AND EXISTS (SELECT 1 FROM alumnx_materia am JOIN docente_materia dm ON dm.id_materia = am.id_course WHERE am.id_alumnx = %s AND dm.id_docente = f.id_docente))) ORDER BY f.start_at IS NULL, f.start_at DESC, f.id DESC", (user_id,user_id))
    surveys = cursor.fetchall()
    print("User ID:", user_id)
    print("Surveys:", surveys)

    cursor.close()

    # GET request
    return render_template('alumnxs/inicio-alumnxs.html', error=error, encuestas=surveys)

# Función para el botón "contestar encuesta" que obtiene las preguntas y respuestas de cada encuesta
@app.route('/alumnxs/inicio-alumnxs/<int:id_encuesta>', methods=['GET', 'POST'])
def contestar_encuesta(id_encuesta):
    error = None

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    cursor = db.cursor(dictionary=True)
    cursor.close()


if __name__ == '__main__':
    app.run(debug=True)
