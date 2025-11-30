
from flask import Flask, render_template, redirect, url_for, session, abort, jsonify, flash, current_app
from flask import request, g, make_response, send_file

from functools import wraps
import mysql.connector
import time
from mysql.connector import Error
from jinja2 import TemplateNotFound
import hashlib

import re
import os
from io import BytesIO
from datetime import datetime, timedelta
import calendar

from uuid import uuid4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from gengraphics import generate_graphics, figs_to_pdf


app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY') or "8so138bs28d32s4wz3872s8ou6oqwo74368o283"

app.config.update({
    'SESSION_COOKIE_SECURE': os.environ.get('FLASK_ENV') == 'production',
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax',
    'PERMANENT_SESSION_LIFETIME': timedelta(days=7),
})

# lee desde variables de entorno. Dentro de Docker el host por defecto será 'db'.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "evaluaciones"),
}


def get_conn_and_cursor(retries=15, delay=2):
    for i in range(1, retries + 1):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            print(f"Conectado a MySQL en intento {i}")
            return conn, conn.cursor(dictionary=True)

        except Error as e:
            print(f"⏳ Intento {i}/{retries} - esperando MySQL → {e}")
            time.sleep(delay)

    raise RuntimeError("No se pudo conectar a MySQL.")


def require_role(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = session.get('user_id')
            if not user_id:
                return redirect(url_for('login', next=request.path))

            # normalizar role
            session_role = (session.get('role') or '').strip().lower()
            if allowed_roles and session_role not in [r.lower() for r in allowed_roles]:
                current_app.logger.warning("Acceso denegado por rol: path=%s role=%s user=%s", request.path, session_role, user_id)
                session.clear()
                return "Acceso denegado", 403

            # comprobar token + role guardados en DB (inmediata invalidación si no coinciden)
            conn = cursor = None
            try:
                conn, cursor = get_conn_and_cursor()
                cursor.execute("SELECT current_session_token, role FROM `user` WHERE id = %s", (user_id,))
                db_row = cursor.fetchone()
            except Exception as e:
                current_app.logger.exception("Error validando sesión: %s", e)
                return "Error interno", 500
            finally:
                try: cursor.close()
                except: pass
                try: conn.close()
                except: pass

            db_token = db_row.get('current_session_token') if db_row else None
            db_role = (db_row.get('role') or '').strip().lower() if db_row else None

            # si el token o el role no coinciden, forzamos logout y redirigimos
            if (db_token is None) or (session.get('session_token') != db_token) or (session_role != db_role):
                current_app.logger.info("Sesión inválida/incongruente, forzando logout. session_role=%s db_role=%s user=%s", session_role, db_role, user_id)
                session.clear()
                return redirect(url_for('login'))

            # todo ok
            g.current_user_id = user_id
            g.current_user_role = session_role
            return f(*args, **kwargs)
        return wrapper
    return decorator



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
        app.logger.debug(f"Página no encontrada: templates/{template}")
        abort(404)

@app.route('/preguntas-freq')
def preguntas_freq():
    return render_template('preguntas-freq.html')

# Funciones para redirigir según tipo de usuario en el login

@app.route('/alumnxs/inicio')
@require_role("alumnx")
def alumnxs_inicio():
    return render_template('alumnxs/inicio-alumnxs.html')

@app.route('/teachers/inicio')
@require_role("docente")
def teachers_inicio():
    return render_template('teachers/inicio-teachers.html')


# Función para logear usuarios
@app.route('/login', methods=['GET', 'POST'])
def login():

    conn = None
    cursor = None
    error = None
    if request.method == 'POST':
        uname = request.form.get('uname', '').strip()
        psw = request.form.get('psw', '')
        role = (request.form.get("role") or '').strip().lower()
        # validar role...
        conn = cursor = None
        try:
            conn, cursor = get_conn_and_cursor()
            cursor.execute("SELECT id, name, password, role FROM `user` WHERE matricula = %s AND role = %s", (uname, role))
            user = cursor.fetchone()
        except Exception as e:
            current_app.logger.exception("Error en login - consulta user: %s", e)
            user = None
        finally:
            try: cursor.close()
            except: pass
            try: conn.close()
            except: pass

        stored_hash = (user.get('password') if user else None)
        if not user or not stored_hash or hashlib.md5(psw.encode()).hexdigest() != stored_hash:
            error = "Usuario o contraseña incorrectos"
            # render según role...
        else:

            session.clear()
            session.permanent = True
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['user_name'] = user['name']

            session_token = uuid4().hex
            session['session_token'] = session_token

            # guardar token en DB
            conn = cursor = None
            try:
                conn, cursor = get_conn_and_cursor()
                cursor.execute("UPDATE `user` SET current_session_token = %s WHERE id = %s", (session_token, user['id']))
                conn.commit()
            except Exception:
                current_app.logger.exception("Error al guardar token de sesión")
            finally:
                try: cursor.close()
                except: pass
                try: conn.close()
                except: pass


            # redirect según role...


        if role == 'alumnx':
            return redirect(url_for('encuestas_alumnx'))
        elif role == 'docente':
            return redirect(url_for('teachers_inicio'))
        elif role == 'admin':
            return redirect(url_for('admin_users'))

    # GET request
    return render_template('index.html', error=error)


@app.route('/logout')
def logout():
    uid = session.get('user_id')
    if uid:
        try:
            conn, cursor = get_conn_and_cursor()
            cursor.execute("UPDATE `user` SET current_session_token = NULL WHERE id = %s", (uid,))
            conn.commit()
        except Exception:
            current_app.logger.exception("Error invalidando token al logout")
        finally:
            try: cursor.close()
            except: pass
            try: conn.close()
            except: pass
    session.clear()
    return redirect(url_for('index'))

# Guardar historial en session 
@app.after_request
def save_history(response):
    try:
        # Guardar solo GET
        if request.method != 'GET':
            return response

        # Ignorar archivos estáticos
        if request.path.startswith("/static/"):
            return response

        # Ignorar APIs
        if request.path.startswith("/admin/api/") or request.path.startswith("/api/"):
            return response

        # Solo guardar respuestas 200
        if not (200 <= response.status_code < 300):
            return response

        clean_url = request.full_path.rstrip('?') or request.path

        entry = {
            "url": clean_url,
            "endpoint": request.endpoint,    
            "view_args": request.view_args or {},
        }

        history = session.get("history", [])

        # Evitar duplicados exactos seguidos
        if history and history[-1].get("url") == entry["url"]:
            return response

        history.append(entry)
        session["history"] = history[-10:]

    except Exception:
        pass

    return response

# Función para obtener URL anterior válida
def previous_url():
    history = session.get("history", [])

    if len(history) < 2:
        # no hay anterior → fallback por rol
        role = session.get("role") or session.get("user_role")
        if role == "admin":
            return url_for("admin_users")
        if role == "docente":
            return url_for("inicio_docente")
        if role == "alumnx":
            return url_for("inicio_alumn")
        return url_for("index")

    previous = history[-2]

    ep = previous.get("endpoint")
    args = previous.get("view_args") or {}
    if ep:
        try:
            return url_for(ep, **args)
        except:
            pass
    return previous.get("url") or url_for("index")

# Exponer la función a Jinja templates
@app.context_processor
def inject_previous_url():
    return dict(previous_url=previous_url)

@app.route("/go-back")
def go_back():
    return redirect(previous_url())

@app.route('/go-back-2')
def go_back_2():
    history = session.get('history', [])
    
    if len(history) < 3:
        return redirect(previous_url())   # fallback
    
    prev2 = history[-3]
    return redirect(prev2['url'])


# Función consulta la base de datos para ver qué encuestas están activas y cuáles ya contestó el alumno
@app.route('/alumnxs/inicio-alumnxs', methods=['GET'])
@require_role("alumnx")
def encuestas_alumnx():
    error = None
    user_id = session['user_id']
    now = datetime.now() 

    cursor = None
    try:
        conn, cursor = get_conn_and_cursor()
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
        try:
            if conn:
                conn.close()
        except:
            pass

    return render_template('alumnxs/inicio-alumnxs.html', error=error, encuestas=surveys)

# Función para el botón "contestar encuesta" que obtiene las preguntas y respuestas de cada encuesta
@app.route('/alumnxs/inicio-alumnxs/<int:id_encuesta>', methods=['GET'])
@require_role("alumnx")
def contestar_encuesta(id_encuesta):
    error = None
    cursor = None
    try:
        conn, cursor = get_conn_and_cursor()
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
        try:
            if conn:
                conn.close()
        except:
            pass

    return render_template('alumnxs/encuesta.html', error=error, id_encuesta=id_encuesta, form_title=form_title, questions=questions, options=options)

# Función para el botón "enviar respuestas" que registra las respuestas en la bd
@app.route('/alumnxs/inicio-alumnxs/<int:id_encuesta>', methods=['POST'])
@require_role("alumnx")
def enviar_respuestas(id_encuesta):
    try:
        conn, cursor = get_conn_and_cursor()
        user_id = session['user_id']
        now = datetime.now()

        # Insertar fila de response y obtener response_id
        cursor.execute(
            "INSERT INTO response (id_form, id_alumnx, submitted_at) VALUES (%s, %s, %s)",
            (id_encuesta, user_id, now)
        )

        response_id = cursor.lastrowid

        respuestas = request.form

        for key, value in respuestas.items():
            # ignorar campos que no sean de pregunta
            if not key.startswith('q'):
                continue

            # Determinar si es comentario o choice
            if key.endswith('_comments'):

                question_part = key[len('q'):]               
                question_id = int(question_part.replace('_comments', ''))
                texto_respuesta = value
                choice_id = None
            else:
                question_id = int(key[1:])
                choice_id = int(value) if value else None
                # obtener texto de la pregunta (opcional)
                cursor.execute("SELECT texto_pregunta FROM question WHERE id = %s", (question_id,))
                qres = cursor.fetchone()
                texto_respuesta = qres['texto_pregunta'] if qres and 'texto_pregunta' in qres else None

            # Insertar la respuesta concreta
            cursor.execute(
                "INSERT INTO answer (response_id, id_question, choice_id, texto_respuesta) VALUES (%s, %s, %s, %s)",
                (response_id, question_id, choice_id, texto_respuesta)
            )

        
        conn.commit()
        flash("Encuesta enviada correctamente")
    except Exception as e:
        # Rollback en la conexión usada
        try:
            if conn:
                conn.rollback()
        except Exception as rollback_err:
            current_app.logger.exception("Error en rollback: %s", rollback_err)
        current_app.logger.exception("Error enviando respuestas: %s", e)
        flash("Ocurrió un error al enviar la encuesta")
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass

    return redirect(url_for('encuestas_alumnx'))


@app.route('/teachers/inicio-teachers', methods=['GET', 'POST'])
@require_role("docente")
def results_teachers():
    conn = None
    cursor = None

    user_id = session['user_id']

    # POST: devuelve opciones para el segundo select 
    if request.method == 'POST':
        data = request.get_json() or {}
        first_filter = (data.get('first_filter') or '').strip()

        try:
            conn, cursor = get_conn_and_cursor()
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
            try:
                if conn:
                    conn.close()
            except:
                pass

    # GET: carga inicial / renderizado de la página con gráficos 
    cursor = None
    try:
        conn, cursor = get_conn_and_cursor()
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
            if conn:
                conn.close()
        except:
            pass

    try:
        _, figures_base64, _ = generate_graphics(info_for_graphics)
        if not isinstance(figures_base64, dict):
            figures_base64 = dict(figures_base64)
    except Exception as e:
        app.logger.exception("Error en generate_graphics: %s", e)
        figures_base64 = {}

    # Parámetros para filtrado vía GET (cuando el usuario hace submit en el second-form)
    filter_type = request.args.get('filter-type')  
    selected_id = request.args.get('second-filter')

    message = None
    display_figures = {}

    if filter_type and selected_id:
        try:
            selected_id_int = int(selected_id)
        except:
            selected_id_int = None

        if selected_id_int is not None:
            try:
                conn, cursor = get_conn_and_cursor()
                filtered = {}
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

                    if cursor.fetchone():
                        filtered[name] = img

                if not filtered:
                    message = f"Los alumnos no han contestado el formulario de esta {filter_type}"
                else:
                    display_figures = filtered
                    
            except Exception as e:
                app.logger.exception("Error en filtrado: %s", e)
                message = "Ocurrió un error cargando los resultados."
            finally:
                try: cursor.close()
                except:pass
                try:conn.close()
                except:pass
    else:
    # No hay filtro → mostrar todos los gráficos
        display_figures = figures_base64 or {}
        if not display_figures:
            message = "No hay gráficos disponibles."

    return render_template(
        'teachers/inicio-teachers.html',
        figures=figures_base64,
        display_figures=display_figures,
        message=message
    )



@app.route('/teachers/download-report', methods=['GET'])
@require_role("docente")
def download_teacher_report():
    user_id = session['user_id']

    try:
        conn, cursor = get_conn_and_cursor()
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

    try:
        figures, _, figs_forms = generate_graphics(info_for_graphics)
        pdf_path = f"/tmp/teacher_{user_id}_metrics.pdf"
        figs_to_pdf(figs_forms, pdf_path)
    except Exception as e:
        app.logger.exception("Error al crear PDF: %s", e)
        return "Error creando el PDF", 500

    # Descargar el PDF
    return send_file(pdf_path, as_attachment=True, download_name="Reporte_Métricas.pdf")




@app.route('/admin/inicio', methods=['GET'])
@require_role("admin")
def admin_users():
    try:
        conn, cursor = get_conn_and_cursor()
        cursor.execute("""
            SELECT g.id AS id, g.nombre AS name
            FROM grupo g
            ORDER BY g.id;
        """)
        grupos = cursor.fetchall() or []
    except Exception as e:
        current_app.logger.exception("Error listando grupos: ", e)

    try:
        cursor.execute("""
            SELECT m.id AS id, m.name AS name
            FROM materia m
            ORDER BY m.id;
        """)
        materias = cursor.fetchall() or []
    except Exception as e:
        current_app.logger.exception("Error listando materias: ", e)

    try:
        cursor.execute("""
            SELECT d.id AS id, d.name AS name
            FROM user d
            WHERE role = 'docente'
            ORDER BY d.id;
        """)
        docentes = cursor.fetchall() or []
    except Exception as e:
        current_app.logger.exception("Error listando docentes: ", e)
    
    try:
        cursor.execute("""
            SELECT f.id AS id, f.title AS name
            FROM form f
            ORDER BY f.id;
        """)
        forms = cursor.fetchall() or []
    except Exception as e:
        current_app.logger.exception("Error listando formularios: ", e)
    
    try:
        cursor.execute("""
            SELECT a.id AS id, a.name AS name
            FROM user a
            WHERE role = 'alumnx'
            ORDER BY a.id;
        """)
        alumnxs = cursor.fetchall() or []
    except Exception as e:
        current_app.logger.exception("Error listando alumnxs: ", e)

    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass



    return render_template(
        'admin/inicio-admin.html',
        grupos=grupos,
        materias=materias,
        docentes=docentes,
        forms=forms,
        alumnxs=alumnxs
    )

@app.route('/admin/api/users-all', methods=['GET'])
def admin_api_users_all():
    conn = None
    cursor = None
    try:
        conn, cursor = get_conn_and_cursor()

        role_filter = (request.args.get('role') or '').strip()
        q = (request.args.get('q') or '').strip()
        date_filter = (request.args.get('date') or '').strip() 

        where = []
        params = []

        if role_filter:
            where.append("u.role = %s")
            params.append(role_filter)

        if q:
            where.append("(u.name LIKE %s OR u.matricula LIKE %s)")
            like = f"%{q}%"
            params += [like, like]


        current_app.logger.debug("admin_api_users_all - date_filter raw: '%s'", date_filter)

        if date_filter:
            # YYYY-MM
            if len(date_filter) == 7 and date_filter[4] == '-':
                try:
                    year = int(date_filter[0:4])
                    month = int(date_filter[5:7])
                    first_day = datetime(year, month, 1).date()
                    last_day_num = calendar.monthrange(year, month)[1]
                    last_day = datetime(year, month, last_day_num).date()
                    # filtramos por rango 
                    where.append("u.created_at BETWEEN %s AND %s")
                    params.append(first_day.strftime("%Y-%m-%d") + " 00:00:00")
                    params.append(last_day.strftime("%Y-%m-%d") + " 23:59:59")
                    current_app.logger.debug("admin_api_users_all - date range: %s to %s", params[-2], params[-1])
                except Exception as ex:
                    current_app.logger.exception("admin_api_users_all - invalid YYYY-MM parsing: %s", ex)
                    return jsonify({"error": "invalid_date_format", "details": "date must be YYYY-MM or YYYY-MM-DD"}), 400
            # YYYY-MM-DD
            elif len(date_filter) == 10 and date_filter[4] == '-' and date_filter[7] == '-':
                where.append("DATE(u.created_at) = %s")
                params.append(date_filter)
                current_app.logger.debug("admin_api_users_all - exact date filter: %s", date_filter)
            else:
                return jsonify({"error": "invalid_date_format", "details": "date must be YYYY-MM or YYYY-MM-DD"}), 400

        where_sql = "WHERE " + " AND ".join(where) if where else ""

        sql = f"""
            SELECT u.id, u.name, u.matricula, u.role, u.created_at
            FROM `user` u
            {where_sql}
            ORDER BY u.id DESC;
        """
        current_app.logger.debug("admin_api_users_all - SQL: %s -- params: %s", sql, params)

        cursor.execute(sql, tuple(params))
        users = cursor.fetchall() or []

        return jsonify(users)

    except Exception as e:
        current_app.logger.exception("Error en admin_api_users_all: %s", e)
        return jsonify({"error": "Error al filtrar", "details": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
        except:
            pass

@app.route('/admin/api/materias', methods=['GET'])
def admin_api_materias():
    conn = None
    cursor = None
    try:
        conn, cursor = get_conn_and_cursor()
        grupo_filter = (request.args.get('grupo') or '').strip()
        docente_filter = (request.args.get('docente') or '').strip()

        where = []
        params = []

        if grupo_filter:
            try:
                gid = int(grupo_filter)
                where.append("mg.id_grupo = %s")
                params.append(gid)
            except ValueError:
                # filtro por nombre del grupo
                where.append("g.nombre = %s")
                params.append(grupo_filter)

        if docente_filter:
            try:
                did = int(docente_filter)
                where.append("dm.id_docente = %s")
                params.append(did)
            except ValueError:
                # filtro por nombre del docente
                where.append("d.name = %s")
                params.append(docente_filter)

        where_sql = "WHERE " + " AND ".join(where) if where else ""

        sql = f"""
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
            {where_sql}
            ORDER BY m.id;
        """

        current_app.logger.debug("admin_api_materias - SQL: %s -- params: %s", sql, params)
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall() or []

    except Exception as e:
        current_app.logger.exception("Error en admin_api_materias: %s", e)
        return jsonify({'error': 'Error al cargar las materias', 'details': str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
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
            if not any(gx['id'] == gid for gx in materias_map[mid]['grupos']):
                materias_map[mid]['grupos'].append({
                    'id': gid,
                    'nombre': r.get('grupo_nombre')
                })
    materias = [materias_map[k] for k in sorted(materias_map.keys())]
    return jsonify(materias)

@app.route('/admin/api/respuestas', methods=['GET'])
def admin_api_respuestas():
    conn = None
    cursor = None
    filtros = []
    params = []

    form_id = (request.args.get('form') or '').strip()
    alumnx_id = (request.args.get('alumnx') or '').strip()
    date_filter = (request.args.get('date') or '').strip()

    try:
        if form_id:
            form_id_int = int(form_id)
            filtros.append("r.id_form = %s")
            params.append(form_id_int)
        if alumnx_id:
            alumnx_id_int = int(alumnx_id)
            filtros.append("r.id_alumnx = %s")
            params.append(alumnx_id_int)


        if date_filter:
            current_app.logger.debug("admin_api_respuestas - date_filter raw: '%s'", date_filter)
            # YYYY-MM
            if len(date_filter) == 7 and date_filter[4] == '-':
                try:
                    year = int(date_filter[0:4])
                    month = int(date_filter[5:7])
                    first_day = datetime(year, month, 1).date()
                    last_day_num = calendar.monthrange(year, month)[1]
                    last_day = datetime(year, month, last_day_num).date()
                    filtros.append("r.submitted_at BETWEEN %s AND %s")
                    params.append(first_day.strftime("%Y-%m-%d") + " 00:00:00")
                    params.append(last_day.strftime("%Y-%m-%d") + " 23:59:59")
                    current_app.logger.debug("admin_api_respuestas - date range: %s to %s", params[-2], params[-1])
                except Exception as ex:
                    current_app.logger.exception("admin_api_respuestas - invalid YYYY-MM parsing: %s", ex)
                    return jsonify({"error": "invalid_date_format", "details": "date must be YYYY-MM or YYYY-MM-DD"}), 400
            # YYYY-MM-DD
            elif len(date_filter) == 10 and date_filter[4] == '-' and date_filter[7] == '-':
                filtros.append("DATE(r.submitted_at) = %s")
                params.append(date_filter)
                current_app.logger.debug("admin_api_respuestas - exact date filter: %s", date_filter)
            else:
                return jsonify({"error": "invalid_date_format", "details": "date must be YYYY-MM or YYYY-MM-DD"}), 400

    except ValueError:
        return jsonify({'error': 'Valor de filtro inválido.', 'details': 'form and alumnx must be integers'}), 400

    where_sql = ("WHERE " + " AND ".join(filtros)) if filtros else ""

    try:
        conn, cursor = get_conn_and_cursor()
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
        current_app.logger.debug("admin_api_respuestas - SQL: %s -- params: %s", sql, params)
        cursor.execute(sql, tuple(params))
        rows = cursor.fetchall() or []
    except Exception as e:
        current_app.logger.exception("Error en las respuestas (filtradas): %s", e)
        try:
            cursor.close()
        except:
            pass
        return jsonify({'error': 'Error al cargar las respuestas.', 'details': str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if conn:
                conn.close()
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


@app.route('/admin/download-answers', methods=['GET'])
def download_admin_report():

    try:
        conn, cursor = get_conn_and_cursor()
        cursor.execute("""
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
            ORDER BY r.id DESC, a.id ASC;
        """)
        info_for_pdf = cursor.fetchall() or []

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        title = Paragraph("Reporte de Respuestas", styles["Title"])
        elements.append(title)


        styleN = ParagraphStyle(
            name="normal",
            fontSize=9,
            leading=11,   
        )

        data = [[
            Paragraph("ID Respuesta", styleN),
            Paragraph("Formulario", styleN),
            Paragraph("Alumno", styleN),
            Paragraph("Fecha", styleN),
            Paragraph("Pregunta", styleN),
            Paragraph("Respuesta", styleN)
        ]]

        for row in info_for_pdf:
            respuesta = row["texto_respuesta"] or row["choice_text"] or ""
            fecha = row["submitted_at"].strftime("%d/%m/%Y %H:%M") if row["submitted_at"] else ""


            data.append([
                Paragraph(str(row["response_id"]), styleN),
                Paragraph(f"{row['form_title']} ({row['form_title']})", styleN),
                Paragraph(f"{row['alumnx_name']} ({row['alumnx_matricula']})", styleN),
                Paragraph(fecha, styleN),
                Paragraph(row["texto_pregunta"], styleN),
                Paragraph(respuesta, styleN),
            ])


        table = Table(data, colWidths=[50, 150, 80, 100, 100, 100])

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0710b")),  # encabezado
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#331901")),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),

            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),

            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fbbe47")),

            # Filas
            ("BACKGROUND", (0, 0), (-1, -1), colors.white)
        ]))

        elements.append(table)

        # Construir PDF
        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name="reporte_respuestas.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print("Error generando PDF:", e)
        return "Error generando PDF", 500


@app.route('/admin/api/user-create', methods=['POST'])
def admin_api_user_create():

    data = request.get_json() or {}

    id = (data.get('id') or '').strip()
    name = (data.get('name') or '').strip()
    matricula = (data.get('matricula') or '').strip()
    password = data.get('password') or ''
    role = (data.get('role') or '').strip()
    
    if not name or not matricula or not role:
        return jsonify({'error': 'Falta rellenar campos'}), 400
    
    pw_hash = hashlib.md5(password.encode()).hexdigest() if password else None

    conn = cursor = None
    try:
        conn, cursor = get_conn_and_cursor()
        cursor.execute(
            "SELECT 1 FROM user WHERE matricula = %s", (matricula, ))
        exists = cursor.fetchall()

        if exists:
            return jsonify({'error': 'Este usuario ya está registrado.'}), 400
    
        cursor.execute(
            "INSERT INTO `user` (name, matricula, password, role, created_at) VALUES (%s, %s, %s, %s, NOW())",
            (name, matricula, pw_hash, role)
        )
        user_id = cursor.lastrowid

        if role == 'alumnx':
            group_id = data.get('alumnx_grupo')
            cursor.execute(
             "SELECT id_materia FROM materia_grupo WHERE id_grupo = %s", (group_id, ) ) #id de las materias que se dan en ese grupo
            materias_ids = cursor.fetchall()
            for id_materia in materias_ids:
                cursor.execute("INSERT INTO `alumnx_materia` (id_alumnx, id_course) VALUES (%s, %s)", (user_id,id_materia['id_materia']))
                

        if role == 'docente':
            materias_ids = data.get('docente_materias', [])

            # 1. Insertar relaciones docente ↔ materias
            for materia_id in materias_ids:
                cursor.execute(
                    "INSERT INTO docente_materia (id_docente, id_materia) VALUES (%s, %s)",
                    (user_id, materia_id)
                )

            # 2. Crear un único form para el docente
            form_title = f'Docente: {name}'
            description = f'Evaluación del/la docente ({name})'

            cursor.execute("""
                INSERT INTO form (title, description, id_docente, id_materia, start_at, end_at, active)
                VALUES (%s, %s, %s, NULL, NOW(), '2025-12-31 23:59:59', 1)
            """, (form_title, description, user_id))

            form_id = cursor.lastrowid

            # 3. Crear preguntas
            preguntas = [
                "El docente explica los conceptos claramente.",
                "El docente fomenta la participación.",
                "El docente domina el contenido.",
                "Los recursos son adecuados.",
                "El docente muestra interés por el aprendizaje.",
                "Comentarios adicionales (texto libre)."
            ]

            for texto in preguntas[:-1]:  # multiple choice
                cursor.execute("""
                    INSERT INTO question (id_form, texto_pregunta, tipo)
                    VALUES (%s, %s, 'multiple')
                """, (form_id, texto))
                q_id = cursor.lastrowid
                for i, choice in enumerate(["Muy de acuerdo", "De acuerdo", "En desacuerdo", "Muy en desacuerdo"], start=1):
                    cursor.execute("""
                        INSERT INTO choice (id_question, choice_text, sort_order)
                        VALUES (%s, %s, %s)
                    """, (q_id, choice, i))

            # último texto libre
            cursor.execute("""
                INSERT INTO question (id_form, texto_pregunta, tipo)
                VALUES (%s, %s, 'texto')
            """, (form_id, preguntas[-1]))


        conn.commit()
        
        cursor.execute("SELECT id, name, matricula, role, created_at FROM `user` WHERE id = %s", (user_id,))
        new_user = cursor.fetchone()
        flash("Usuario registrado correctamente")
        return jsonify({'ok': True, 'user': new_user}), 201
    except Exception as e:
        current_app.logger.exception("Error creando usuario admin: %s", e)
        return jsonify({'error': 'Error creando usuario', 'details': str(e)}), 500
    finally:
        try:
            if cursor: cursor.close()
        except: pass
        try:
            if conn: conn.close()
        except: pass

@app.route('/admin/api/user-update', methods=['POST'])
def admin_api_user_update():
    data = request.get_json() or {}
    uid = data.get('id')
    if not uid:
        return jsonify({'error': 'Falta id'}), 400
    name = (data.get('name') or '').strip()
    matricula = (data.get('matricula') or '').strip()
    password = data.get('password')  
    role = (data.get('role') or '').strip()

    fields = []
    params = []
    if name:
        fields.append("name = %s"); params.append(name)
    if matricula:
        fields.append("matricula = %s"); params.append(matricula)
    if role:
        fields.append("role = %s"); params.append(role)
    if password:
        pw_hash = hashlib.md5(password.encode()).hexdigest()
        fields.append("password = %s"); params.append(pw_hash)

    if not fields:
        return jsonify({'error': 'No hay campos.'}), 400

    params.append(uid)
    sql = f"UPDATE `user` SET {', '.join(fields)} WHERE id = %s"
    conn = cursor = None
    try:
        conn, cursor = get_conn_and_cursor()
        cursor.execute(sql, tuple(params))

        if role == 'alumnx':
            cursor.execute("DELETE FROM alumnx_materia WHERE id_alumnx=%s", (uid,))

            group_id = data.get('alumnx_grupo')
            cursor.execute(
             "SELECT id_materia FROM materia_grupo WHERE id_grupo = %s", (group_id, ) ) #id de las materias que se dan en ese grupo
            materias_ids = cursor.fetchall()

            for id_materia in materias_ids:
                cursor.execute("INSERT INTO `alumnx_materia` (id_alumnx, id_course) VALUES (%s, %s)", (uid, id_materia['id_materia']))

        if role == 'docente':
            cursor.execute("DELETE FROM docente_materia WHERE id_docente=%s", (uid,))
            materias_ids = data.get('docente_materias')

            for id_materia in materias_ids:
                cursor.execute("INSERT INTO `docente_materia` (id_docente, id_materia) VALUES (%s, %s)", (uid, id_materia))

        conn.commit()
        cursor.execute("SELECT id, name, matricula, role, created_at FROM `user` WHERE id = %s", (uid,))
        user = cursor.fetchone()
        flash("Usuario editado correctamente")
        return jsonify({'ok': True, 'user': user})
    except Exception as e:
        current_app.logger.exception("Error actualizando usuario admin: %s", e)
        return jsonify({'error': 'Error actualizando usuario', 'details': str(e)}), 500
    finally:
        try:
            if cursor: cursor.close()
        except: pass
        try:
            if conn: conn.close()
        except: pass

@app.route('/admin/api/user-delete', methods=['POST'])
def admin_api_user_delete():

    data = request.get_json() or {}
    uid = data.get('id')

    if not uid:
        return jsonify({'error': 'Falta de id.'}), 400
    conn = cursor = None
    try:
        conn, cursor = get_conn_and_cursor()

        cursor.execute("DELETE FROM `user` WHERE id = %s", (uid,))

        conn.commit()
        flash("Usuario eliminado correctamente")
        return jsonify({'ok': True, 'deleted_id': uid})
    except Exception as e:
        current_app.logger.exception("Error borrando usuario admin: %s", e)
        return jsonify({'error': 'Error borrando usuario', 'details': str(e)}), 500
    finally:
        try:
            if cursor: cursor.close()
        except: pass
        try:
            if conn: conn.close()
        except: pass


@app.route('/admin/api/materia-create', methods=['POST'])
def admin_api_materia_create():

    
    data = request.get_json() or {}

    name = (data.get('name') or '').strip()
    id_docente = data.get('docente')  
    id_grupo = data.get('grupo')     

    if not name or not id_docente or not id_grupo:
        return jsonify({'error': 'Faltan campos'}), 400
    
    conn = cursor = None
    try:
        conn, cursor = get_conn_and_cursor()

        # validar duplicado
        cursor.execute("SELECT 1 FROM materia WHERE name = %s", (name,))
        if cursor.fetchone():
            return jsonify({'error': 'Esta materia ya existe.'}), 400

        # insertar materia
        cursor.execute("INSERT INTO materia (name) VALUES (%s)", (name,))
        materia_id = cursor.lastrowid

        # relaciones
        cursor.execute(
            "INSERT INTO materia_grupo (id_materia, id_grupo) VALUES (%s, %s)",
            (materia_id, id_grupo)
        )
        cursor.execute(
            "INSERT INTO docente_materia (id_materia, id_docente) VALUES (%s, %s)",
            (materia_id, id_docente)
        )

        # Crear form de materia
        form_title = f"Form - Materia: {name}"
        description = f"Evaluación de la materia ({name})"

        cursor.execute("""
            INSERT INTO form (title, description, id_materia, start_at, end_at, active)
            VALUES (%s, %s, %s, NOW(), '2025-12-31 23:59:59', 1)
        """, (form_title, description, materia_id))
        
        form_id = cursor.lastrowid

        # Preguntas
        preguntas = [
            "Los temas son interesantes",
            "El semestre es suficiente para abarcar lo necesario",
            "El temario es completo.",
            "Los recursos son adecuados.",
            "Me interesa el contenido de la materia.",
            "Comentarios adicionales (texto libre)."
        ]

        # Multiple choice
        for texto in preguntas[:-1]:
            cursor.execute("""
                INSERT INTO question (id_form, texto_pregunta, tipo)
                VALUES (%s, %s, 'multiple')
            """, (form_id, texto))
            q_id = cursor.lastrowid

            for i, choice in enumerate(["Muy de acuerdo", "De acuerdo", "En desacuerdo", "Muy en desacuerdo"], start=1):
                cursor.execute("""
                    INSERT INTO choice (id_question, choice_text, sort_order)
                    VALUES (%s, %s, %s)
                """, (q_id, choice, i))

        # Pregunta texto
        cursor.execute("""
            INSERT INTO question (id_form, texto_pregunta, tipo)
            VALUES (%s, %s, 'texto')
        """, (form_id, preguntas[-1]))

        conn.commit()

        return jsonify({'ok': True, 'materia_id': materia_id}), 201

    except Exception as e:
        current_app.logger.exception("Error creando materia admin: %s", e)
        return jsonify({'error': 'Error creando materia', 'details': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/admin/api/materia-delete', methods=['POST'])
def admin_api_materia_delete():

    data = request.get_json() or {}
    uid = data.get('id')

    if not uid:
        return jsonify({'error': 'Falta de id.'}), 400
    conn = cursor = None
    try:
        conn, cursor = get_conn_and_cursor()

        cursor.execute("DELETE FROM materia WHERE id = %s", (uid,))

        conn.commit()
        flash("Materia eliminado correctamente")
        return jsonify({'ok': True, 'deleted_id': uid})
    except Exception as e:
        current_app.logger.exception("Error borrando materia: %s", e)
        return jsonify({'error': 'Error borrando materia', 'details': str(e)}), 500
    finally:
        try:
            if cursor: cursor.close()
        except: pass
        try:
            if conn: conn.close()
        except: pass


@app.route('/admin/api/materia-update', methods=['POST'])
def admin_api_materia_update():
    
    data = request.get_json() or {}
    uid = data.get('id')
    
    if not uid:
        return jsonify({'error': 'Falta id'}), 400
    
    name = (data.get('name') or '').strip()
    id_docente = data.get('docente')
    id_grupo = data.get('grupo')    

    conn = cursor = None
    try:
        conn, cursor = get_conn_and_cursor()
        if name:
            cursor.execute("UPDATE materia SET name = %s WHERE id = %s", (name, uid))
        
        cursor.execute("DELETE FROM docente_materia WHERE id_materia = %s", (uid, ))
        if id_docente:
            cursor.execute("INSERT INTO docente_materia (id_materia, id_docente) VALUES (%s, %s)", (uid, id_docente))
        
        cursor.execute("DELETE FROM materia_grupo WHERE id_materia = %s", (uid,))
        if id_grupo:
            cursor.execute("INSERT INTO materia_grupo (id_materia, id_grupo) VALUES (%s, %s)", (uid, id_grupo))

        conn.commit()
        cursor.execute("SELECT id, name FROM materia WHERE id = %s", (uid,))
        materia = cursor.fetchone()

        cursor.execute("SELECT id_docente FROM docente_materia WHERE id_materia = %s", (uid,))
        docente_row = cursor.fetchone()
        materia_docente = docente_row['id_docente'] if docente_row else None


        cursor.execute("SELECT id_grupo FROM materia_grupo WHERE id_materia = %s", (uid,))
        grupo_row = cursor.fetchone()
        materia_grupo = grupo_row['id_grupo'] if grupo_row else None


        flash("Materia editada correctamente")

        return jsonify({
            'ok': True,
            'materia': {
                'id': materia['id'],
                'name': materia['name'],
                'id_docente': materia_docente,
                'id_grupo': materia_grupo
            }
        })
    
    except Exception as e:
        current_app.logger.exception("Error actualizando materia admin: %s", e)
        return jsonify({'error': 'Error actualizando materia', 'details': str(e)}), 500
    finally:
        try:
            if cursor: cursor.close()
        except: pass
        try:
            if conn: conn.close()
        except: pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
