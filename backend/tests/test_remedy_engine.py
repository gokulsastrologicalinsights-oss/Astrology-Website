"""Comprehensive unit and integration test suite for Remedies & Pariharam Engine.

Verifies:
1. Complete Problem Taxonomy (39 verified categories, bilingual, karakas, houses).
2. Authentic 9 Kaveri Delta Navagraha Temples (coordinates, Tamil names, offerings).
3. Devanagari Sanskrit mantras and Tamil phonetic transliterations.
4. Classical Vedic Astrological Safeguards (Yogakaraka protection, Daan restrictions).
5. Fast-API endpoints, validation audit, and filter queries.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.remedy_engine.taxonomy import PROBLEM_TAXONOMY_REGISTRY
from app.services.remedy_engine.validation import RemedyValidator
from app.services.remedy_engine.eligibility import RemedyEligibilityEngine

client = TestClient(app)


# ==============================================================================
# 1. Problem Taxonomy Integrity Tests
# ==============================================================================

def test_problem_taxonomy_count_and_completeness():
    """Verify that all 39 verified classical problem categories are defined."""
    assert len(PROBLEM_TAXONOMY_REGISTRY) == 39
    
    expected_categories = {
        "career",
        "relationships_marriage",
        "health_wellness",
        "finance_wealth",
        "property_legal",
        "education_intellect",
        "spiritual_growth",
        "travel_foreign",
    }
    actual_categories = {item["category"] for item in PROBLEM_TAXONOMY_REGISTRY.values()}
    assert expected_categories == actual_categories


def test_problem_taxonomy_bilingual_and_astrological_fields():
    """Verify that every taxonomy item has valid English and Tamil names, karakas, and houses."""
    valid_karakas = {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"}
    
    for item in PROBLEM_TAXONOMY_REGISTRY.values():
        slug = item["slug"]
        # English and Tamil names
        assert item["name_en"], f"{slug} missing English name"
        assert item["name_ta"], f"{slug} missing Tamil name"
        assert RemedyValidator.contains_tamil(item["name_ta"]), f"{slug} Tamil name has no Tamil Unicode: {item['name_ta']}"
        assert not RemedyValidator.contains_corrupted_characters(item["name_ta"]), f"{slug} contains corrupted characters"
        
        # Astrological Karakas & Houses
        assert len(item["primary_karakas"]) > 0, f"{slug} has no primary karakas"
        for k in item["primary_karakas"]:
            assert k in valid_karakas, f"{slug} contains unknown karaka {k}"
            
        assert len(item["governing_houses"]) > 0, f"{slug} has no governing houses"
        for h in item["governing_houses"]:
            assert 1 <= h <= 12, f"{slug} house {h} outside 1-12 range"


# ==============================================================================
# 2. Kaveri Delta Navagraha Temples Tests
# ==============================================================================

def test_navagraha_temples_nine_grahas_coverage():
    """Verify all 9 Navagrahas are covered with authentic Kaveri Delta temples."""
    response = client.get("/api/v1/remedies/temples")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 9
    
    expected_grahas = {"sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu"}
    actual_grahas = {t["graha"] for t in data["items"]}
    assert expected_grahas == actual_grahas


def test_navagraha_temples_coordinates_and_tamil_script():
    """Verify geographic bounds (Kaveri Delta: Thanjavur / Mayiladuthurai / Nagapattinam / Tiruvarur)."""
    response = client.get("/api/v1/remedies/temples")
    data = response.json()
    
    for t in data["items"]:
        code = t["code"]
        assert 10.0 <= t["latitude"] <= 12.0, f"{code} latitude {t['latitude']} out of Kaveri Delta range"
        assert 78.5 <= t["longitude"] <= 80.5, f"{code} longitude {t['longitude']} out of Kaveri Delta range"
        assert RemedyValidator.contains_tamil(t["name_ta"]), f"{code} Tamil name lacks Tamil script"
        assert RemedyValidator.contains_tamil(t["presiding_deity_ta"]), f"{code} deity lacks Tamil script"
        assert RemedyValidator.contains_tamil(t["visiting_day_ta"]), f"{code} visiting day lacks Tamil script"


# ==============================================================================
# 3. Remedy Catalog, Sanskrit Mantras & Tamil Transliteration Tests
# ==============================================================================

def test_remedy_catalog_sanskrit_and_tamil_fidelity():
    """Verify mantras have authentic Devanagari Sanskrit and accurate Tamil transliteration."""
    response = client.get("/api/v1/remedies/catalog")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] >= 10
    
    mantra_count = 0
    for rem in data["items"]:
        if rem["remedy_type"] == "mantra":
            mantra_count += 1
            code = rem["code"]
            assert rem["sanskrit_text"], f"{code} missing Sanskrit text"
            assert RemedyValidator.contains_devanagari(rem["sanskrit_text"]), f"{code} lacks Devanagari Unicode"
            assert rem["transliteration_ta"], f"{code} missing Tamil transliteration"
            assert RemedyValidator.contains_tamil(rem["transliteration_ta"]), f"{code} lacks Tamil Unicode in transliteration"
            assert rem["japa_count"] == 108 or rem["japa_count"] > 0, f"{code} invalid japa count"
            assert rem["source_code"], f"{code} lacks Shastra source code"
            
    assert mantra_count >= 8, f"Expected at least 8 verified mantras, found {mantra_count}"


# ==============================================================================
# 4. Classical Astrological Eligibility Safeguards (Yogakaraka Protection)
# ==============================================================================

def test_yogakaraka_protection_taurus_saturn():
    """Taurus Lagna: Saturn is Yogakaraka (9th & 10th lord) -> Daan must be strictly RESTRICTED."""
    res = RemedyEligibilityEngine.evaluate_eligibility(
        ascendant_sign="Taurus",
        graha="saturn",
        remedy_type="charity",
    )
    assert res.is_eligible is False
    assert res.is_yogakaraka is True
    assert "Yogakaraka" in res.restriction_reason
    assert "BPHS Ch. 34" in res.restriction_reason
    assert "Instead of charity, strengthen" in res.safe_alternative_recommendation


def test_yogakaraka_protection_cancer_mars():
    """Cancer Lagna: Mars is Yogakaraka (5th & 10th lord) -> Daan must be strictly RESTRICTED."""
    res = RemedyEligibilityEngine.evaluate_eligibility(
        ascendant_sign="Cancer",
        graha="mars",
        remedy_type="charity",
    )
    assert res.is_eligible is False
    assert res.is_yogakaraka is True
    assert "Yogakaraka" in res.restriction_reason


def test_yogakaraka_protection_capricorn_venus():
    """Capricorn Lagna: Venus is Yogakaraka (5th & 10th lord) -> Daan must be strictly RESTRICTED."""
    res = RemedyEligibilityEngine.evaluate_eligibility(
        ascendant_sign="Capricorn",
        graha="venus",
        remedy_type="charity",
    )
    assert res.is_eligible is False
    assert res.is_yogakaraka is True


def test_mantras_are_universally_eligible_for_yogakaraka():
    """Mantra chanting is auspicious and permitted for Yogakarakas (strengthens sattvic energy)."""
    res = RemedyEligibilityEngine.evaluate_eligibility(
        ascendant_sign="Taurus",
        graha="saturn",
        remedy_type="mantra",
    )
    assert res.is_eligible is True
    assert res.is_yogakaraka is True
    assert res.restriction_reason is None


def test_daan_permitted_for_functional_malefics():
    """Saturn for Aries Lagna is functional malefic (10th & 11th lord) -> Daan is permitted for pacification."""
    res = RemedyEligibilityEngine.evaluate_eligibility(
        ascendant_sign="Aries",
        graha="saturn",
        remedy_type="charity",
    )
    assert res.is_eligible is True
    assert res.is_functional_malefic is True


def test_rahu_ketu_charity_always_eligible():
    """Rahu and Ketu are natural malefics; pacification via charity is always permitted."""
    res = RemedyEligibilityEngine.evaluate_eligibility(
        ascendant_sign="Leo",
        graha="rahu",
        remedy_type="charity",
    )
    assert res.is_eligible is True
    assert res.is_functional_malefic is True


# ==============================================================================
# 5. Fast-API Endpoints Integration Tests
# ==============================================================================

def test_api_taxonomy_endpoint():
    """Test /api/v1/remedies/taxonomy endpoint."""
    response = client.get("/api/v1/remedies/taxonomy")
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 39
    assert len(data["categories"]) == 8

    # Filter by category
    resp_career = client.get("/api/v1/remedies/taxonomy?category=career")
    assert resp_career.status_code == 200
    career_data = resp_career.json()
    assert career_data["total_count"] >= 5
    for item in career_data["items"]:
        assert item["category"] == "career"


def test_api_catalog_endpoint_and_filters():
    """Test /api/v1/remedies/catalog endpoint with various filters."""
    # Filter by graha
    resp_sun = client.get("/api/v1/remedies/catalog?graha=sun")
    assert resp_sun.status_code == 200
    sun_data = resp_sun.json()
    assert sun_data["total_count"] >= 1
    for r in sun_data["items"]:
        assert r["graha"] == "sun"

    # Filter by remedy_type
    resp_mantra = client.get("/api/v1/remedies/catalog?remedy_type=mantra")
    assert resp_mantra.status_code == 200
    mantra_data = resp_mantra.json()
    assert mantra_data["total_count"] >= 8
    for r in mantra_data["items"]:
        assert r["remedy_type"] == "mantra"

    # Single remedy detail
    first_code = mantra_data["items"][0]["code"]
    resp_single = client.get(f"/api/v1/remedies/catalog/{first_code}")
    assert resp_single.status_code == 200
    assert resp_single.json()["code"] == first_code


def test_api_temple_single_detail_and_404():
    """Test /api/v1/remedies/temples/{code} endpoint."""
    resp = client.get("/api/v1/remedies/temples/TEMPLE_SURYANAR_KOVIL")
    assert resp.status_code == 200
    assert resp.json()["graha"] == "sun"
    assert "Suryanar Kovil" in resp.json()["place_name_en"]

    # 404 test
    resp_404 = client.get("/api/v1/remedies/temples/NON_EXISTENT_TEMPLE")
    assert resp_404.status_code == 404


def test_api_sources_endpoint():
    """Test /api/v1/remedies/sources endpoint."""
    resp = client.get("/api/v1/remedies/sources")
    assert resp.status_code == 200
    sources = resp.json()
    assert len(sources) >= 5
    codes = [s["code"] for s in sources]
    assert "BPHS" in codes
    assert "PHALADEEPIKA" in codes
    assert "NAVAGRAHA_STOTRAM" in codes


def test_api_validate_content_endpoint():
    """Test /api/v1/remedies/validate-content audit endpoint."""
    resp = client.post("/api/v1/remedies/validate-content")
    assert resp.status_code == 200
    report = resp.json()
    assert report["all_passed"] is True
    assert report["total_problems_audited"] == 39
    assert report["total_temples_audited"] == 9
    assert report["total_remedies_audited"] >= 10


def test_api_eligibility_check_endpoint():
    """Test /api/v1/remedies/eligibility-check endpoint."""
    payload = {
        "ascendant_sign": "Taurus",
        "graha": "saturn",
        "remedy_type": "charity",
    }
    resp = client.post("/api/v1/remedies/eligibility-check", json=payload)
    assert resp.status_code == 200
    result = resp.json()
    assert result["is_eligible"] is False
    assert result["is_yogakaraka"] is True
    assert result["restriction_reason"] is not None


# ==============================================================================
# 6. Chart Context Extraction & Classical Diagnostics Tests
# ==============================================================================

def test_extract_chart_context_and_diagnostics():
    """Verify context extraction and diagnostics from a sample chart without recalculating ephemeris."""
    from app.services.remedy_engine.analysis import extract_chart_context, diagnose_chart_factors

    sample_chart = {
        "ascendant": {"sign": "Taurus", "degree": 14.5},
        "planets": [
            {"name": "Sun", "sign": "Libra", "longitude": 190.0, "house": 6, "is_combust": False},      # Debilitated in Libra & 6th house
            {"name": "Moon", "sign": "Taurus", "longitude": 33.0, "house": 1, "is_combust": False},     # Exalted in Taurus
            {"name": "Mars", "sign": "Cancer", "longitude": 95.0, "house": 3, "is_combust": False},     # Debilitated in Cancer
            {"name": "Mercury", "sign": "Libra", "longitude": 194.0, "house": 6, "is_combust": True},   # Combust with Sun
            {"name": "Jupiter", "sign": "Pisces", "longitude": 345.0, "house": 11, "is_combust": False},
            {"name": "Venus", "sign": "Virgo", "longitude": 160.0, "house": 5, "is_combust": False},    # Debilitated in Virgo
            {"name": "Saturn", "sign": "Aquarius", "longitude": 310.0, "house": 10, "is_combust": False},# Yogakaraka in 10th
            {"name": "Rahu", "sign": "Aries", "longitude": 20.0, "house": 12, "is_combust": False},
            {"name": "Ketu", "sign": "Libra", "longitude": 200.0, "house": 6, "is_combust": False},
        ],
        "panchang": {"nakshatra": "Rohini"},
    }

    sample_dasa = {
        "active_period": {
            "mahadasha": "saturn",
            "antardasha": "mercury",
        }
    }

    context = extract_chart_context(sample_chart, sample_dasa)

    assert context.lagna_sign == "Taurus"
    assert context.moon_sign == "Taurus"
    assert context.moon_nakshatra == "Rohini"
    assert "saturn" in context.yogakaraka_planets
    assert context.running_mahadasha == "Saturn"
    assert context.running_bhukti == "Mercury"
    assert "sun" in context.debilitated_planets
    assert "mars" in context.debilitated_planets
    assert "venus" in context.debilitated_planets
    assert "mercury" in context.combust_planets
    assert "sun" in context.dusthana_planets.get("6", [])

    factors = diagnose_chart_factors(context, sample_chart)
    assert len(factors) >= 4
    factor_types = [f.factor_type for f in factors]
    assert "debilitation" in factor_types
    assert "combustion" in factor_types
    assert "dusthana" in factor_types
    assert "running_dasa" in factor_types


def test_kuja_dosha_cancellations():
    """Verify BPHS cancellation exceptions for Kuja Dosha (Manglik)."""
    from app.services.remedy_engine.analysis import extract_chart_context

    # Case 1: Cancer Lagna -> Mars is Yogakaraka -> Neutralized
    chart_cancer = {
        "ascendant": {"sign": "Cancer"},
        "planets": [{"name": "Mars", "sign": "Leo", "house": 2}],
    }
    ctx_cancer = extract_chart_context(chart_cancer)
    assert ctx_cancer.kuja_dosha_status == "cancelled"
    assert "Yogakaraka" in str(ctx_cancer.kuja_dosha_details)

    # Case 2: Aries 1st house -> Mars in own house -> Cancelled
    chart_own = {
        "ascendant": {"sign": "Aries"},
        "planets": [{"name": "Mars", "sign": "Aries", "house": 1}],
    }
    ctx_own = extract_chart_context(chart_own)
    assert ctx_own.kuja_dosha_status == "cancelled"

    # Case 3: Gemini Lagna, Mars in 7th house in Sagittarius without Jupiter -> Present
    chart_afflicted = {
        "ascendant": {"sign": "Gemini"},
        "planets": [
            {"name": "Mars", "sign": "Sagittarius", "house": 7},
            {"name": "Jupiter", "sign": "Virgo", "house": 4},
        ],
    }
    ctx_afflicted = extract_chart_context(chart_afflicted)
    assert ctx_afflicted.kuja_dosha_status == "present"


def test_ranking_enforces_yogakaraka_daan_protection():
    """Verify that Daan (charity) is omitted for Yogakarakas, while mantras are ranked at top."""
    from app.services.remedy_engine.analysis import extract_chart_context, diagnose_chart_factors, rank_and_retrieve_remedies
    from app.services.remedy_engine.repository import VERIFIED_REMEDIES, VERIFIED_TEMPLES

    # Taurus Lagna: Saturn is Yogakaraka
    chart = {
        "ascendant": {"sign": "Taurus"},
        "planets": [{"name": "Saturn", "sign": "Capricorn", "house": 9, "is_combust": False}],
    }
    sample_dasa = {"active_period": {"mahadasha": "saturn"}}

    context = extract_chart_context(chart, sample_dasa)
    factors = diagnose_chart_factors(context, chart)
    ranked = rank_and_retrieve_remedies(context, factors, VERIFIED_REMEDIES, VERIFIED_TEMPLES)

    saturn_remedies = [r for r in ranked if r.remedy.graha == "saturn"]
    assert len(saturn_remedies) > 0

    # Ensure NO charity (Daan) is recommended for Saturn for Taurus Lagna
    for r in saturn_remedies:
        assert r.remedy.remedy_type != "charity", "Daan charity recommended for Yogakaraka planet!"
        assert r.relevance_score >= 60, "Expected high relevance score for Yogakaraka active Dasa"

    # Top recommendation should be essential
    assert ranked[0].priority_tier == "essential"
    assert "Saturn" in ranked[0].reason_en or "Shani" in ranked[0].reason_en


# ==============================================================================
# 7. Live & Saved Remedy Analysis API Tests
# ==============================================================================

def test_api_live_remedy_analysis_with_coordinates():
    """Verify POST /api/v1/remedies/analysis/live calculates context and ranks remedies."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "ayanamsa": 0,
    }
    resp = client.post("/api/v1/remedies/analysis/live", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "complete"
    assert "chart_context" in data
    assert data["chart_context"]["lagna_sign"]
    assert data["chart_context"]["moon_sign"]
    assert len(data["recommendations"]) >= 5
    assert data["input_fingerprint"] is not None


def test_api_live_remedy_analysis_validation_error():
    """Verify POST /api/v1/remedies/analysis/live rejects missing coordinates with 422."""
    payload = {
        "birth_date": "1990-05-15",
        "birth_time": "14:30",
        # Missing latitude and longitude
    }
    resp = client.post("/api/v1/remedies/analysis/live", json=payload)
    assert resp.status_code == 422


# ==============================================================================
# 8. Remedy Reports Lifecycle & Authorization Security Tests
# ==============================================================================

def test_remedy_reports_save_retrieve_and_auth_isolation():
    """Verify saving, retrieving, and server-side authorization enforcement for reports."""
    from app.services.auth_service import get_current_user

    user_a = {"id": "11111111-1111-1111-1111-111111111111", "email": "usera@example.com", "role": "user"}
    user_b = {"id": "22222222-2222-2222-2222-222222222222", "email": "userb@example.com", "role": "user"}

    # Mock user A
    app.dependency_overrides[get_current_user] = lambda: user_a

    # 1. Generate live analysis to get a valid analysis snapshot
    live_resp = client.post("/api/v1/remedies/analysis/live", json={
        "birth_date": "1995-10-20",
        "birth_time": "10:15",
        "timezone": "Asia/Kolkata",
        "latitude": 13.0827,
        "longitude": 80.2707,
    })
    assert live_resp.status_code == 200
    analysis_data = live_resp.json()

    horoscope_id = "33333333-3333-3333-3333-333333333333"

    save_payload = {
        "horoscope_id": horoscope_id,
        "input_data_fingerprint": analysis_data["input_fingerprint"],
        "person_name": "Test Client",
        "review_status": "reviewed",
        "astrologer_notes": "Prescribed Surya Gayatri and Navagraha temple archana.",
        "selected_remedy_codes": ["REM_SUN_MANTRA_01", "REM_SHANI_MANTRA_01"],
        "language": "en",
        "analysis_snapshot": analysis_data,
    }

    # 2. Save report as User A
    save_resp = client.post("/api/v1/remedies/reports", json=save_payload)
    assert save_resp.status_code == 200
    report_record = save_resp.json()
    report_id = report_record["id"]
    assert report_record["user_id"] == user_a["id"]
    assert report_record["review_status"] == "reviewed"

    # 3. Retrieve report as User A (owner) -> 200 OK
    get_resp = client.get(f"/api/v1/remedies/reports/{report_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == report_id

    # 4. List reports for horoscope as User A -> 200 OK
    list_resp = client.get(f"/api/v1/remedies/reports/by-horoscope/{horoscope_id}")
    assert list_resp.status_code == 200
    assert list_resp.json()["total_count"] >= 1

    # 5. Switch to User B -> Must NOT be able to read User A's report (404 Unauthorized)
    app.dependency_overrides[get_current_user] = lambda: user_b
    get_unauth_resp = client.get(f"/api/v1/remedies/reports/{report_id}")
    assert get_unauth_resp.status_code == 404, "User B should not have access to User A's remedy report!"

    # 6. Test invalid UUID format rejection -> 400 Bad Request
    invalid_uuid_resp = client.get("/api/v1/remedies/reports/NOT-A-VALID-UUID")
    assert invalid_uuid_resp.status_code == 400

    # Clean up overrides
    app.dependency_overrides.clear()


def test_saved_remedy_analysis_requires_auth():
    """Verify that saved remedy analysis and reports endpoints reject unauthenticated requests with 401."""
    # Ensure overrides are clear so real authentication is tested
    app.dependency_overrides.clear()

    horoscope_id = "11111111-1111-1111-1111-111111111111"

    # 1. Unauthenticated GET /analysis/saved/{horoscope_id} -> 401
    resp = client.get(f"/api/v1/remedies/analysis/saved/{horoscope_id}")
    assert resp.status_code == 401
    assert "Authentication token required." in resp.json().get("detail", "")

    # 2. Invalid Bearer token -> 401
    resp_invalid = client.get(
        f"/api/v1/remedies/analysis/saved/{horoscope_id}",
        headers={"Authorization": "Bearer invalid.token.payload"}
    )
    assert resp_invalid.status_code == 401

    # 3. Unauthenticated POST /reports -> 401
    resp_reports = client.post("/api/v1/remedies/reports", json={"horoscope_id": horoscope_id})
    assert resp_reports.status_code == 401
    assert "Authentication token required." in resp_reports.json().get("detail", "")


# ==============================================================================
# 9. D9-Aware Neecha Bhanga Assessment & Gemstone Policy Regression Tests
# ==============================================================================

def test_d9_aware_neecha_bhanga_exaltation_in_d9():
    """Verify D1-debilitated planet with D9 exaltation triggers complete NBRY and mild severity."""
    from app.services.remedy_engine.analysis import extract_chart_context, diagnose_chart_factors

    # Sun debilitated in Libra in D1 (House 1 for Libra Lagna, or House 7 for Aries Lagna)
    # Sun in Aries in D9 Navamsa (Exalted in D9!)
    chart = {
        "ascendant": {"sign": "Aries", "degree": 15.0},
        "planets": [
            {
                "name": "Sun",
                "sign": "Libra",
                "house": 7,
                "d9_sign": "Aries", # Exalted in D9!
                "longitude": 190.0,
                "is_combust": False,
            },
            {
                "name": "Venus",
                "sign": "Taurus",
                "house": 2,
                "longitude": 40.0,
            },
            {
                "name": "Moon",
                "sign": "Cancer",
                "house": 4,
                "longitude": 100.0,
            },
        ],
    }

    context = extract_chart_context(chart)
    assert "sun" in context.debilitated_planets
    assert len(context.neecha_bhanga_assessments) == 1

    nb = context.neecha_bhanga_assessments[0]
    assert nb.graha == "sun"
    assert nb.d1_sign == "Libra"
    assert nb.d9_sign == "Aries"
    assert nb.is_d1_debilitated is True
    assert nb.is_d9_exalted is True
    assert nb.is_d9_own_sign is False
    assert nb.has_cancellation_indicator is True
    assert nb.is_complete_nbry is True
    assert nb.cancellation_status == "complete_nbry_qualifying"
    assert nb.severity == "mild"
    assert any("Phaladeepika Ch. 6, v. 29" in r for r in nb.rule_identifiers)

    # Check factors
    factors = diagnose_chart_factors(context, chart)
    sun_factors = [f for f in factors if f.graha == "sun" and f.factor_type == "debilitation"]
    assert len(sun_factors) == 1
    sf = sun_factors[0]
    assert sf.severity == "mild"
    assert sf.neecha_bhanga is not None
    assert "Neecha Bhanga Raja Yoga" in sf.title_en
    assert "நீச பங்க ராஜ யோகம்" in sf.title_ta
    assert sf.description_en
    assert sf.description_ta


def test_d9_aware_neecha_bhanga_own_sign_in_d9():
    """Verify D1-debilitated planet with D9 own-sign placement qualifies for Neecha Bhanga."""
    from app.services.remedy_engine.analysis import extract_chart_context

    # Mars debilitated in Cancer in D1 (House 10 for Libra Lagna)
    # Mars in Scorpio in D9 Navamsa (Own sign in D9!)
    chart = {
        "ascendant": {"sign": "Libra", "degree": 10.0},
        "planets": [
            {
                "name": "Mars",
                "sign": "Cancer",
                "house": 10,
                "d9_sign": "Scorpio", # Own sign in D9!
                "longitude": 95.0,
                "is_combust": False,
            },
            {
                "name": "Moon",
                "sign": "Taurus",
                "house": 8,
                "longitude": 35.0,
            },
        ],
    }

    context = extract_chart_context(chart)
    assert "mars" in context.debilitated_planets
    nb = context.neecha_bhanga_assessments[0]
    assert nb.graha == "mars"
    assert nb.is_d1_debilitated is True
    assert nb.is_d9_own_sign is True
    assert nb.is_d9_exalted is False
    assert nb.has_cancellation_indicator is True
    assert nb.is_complete_nbry is True
    assert nb.cancellation_status == "complete_nbry_qualifying"
    assert any("Saravali Ch. 26" in r or "Phaladeepika" in r for r in nb.rule_identifiers)


def test_d9_aware_neecha_bhanga_vargottama():
    """Verify Vargottama in debilitation sign is recognized as an authentic resilience cancellation."""
    from app.services.remedy_engine.analysis import extract_chart_context

    # Saturn debilitated in Aries in D1 and also in Aries in D9 (Vargottama)
    chart = {
        "ascendant": {"sign": "Leo", "degree": 5.0},
        "planets": [
            {
                "name": "Saturn",
                "sign": "Aries",
                "house": 9,
                "d9_sign": "Aries", # Vargottama!
                "longitude": 21.0,
                "is_combust": False,
            },
        ],
    }

    context = extract_chart_context(chart)
    assert "saturn" in context.debilitated_planets
    assert "Saturn" in context.vargottama_planets
    nb = context.neecha_bhanga_assessments[0]
    assert nb.graha == "saturn"
    assert nb.is_vargottama is True
    assert nb.has_cancellation_indicator is True
    assert any("BPHS Ch. 6" in r or "Phaladeepika" in r for r in nb.rule_identifiers)
    assert nb.unresolved_interpretation is not None
    assert "Vargottama in debility" in nb.unresolved_interpretation


def test_d9_aware_neecha_bhanga_no_cancellation():
    """Verify debilitated planet with no cancellation rules satisfied retains unmitigated status."""
    from app.services.remedy_engine.analysis import extract_chart_context, diagnose_chart_factors

    # Jupiter debilitated in Capricorn in D1 in 6th house (dusthana, Leo Lagna)
    # Jupiter in Gemini in D9 (enemy sign, neither exalted nor own sign)
    # Saturn (dispositor) in 3rd house Libra (not in Kendra from Lagna or Moon, does not aspect Jupiter)
    chart = {
        "ascendant": {"sign": "Leo", "degree": 12.0},
        "planets": [
            {
                "name": "Jupiter",
                "sign": "Capricorn",
                "house": 6,
                "d9_sign": "Gemini",
                "longitude": 280.0,
                "is_combust": False,
            },
            {
                "name": "Saturn",
                "sign": "Libra",
                "house": 3,
                "longitude": 200.0,
                "is_combust": False,
            },
            {
                "name": "Moon",
                "sign": "Virgo",
                "house": 2,
                "longitude": 160.0,
            },
        ],
    }

    context = extract_chart_context(chart)
    assert "jupiter" in context.debilitated_planets
    nb = context.neecha_bhanga_assessments[0]
    assert nb.graha == "jupiter"
    assert nb.is_d1_debilitated is True
    assert nb.has_cancellation_indicator is False
    assert nb.is_complete_nbry is False
    assert nb.cancellation_status == "none"
    assert nb.severity in ("moderate", "high")

    factors = diagnose_chart_factors(context, chart)
    jup_factor = next(f for f in factors if f.graha == "jupiter" and f.factor_type == "debilitation")
    assert jup_factor.severity in ("moderate", "high")
    assert "without any classical cancellation" in jup_factor.description_en


def test_d9_aware_neecha_bhanga_missing_d9_never_substitutes_d1():
    """Verify that when D9 Navamsa data is missing, D1 is NEVER substituted and status is insufficient_data."""
    from app.services.remedy_engine.analysis import extract_chart_context

    # Venus debilitated in Virgo in D1, NO D9 fields and NO longitude provided
    chart = {
        "ascendant": {"sign": "Aries"},
        "planets": [
            {
                "name": "Venus",
                "sign": "Virgo",
                "house": 6,
                # Neither d9_sign nor longitude provided!
            },
        ],
    }

    context = extract_chart_context(chart)
    assert context.d9_data_status == "unavailable"
    assert "venus" in context.debilitated_planets

    nb = context.neecha_bhanga_assessments[0]
    assert nb.graha == "venus"
    assert nb.d9_data_status == "unavailable"
    # CRITICAL INVARIANT: Never substitute D1 for D9!
    assert nb.d9_sign is None, f"D1 sign was erroneously substituted for D9: {nb.d9_sign}"
    assert nb.cancellation_status == "insufficient_data"
    assert nb.confidence_status == "conditional"
    assert "True D9 Navamsa placements were unavailable" in nb.reason_en


def test_d9_aware_neecha_bhanga_combustion_neutralization():
    """Verify that solar combustion (Astangata) neutralizes Raja Yoga fruit per Phaladeepika Ch. 6."""
    from app.services.remedy_engine.analysis import extract_chart_context

    # Mercury debilitated in Pisces in D1, exalted in Virgo in D9, BUT combust Sun in Pisces
    chart = {
        "ascendant": {"sign": "Taurus", "degree": 20.0},
        "planets": [
            {
                "name": "Sun",
                "sign": "Pisces",
                "house": 11,
                "longitude": 340.0,
                "is_combust": False,
            },
            {
                "name": "Mercury",
                "sign": "Pisces",
                "house": 11,
                "d9_sign": "Virgo", # Exalted in D9!
                "longitude": 344.0, # Within 4 degrees of Sun -> Combust!
                "is_combust": True,
            },
        ],
    }

    context = extract_chart_context(chart)
    assert "mercury" in context.debilitated_planets
    assert "mercury" in context.combust_planets

    nb = context.neecha_bhanga_assessments[0]
    assert nb.graha == "mercury"
    assert nb.is_d9_exalted is True
    assert nb.is_combust is True
    assert nb.cancellation_status == "nbry_neutralized_by_combustion"
    assert nb.is_complete_nbry is False
    # Severity must NOT be downgraded to mild because combustion is an impediment
    assert nb.severity in ("moderate", "high")
    assert "solar combustion (Astangata)" in nb.reason_en


def test_gemstone_eligibility_review_gating_and_malefic_prohibition():
    """Verify gemstone safeguard: functional malefics strictly forbidden, benefics review-gated."""
    # 1. Saturn for Aries Lagna is functional malefic (10th & 11th lord) -> Gemstone forbidden!
    res_malefic = RemedyEligibilityEngine.evaluate_eligibility(
        ascendant_sign="Aries",
        graha="saturn",
        remedy_type="gemstone",
    )
    assert res_malefic.is_eligible is False
    assert res_malefic.requires_manual_astrologer_review is True
    assert res_malefic.is_review_gated is True
    assert "strictly forbids wearing gemstones for functional malefics" in res_malefic.restriction_reason

    # 2. Saturn for Taurus Lagna is Yogakaraka (9th & 10th lord) -> Favorable, but review-gated!
    res_benefic = RemedyEligibilityEngine.evaluate_eligibility(
        ascendant_sign="Taurus",
        graha="saturn",
        remedy_type="gemstone",
    )
    assert res_benefic.is_eligible is True
    assert res_benefic.is_yogakaraka is True
    assert res_benefic.requires_manual_astrologer_review is True
    assert res_benefic.is_review_gated is True
    assert "strictly requires manual certified astrologer review" in res_benefic.restriction_reason


def test_gemstones_strictly_excluded_from_automated_recommendations():
    """Verify that automated personalized recommendations never prescribe unreviewed gemstones."""
    from app.services.remedy_engine.analysis import extract_chart_context, diagnose_chart_factors, rank_and_retrieve_remedies

    chart = {
        "ascendant": {"sign": "Taurus"},
        "planets": [{"name": "Saturn", "sign": "Capricorn", "house": 9, "is_combust": False}],
    }
    sample_dasa = {"active_period": {"mahadasha": "saturn"}}

    mock_catalog = [
        {
            "code": "REM_SAT_MANTRA_01",
            "graha": "saturn",
            "remedy_type": "mantra",
            "name_en": "Shani Moola Mantra",
            "name_ta": "சனி மூல மந்திரம்",
            "description_en": "Mantra for Saturn",
            "description_ta": "சனி மந்திரம்",
            "deity_en": "Lord Shani",
            "deity_ta": "சனீஸ்வரர்",
            "procedure_en": "Chant 108 times",
            "procedure_ta": "108 முறை ஜபம்",
            "sanskrit_text": "ॐ शं शनैश्चराय नमः ॥",
            "transliteration_ta": "ஓம் சம் சனைச்சராய நமஹ ॥",
            "source_code": "BPHS",
        },
        {
            "code": "REM_SAT_GEMSTONE_01",
            "graha": "saturn",
            "remedy_type": "gemstone",
            "name_en": "Blue Sapphire (Neelam)",
            "name_ta": "நீலக்கல்",
            "description_en": "Blue sapphire gemstone",
            "description_ta": "நீல மாணிக்கம்",
            "deity_en": "Lord Shani",
            "deity_ta": "சனீஸ்வரர்",
            "procedure_en": "Wear on Saturday",
            "procedure_ta": "சனிக்கிழமை அணியவும்",
            "source_code": "JATAKA_PARIJATA",
        },
    ]

    context = extract_chart_context(chart, sample_dasa)
    factors = diagnose_chart_factors(context, chart)
    ranked = rank_and_retrieve_remedies(context, factors, mock_catalog, [])

    # The mantra should be recommended
    assert any(r.remedy.code == "REM_SAT_MANTRA_01" for r in ranked)
    # The gemstone MUST be strictly excluded from automated recommendations!
    assert not any(r.remedy.remedy_type in ("gemstone", "ratna") for r in ranked), "Gemstone was automatically recommended!"


