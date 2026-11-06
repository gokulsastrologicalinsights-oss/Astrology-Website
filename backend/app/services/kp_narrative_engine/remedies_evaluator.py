"""Actionable Do's, Don'ts and Tailored Remedial Advice Evaluator.

Tailored to active sub-lord significations and current Dasha-Bhukti planetary lords.
"""

from typing import Any, Dict, List, Set, Tuple
from app.schemas.kp_narrative import RemedialAdviceSection
from .constants import PLANETARY_REMEDIES, PLANET_NAMES_TA
from .natal_evaluator import _get_planet_signified_houses


def evaluate_tailored_remedies(
    kp_chart: Any,
    active_bhukti_lord: str,
    active_mahadasha_lord: str,
) -> RemedialAdviceSection:
    """Generates tailored Do's, Don'ts, deity meditation, charitable deeds, and lifestyle advice."""
    primary_remedy_planet = active_bhukti_lord if active_bhukti_lord in PLANETARY_REMEDIES else active_mahadasha_lord
    rem_info = PLANETARY_REMEDIES.get(primary_remedy_planet, PLANETARY_REMEDIES["Jupiter"])

    # Analyze combined house significations of the active period
    bhukti_sigs = set(_get_planet_signified_houses(active_bhukti_lord, kp_chart))
    md_sigs = set(_get_planet_signified_houses(active_mahadasha_lord, kp_chart))
    combined_sigs = bhukti_sigs | md_sigs

    has_health_caution = bool(combined_sigs & {6, 8, 12})
    has_loss_caution = bool(combined_sigs & {5, 8, 12})
    has_career_strength = bool(combined_sigs & {2, 6, 10, 11})
    has_relationship_strength = bool(combined_sigs & {2, 7, 11})

    dos_en: List[str] = []
    dos_ta: List[str] = []
    donts_en: List[str] = []
    donts_ta: List[str] = []

    # Concrete Do's tailored to active energies
    if has_career_strength:
        dos_en.append("Take calculated initiatives at work and pitch new ideas to seniors with structured data.")
        dos_ta.append("பணியிடத்தில் தைரியமாக புதிய முயற்சிகளை எடுத்து, உங்கள் திறமைகளை மேலதிகாரிகளுக்கு நிரூபியுங்கள்.")

    dos_en.append("Maintain rigorous accounting of monthly inflows and lock surplus cash in bank fixed deposits or gold.")
    dos_ta.append("மாதாந்திர வரவு-செலவுகளை முறையாக கணக்கிட்டு, உபரி பணத்தை சேமிப்பு பத்திரங்கள் அல்லது தங்கத்தில் முதலீடு செய்யுங்கள்.")

    if has_relationship_strength:
        dos_en.append("Foster warm, empathetic communication with your spouse and celebrate family milestones together.")
        dos_ta.append("வாழ்க்கைத் துணையுடன் மனம் விட்டுப் பேசி, குடும்ப சுபநிகழ்ச்சிகளில் மகிழ்ச்சியுடன் பங்கெடுங்கள்.")

    dos_en.append(rem_info.get("habit_en", "Maintain clean daily routines and speak truthfully with integrity."))
    dos_ta.append(rem_info.get("habit_ta", "நேர்மையான வாழ்க்கை முறையையும், உரிய காலந்தவறாமையையும் கடைப்பிடியுங்கள்."))

    # Concrete Don'ts tailored to active challenges
    if has_loss_caution:
        donts_en.append("Do NOT engage in speculative intraday stock trading, cryptocurrency bets, or lottery schemes.")
        donts_ta.append("பங்குச்சந்தை யூக வணிகம், அதிக வட்டி தரும் போலி கவர்ச்சி திட்டங்கள் அல்லது சூதாட்டங்களில் பணம் போட வேண்டாம்.")
        donts_en.append("Do NOT stand as financial guarantor or co-signer for friends or distant relatives.")
        donts_ta.append("நண்பர்களுக்கோ அல்லது உறவினர்களுக்கோ கடன் ஜாமீன் கையெழுத்து போடுவதை முற்றிலும் தவிருங்கள்.")

    if has_health_caution:
        donts_en.append("Do NOT skip regular meals or neglect persistent digestive, fatigue, or sleep symptoms.")
        donts_ta.append("உடல் சோர்வு அல்லது அஜீரணக் கோளாறுகளை அலட்சியம் செய்யாமல் உரிய மருத்துவ ஆலோசனைகளை பெறுங்கள்.")

    donts_en.append("Do NOT make life-altering decisions in anger, exhaustion, or during heated domestic arguments.")
    donts_ta.append("கோபத்திலோ அல்லது மனச்சோர்விலோ அவசரப்பட்டு முக்கிய முடிவுகளை எடுக்காதீர்கள்.")

    # Planetary Deity Meditation
    deity_en = f"Dedicated prayer to {rem_info['deity_en']} to channel the harmonizing rays of {primary_remedy_planet}."
    deity_ta = f"{rem_info['deity_ta']} வழிபாடு செய்து வர, {PLANET_NAMES_TA.get(primary_remedy_planet, primary_remedy_planet)} நற்பலன்களை வாரி வழங்குவார்."

    # Charitable Action (Dhanam)
    charity_en = f"{rem_info['charity_en']} This constructive karmic charity resolves friction and balances your active house vibrations."
    charity_ta = f"{rem_info['charity_ta']} இந்த எளிய தானத்தை மனமுவந்து செய்வது கர்ம வினைகளை தணித்து குடும்பத்தில் சுபத்தை உண்டாக்கும்."

    # Practical Lifestyle Guidance
    lifestyle_en = (
        f"Harmonize your biological clock with your active planetary lord: {rem_info['habit_en']} "
        f"Keep your workspace decluttered and practice 10 minutes of silent breath meditation each morning."
    )
    lifestyle_ta = (
        f"தற்போதைய கிரக அமைப்பிற்கு ஏற்ப வாழ்க்கை முறையை சீரமையுங்கள்: {rem_info['habit_ta']} "
        f"தினமும் காலையில் 10 நிமிடங்கள் அமைதியாக தியானம் செய்வதும், பணிபுரியும் இடத்தை சுத்தமாக வைப்பதும் மன அமைதியைத் தரும்."
    )

    # Lucky Day and Color
    lucky_en = f"Most Favorable Day: {rem_info['lucky_days_en']} | Supportive Colors: {rem_info['lucky_color_en']}"
    lucky_ta = f"சாதகமான சுப தினம்: {rem_info['lucky_days_ta']} | அதிர்ஷ்ட நிறங்கள்: {rem_info['lucky_color_ta']}"

    return RemedialAdviceSection(
        dos_en=dos_en[:4],
        dos_ta=dos_ta[:4],
        donts_en=donts_en[:4],
        donts_ta=donts_ta[:4],
        deity_prayer_en=deity_en,
        deity_prayer_ta=deity_ta,
        charity_action_en=charity_en,
        charity_action_ta=charity_ta,
        lifestyle_guidance_en=lifestyle_en,
        lifestyle_guidance_ta=lifestyle_ta,
        lucky_day_color_en=lucky_en,
        lucky_day_color_ta=lucky_ta,
    )
