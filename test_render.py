import sys, os, tempfile, subprocess, shutil
sys.path.insert(0, r"d:\GAI\Astrology Website\backend")
from app.services.pdf_report_engine.single_page_generator import SinglePageHoroscopePdfGenerator
from app.schemas.common import BirthInput
from datetime import date, time

b = BirthInput(birth_date=date(1999, 1, 3), birth_time=time(5, 58), timezone="Asia/Kolkata", latitude=13.0827, longitude=80.2707)
gen = SinglePageHoroscopePdfGenerator(birth_input=b, native_name="Gokul", native_id="#01")
html_content = gen.generate_html()

browser_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
    f.write(html_content)
    html_path = f.name

pdf_path = html_path.replace(".html", ".pdf")
file_url = "file:///" + html_path.replace("\\", "/")
cmd = [
    browser_path,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    file_url
]
res = subprocess.run(cmd, capture_output=True, timeout=30)
print("CLI exit code:", res.returncode)
print("CLI PDF exists:", os.path.exists(pdf_path))
if os.path.exists(pdf_path):
    print("CLI PDF size:", os.path.getsize(pdf_path))
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(pdf_path)
    page = doc[0]
    img = page.render(scale=2).to_pil()
    img.save("test_cli_render.png")
    print("CLI PDF rendered to test_cli_render.png")
