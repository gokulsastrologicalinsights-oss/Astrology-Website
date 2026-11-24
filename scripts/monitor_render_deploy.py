"""Monitors Render production deployment of commit 7b56263 / a3dfc75.

Probes https://gai-astrology-backend.onrender.com/health and
checks the Content-Disposition header on /api/v1/reports/horoscope/single-page-pdf
to detect the exact moment the new container with RFC 6266 headers and official letterhead goes live.
"""

import io
import json
import sys
import time
import urllib.error
import urllib.request
import pypdf

BACKEND_URL = "https://gai-astrology-backend.onrender.com"
HEALTH_URL = f"{BACKEND_URL}/health"
PDF_URL = f"{BACKEND_URL}/api/v1/reports/horoscope/pdf"

SAMPLE_PAYLOAD = {
    "birth_input": {
        "birth_date": "1999-01-03",
        "birth_time": "05:58:00",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
    },
    "native_name": "Deployment Monitor",
    "language": "en",
    "report_style": "full",
}

def probe_health():
    try:
        req = urllib.request.Request(HEALTH_URL, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            rndr_id = resp.headers.get("Rndr-Id", "")
            return resp.status, resp.read().decode("utf-8", errors="replace"), rndr_id
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace"), e.headers.get("Rndr-Id", "")
    except Exception as exc:
        return 0, str(exc), ""

def probe_pdf():
    try:
        data = json.dumps(SAMPLE_PAYLOAD).encode("utf-8")
        req = urllib.request.Request(
            PDF_URL,
            data=data,
            headers={"Content-Type": "application/json", "Accept": "application/pdf"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            cd = resp.headers.get("Content-Disposition", "")
            rndr_id = resp.headers.get("Rndr-Id", "")
            body = resp.read()
            # Inspect image in PDF
            r = pypdf.PdfReader(io.BytesIO(body))
            img_dims = []
            if len(r.pages) > 0 and len(r.pages[0].images) > 0:
                for img in r.pages[0].images:
                    img_dims.append(img.image.size)
            return resp.status, cd, img_dims, rndr_id
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Disposition", ""), [], e.headers.get("Rndr-Id", "")
    except Exception as exc:
        return 0, str(exc), [], ""

def main():
    print(f"Monitoring Render deployment at {BACKEND_URL}...")
    start_time = time.time()
    for attempt in range(1, 31):
        elapsed = int(time.time() - start_time)
        h_code, h_body, h_rndr = probe_health()
        print(f"\n[Attempt {attempt} | {elapsed}s] Health: HTTP {h_code} (Rndr-Id: {h_rndr})")

        p_code, p_cd, p_imgs, p_rndr = probe_pdf()
        print(f"  Horoscope PDF: HTTP {p_code} | CD: {p_cd[:70]} | Images: {p_imgs}")

        # Check for RFC 6266 header format: filename*=UTF-8'' or letterhead image dimensions (718, 1016)
        if "filename*=UTF-8''" in p_cd or any(dim == (718, 1016) for dim in p_imgs):
            print("\n=======================================================")
            print(">>> NEW DEPLOYMENT DETECTED LIVE ON RENDER! <<<")
            print(f">>> Content-Disposition: {p_cd}")
            print(f">>> Image Dimensions: {p_imgs}")
            print(f">>> Render Request ID: {p_rndr}")
            print("=======================================================")
            return True

        time.sleep(15)

    print("\nTimeout waiting for new deployment to show active.")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
