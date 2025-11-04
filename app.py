# app.py (versión corregida)
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify, flash, current_app
import math
from functools import wraps
import datetime
import mysql.connector
import os
from jinja2 import TemplateNotFound
import hashlib
import matplotlib.pyplot as plt
import numpy as np
import re

from gengraphics import generate_graphics, figs_to_pdf

from datetime import datetime as dt

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "8so138bs28d32s4wz3872s8ou6oqwo74368o283"

# --- Configuración de la BD (centralizada) ---
DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "",   # pon tu contraseña si aplica
    'database': "evaluaciones",
    # opcionalmente add: 'pool_name': 'mypool', 'pool_size': 3
}

# inicializamos la conexión (la función connect_db la recreará si se pierde)
def connect_db():
    return mysql.connector.connect(**DB_CONFIG)

db = connect_db()

def get_cursor(buffered=True, dictionary=True):
    """
    Asegurarse que la conexión esté viva; si no, intentar reconectarla.
    Devuelve un cursor listo para usar.
    """
    global db
    try:
        # intenta hacer ping y reconectar automáticamente si fue necesario
        # mysql-connector soporta ping(reconnect=True)
        db.ping(reconnect=True, attempts=3, delay=1)
    except Exception as e:
        current_app.logger.warning("DB ping falló, reconectando: %s", e)
        try:
            db = connect_db()
        except Exception as e2:
            current_app.logger.exception("No se pudo reconectar a la BD: %s", e2)
            raise
    return db.cursor(buffered=buffered, dictionary=dictionary)


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

# NOTA: elimine la definición duplicada de /admin/inicio que antes causaba conflicto.
# La ruta real de admin se declara más abajo como admin_users (y redirige si es necesario).

# Función para logear usuarios
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        uname = request.form.get('uname', '').strip()
        psw = request.form.get('psw', '')

        cursor = None
        user = None
        try:
            cursor = get_cursor()
            cursor.execute("SELECT id, name, password, role FROM `user` WHERE matricula = %s", (uname,))
            user = cursor.fetchone()
        except Exception as e:
            current_app.logger.exception("Error en login - consulta user: %s", e)
            user = None
        finally:
            try:
                if cursor:
                    cursor.close()
            except:
                pass

        # Validar usuario (protección: user['password'] podría ser None)
        stored_hash = (user.get('password') if user else None)
        if not user or not stored_hash or hashlib.md5(psw.encode()).hexdigest() != stored_hash:
            error = "Usuario o contraseña incorrectos"
            return render_template('alumnxs/login-alumnxs.html', error=error)

        # Login OK
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_role'] = user['role']
        session['role'] = user['role']

        role = (user['role'] or '').strip().lower()
        if role == 'alumnx':
            return redirect(url_for('encuestas_alumnx'))
        elif role == 'docente':
            return redirect(url_for('teachers_inicio'))
        elif role == 'admin':
            return redirect(url_for('admin_users'))

    # GET request
    return render_template('alumnxs/login-alumnxs.html', error=error)


# Función consulta la base de datos para ver qué encuestas están activas y cuáles ya contestó el alumno
@app.route('/alumnxs/inicio-alumnxs', methods=['GET'])
def encuestas_alumnx():
    error = None

    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    now = dt.now()   # <-- recalcular el now en cada petición (antes era global e inmóvil)

    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("""
            SELECT f.id, f.title, f.description, f.id_docente, f.id_materia, f.start_at, f.end_at, f.active
            FROM form f
            WHERE f.active = 1
            AND ( (f.start_at IS NULL OR f.start_at <= %s)
                AND (f.end_at IS NULL OR f.end_at >= %s) )
            AND (
                (f.id_materia IS NOT NULL AND EXISTS (
                    SELECT 1 FROM alumnx_materia am
                    WHERE am.id_alumnx = %s
                    AND am.id_course = f.id_materia
                ))
                OR
                (f.id_docente IS NOT NULL AND EXISTS (
                    SELECT 1
                    FROM alumnx_materia am
                    JOIN docente_materia dm ON dm.id_materia = am.id_course
                    WHERE am.id_alumnx = %s
                    AND dm.id_docente = f.id_docente
                ))
            )
            AND NOT EXISTS (
                SELECT 1 FROM response r
                WHERE r.id_form = f.id
                AND r.id_alumnx = %s
            )
            ORDER BY f.start_at IS NULL, f.start_at DESC, f.id DESC
        """, (now, now, user_id, user_id, user_id))
        surveys = cursor.fetchall() or []
    except Exception as e:
        current_app.logger.exception("Error en encuestas_alumnx: %s", e)
        surveys = []
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass

    return render_template('alumnxs/inicio-alumnxs.html', error=error, encuestas=surveys)

# Función para el botón "contestar encuesta" que obtiene las preguntas y respuestas de cada encuesta
@app.route('/alumnxs/inicio-alumnxs/<int:id_encuesta>', methods=['GET'])
def contestar_encuesta(id_encuesta):
    error = None

    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("SELECT title FROM form WHERE id = %s", (id_encuesta, ))
        form_title = cursor.fetchone()
        cursor.execute("SELECT id, texto_pregunta, tipo FROM question WHERE id_form = %s ORDER BY id ASC", (id_encuesta, ))
        questions = cursor.fetchall()

        options = {}
        for question in questions:
            if question['tipo'] == 'multiple':
                cursor.execute("SELECT id, choice_text FROM choice WHERE id_question = %s ORDER BY id ASC", (question['id'], ))
                options[question['id']] = cursor.fetchall()
    except Exception as e:
        current_app.logger.exception("Error en contestar_encuesta: %s", e)
        form_title = None
        questions = []
        options = {}
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass

    return render_template('alumnxs/encuesta.html', error=error, id_encuesta=id_encuesta, form_title=form_title, questions=questions, options=options)

# Función para el botón "enviar respuestas" que registra las respuestas en la bd
@app.route('/alumnxs/inicio-alumnxs/<int:id_encuesta>', methods=['POST'])
def enviar_respuestas(id_encuesta):
    error = None

    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = None
    try:
        cursor = get_cursor()
        user_id = session['user_id']
        now = dt.now()
        cursor.execute("INSERT INTO response (id_form,id_alumnx,submitted_at) VALUES (%s, %s, %s)", (id_encuesta, user_id, now))
        response_id = cursor.lastrowid
        respuestas = request.form

        for key, value in respuestas.items():
            choice_id = None
            if key.startswith('q'):
                question_id = key.lstrip('q')

                if key.endswith('_comments'):
                    texto_respuesta = value
                    question_id = question_id.replace('_comments', '')
                else:
                    choice_id = value
                    cursor.execute("SELECT texto_pregunta FROM question WHERE id=%s",(question_id, ))
                    qres = cursor.fetchone()
                    texto_respuesta = qres['texto_pregunta'] if qres else None

                question_id = int(question_id)
                cursor.execute("INSERT INTO answer (response_id, id_question, choice_id, texto_respuesta) VALUES (%s, %s, %s, %s)",(response_id, question_id, choice_id, texto_respuesta))
        db.commit()
        flash("Encuesta enviada correctamente")
    except Exception as e:
        db.rollback()
        current_app.logger.exception("Error enviando respuestas: %s", e)
        flash("Ocurrió un error al enviar la encuesta")
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass

    return redirect(url_for('encuestas_alumnx'))


@app.route('/teachers/inicio-teachers', methods=['GET', 'POST'])
def results_teachers():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # POST: devuelve opciones para el segundo select 
    if request.method == 'POST':
        data = request.get_json() or {}
        first_filter = (data.get('first_filter') or '').strip()

        cursor = None
        try:
            cursor = get_cursor()
            if first_filter == 'Materia':
                cursor.execute("""
                    SELECT DISTINCT m.id, m.name AS label
                    FROM docente_materia dm
                    JOIN materia m ON dm.id_materia = m.id
                    WHERE dm.id_docente = %s
                    ORDER BY m.name
                """, (user_id,))
            elif first_filter == 'Grupo':
                cursor.execute("""
                    SELECT DISTINCT g.id, g.nombre AS label
                    FROM docente_materia dm
                    JOIN materia_grupo mg ON mg.id_materia = dm.id_materia
                    JOIN grupo g ON mg.id_grupo = g.id
                    WHERE dm.id_docente = %s
                    ORDER BY g.nombre
                """, (user_id,))
            else:
                return jsonify({'results': []})

            rows = cursor.fetchall() or []
            return jsonify({'results': rows})
        except Exception as e:
            app.logger.exception("Error al obtener opciones para second-select: %s", e)
            return jsonify({'results': []})
        finally:
            try:
                if cursor:
                    cursor.close()
            except:
                pass

    # GET: carga inicial / renderizado de la página con gráficos 
    cursor = None
    try:
        cursor = get_cursor()
        cursor.execute("""
            SELECT
                f.id AS form_id,
                f.title AS form_title,
                m.name AS materia,
                q.id AS question_id,
                q.texto_pregunta AS question_text,
                a.id AS answer_id,
                COALESCE(c.choice_text, a.texto_respuesta) AS answer_text
            FROM form f
            LEFT JOIN materia m ON f.id_materia = m.id
            LEFT JOIN docente_materia dm ON dm.id_materia = m.id
            JOIN question q ON q.id_form = f.id
            JOIN answer a ON a.id_question = q.id
            LEFT JOIN choice c ON c.id = a.choice_id
            WHERE f.id_docente = %s OR dm.id_docente = %s
            ORDER BY f.id, q.id;
        """, (user_id, user_id))
        info_for_graphics = cursor.fetchall() or []
    except Exception as e:
        app.logger.exception("Error cargando info_for_graphics: %s", e)
        info_for_graphics = []
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass

    try:
        figures, figures_base64, _ = generate_graphics(info_for_graphics)
        if not isinstance(figures_base64, dict):
            figures_base64 = dict(figures_base64)
    except Exception as e:
        app.logger.exception("Error en generate_graphics: %s", e)
        figures_base64 = {}

    # Parámetros para filtrado vía GET (cuando el usuario hace submit en el second-form)
    filter_type = request.args.get('filter-type')  # "Materia" o "Grupo"
    selected_id = request.args.get('second-filter')

    filtered_figures = None

    if filter_type and selected_id:
        try:
            selected_id_int = int(selected_id)
        except Exception:
            selected_id_int = None

        if selected_id_int is not None:
            cursor = None
            try:
                cursor = get_cursor()
                filtered_figures = {}
                pattern = re.compile(r'f(\d+)')
                for name, img in (figures_base64 or {}).items():
                    m = pattern.search(name)
                    if not m:
                        continue
                    form_id = int(m.group(1))

                    if filter_type == 'Materia':
                        cursor.execute("""
                            SELECT 1 FROM form f
                            WHERE f.id = %s AND f.id_materia = %s
                            LIMIT 1;
                        """, (form_id, selected_id_int))
                    elif filter_type == 'Grupo':
                        cursor.execute("""
                            SELECT 1
                            FROM form f
                            JOIN materia_grupo mg ON mg.id_materia = f.id_materia
                            JOIN grupo g ON g.id = mg.id_grupo
                            WHERE f.id = %s AND g.id = %s
                            LIMIT 1;
                        """, (form_id, selected_id_int))
                    else:
                        continue

                    existe = cursor.fetchone() is not None
                    if existe:
                        filtered_figures[name] = img
            except Exception as e:
                app.logger.exception("Error obteniendo resultados filtrados: %s", e)
                filtered_figures = {}
            finally:
                try:
                    if cursor:
                        cursor.close()
                except:
                    pass

    if filter_type and selected_id is not None:
        display_figures = filtered_figures or {}
    else:
        display_figures = figures_base64 or {}

    return render_template(
        'teachers/inicio-teachers.html',
        figures=figures_base64,
        display_figures=display_figures
    )



@app.route('/teachers/download-report', methods=['GET'])
def download_teacher_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                f.id AS form_id,
                f.title AS form_title,
                m.name AS materia,
                q.id AS question_id,
                q.texto_pregunta AS question_text,
                a.id AS answer_id,
                COALESCE(c.choice_text, a.texto_respuesta) AS answer_text
            FROM form f
            LEFT JOIN materia m ON f.id_materia = m.id
            LEFT JOIN docente_materia dm ON dm.id_materia = m.id
            JOIN question q ON q.id_form = f.id
            JOIN answer a ON a.id_question = q.id
            LEFT JOIN choice c ON c.id = a.choice_id
            WHERE f.id_docente = %s OR dm.id_docente = %s
            ORDER BY f.id, q.id;
        """, (user_id, user_id))
        info_for_graphics = cursor.fetchall() or []
        cursor.close()
    except Exception as e:
        app.logger.exception("Error generando PDF: %s", e)
        return "Error generando PDF", 500

    # Generar figuras con tu función existente
    try:
        figures, _, _ = generate_graphics(info_for_graphics)
        pdf_path = f"/tmp/teacher_{user_id}_metrics.pdf"
        figs_to_pdf(figures, pdf_path)
    except Exception as e:
        app.logger.exception("Error al crear PDF: %s", e)
        return "Error creando el PDF", 500

    # Descargar el PDF
    from flask import send_file
    return send_file(pdf_path, as_attachment=True, download_name="Reporte_Métricas.pdf")


# alias que redirige a la vista admin (ahora admin_users es la única definicion para /admin/inicio)
@app.route('/admin/inicio-admin')
def alias_admin_inicio():
    return redirect(url_for('admin_users'))


@app.route('/admin/inicio', methods=['GET'])
def admin_users():
    """
    Endpoint para listar usuarios (paginado, búsqueda, filtro por rol).
    Devuelve JSON si se pide ?format=json o si Accept: application/json.
    """

    role_in_session = (session.get('role') or session.get('user_role'))
    if 'user_id' not in session or (role_in_session or '').strip().lower() != 'admin':
        current_app.logger.info("Acceso rechazado a /admin/inicio - session keys: %s", dict(session))
        return redirect(url_for('login'))

    try:
        page = max(1, int(request.args.get('page', 1)))
    except Exception:
        page = 1
    try:
        per_page = min(200, max(5, int(request.args.get('per_page', 25))))
    except Exception:
        per_page = 25

    role_filter = (request.args.get('role') or '').strip()
    q = (request.args.get('q') or '').strip()
    offset = (page - 1) * per_page

    where_clauses = []
    params = []

    if role_filter:
        where_clauses.append("u.role = %s")
        params.append(role_filter)

    if q:
        where_clauses.append("(u.name LIKE %s OR u.matricula LIKE %s)")
        likeq = f"%{q}%"
        params.extend([likeq, likeq])

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    cursor = None
    try:
        cursor = get_cursor()
        count_sql = f"SELECT COUNT(*) AS total FROM `user` u {where_sql};"
        cursor.execute(count_sql, tuple(params))
        total_row = cursor.fetchone()
        total = total_row['total'] if total_row else 0

        select_sql = f"""
            SELECT u.id, u.name, u.matricula, u.role, u.created_at
            FROM `user` u
            {where_sql}
            ORDER BY u.id DESC
            LIMIT %s OFFSET %s;
        """
        params_with_limit = list(params) + [per_page, offset]
        cursor.execute(select_sql, tuple(params_with_limit))
        users = cursor.fetchall() or []
    except Exception as e:
        current_app.logger.exception("Error listando usuarios admin: %s", e)
        users = []
        total = 0
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass

    wants_json_via_param = (request.args.get('format') or '').lower() == 'json'
    accept_header = (request.headers.get('Accept') or '')
    wants_json_via_accept = 'application/json' in accept_header.lower()

    current_app.logger.info("admin_users called: args=%s , Accept=%s , session_role=%s , wants_json_param=%s, wants_json_accept=%s",
                            dict(request.args), accept_header, role_in_session, wants_json_via_param, wants_json_via_accept)

    if wants_json_via_param or wants_json_via_accept:
        return jsonify({
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })

    return render_template(
        'admin/inicio-admin.html',
        users=users,
        page=page,
        per_page=per_page,
        total=total,
        role_filter=role_filter,
        q=q
    )


# --- RUTA DE DIAGNÓSTICO: devuelve TODOS los usuarios en JSON (sin auth) ---
@app.route('/admin/api/users-all', methods=['GET'])
def admin_api_users_all():
    try:
        cursor = get_cursor()
        cursor.execute("SELECT id, name, matricula, role, created_at FROM `user` ORDER BY id DESC;")
        users = cursor.fetchall() or []
    except Exception as e:
        current_app.logger.exception("Error en admin_api_users_all: %s", e)
        try:
            cursor.close()
        except:
            pass
        return jsonify({'error': 'DB error', 'details': str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass

    return jsonify(users)


@app.route('/admin/api/materias', methods=['GET'])
def admin_api_materias():
    try:
        cursor = get_cursor()
        cursor.execute("""
            SELECT
                m.id AS materia_id,
                m.name AS materia_name,
                d.id AS docente_id,
                d.name AS docente_name,
                d.matricula AS docente_matricula,
                g.id AS grupo_id,
                g.nombre AS grupo_nombre
            FROM materia m
            LEFT JOIN docente_materia dm ON dm.id_materia = m.id
            LEFT JOIN `user` d ON d.id = dm.id_docente
            LEFT JOIN materia_grupo mg ON mg.id_materia = m.id
            LEFT JOIN grupo g ON g.id = mg.id_grupo
            ORDER BY m.id;
        """)
        rows = cursor.fetchall() or []
    except Exception as e:
        current_app.logger.exception("Error en admin_api_materias: %s", e)
        try:
            cursor.close()
        except:
            pass
        return jsonify({'error': 'DB error', 'details': str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass

    materias_map = {}
    for r in rows:
        mid = r['materia_id']
        if mid not in materias_map:
            materias_map[mid] = {
                'id': mid,
                'name': r['materia_name'],
                'docentes': [],
                'grupos': []
            }
        did = r.get('docente_id')
        if did:
            if not any(d['id'] == did for d in materias_map[mid]['docentes']):
                materias_map[mid]['docentes'].append({
                    'id': did,
                    'name': r.get('docente_name'),
                    'matricula': r.get('docente_matricula'),
                })
        gid = r.get('grupo_id')
        if gid:
            if not any(g['id'] == gid for g in materias_map[mid]['grupos']):
                materias_map[mid]['grupos'].append({
                    'id': gid,
                    'nombre': r.get('grupo_nombre')
                })

    materias = [materias_map[k] for k in sorted(materias_map.keys())]
    return jsonify(materias)


@app.route('/admin/api/respuestas', methods=['GET'])
def admin_api_respuestas():
    filtros = []
    params = []

    form_id = request.args.get('form_id')
    alumnx_id = request.args.get('alumnx_id')

    try:
        if form_id:
            form_id_int = int(form_id)
            filtros.append("r.id_form = %s")
            params.append(form_id_int)
        if alumnx_id:
            alumnx_id_int = int(alumnx_id)
            filtros.append("r.id_alumnx = %s")
            params.append(alumnx_id_int)
    except ValueError:
        return jsonify({'error': 'Invalid filter value', 'details': 'form_id and alumnx_id must be integers'}), 400

    where_sql = ("WHERE " + " AND ".join(filtros)) if filtros else ""

    try:
        cursor = get_cursor()
        sql = f"""
            SELECT
                r.id AS response_id,
                r.id_form,
                r.id_alumnx,
                r.submitted_at,
                f.title AS form_title,
                u.name AS alumnx_name,
                u.matricula AS alumnx_matricula,
                a.id AS answer_id,
                a.id_question,
                q.texto_pregunta,
                q.tipo AS pregunta_tipo,
                a.choice_id,
                c.choice_text,
                a.texto_respuesta
            FROM response r
            LEFT JOIN `form` f ON f.id = r.id_form
            LEFT JOIN `user` u ON u.id = r.id_alumnx
            LEFT JOIN answer a ON a.response_id = r.id
            LEFT JOIN question q ON q.id = a.id_question
            LEFT JOIN choice c ON c.id = a.choice_id
            {where_sql}
            ORDER BY r.id DESC, a.id ASC;
        """
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall() or []
    except Exception as e:
        current_app.logger.exception("Error en admin_api_respuestas (filtered): %s", e)
        try:
            cursor.close()
        except:
            pass
        return jsonify({'error': 'DB error', 'details': str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass

    responses_map = {}
    for r in rows:
        rid = r['response_id']
        if rid not in responses_map:
            responses_map[rid] = {
                'response_id': rid,
                'form_id': r.get('id_form'),
                'form_title': r.get('form_title'),
                'alumnx_id': r.get('id_alumnx'),
                'alumnx_name': r.get('alumnx_name'),
                'alumnx_matricula': r.get('alumnx_matricula'),
                'submitted_at': r.get('submitted_at'),
                'answers': []
            }

        if r.get('answer_id') is not None:
            responses_map[rid]['answers'].append({
                'answer_id': r.get('answer_id'),
                'question_id': r.get('id_question'),
                'question_text': r.get('texto_pregunta'),
                'question_type': r.get('pregunta_tipo'),
                'choice_id': r.get('choice_id'),
                'choice_text': r.get('choice_text'),
                'texto_respuesta': r.get('texto_respuesta')
            })

    responses = list(responses_map.values())
    return jsonify(responses)


if __name__ == '__main__':
    app.run(debug=True)
