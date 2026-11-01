"""Service layer for Tamil Astrology and Daily Dharma Sastra operations.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from app.services.tamil_sastra.knowledge_base import (
    MEDICAL_ASTROLOGY_DEITIES,
    LIFE_WISH_DEITIES,
    RAMAYANA_PARAYANAM_GUIDE,
    NAVAGRAHA_CORRESPONDENCES,
    NAVAGRAHA_DASA_PARIHARAMS,
    VASTU_PURUSHA_TIMINGS,
    VASTU_RULES_CHECKLIST,
    VAARA_SOOLAM_DATA,
    TITHI_SOOLAM_DATA,
    NAKSHATRA_SOOLAM_DATA,
    GOWRI_PERIODS_DEF,
    GOWRI_DAY_ORDER,
    SPECIAL_MUHURTAS,
    TAMIL_NUMEROLOGY_DATA,
)
from app.services.tamil_sastra.models import (
    DailyGuidanceResponse,
    GowriMuhurtaSlot,
)

WEEKDAYS_TA = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"]
WEEKDAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Eye count (Naal Vizhippu)
NAAL_VIZHIPPU = {
    0: ("ஒரு கண்ணுள்ள நாள் (சுமாரானது)", "one_eyed"),    # Mon
    1: ("குருட்டு நாள் (சுபகாரியங்கள் தவிர்க்கவும்)", "blind"),       # Tue
    2: ("இரு கண்ணுள்ள நாள் (சகல சுபகாரியங்களுக்கும் உத்தமம்)", "two_eyed"), # Wed
    3: ("இரு கண்ணுள்ள நாள் (சகல சுபகாரியங்களுக்கும் உத்தமம்)", "two_eyed"), # Thu
    4: ("இரு கண்ணுள்ள நாள் (சகல சுபகாரியங்களுக்கும் உத்தமம்)", "two_eyed"), # Fri
    5: ("குருட்டு நாள் (சுபகாரியங்கள் தவிர்க்கவும்)", "blind"),       # Sat
    6: ("ஒரு கண்ணுள்ள நாள் (சுமாரானது)", "one_eyed"),    # Sun
}

AUSPICIOUS_HORAS_MAP = {
    0: ["சந்திர ஹோரை", "புதன் ஹோரை", "குரு ஹோரை", "சுக்கிர ஹோரை"],
    1: ["சுக்கிர ஹோரை", "புதன் ஹோரை", "குரு ஹோரை"],
    2: ["புதன் ஹோரை", "குரு ஹோரை", "சுக்கிர ஹோரை", "சந்திர ஹோரை"],
    3: ["குரு ஹோரை", "சுக்கிர ஹோரை", "புதன் ஹோரை", "சந்திர ஹோரை"],
    4: ["சுக்கிர ஹோரை", "புதன் ஹோரை", "குரு ஹோரை"],
    5: ["புதன் ஹோரை", "குரு ஹோரை", "சுக்கிர ஹோரை"],
    6: ["குரு ஹோரை", "சுக்கிர ஹோரை", "புதன் ஹோரை"],
}


class TamilSastraService:
    @staticmethod
    def get_medical_deities(query: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        results = MEDICAL_ASTROLOGY_DEITIES
        if category:
            cat_lower = category.lower()
            results = [r for r in results if r.get("category") == cat_lower]
        if query:
            q = query.lower()
            results = [
                r for r in results
                if q in r["disease_en"].lower()
                or q in r["disease_ta"]
                or q in r["deity_en"].lower()
                or q in r["deity_ta"]
            ]
        return results

    @staticmethod
    def get_life_wishes(query: Optional[str] = None) -> List[Dict[str, Any]]:
        results = LIFE_WISH_DEITIES
        if query:
            q = query.lower()
            results = [
                r for r in results
                if q in r["goal_en"].lower()
                or q in r["goal_ta"]
                or q in r["deity_en"].lower()
                or q in r["deity_ta"]
            ]
        return results

    @staticmethod
    def get_ramayana_parayanam(kandam: Optional[str] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        results = RAMAYANA_PARAYANAM_GUIDE
        if kandam:
            k_lower = kandam.lower()
            results = [r for r in results if k_lower in r["kandam_en"].lower() or k_lower in r["kandam_ta"]]
        if query:
            q = query.lower()
            results = [
                r for r in results
                if q in r["purpose_en"].lower()
                or q in r["purpose_ta"]
                or q in r["sarga_title_en"].lower()
                or q in r["sarga_title_ta"]
            ]
        return results

    @staticmethod
    def get_navagraha_catalog() -> List[Dict[str, Any]]:
        return NAVAGRAHA_CORRESPONDENCES

    @staticmethod
    def get_dasa_pariharams() -> List[Dict[str, Any]]:
        return NAVAGRAHA_DASA_PARIHARAMS

    @staticmethod
    def get_vastu_timings() -> List[Dict[str, Any]]:
        return VASTU_PURUSHA_TIMINGS

    @staticmethod
    def get_vastu_rules(category: Optional[str] = None) -> List[Dict[str, Any]]:
        if category:
            cat_lower = category.lower()
            return [r for r in VASTU_RULES_CHECKLIST if r["category"] == cat_lower]
        return VASTU_RULES_CHECKLIST

    @staticmethod
    def get_soolam_data() -> Dict[str, Any]:
        return {
            "vaara_soolam": VAARA_SOOLAM_DATA,
            "tithi_soolam": TITHI_SOOLAM_DATA,
            "nakshatra_soolam": NAKSHATRA_SOOLAM_DATA,
            "remedy_instructions_ta": "சூல திசையில் தவிர்க்க முடியாத பயணம் ஏற்படின், குறிப்பிட்ட பரிகாரப் பொருளை உட்கொண்டு அல்லது தொட்டு நாழிகை 10-க்கு மேல் புறப்படலாம்.",
        }

    @staticmethod
    def get_gowri_panchangam(weekday_idx: int) -> List[GowriMuhurtaSlot]:
        day_sequence = GOWRI_DAY_ORDER.get(weekday_idx, GOWRI_DAY_ORDER[0])
        slots = []
        for idx, key in enumerate(day_sequence):
            info = GOWRI_PERIODS_DEF[key]
            slots.append(
                GowriMuhurtaSlot(
                    order=idx + 1,
                    name_ta=info["name_ta"],
                    name_en=key.capitalize(),
                    nature=info["nature"],
                    is_favorable=info["is_favorable"],
                    description_ta=info["description_ta"],
                )
            )
        return slots

    @staticmethod
    def get_special_muhurtas() -> Dict[str, Any]:
        return SPECIAL_MUHURTAS

    @staticmethod
    def get_tamil_numerology(birth_number: Optional[int] = None) -> Any:
        if birth_number and 1 <= birth_number <= 9:
            return TAMIL_NUMEROLOGY_DATA.get(birth_number)
        return TAMIL_NUMEROLOGY_DATA

    @staticmethod
    def compute_daily_guidance(date_str: str, janma_nakshatra_idx: Optional[int] = None, janma_rasi_idx: Optional[int] = None) -> DailyGuidanceResponse:
        dt = datetime.fromisoformat(date_str)
        # dt.weekday() returns 0=Mon, 1=Tue, ..., 6=Sun
        weekday_idx = dt.weekday()

        weekday_ta = WEEKDAYS_TA[weekday_idx]
        weekday_en = WEEKDAYS_EN[weekday_idx]

        vizhippu_text, vizhippu_cat = NAAL_VIZHIPPU[weekday_idx]
        soolam_info = VAARA_SOOLAM_DATA[weekday_idx]
        gowri_slots = TamilSastraService.get_gowri_panchangam(weekday_idx)
        auspicious_horas = AUSPICIOUS_HORAS_MAP.get(weekday_idx, ["குரு ஹோரை", "சுக்கிர ஹோரை", "புதன் ஹோரை"])

        dos: List[str] = []
        donts: List[str] = []

        if weekday_idx in (2, 3, 4):  # Wed, Thu, Fri
            dos.append("இன்று இரண்டு கண்ணுள்ள நாள்: புதிய முயற்சிகள், வியாபாரம், பத்திரப்பதிவு மற்றும் சுப விசேஷங்கள் துவங்க மிக உன்னதமானது.")
        elif weekday_idx in (0, 6):  # Mon, Sun
            dos.append("இன்று ஒரு கண்ணுள்ள நாள்: அன்றாட பணிகள் மற்றும் சாதாரண பயணங்களுக்கு ஏற்றது.")
        else:  # Tue, Sat
            donts.append("இன்று செவ்வாய்/சனி குருட்டு நாள்: நீண்டகால திருமண ஒப்பந்தங்கள், புதுமனை புகுதல் போன்ற சுபகாரியங்களை தவிர்ப்பது நலம்.")

        # Soolam warning
        donts.append(f"இன்று {soolam_info['direction_ta']} திசையில் சூலம் உள்ளது. தவிர்க்க முடியாத பயணம் ஏற்படின் {soolam_info['pariharam_ta']}.")

        # Oil bath rules
        if weekday_idx in (2, 5):
            dos.append("ஆண்களுக்கு இன்று எண்ணெய் தேய்த்துக் குளிக்க (தைல ஸ்நானம்) உகந்த நாள்.")
        elif weekday_idx in (1, 4):
            dos.append("பெண்களுக்கு இன்று எண்ணெய் தேய்த்துக் குளிக்க உகந்த நன்னாள்.")
        elif weekday_idx == 6:
            donts.append("ஞாயிற்றுக்கிழமையில் எண்ணெய் தேய்த்துக் குளிப்பது உடலுக்கும் ஆயுளுக்கும் நல்லதல்ல.")

        # Deepam tip
        deepam_tip = "வீட்டில் விளக்கேற்றும் போது 2 திரிகளை ஒன்றாக முறுக்கி கிழக்கு அல்லது வடக்கு நோக்கி ஏற்றுவது மங்கலத்தை சேர்க்கும். தாமரை நூல் திரி மகாலட்சுமி கடாட்சம் தரும்."

        # General Dharma tip
        general_dharma = "சாப்பிடும் போது முதலில் இனிப்பு, பின் உவர்ப்பு, புளிப்பு, கசப்பு ஆகியவற்றை உண்டு பின் நீர் அருந்துவது ஆயுளை பெருக்கும். வடக்கு அல்லது கிழக்கு நோக்கி அமர்ந்து உணவருந்தவும்."

        return DailyGuidanceResponse(
            date=date_str,
            weekday_ta=weekday_ta,
            weekday_en=weekday_en,
            naal_vizhippu_ta=vizhippu_text,
            naal_vizhippu_category=vizhippu_cat,
            vaara_soolam_ta=soolam_info["direction_ta"],
            vaara_soolam_direction=soolam_info["direction_en"],
            pariharam_ta=soolam_info["pariharam_ta"],
            gowri_panchangam_day=gowri_slots,
            auspicious_horas_ta=auspicious_horas,
            chandrashtama_warning=False,
            dos_for_today_ta=dos,
            donts_for_today_ta=donts,
            deepam_worship_tip_ta=deepam_tip,
            general_dharma_tip_ta=general_dharma,
        )
