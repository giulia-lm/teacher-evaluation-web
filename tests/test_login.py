"""
Probar un tipo de usuario especifico:
pytest tests/test_login.py::test_logins -q -k "alumnx"
pytest tests/test_login.py::test_logins -q -k "docente"
pytest tests/test_login.py::test_logins -q -k "admin"

Probar todos los tipos:
pytest tests/test_login.py -q


"""
import os
import pytest
from playwright.sync_api import sync_playwright
from utils import take_debug_artifacts  


ALUMNO_USER = os.getenv("TEST_ALUMNO_USER", "A004")
ALUMNO_PASS = os.getenv("TEST_ALUMNO_PASS", "p4nda")
DOCENTE_USER = os.getenv("TEST_DOCENTE_USER", "D002")
DOCENTE_PASS = os.getenv("TEST_DOCENTE_PASS", "ham1lton")
ADMIN_USER = os.getenv("TEST_ADMIN_USER", "00000")
ADMIN_PASS = os.getenv("TEST_ADMIN_PASS", "Admin123!")

def single_login_flow(login_url, url_glob, username, password, panel_selector, headless=True):
    """Función reutilizable para realizar un login y validar el panel.
       url_glob: glob aceptado por wait_for_url, por ejemplo "**/alumnxs/inicio-alumnxs"
       panel_selector: selector esperado en el dashboard (p. ej. "nav", "h1")
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(login_url, timeout=15000)
            page.fill("input[name='uname']", username)
            page.fill("input[name='psw']", password)
            page.click("button[type='submit']")

            try:
                page.wait_for_url(url_glob, timeout=10000)
            except Exception:
                print("No se detectó redirección exacta. URL actual:", page.url)

            try:
                page.wait_for_selector(panel_selector, timeout=5000)
            except Exception:
                take_debug_artifacts(page, f"login_no_panel_{username}")
                raise AssertionError(f"No se encontró el selector del panel '{panel_selector}'. URL: {page.url}")
            
            panel_text = page.inner_text(panel_selector)
            assert panel_text.strip() != "", "El selector del panel está vacío"

        except Exception:
            try:
                take_debug_artifacts(page, f"login_exception_{username}")
            except Exception as e:
                print("Error guardando artefactos:", e)
            raise
        finally:
            context.close()
            browser.close()


@pytest.mark.parametrize("login_url,url_glob,username,password,panel_selector", [
    ("http://localhost:5000/alumnxs/login-alumnxs", "**/alumnxs/inicio-alumnxs", ALUMNO_USER, ALUMNO_PASS, "nav"),
    ("http://localhost:5000/teachers/login-teachers", "**/teachers/inicio", DOCENTE_USER, DOCENTE_PASS, "nav"),
    ("http://localhost:5000/admin/login-admin", "**/admin/inicio", ADMIN_USER, ADMIN_PASS, "nav"),
])
def test_logins(login_url, url_glob, username, password, panel_selector):
    single_login_flow(login_url, url_glob, username, password, panel_selector, headless=True)
