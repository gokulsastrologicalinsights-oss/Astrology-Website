"""Monitors Render and Vercel production deployment of checkpoint 6cb007d / c081de6.

Probes https://gai-astrology-backend.onrender.com/health and https://astro.gaionline.in/health
to detect the exact moment the sanitized production container with zero engine disclosures goes live.
"""

import json
import sys
import time
import urllib.error
import urllib.request

BACKEND_URL = "https://gai-astrology-backend.onrender.com"
FRONTEND_URL = "https://astro.gaionline.in"

def probe(url):
    try:
        req = urllib.request.Request(f"{url}/health", headers={"Accept": "application/json", "User-Agent": "GAI-Deployment-Monitor/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            rndr_id = resp.headers.get("Rndr-Id", "")
            body = json.loads(resp.read().decode("utf-8", errors="replace"))
            return resp.status, body, rndr_id
    except urllib.error.HTTPError as e:
        return e.code, str(e), e.headers.get("Rndr-Id", "")
    except Exception as exc:
        return 0, str(exc), ""

def main():
    print(f"Monitoring production deployment of checkpoint 6cb007d...")
    start_time = time.time()
    max_duration = 600  # 10 minutes max
    poll_interval = 15

    while time.time() - start_time < max_duration:
        elapsed = int(time.time() - start_time)
        b_status, b_body, b_rndr = probe(BACKEND_URL)
        f_status, f_body, f_rndr = probe(FRONTEND_URL)

        has_engine_b = isinstance(b_body, dict) and "engine" in b_body
        has_engine_f = isinstance(f_body, dict) and "engine" in f_body

        print(f"[{elapsed}s elapsed] Backend: HTTP {b_status} (engine_disclosed={has_engine_b}, rndr={b_rndr}) | Frontend Proxy: HTTP {f_status} (engine_disclosed={has_engine_f})")

        if b_status == 200 and not has_engine_b:
            print("\n" + "=" * 60)
            print(">>> NEW SANITIZED BUILD IS LIVE ON RENDER PRODUCTION! <<<")
            print(f"Response: {b_body}")
            print(f"Render ID: {b_rndr}")
            print("=" * 60 + "\n")
            return 0

        time.sleep(poll_interval)

    print("\nTimeout waiting for new deployment to show active.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
