from playwright.sync_api import sync_playwright
from utils import take_debug_artifacts

def test_login_success():
    with sync_playwright() as p:
        # headless para no  depurar visualmente 
        browser = p.chromium.launch(headless=True)  
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto("http://localhost:5000/alumnxs/login-alumnxs", timeout=15000)
            
            page.fill("input[name='uname']", "A004")
            page.fill("input[name='psw']", "p4nda")
            page.click("button[type='submit']")

            try:
                page.wait_for_url("**/alumnxs/inicio-alumnxs**", timeout=10000)
            except:
                print("No se detectó redirección exacta a /alumnxs/inicio-alumnxs. URL actual:", page.url)

            try:
                assert "Evaluación Docente" in page.inner_text("nav")
                print(f"Selector encontrado")
            
            except:
                take_debug_artifacts(page, "login_no_panel")
                assert False, f"No se encontró selector de panel. URL actual: {page.url}"


        except Exception as e:
            try:
                take_debug_artifacts(page, "login_exception")
            except:
                pass
            raise
        finally:
            context.close()
            browser.close()