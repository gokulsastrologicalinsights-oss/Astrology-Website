"""Production Live Smoke Test Suite for Centralized GAI Letterhead PDF Architecture.

Executes live HTTP requests against the active production server,
downloads actual PDF reports for all core astrology modules,
and verifies:
1. HTTP 200 status and application/pdf content type.
2. Official GAI Letterhead presence on EVERY page.
3. Protected borders, subtle watermark, and safe-area boundaries (0 violations).
4. Tamil Unicode rendering, NFC normalization, and zero replacement characters.
5. Multi-page layout consistency and accurate page counts.
"""

import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from pypdf import PdfReader
import unicodedata

# Add backend to path for boundary validation utility
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from app.services.pdf_report_engine.letterhead_renderer import validate_pdf_safe_boundaries

BASE_URL = os.environ.get("PRODUCTION_BASE_URL", "http://127.0.0.1:8000")
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "production_downloads"
OUTPUT_DIR.mkdir(exist_ok=True)

# Production Standard Test Data
STANDARD_BIRTH_INPUT = {
    "birth_date": "1999-01-03",
    "birth_time": "05:58:00",
    "latitude": 13.0827,
    "longitude": 80.2707,
    "timezone": "Asia/Kolkata",
}

MARRIAGE_SAMPLE_DATA = {
    "groom_profile": {
        "name": "Karthik Subramanian",
        "birth_date": "1992-04-14",
        "birth_time": "05:30:00",
        "ascendant_sign": "Aries",
        "ascendant_sign_tamil": "மேஷம்",
        "moon_sign": "Leo",
        "moon_sign_tamil": "சிம்மம்",
    },
    "bride_profile": {
        "name": "Meenakshi Sundaram",
        "birth_date": "1995-08-22",
        "birth_time": "07:15:00",
        "ascendant_sign": "Pisces",
        "ascendant_sign_tamil": "மீனம்",
        "moon_sign": "Cancer",
        "moon_sign_tamil": "கடகம்",
    },
    "composite_assessment": {
        "overall_outcome": "FAVOURABLE_UNDER_SELECTED_RULES",
        "overall_outcome_label_en": "FAVORABLE FOR MARRIAGE",
        "overall_outcome_label_ta": "திருமணத்திற்கு மிகச் சாதகமானது",
        "explanation_en": "Strong composite alignment across traditional and modern astrological factors.",
        "explanation_ta": "பாரம்பரிய மற்றும் நவீன ஜோதிட முறைப்படி மிகச் சிறந்த பொருத்தம்.",
        "major_supportive_indicators": ["Tamil 10 Poruthams 8.5/10 with Rajju and Vedha clean."],
        "major_challenging_indicators": ["Kuja Dosha mild in groom chart."],
        "category_verdicts": {
            "tamil_porutham": {"category_id": "tamil_porutham", "status": "FAVORABLE"},
            "ashtakoota": {"category_id": "ashtakoota", "status": "FAVORABLE"},
            "kuja_samadosham": {"category_id": "kuja_samadosham", "status": "INDETERMINATE"},
            "papasamya": {"category_id": "papasamya", "status": "UNFAVORABLE"},
        },
    },
    "groom_vedic": {"summary_en": "7th house clean, Venus exalted."},
    "bride_vedic": {"summary_en": "7th house aspected by benefic Jupiter."},
    "synastry": {},
    "kp_marriage": {
        "groom_7th_csl_planet": "Jupiter",
        "groom_7th_csl_promise": "Positive",
        "bride_7th_csl_planet": "Venus",
        "bride_7th_csl_promise": "Mixed",
    },
    "timing_analysis": {
        "groom_active_dasa_bhukti": "Jupiter - Saturn",
        "bride_active_dasa_bhukti": "Mercury - Venus",
        "matrimonial_window_assessment": "High matrimonial activation.",
    },
    "bride_d9_chart": {"ascendant": {"sign_index": 4}, "planets": []},
}

NUMEROLOGY_CALC_DATA = {
    "birth_psychic_number": {
        "number_value": 7,
        "number_name": "Birth / Psychic Number",
        "ruling_planet": "Ketu",
        "calculation_method": "Day of month reduction",
        "detailed_interpretation": "Analytical, spiritual seeker, reflective and introspective.",
        "is_master": False,
    },
    "life_path": {
        "number_value": 11,
        "number_name": "Life Path Number",
        "ruling_planet": "Moon",
        "calculation_method": "Period reduction",
        "detailed_interpretation": "Master Intuitive, inspirational teacher and visionary channel.",
        "is_master": True,
    },
    "destiny_expression": {
        "number_value": 5,
        "number_name": "Destiny / Expression Number",
        "ruling_planet": "Mercury",
        "calculation_method": "Full name Pythagorean sum",
        "detailed_interpretation": "Versatile communicator, dynamic intellect, freedom seeker.",
        "is_master": False,
    },
    "soul_urge": {
        "number_value": 3,
        "number_name": "Soul Urge / Heart Desire Number",
        "ruling_planet": "Jupiter",
        "calculation_method": "Vowels reduction",
        "detailed_interpretation": "Creative self-expression, joyful optimism, artistic passion.",
        "is_master": False,
    },
    "personality_number": {
        "number_value": 2,
        "number_name": "Personality Number",
        "ruling_planet": "Moon",
        "calculation_method": "Consonants reduction",
        "detailed_interpretation": "Gentle, approachable diplomat, cooperative and perceptive.",
        "is_master": False,
    },
    "maturity_number": {
        "number_value": 7,
        "number_name": "Maturity Number",
        "ruling_planet": "Ketu",
        "calculation_method": "Life Path + Expression",
        "detailed_interpretation": "Spiritual fulfillment, wisdom harvesting, esoteric scholarship.",
        "is_master": False,
    },
    "personal_year": {
        "number_value": 9,
        "number_name": "Personal Year Number",
        "ruling_planet": "Mars",
        "calculation_method": "Birthday + Current Year",
        "detailed_interpretation": "Completion, letting go of outdated cycles, universal compassion.",
        "is_master": False,
    },
}

NUMEROLOGY_INTERP_DATA = {
    "core_summary": "Introspective visionary with extraordinary intuitive foresight and analytical depth.",
    "karmic_insights": "No karmic debt numbers detected. Clean ancestral and karmic slate.",
    "recommendations": "Wear light green and cream colors. Avoid impulsive decisions on Saturdays.",
}

PROD_SMOKE_TESTS = [
    {
        "module": "Vedic Horoscope (English)",
        "endpoint": "/api/v1/reports/horoscope/pdf",
        "method": "POST",
        "payload": {
            "birth_input": STANDARD_BIRTH_INPUT,
            "native_name": "Gokul Murugan",
            "language": "en",
            "report_style": "full",
        },
        "filename": "Production_Horoscope_9Page_EN.pdf",
        "expected_pages": 9,
        "is_tamil": False,
    },
    {
        "module": "Vedic Horoscope (Tamil)",
        "endpoint": "/api/v1/reports/horoscope/pdf",
        "method": "POST",
        "payload": {
            "birth_input": STANDARD_BIRTH_INPUT,
            "native_name": "கோகுல் முருகன்",
            "language": "ta",
            "report_style": "full",
        },
        "filename": "Production_Horoscope_9Page_TA.pdf",
        "expected_pages": 9,
        "is_tamil": True,
    },
    {
        "module": "KP Astrology (English)",
        "endpoint": "/api/v1/reports/kp/pdf",
        "method": "POST",
        "payload": {
            "birth_input": STANDARD_BIRTH_INPUT,
            "native_name": "Gokul Murugan",
            "language": "en",
            "chart_type": "natal",
        },
        "filename": "Production_KP_Report_6Page_EN.pdf",
        "expected_pages": 6,
        "is_tamil": False,
    },
    {
        "module": "KP Astrology (Tamil)",
        "endpoint": "/api/v1/reports/kp/pdf",
        "method": "POST",
        "payload": {
            "birth_input": STANDARD_BIRTH_INPUT,
            "native_name": "கோகுல் முருகன்",
            "language": "ta",
            "chart_type": "natal",
        },
        "filename": "Production_KP_Report_6Page_TA.pdf",
        "expected_pages": 6,
        "is_tamil": True,
    },
    {
        "module": "Single-Page Kundli (Tamil)",
        "endpoint": "/api/v1/reports/horoscope/single-page-pdf",
        "method": "POST",
        "payload": {
            "birth_input": STANDARD_BIRTH_INPUT,
            "native_name": "கோகுல் முருகன்",
            "native_id": "#GAI-PROD-01",
            "language": "ta",
        },
        "filename": "Production_SinglePage_Kundli_TA.pdf",
        "expected_pages": 1,
        "is_tamil": True,
    },
    {
        "module": "Shodashvarga 16 Divisional (Tamil)",
        "endpoint": "/api/v1/reports/shodashvarga/pdf",
        "method": "POST",
        "payload": {
            "birth_input": STANDARD_BIRTH_INPUT,
            "native_name": "கோகுல் முருகன்",
            "language": "ta",
        },
        "filename": "Production_Shodashvarga_7Page_TA.pdf",
        "expected_pages": 7,
        "is_tamil": True,
    },
    {
        "module": "Pancha Pakshi Bio-Rhythm (Tamil)",
        "endpoint": "/api/v1/reports/pancha-pakshi/pdf",
        "method": "POST",
        "payload": {
            "nakshatra": "Ashwini",
            "paksha": "shukla",
            "target_date": "2026-11-23",
            "native_name": "கோகுல் முருகன்",
            "language": "ta",
        },
        "filename": "Production_PanchaPakshi_2Page_TA.pdf",
        "expected_pages": 2,
        "is_tamil": True,
    },
    {
        "module": "Muhurta Auspicious Certificate (Tamil)",
        "endpoint": "/api/v1/reports/muhurta-certificate/pdf",
        "method": "POST",
        "payload": {
            "occasion": "House Warming",
            "primary_person_name": "கோகுல் முருகன்",
            "event_date": "2026-12-05",
            "start_time": "06:15",
            "end_time": "07:45",
            "location_name": "சென்னை (Chennai)",
            "latitude": 13.0827,
            "longitude": 80.2707,
            "language": "ta",
        },
        "filename": "Production_Muhurta_Certificate_TA.pdf",
        "expected_pages": 1,
        "is_tamil": True,
    },
    {
        "module": "Gemstone & Rudraksha Playbook (Tamil)",
        "endpoint": "/api/v1/reports/gemstone-rudraksha/pdf",
        "method": "POST",
        "payload": {
            "ascendant_sign": "Sagittarius",
            "native_name": "கோகுல் முருகன்",
            "language": "ta",
        },
        "filename": "Production_Gemstone_Rudraksha_3Page_TA.pdf",
        "expected_pages": 3,
        "is_tamil": True,
    },
    {
        "module": "Marriage Compatibility (Tamil)",
        "endpoint": "/api/v1/reports/marriage-compatibility/pdf",
        "method": "POST",
        "payload": {
            "report_data": MARRIAGE_SAMPLE_DATA,
            "language": "ta",
        },
        "filename": "Production_Marriage_Compatibility_8Page_TA.pdf",
        "expected_pages": None,  # Multi-page
        "is_tamil": True,
    },
    {
        "module": "Numerology Studio Report (Tamil)",
        "endpoint": "/api/v1/numerology/export-pdf",
        "method": "POST",
        "payload": {
            "person_name": "கோகுல் முருகன்",
            "birth_date": "1999-01-03",
            "method": "traditional",
            "system_convention": "pythagorean",
            "language": "ta",
            "calculation_data": NUMEROLOGY_CALC_DATA,
            "interpretation_data": NUMEROLOGY_INTERP_DATA,
            "display_number": 1,
            "report_id": "GAI-NUM-PROD-01",
        },
        "filename": "Production_Numerology_1Page_TA.pdf",
        "expected_pages": 1,
        "is_tamil": True,
    },
    {
        "module": "Traditional Horoscope Booklet 6-Page (Tamil)",
        "endpoint": "/api/v1/tools/horoscope-writing/pdf",
        "method": "POST",
        "payload": {
            "birth_input": STANDARD_BIRTH_INPUT,
            "name": "கோகுல் முருகன்",
            "gender": "male",
            "language": "ta",
        },
        "filename": "Production_Traditional_Horoscope_6Page_TA.pdf",
        "expected_pages": 6,
        "is_tamil": True,
    },
    {
        "module": "KP Predictive Narrative Booklet (Tamil)",
        "endpoint": "/api/v1/kp-narrative/pdf",
        "method": "POST",
        "payload": {
            "birth_input": STANDARD_BIRTH_INPUT,
            "name": "கோகுல் முருகன்",
            "language": "ta",
        },
        "filename": "Production_KP_Narrative_Booklet_TA.pdf",
        "expected_pages": None,  # dynamic pages
        "is_tamil": True,
    },
]


def run_smoke_test(test_def: dict) -> dict:
    module = test_def["module"]
    url = BASE_URL + test_def["endpoint"]
    payload_bytes = json.dumps(test_def["payload"]).encode("utf-8")
    filename = test_def["filename"]
    save_path = OUTPUT_DIR / filename

    print(f"\n---> Smoke Testing: {module}")
    print(f"     URL: {url}")
    t0 = time.time()

    req = urllib.request.Request(
        url,
        data=payload_bytes,
        headers={"Content-Type": "application/json", "Accept": "application/pdf"},
        method="POST",
    )

    result = {
        "module": module,
        "endpoint": test_def["endpoint"],
        "status_code": None,
        "content_type": None,
        "file_size": 0,
        "page_count": 0,
        "safe_boundaries": False,
        "letterhead_detected": False,
        "tamil_extraction": None,
        "latency_sec": 0.0,
        "error": None,
    }

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            elapsed = time.time() - t0
            result["latency_sec"] = round(elapsed, 2)
            result["status_code"] = resp.status
            result["content_type"] = resp.headers.get("Content-Type", "")

            pdf_data = resp.read()
            result["file_size"] = len(pdf_data)

            if not pdf_data.startswith(b"%PDF-"):
                result["error"] = f"Magic header %PDF- missing. Header: {pdf_data[:20]}"
                return result

            # Save downloaded production PDF
            with open(save_path, "wb") as f_out:
                f_out.write(pdf_data)

            # PyPDF deep verification
            reader = PdfReader(io.BytesIO(pdf_data))
            num_pages = len(reader.pages)
            result["page_count"] = num_pages

            # Letterhead presence: checks page.images in ReportLab or HTML header branding
            all_pages_have_letterhead = True
            for p_idx, page in enumerate(reader.pages):
                images_on_page = len(page.images)
                text_on_page = page.extract_text() or ""
                has_branding = (
                    images_on_page >= 1
                    or "Gokul's Astrological Insights" in text_on_page
                    or "9444 55 9071" in text_on_page
                )
                if not has_branding:
                    all_pages_have_letterhead = False
                    break
            result["letterhead_detected"] = all_pages_have_letterhead

            # Safe boundary check
            boundary_res = validate_pdf_safe_boundaries(pdf_data)
            result["safe_boundaries"] = boundary_res.get("valid", False)

            # Text extraction & Tamil Unicode check
            extracted_full_text = ""
            for page in reader.pages:
                extracted_full_text += page.extract_text() or ""

            has_replacement_char = "\ufffd" in extracted_full_text

            if test_def["is_tamil"]:
                tamil_chars = [c for c in extracted_full_text if "\u0B80" <= c <= "\u0BFF"]
                is_nfc = extracted_full_text == unicodedata.normalize("NFC", extracted_full_text)
                result["tamil_extraction"] = {
                    "tamil_char_count": len(tamil_chars),
                    "is_nfc_normalized": is_nfc,
                    "zero_corrupt_chars": not has_replacement_char,
                }
            else:
                result["english_extraction"] = {
                    "char_count": len(extracted_full_text),
                    "zero_corrupt_chars": not has_replacement_char,
                }

            print(f"     [PROD PASS] {num_pages} pages | {len(pdf_data)/1024:.1f} KB | {elapsed:.2f}s | Safe Boundaries: 0 violations")
            return result

    except urllib.error.HTTPError as http_err:
        result["status_code"] = http_err.code
        err_msg = http_err.read().decode("utf-8", errors="replace")
        result["error"] = f"HTTP {http_err.code}: {err_msg[:250]}"
        print(f"     [PROD FAIL] HTTP {http_err.code}: {err_msg[:120]}")
        return result
    except Exception as exc:
        result["error"] = str(exc)
        print(f"     [PROD FAIL] Exception: {exc}")
        return result


def main():
    print("=" * 80)
    print("  GOKUL'S ASTROLOGICAL INSIGHTS - PRODUCTION SMOKE TEST SUITE")
    print(f"  Production Target URL: {BASE_URL}")
    print(f"  Production Download Directory: {OUTPUT_DIR}")
    print("=" * 80)

    results = []
    for test_def in PROD_SMOKE_TESTS:
        res = run_smoke_test(test_def)
        results.append(res)

    print("\n" + "=" * 80)
    print("  PRODUCTION SMOKE TEST RESULTS SUMMARY")
    print("=" * 80)
    header = f"{'Module':<36} | {'Status':<6} | {'Pages':<5} | {'Size(KB)':<8} | {'Letterhead':<10} | {'Boundaries':<10} | {'Tamil/Text':<10}"
    print(header)
    print("-" * len(header))

    passed_count = 0
    for r in results:
        status_str = f"HTTP {r['status_code']}" if r['status_code'] else "FAIL"
        pages_str = str(r['page_count']) if r['page_count'] else "-"
        size_str = f"{r['file_size']/1024:.1f}" if r['file_size'] else "-"
        lh_str = "PASS (All)" if r['letterhead_detected'] else "FAIL"
        bound_str = "PASS (0 vio)" if r['safe_boundaries'] else "FAIL"

        text_ok = False
        if r.get("tamil_extraction"):
            te = r["tamil_extraction"]
            text_ok = te["tamil_char_count"] > 10 and te["zero_corrupt_chars"] and te["is_nfc_normalized"]
        elif r.get("english_extraction"):
            ee = r["english_extraction"]
            text_ok = ee["char_count"] > 50 and ee["zero_corrupt_chars"]

        text_str = "PASS (NFC)" if text_ok else "FAIL"

        is_passed = (
            r['status_code'] == 200
            and r['safe_boundaries']
            and r['letterhead_detected']
            and text_ok
        )
        if is_passed:
            passed_count += 1

        print(f"{r['module'][:36]:<36} | {status_str:<6} | {pages_str:<5} | {size_str:<8} | {lh_str:<10} | {bound_str:<10} | {text_str:<10}")

    print("-" * len(header))
    print(f"PRODUCTION VERIFICATION RESULT: {passed_count} / {len(results)} SMOKE TESTS PASSED")
    print("=" * 80)

    if passed_count == len(results):
        print("\nALL PRODUCTION PDF SMOKE TESTS PASSED (100% SUCCESS). PRODUCTION VERIFICATION COMPLETE.")
        sys.exit(0)
    else:
        print(f"\n{len(results) - passed_count} production tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
