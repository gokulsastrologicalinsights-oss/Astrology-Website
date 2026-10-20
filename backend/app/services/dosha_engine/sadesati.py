"""Sadesati, Kantaka, and Ashtama Shani transit evaluation module.

Calculates transiting Saturn's sidereal position using XALEN ephemeris for any requested date,
evaluates the transit relative to the natal Moon sign, and incorporates Saturn's natal
Bhinnashtakavarga (BAV) bindus to provide nuanced, non-fatalistic interpretations.
"""

from datetime import datetime, date, time, timezone
from typing import Dict, Optional, Tuple
import xalen
from app.schemas.dosha import SadesatiPhaseInfo
from app.services.timezone_utils import resolve_birth_datetime
from app.services.dosha_engine.models import (
    DoshaChartContext,
    SIGN_NAMES_EN,
    SIGN_NAMES_TA,
)


def compute_transit_saturn(
    transit_date: Optional[str] = None,
    transit_time: Optional[str] = "12:00:00",
    ayanamsa_id: int = 0,
) -> Tuple[float, bool, int, str, float]:
    """Compute transiting Saturn sidereal position via XALEN.

    Returns:
        (longitude, is_retrograde, sign_index 1-12, sign_name, degree_in_sign 0-30)
    """
    if transit_date:
        t_date = date.fromisoformat(transit_date) if isinstance(transit_date, str) else transit_date
    else:
        t_date = datetime.now(timezone.utc).date()

    if transit_time:
        t_time = time.fromisoformat(transit_time) if isinstance(transit_time, str) else transit_time
    else:
        t_time = time(12, 0, 0)

    _, _, jd_transit, _, _ = resolve_birth_datetime(t_date, t_time, "UTC")

    # Body 6 is Saturn in Swiss Ephemeris / XALEN
    pos = xalen.planet_position(jd_transit, 6, True, ayanamsa_id)
    lon = pos["longitude"] % 360.0
    is_retro = bool(pos["is_retrograde"])

    sign_idx = int(lon // 30.0) + 1
    deg_in_sign = lon % 30.0
    sign_name = SIGN_NAMES_EN.get(sign_idx, "Unknown")

    return lon, is_retro, sign_idx, sign_name, deg_in_sign


def evaluate_sadesati(
    ctx: DoshaChartContext,
    transit_date: Optional[str] = None,
    transit_time: Optional[str] = "12:00:00",
    ayanamsa_id: int = 0,
    saturn_bav_bindus: Optional[Dict[int, int]] = None,
) -> SadesatiPhaseInfo:
    """Evaluate Sadesati (7.5-year Saturn transit) plus Kantaka and Ashtama Shani."""
    lon, is_retro, trans_sign_idx, trans_sign_name, deg_in_sign = compute_transit_saturn(
        transit_date=transit_date,
        transit_time=transit_time,
        ayanamsa_id=ayanamsa_id,
    )

    natal_moon_sign_idx = ctx.moon_sign_idx
    natal_moon_sign_name = SIGN_NAMES_EN.get(natal_moon_sign_idx, "Unknown")

    # House offset from natal Moon sign (1-12)
    house_from_moon = ((trans_sign_idx - natal_moon_sign_idx) % 12) + 1

    # Classify phase
    if house_from_moon == 12:
        phase = "Rising"
        phase_ta = "விரைய சனி (முதற்கட்டம்)"
        is_active = True
    elif house_from_moon == 1:
        phase = "Peak"
        phase_ta = "ஜென்ம சனி (இரண்டாம்கட்டம்)"
        is_active = True
    elif house_from_moon == 2:
        phase = "Setting"
        phase_ta = "பாத சனி (மூன்றாம்கட்டம்)"
        is_active = True
    elif house_from_moon == 4:
        phase = "Kantaka"
        phase_ta = "கண்டக சனி"
        is_active = True
    elif house_from_moon == 8:
        phase = "Ashtama"
        phase_ta = "அஷ்டம சனி"
        is_active = True
    else:
        phase = "None"
        phase_ta = "இல்லை"
        is_active = False

    # Extract Saturn's BAV bindus in transiting sign if available
    bav_count: Optional[int] = None
    if saturn_bav_bindus and trans_sign_idx in saturn_bav_bindus:
        bav_count = saturn_bav_bindus[trans_sign_idx]

    # Determine nature of transit
    if bav_count is not None:
        if bav_count >= 4:
            nature = "Benefic / Constructive"
        elif bav_count == 3:
            nature = "Moderate / Disciplined"
        else:
            nature = "Testing / Transformative"
    else:
        if not is_active:
            nature = "Benefic / Constructive"
        elif phase in ("Rising", "Setting", "Kantaka"):
            nature = "Moderate / Disciplined"
        else:
            nature = "Testing / Transformative"

    # Retrograde descriptor
    retro_desc = " (Retrograde/வக்ரம்)" if is_retro else ""
    bav_desc = f" with {bav_count} bindus in Saturn's Ashtakavarga" if bav_count is not None else ""

    # Interpretations
    if phase == "Rising":
        interp_en = (
            f"Transiting Saturn is in {trans_sign_name}{retro_desc}, occupying the 12th house from natal Moon ({natal_moon_sign_name}). "
            f"This marks the Rising Phase (Aadyanta / 1st phase) of Sadesati{bav_desc}. "
            f"Karmic emphasis shifts to restructuring expenses, planning long-term foundations, reducing unnecessary commitments, "
            f"and cultivating meditative introspection. Nature of transit is {nature.lower()}."
        )
        interp_ta = (
            f"சனி பகவான் {SIGN_NAMES_TA.get(trans_sign_idx, trans_sign_name)} ராசியில் சஞ்சரிக்கிறார்{retro_desc}. "
            f"இது உங்கள் சந்திர ராசியான {SIGN_NAMES_TA.get(natal_moon_sign_idx, natal_moon_sign_name)}க்கு 12-ம் வீடான விரைய சனியாகும். "
            "தேவையற்ற விரயங்களை கட்டுப்படுத்துவதும், ஆன்மீக ஈடுபாடும், எதிர்கால திட்டங்களை நிதானமாக தீட்டுவதும் மன அமைதி தரும்."
        )
    elif phase == "Peak":
        interp_en = (
            f"Transiting Saturn is in {trans_sign_name}{retro_desc}, directly traversing the natal Moon sign ({natal_moon_sign_name}). "
            f"This represents the Peak Phase (Janma Shani / 2nd phase) of Sadesati{bav_desc}. "
            f"Demands intense emotional discipline, accountability, perseverance, and health care. "
            f"Under Saturn's strict gaze, superficial dependencies dissolve, forging immense inner strength and resilience. Nature is {nature.lower()}."
        )
        interp_ta = (
            f"சனி பகவான் ஜென்ம ராசியான {SIGN_NAMES_TA.get(natal_moon_sign_idx, natal_moon_sign_name)} மீது நேரிடையாக சஞ்சரிக்கிறார் (ஜென்ம சனி){retro_desc}. "
            "மனதில் தேவையற்ற சஞ்சலங்களைத் தவிர்த்து, கடமைகளை நேர்மையுடன் செய்வதன் மூலம் தனித்துவமான முதிர்ச்சியையும் மனவலிமையையும் அடையலாம்."
        )
    elif phase == "Setting":
        interp_en = (
            f"Transiting Saturn is in {trans_sign_name}{retro_desc}, traversing the 2nd house from natal Moon ({natal_moon_sign_name}). "
            f"This is the Setting Phase (Antya/Pada Shani / 3rd phase) of Sadesati{bav_desc}. "
            f"Focus turns to stabilizing family dynamics, financial consolidation, and prudent speech. "
            f"As Sadesati concludes, the hard-earned lessons crystallize into permanent life wisdom and financial security. Nature is {nature.lower()}."
        )
        interp_ta = (
            f"சனி பகவான் சந்திரனுக்கு 2-ம் வீடான {SIGN_NAMES_TA.get(trans_sign_idx, trans_sign_name)} ராசியில் சஞ்சரிக்கிறார் (பாத சனி){retro_desc}. "
            "குடும்பப் பொறுப்புகளிலும் தன வரவுகளிலும் நிதானத்தைக் கடைப்பிடிப்பது நல்லது. ஏழரைச் சனியின் நிறைவுக் கட்டத்தில் நற்பலன்கள் உறுதிப்படும்."
        )
    elif phase == "Kantaka":
        interp_en = (
            f"Transiting Saturn is in {trans_sign_name}{retro_desc}, situated in the 4th house from natal Moon ({natal_moon_sign_name}), "
            f"activating Kantaka Shani{bav_desc}. "
            f"Indicates restructuring domestic matters, property, mother's wellbeing, or career foundation. "
            f"Methodical execution and patience yield substantial long-term stability. Nature is {nature.lower()}."
        )
        interp_ta = (
            f"சனி பகவான் சந்திரனுக்கு 4-ம் வீட்டில் சஞ்சரிப்பதால் கண்டக சனி உருவாகிறது{retro_desc}. "
            "வீடு, வாகனம், தாய்வழி உறவுகளில் கூடுதல் கவனம் தேவை. நிதானமான செயல்கள் நன்மையை உண்டாக்கும்."
        )
    elif phase == "Ashtama":
        interp_en = (
            f"Transiting Saturn is in {trans_sign_name}{retro_desc}, situated in the 8th house from natal Moon ({natal_moon_sign_name}), "
            f"forming Ashtama Shani{bav_desc}. "
            f"Represents a transformative karmic audit requiring avoidance of rash speculation, adherence to legal rectitude, "
            f"and focus on holistic wellness and research. Nature is {nature.lower()}."
        )
        interp_ta = (
            f"சனி பகவான் சந்திரனுக்கு 8-ம் வீட்டில் சஞ்சரிப்பதால் அஷ்டம சனி காலமாகிறது{retro_desc}. "
            "வேகமான முடிவுகளையும் சூதாட்டங்களையும் தவிர்த்து, பொறுமையுடனும் இறை வழிபாட்டுடனும் செயல்படுவது மேன்மை தரும்."
        )
    else:
        interp_en = (
            f"Transiting Saturn is currently in {trans_sign_name} ({deg_in_sign:.1f}°){retro_desc}, placed in house {house_from_moon} "
            f"from natal Moon ({natal_moon_sign_name}). Sadesati, Kantaka, and Ashtama Shani are not active. "
            "Saturn's transit supports steady vocational progress and constructive development."
        )
        interp_ta = (
            f"சனி பகவான் தற்போது {SIGN_NAMES_TA.get(trans_sign_idx, trans_sign_name)} ராசியில் ({deg_in_sign:.1f}°) சஞ்சரிக்கிறார்{retro_desc}. "
            f"சந்திரனுக்கு {house_from_moon}-ம் இடத்தில் உள்ளதால் ஏழரை சனியோ, கண்டக சனியோ, அஷ்டம சனியோ தற்போது இல்லை. அமைதியான நற்பலன்கள் அமையும்."
        )

    return SadesatiPhaseInfo(
        is_active=is_active,
        phase=phase,
        phase_name_tamil=phase_ta,
        natal_moon_sign_index=natal_moon_sign_idx,
        natal_moon_sign_name=natal_moon_sign_name,
        transit_saturn_sign_index=trans_sign_idx,
        transit_saturn_sign_name=trans_sign_name,
        transit_saturn_degree_in_sign=round(deg_in_sign, 2),
        saturn_is_retrograde=is_retro,
        house_from_moon=house_from_moon,
        saturn_ashtakavarga_bindus=bav_count,
        nature_of_transit=nature,
        interpretation=interp_en,
        interpretation_tamil=interp_ta,
    )
