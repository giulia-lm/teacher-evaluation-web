import os

def take_debug_artifacts(page, name="failure"):
    os.makedirs("artifacts", exist_ok=True)
    screenshot_path = f"artifacts/{name}.png"
    html_path = f"artifacts/{name}.html"
    try:
        page.screenshot(path=screenshot_path, full_page=True)
    except Exception as e:
        print("Error taking screenshot:", e)
    try:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(page.content())
    except Exception as e:
        print("Error dumping HTML:", e)
    print(f"Saved artifacts: {screenshot_path}, {html_path}")