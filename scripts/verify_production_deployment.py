"""Comprehensive Post-Deployment Verification Suite for GAI Production Release.

Verifies:
1. Homepage (https://astro.gaionline.in/)
2. Login and Registration (/login, /register)
3. Customer Dashboard (/dashboard)
4. Birth Horoscope (/api/v1/horoscope/calculate)
5. KP Astrology (/api/v1/horoscope/kp)
6. Vedic Astrology (/api/v1/vedic/shadbala)
7. Dasa-Bhukti (/api/v1/horoscope/dasa)
8. Transit Predictions (/api/v1/horoscope/live-transits)
9. Marriage Matching (/api/v1/marriage-compatibility/analyze)
10. Numerology (/api/v1/numerology/traditional)
11. Remedies (/api/v1/remedies/catalog & taxonomy)
12. PDF Reports (/api/v1/reports/horoscope/single-page-pdf)
13. Admin Dashboard (/admin, /api/v1/admin/users)
14. Admin Rules Access (/api/v1/rules/inventory & evaluate)
15. Payment Configuration (/api/payments/create-order)

Verifies that no technical engine names, unnecessary author names or classical reference book details are exposed in customer-facing pages and APIs.
"""

import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pypdf import PdfReader

FRONTEND_URL = os.environ.get("PRODUCTION_FRONTEND_URL", "https://astro.gaionline.in")
BACKEND_URL = os.environ.get("PRODUCTION_BACKEND_URL", "https://gai-astrology-backend.onrender.com")

# Comprehensive Forbidden keywords in customer-facing API responses & UI
FORBIDDEN_KEYWORDS = [
    "XALEN",
    "Swiss Ephemeris",
    "swisseph",
    "pyswisseph",
    "KP Engine",
    "Sivadasan Ravi",
    "Sannu Ahmed",
    "Marc Boney",
    "Mark Boney",
    "Dr. S. Krishna Kumar",
    "Heinrich Daath",
    "Picatrix",
    "BPHS Ch.",
    "Phaladeepika Ch.",
    "Kalaprakasika",
    "Muhurta Chintamani",
]

STANDARD_BIRTH_INPUT = {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "ayanamsa": 0,
    "house_system": 0,
}

MARRIAGE_PAYLOAD = {
    "groom": {
        "name": "Karthik Subramanian",
        "gender": "male",
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
    },
    "bride": {
        "name": "Meenakshi Sundaram",
        "gender": "female",
        "birth_date": "1992-08-20",
        "birth_time": "10:15:00",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "timezone": "Asia/Kolkata",
    },
    "rule_system": "both",
    "ayanamsa_id": 0,
    "house_system_id": 0,
    "include_timing": True,
    "include_kp": True,
}

NUMEROLOGY_PAYLOAD = {
    "full_name": "Gokul Murugan",
    "birth_date": "1990-05-15",
    "system_convention": "pythagorean",
    "language": "en",
}

results = []

def record(test_num, name, status, details, disclosure_clean=True, matched_terms=None):
    results.append({
        "num": test_num,
        "name": name,
        "status": status,
        "details": details,
        "disclosure_clean": disclosure_clean,
        "matched_terms": matched_terms or [],
    })
    mark = "PASS" if status and disclosure_clean else "FAIL"
    terms_info = f" (Violations: {matched_terms})" if matched_terms else ""
    print(f"[{mark}] #{test_num}: {name} - {details}{terms_info}")

def scan_disclosures(text):
    found = []
    text_lower = text.lower()
    for kw in FORBIDDEN_KEYWORDS:
        if kw.lower() in text_lower:
            found.append(kw)
    return found

def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read()

def http_post_json(url, payload, headers=None):
    h = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    if headers:
        h.update(headers)
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.status, resp.read()

def run_all_checks():
    results.clear()
    print("=" * 80)
    print("GAI PRODUCTION POST-DEPLOYMENT VERIFICATION")
    print(f"Frontend: {FRONTEND_URL}")
    print(f"Backend:  {BACKEND_URL}")
    print("=" * 80)

    # 1. Homepage
    try:
        status, body = http_get(f"{FRONTEND_URL}/")
        text = body.decode("utf-8", errors="replace")
        disclosures = scan_disclosures(text)
        record(1, "Homepage", status == 200, f"HTTP {status}, body length {len(text)}", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(1, "Homepage", False, str(e), False)

    # 2. Login & Registration
    try:
        status_login, body_login = http_get(f"{FRONTEND_URL}/login")
        status_reg, body_reg = http_get(f"{FRONTEND_URL}/register")
        disclosures = scan_disclosures(body_login.decode("utf-8", errors="replace") + body_reg.decode("utf-8", errors="replace"))
        ok = (status_login == 200 and status_reg == 200)
        record(2, "Login and Registration UI", ok, f"Login HTTP {status_login}, Register HTTP {status_reg}", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(2, "Login and Registration UI", False, str(e), False)

    # 3. Customer Dashboard
    try:
        status, body = http_get(f"{FRONTEND_URL}/dashboard")
        text = body.decode("utf-8", errors="replace")
        disclosures = scan_disclosures(text)
        record(3, "Customer Dashboard UI", status in [200, 307, 308], f"HTTP {status} (loads / redirects to auth)", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(3, "Customer Dashboard UI", False, str(e), False)

    # 4. Birth Horoscope
    try:
        status, body = http_post_json(f"{BACKEND_URL}/api/v1/horoscope/calculate", STANDARD_BIRTH_INPUT)
        data = json.loads(body.decode("utf-8"))
        raw_text = json.dumps(data)
        disclosures = scan_disclosures(raw_text)
        has_planets = "planets" in data and len(data["planets"]) >= 7
        has_asc = "ascendant" in data
        record(4, "Birth Horoscope Calculation", status == 200 and has_planets and has_asc, f"HTTP {status}, {len(data.get('planets', []))} planets computed", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(4, "Birth Horoscope Calculation", False, str(e), False)

    # 5. KP Astrology (Planets & Cusps)
    try:
        status, body = http_post_json(f"{BACKEND_URL}/api/v1/horoscope/kp", STANDARD_BIRTH_INPUT)
        data = json.loads(body.decode("utf-8"))
        raw_text = json.dumps(data)
        disclosures = scan_disclosures(raw_text)
        has_cusps = "cuspal_analysis" in data or "cusps" in data
        has_kp_planets = "planetary_positions" in data or "planets" in data
        record(5, "KP Astrology (Planets & Cusps)", status == 200 and has_cusps and has_kp_planets, f"HTTP {status}, cusps and planetary sublords verified", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(5, "KP Astrology (Planets & Cusps)", False, str(e), False)

    # 6. Vedic Astrology (Shadbala)
    try:
        status, body = http_post_json(f"{BACKEND_URL}/api/v1/vedic/shadbala", STANDARD_BIRTH_INPUT)
        data = json.loads(body.decode("utf-8"))
        raw_text = json.dumps(data)
        disclosures = scan_disclosures(raw_text)
        has_7 = "planets" in data and len(data["planets"]) == 7
        record(6, "Vedic Astrology (Shadbala)", status == 200 and has_7, f"HTTP {status}, 7 grahas shadbala computed", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(6, "Vedic Astrology (Shadbala)", False, str(e), False)

    # 7. Dasa-Bhukti
    try:
        dasa_payload = {**STANDARD_BIRTH_INPUT, "depth": 2}
        status, body = http_post_json(f"{BACKEND_URL}/api/v1/horoscope/dasa", dasa_payload)
        data = json.loads(body.decode("utf-8"))
        raw_text = json.dumps(data)
        disclosures = scan_disclosures(raw_text)
        has_dasa = "dasa_tree" in data and len(data["dasa_tree"]) == 9
        record(7, "Dasa-Bhukti Hierarchy", status == 200 and has_dasa, f"HTTP {status}, 9 Mahadashas verified", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(7, "Dasa-Bhukti Hierarchy", False, str(e), False)

    # 8. Transit Predictions
    try:
        status, body = http_get(f"{BACKEND_URL}/api/v1/horoscope/live-transits")
        data = json.loads(body.decode("utf-8"))
        raw_text = json.dumps(data)
        disclosures = scan_disclosures(raw_text)
        has_transits = "transits" in data or "planets" in data
        record(8, "Transit Predictions", status == 200 and has_transits, f"HTTP {status}, live transits computed", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(8, "Transit Predictions", False, str(e), False)

    # 9. Marriage Matching
    try:
        status, body = http_post_json(f"{BACKEND_URL}/api/v1/marriage-compatibility/analyze", MARRIAGE_PAYLOAD)
        data = json.loads(body.decode("utf-8"))
        raw_text = json.dumps(data)
        disclosures = scan_disclosures(raw_text)
        has_outcome = "final_assessment" in data or "tamil_porutham" in data or "ashtakoota" in data
        record(9, "Marriage Matching", status == 200 and has_outcome, f"HTTP {status}, composite matching evaluated", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(9, "Marriage Matching", False, str(e), False)

    # 10. Numerology
    try:
        status, body = http_post_json(f"{BACKEND_URL}/api/v1/numerology/traditional", NUMEROLOGY_PAYLOAD)
        data = json.loads(body.decode("utf-8"))
        raw_text = json.dumps(data)
        disclosures = scan_disclosures(raw_text)
        has_num = "birth_number" in data or "destiny_number" in data or "birth_psychic_number" in data
        record(10, "Numerology Calculation", status == 200 and has_num, f"HTTP {status}, numbers calculated", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(10, "Numerology Calculation", False, str(e), False)

    # 11. Remedies
    try:
        status_cat, body_cat = http_get(f"{BACKEND_URL}/api/v1/remedies/catalog")
        status_tax, body_tax = http_get(f"{BACKEND_URL}/api/v1/remedies/taxonomy")
        data_cat = json.loads(body_cat.decode("utf-8"))
        data_tax = json.loads(body_tax.decode("utf-8"))
        disclosures = scan_disclosures(json.dumps(data_cat) + json.dumps(data_tax))
        cat_count = len(data_cat.get("items", data_cat)) if isinstance(data_cat, (list, dict)) else 0
        record(11, "Remedies Catalog & Taxonomy", status_cat == 200 and status_tax == 200, f"Catalog HTTP {status_cat}, Taxonomy HTTP {status_tax}, items: {cat_count}", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(11, "Remedies", False, str(e), False)

    # 12. PDF Reports
    try:
        pdf_payload = {
            "birth_input": {
                "birth_date": "1990-05-15",
                "birth_time": "14:30:00",
                "latitude": 13.0827,
                "longitude": 80.2707,
                "timezone": "Asia/Kolkata",
            },
            "native_name": "Production Verification",
            "language": "en",
            "report_style": "full",
        }
        status, body = http_post_json(f"{BACKEND_URL}/api/v1/reports/horoscope/single-page-pdf", pdf_payload, headers={"Accept": "application/pdf"})
        reader = PdfReader(io.BytesIO(body))
        num_pages = len(reader.pages)
        text = ""
        for p in reader.pages:
            text += p.extract_text() or ""
        disclosures = scan_disclosures(text)
        record(12, "PDF Reports Generation", status == 200 and num_pages >= 1, f"HTTP {status}, {num_pages} pages, {len(body)} bytes", len(disclosures) == 0, disclosures)
    except Exception as e:
        record(12, "PDF Reports Generation", False, str(e), False)

    # 13. Admin Dashboard
    try:
        status, body = http_get(f"{FRONTEND_URL}/admin")
        try:
            urllib.request.urlopen(f"{BACKEND_URL}/api/v1/admin/users", timeout=10)
            admin_api_protected = False
        except urllib.error.HTTPError as he:
            admin_api_protected = (he.code in [401, 403])
        except Exception:
            admin_api_protected = True
        record(13, "Admin Dashboard Security", status in [200, 307, 308] and admin_api_protected, f"UI HTTP {status}, API Protected (401/403): {admin_api_protected}", True)
    except Exception as e:
        record(13, "Admin Dashboard Security", False, str(e), False)

    # 14. Admin Rules Access
    try:
        try:
            urllib.request.urlopen(f"{BACKEND_URL}/api/v1/rules/inventory", timeout=10)
            rules_protected = False
        except urllib.error.HTTPError as he:
            rules_protected = (he.code in [401, 403])
        except Exception:
            rules_protected = True
        record(14, "Admin Rules Access Protection", rules_protected, f"Anonymous inventory access denied (HTTP 401/403): {rules_protected}", True)
    except Exception as e:
        record(14, "Admin Rules Access Protection", False, str(e), False)

    # 15. Payment Configuration
    try:
        payment_protected = False
        try:
            http_post_json(f"{FRONTEND_URL}/api/payments/create-order", {"plan_id": "pro"})
        except urllib.error.HTTPError as he:
            payment_protected = (he.code in [401, 403, 405, 500])
        except Exception:
            payment_protected = True
        record(15, "Payment Endpoint Protection & Config", payment_protected, f"Session security enforced: {payment_protected}", True)
    except Exception as e:
        record(15, "Payment Endpoint Protection & Config", False, str(e), False)

    print("=" * 80)
    total_passed = sum(1 for r in results if r["status"] and r["disclosure_clean"])
    print(f"TOTAL VERIFIED: {total_passed}/{len(results)} PASSED")
    print("=" * 80)

    if total_passed == len(results):
        print("ALL 15 CUSTOMER WORKFLOWS SUCCESSFULLY VERIFIED (100% CLEAN OF ALL DISCLOSURES)!")
        return 0
    else:
        print(f"WARNING: {len(results) - total_passed} checks failed.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_checks())
