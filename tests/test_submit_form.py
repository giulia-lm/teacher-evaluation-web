"""
pytest tests/test_submit_form.py -q

"""

import time
import os
import pytest
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from utils import take_debug_artifacts  


ALUMNO_USER = os.getenv("TEST_ALUMNO_USER", "A004")
ALUMNO_PASS = os.getenv("TEST_ALUMNO_PASS", "p4nda")

# umbral para RnF-C.5 (segundos). Ajusta si tu máquina de CI es más lenta.
CONFIRMATION_THRESHOLD_SEC = 1.0

def login_as_alumno(page, username, password):
    page.goto("http://localhost:5000/alumnxs/login-alumnxs", timeout=15000)
    page.fill("input[name='uname']", username)
    page.fill("input[name='psw']", password)
    page.click("button[type='submit']")

    page.wait_for_url("**/alumnxs/inicio-alumnxs**", timeout=10000)

def open_first_questionnaire(page):
    try:
        page.wait_for_selector('div[name="forms-list"] .form-card, .available-forms-container .form-card', timeout=7000)
    except PWTimeout:
        raise AssertionError("No se encontraron cuestionarios visibles en inicio-alumnxs")

    first_item = page.query_selector('div[name="forms-list"] .form-card, .available-forms-container .form-card')
    if not first_item:
        raise AssertionError("No se pudo localizar el primer cuestionario")
    anchor = first_item.query_selector("a[href]")
    if anchor:
        anchor.click()
    else:

        btn = first_item.query_selector(".btn-open-form, button[name='btn-open']")
        if btn:
            btn.click()
        else:
            first_item.click()

    try:
        page.wait_for_url("**/alumnxs/inicio-alumnxs/**", timeout=10000)
    except PWTimeout:
        raise AssertionError("El formulario del cuestionario no se mostró tras abrirlo; URL actual: " + page.url)


def answer_all_closed_questions(page):
    try:
        page.wait_for_selector('section[name="form-card"], .survey-section, form.survey-form, form#questionnaireForm', timeout=7000)
    except PWTimeout:
        raise AssertionError("No se encontró el formulario del cuestionario")

    question_cards = page.query_selector_all(".question-card")
    if not question_cards:
        radios = page.query_selector_all("input[type='radio']")
        if not radios:
            raise AssertionError("No se detectaron preguntas cerradas (radios) en el formulario")
        seen = set()
        for r in radios:
            name = r.get_attribute("name")
            if name and name not in seen:
                r.click()
                seen.add(name)
        return

    for qc in question_cards:
        radio = qc.query_selector("input[type='radio']")
        if radio:
            radio.click()
        else:
            chk = qc.query_selector("input[type='checkbox']")
            if chk:
                chk.click()
            else:
                sel = qc.query_selector("select")
                if sel:
                    options = sel.query_selector_all("option")
                    for o in options:
                        v = o.get_attribute("value")
                        if v and v.strip() != "":
                            sel.select_option(v)
                            break


def fill_comment_if_present(page, text="Buen curso, gracias."):
    ta = page.query_selector("textarea[name$='_comments'], textarea[name^='q'][name$='_comments'], textarea[placeholder*='Escribe tu respuesta']")
    if ta:
        ta.fill(text)
        return

    ta_any = page.query_selector("form textarea")
    if ta_any:
        ta_any.fill(text)


def submit_and_wait_confirmation(page):
    submit_btn = page.query_selector("form button[type='submit'], .btn-submit, button[name='btn-submit']")
    if not submit_btn:
        raise AssertionError("No se encontró botón de envío en el formulario")

    # medir tiempo
    start = time.time()
    submit_btn.click()

    try:
        page.wait_for_url("**/alumnxs/inicio-alumnxs**", timeout=10000)
    except PWTimeout:
        pass

    confirmation_selector = ".alert-section .flashes li, .flashes li, section.alert-section .flashes li"
    found = False
    elapsed = None
    try:
        page.wait_for_selector(confirmation_selector, timeout=int(CONFIRMATION_THRESHOLD_SEC * 1000))
        elapsed = time.time() - start
        found = True
    except PWTimeout:

        try:
            page.wait_for_selector(confirmation_selector, timeout=5000)
            elapsed = time.time() - start
            found = True
        except PWTimeout:
            found = False

    if not found:
        take_debug_artifacts(page, "submit_no_confirmation")
        raise AssertionError("No se detectó confirmación de envío (no se halló .flashes li)")

    # comprobación de RnF-C.5
    if elapsed is None:
        elapsed = time.time() - start

    assert elapsed <= CONFIRMATION_THRESHOLD_SEC, (
        f"Confirmación visible en {elapsed:.2f}s — excede el umbral de {CONFIRMATION_THRESHOLD_SEC:.2f}s"
    )

    text = page.inner_text(confirmation_selector)
    return elapsed, text


@pytest.mark.order(1)
def test_alumno_submit_questionnaire():
    """Test e2e: login alumno -> abrir cuestionario -> responder -> enviar -> confirmar estado"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            login_as_alumno(page, ALUMNO_USER, ALUMNO_PASS)
            page.wait_for_selector('div[name="forms-list"] .form-card, .available-forms-container .form-card', timeout=7000)
            open_first_questionnaire(page)
            #  en el form
            answer_all_closed_questions(page)
            fill_comment_if_present(page, "Prueba automatizada: todo bien.")
            elapsed = submit_and_wait_confirmation(page)
        except Exception:
            take_debug_artifacts(page, "alumno_submit_exception")
            raise
        finally:
            context.close()
            browser.close()
