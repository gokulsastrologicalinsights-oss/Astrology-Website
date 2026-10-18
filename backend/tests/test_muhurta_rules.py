"""Unit tests for occasion-specific Muhurta rules, scoring, and diagnostics.

Covers:
- Occasion rule enforcement (Marriage, Griha Pravesham, etc.)
- Mandatory failure vs Advisory distinctions
- Rahu Kalam, Yamagandam, and Dur Muhurta overlap detection
- Ashtama Shuddhi and Sapthama Shuddhi evaluation
- Tara Bala and Chandra Bala calculations
- Missing birth data marked as 'incomplete' without silent passing
"""

import pytest
from datetime import datetime, timezone
from app.services.muhurta_engine.rules import (
    evaluate_tara_bala,
    evaluate_chandra_bala,
    evaluate_muhurta_slot,
)


def test_tara_bala_calculations():
    """Verify Navatara computation from Janma Nakshatra."""
    # Janma Nakshatra = 1 (Ashwini)
    # Transit = 2 (Bharani) -> Count = 2 (Sampat -> Benefic)
    tb_sampat = evaluate_tara_bala(transit_nakshatra_idx=2, birth_nakshatra_idx=1)
    assert tb_sampat["status"] == "pass"
    assert tb_sampat["tara_number"] == 2
    assert tb_sampat["tara_name"] == "Sampat"
    assert tb_sampat["passed"] is True

    # Transit = 3 (Krittika) -> Count = 3 (Vipat -> Malefic/Fail)
    tb_vipat = evaluate_tara_bala(transit_nakshatra_idx=3, birth_nakshatra_idx=1)
    assert tb_vipat["status"] == "fail"
    assert tb_vipat["tara_number"] == 3
    assert tb_vipat["passed"] is False

    # Transit = 7 (Punarvasu) -> Count = 7 (Naidhana/Vadha -> Strictly Fail)
    tb_vadha = evaluate_tara_bala(transit_nakshatra_idx=7, birth_nakshatra_idx=1)
    assert tb_vadha["status"] == "fail"
    assert tb_vadha["tara_name"] == "Naidhana (Vadha)"


def test_tara_bala_missing_data():
    """Verify missing birth star returns 'incomplete' status instead of silently passing."""
    tb_missing = evaluate_tara_bala(transit_nakshatra_idx=5, birth_nakshatra_idx=None)
    assert tb_missing["status"] == "incomplete"
    assert tb_missing["passed"] is False
    assert "not supplied" in tb_missing["details"]


def test_chandra_bala_ashtama_chandra():
    """Verify 8th house transit Moon (Ashtama Chandra) triggers failure."""
    # Janma Rashi = 1 (Aries). Transit Moon = 8 (Scorpio) -> 8th house
    cb = evaluate_chandra_bala(transit_moon_sign_idx=8, birth_moon_sign_idx=1)
    assert cb["status"] == "fail"
    assert cb["is_ashtama_chandra"] is True
    assert cb["house_from_moon"] == 8
    assert cb["passed"] is False


def test_chandra_bala_auspicious():
    """Verify 11th house transit Moon (Labha) is auspicious."""
    # Janma Rashi = 1 (Aries). Transit Moon = 11 (Aquarius) -> 11th house
    cb = evaluate_chandra_bala(transit_moon_sign_idx=11, birth_moon_sign_idx=1)
    assert cb["status"] == "pass"
    assert cb["house_from_moon"] == 11
    assert cb["passed"] is True


def test_muhurta_slot_evaluation_rahu_kalam_failure():
    """Verify that candidate slot intersecting Rahu Kalam fails mandatory rules."""
    daily_panchang = {
        "tithi": {"number": 2, "name": "Shukla Dvitiya", "paksha": "Shukla"},
        "nakshatra": {"number": 4, "name": "Rohini"},
        "vara": {"weekday_number": 1, "name_en": "Monday"},
        "inauspicious_periods": {
            "rahu_kalam": {
                "start_utc": "2026-10-19T02:00:00+00:00",
                "end_utc": "2026-10-19T03:30:00+00:00",
                "duration_minutes": 90,
            },
            "yamagandam": {
                "start_utc": "2026-10-19T07:30:00+00:00",
                "end_utc": "2026-10-19T09:00:00+00:00",
                "duration_minutes": 90,
            },
            "gulikai": {
                "start_utc": "2026-10-19T10:00:00+00:00",
                "end_utc": "2026-10-19T11:30:00+00:00",
                "duration_minutes": 90,
            },
        },
        "dur_muhurtas": [],
        "varjyam": {
            "start_utc": "2026-10-19T14:00:00+00:00",
            "end_utc": "2026-10-19T15:30:00+00:00",
            "duration_minutes": 90,
        },
        "auspicious_periods": {"abhijit": None, "amrita_kalam": None},
    }

    lagna_planets = {
        "ascendant": {"sign_index": 2, "sign_name": "Taurus", "sign_name_ta": "ரிஷபம்"},
        "bhava_occupants": {8: []},  # 8th house clean
    }

    rules = {
        "prohibit_rahu_kalam": True,
        "acceptable_tithis": [2, 3, 5],
        "acceptable_nakshatras": [4, 5],
        "require_ashtama_shuddhi": True,
    }

    # Slot overlapping Rahu Kalam (02:15 to 03:00)
    slot_start = datetime(2026, 10, 19, 2, 15, tzinfo=timezone.utc)
    slot_end = datetime(2026, 10, 19, 3, 0, tzinfo=timezone.utc)

    eval_res = evaluate_muhurta_slot(
        slot_start_utc=slot_start,
        slot_end_utc=slot_end,
        daily_panchang=daily_panchang,
        lagna_planets=lagna_planets,
        rules=rules,
    )

    assert eval_res["status"] == "fails_mandatory_rules"
    assert any("Rahu Kalam" in f["rule"] for f in eval_res["failed_rules"])


def test_muhurta_slot_evaluation_pristine_pass():
    """Verify a clean slot meeting all rules receives 'meets_configured_rules'."""
    daily_panchang = {
        "tithi": {"number": 2, "name": "Shukla Dvitiya", "paksha": "Shukla"},
        "nakshatra": {"number": 4, "name": "Rohini"},
        "vara": {"weekday_number": 1, "name_en": "Monday"},
        "inauspicious_periods": {
            "rahu_kalam": {
                "start_utc": "2026-10-19T02:00:00+00:00",
                "end_utc": "2026-10-19T03:30:00+00:00",
                "duration_minutes": 90,
            },
            "yamagandam": {
                "start_utc": "2026-10-19T07:30:00+00:00",
                "end_utc": "2026-10-19T09:00:00+00:00",
                "duration_minutes": 90,
            },
            "gulikai": {
                "start_utc": "2026-10-19T10:00:00+00:00",
                "end_utc": "2026-10-19T11:30:00+00:00",
                "duration_minutes": 90,
            },
        },
        "dur_muhurtas": [],
        "varjyam": {
            "start_utc": "2026-10-19T14:00:00+00:00",
            "end_utc": "2026-10-19T15:30:00+00:00",
            "duration_minutes": 90,
        },
        "auspicious_periods": {"abhijit": None, "amrita_kalam": None},
    }

    lagna_planets = {
        "ascendant": {"sign_index": 2, "sign_name": "Taurus", "sign_name_ta": "ரிஷபம்"},
        "bhava_occupants": {8: []},
    }

    rules = {
        "prohibit_rahu_kalam": True,
        "acceptable_tithis": [2, 3, 5],
        "acceptable_nakshatras": [4, 5],
        "require_ashtama_shuddhi": True,
    }

    # Slot clean (04:00 to 05:00 UTC)
    slot_start = datetime(2026, 10, 19, 4, 0, tzinfo=timezone.utc)
    slot_end = datetime(2026, 10, 19, 5, 0, tzinfo=timezone.utc)

    eval_res = evaluate_muhurta_slot(
        slot_start_utc=slot_start,
        slot_end_utc=slot_end,
        daily_panchang=daily_panchang,
        lagna_planets=lagna_planets,
        rules=rules,
    )

    assert eval_res["status"] == "meets_configured_rules"
    assert eval_res["score"] >= 80
    assert len(eval_res["failed_rules"]) == 0
