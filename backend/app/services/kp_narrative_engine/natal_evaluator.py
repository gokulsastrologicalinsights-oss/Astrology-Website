"""Natal Event Promise Evaluator for KP Predictive Narrative Engine.

Evaluates primary cuspal sub-lords (1st, 2nd, 5th, 7th, 10th, 11th) and generates
clear, plain-language predictive narratives in both English and Tamil.
"""

from typing import Any, Dict, List, Set, Tuple
from app.schemas.kp_narrative import CuspalPromiseItem, NatalPromiseSection
from .constants import (
    PRIMARY_PROMISE_CUSPS,
    CUSP_DOMAINS,
    CUSP_SUPPORTIVE_HOUSES,
    CUSP_CHALLENGING_HOUSES,
    PLANET_NAMES_TA,
)


def _get_planet_signified_houses(planet: str, kp_chart: Any) -> List[int]:
    """Extracts all unique houses signified by the given planet across all 4 tiers (A, B, C, D)."""
    signified: Set[int] = set()
    
    # 1. Check planet_significators attribute if available
    sig_map = getattr(kp_chart, "significators", None)
    if sig_map and isinstance(sig_map, dict):
        entries = sig_map.get(planet, [])
        for entry in entries:
            h = getattr(entry, "house", None)
            if h is not None:
                signified.add(int(h))
            elif isinstance(entry, dict) and "house" in entry:
                signified.add(int(entry["house"]))

    # 2. Check house_significators list / dict if available
    house_sigs = getattr(kp_chart, "house_significators", None)
    if house_sigs:
        if isinstance(house_sigs, dict):
            for h_str, sig_data in house_sigs.items():
                try:
                    h_num = int(h_str)
                    all_p = (
                        sig_data.get("level_a", [])
                        + sig_data.get("level_b", [])
                        + sig_data.get("level_c", [])
                        + sig_data.get("level_d", [])
                    )
                    if planet in all_p:
                        signified.add(h_num)
                except (ValueError, TypeError):
                    continue
        elif isinstance(house_sigs, list):
            for i, h_entry in enumerate(house_sigs):
                h_num = getattr(h_entry, "house", i + 1)
                all_p = (
                    getattr(h_entry, "level_a", [])
                    + getattr(h_entry, "level_b", [])
                    + getattr(h_entry, "level_c", [])
                    + getattr(h_entry, "level_d", [])
                )
                if planet in all_p:
                    signified.add(h_num)

    # Fallback default houses based on natural rulership if none discovered
    if not signified:
        signified = {1, 2, 11}
    return sorted(list(signified))


def _evaluate_cusp_verdict(
    cusp: int,
    csl: str,
    signified_houses: List[int],
) -> Tuple[str, str, str]:
    """Determines verdict ('strongly_promised', 'delayed_fruition', 'denied_or_caution')

    and returns (verdict_key, label_en, label_ta).
    """
    sig_set = set(signified_houses)
    supportive = CUSP_SUPPORTIVE_HOUSES.get(cusp, set())
    challenging = CUSP_CHALLENGING_HOUSES.get(cusp, set())

    matched_support = sig_set & supportive
    matched_challenge = sig_set & challenging

    # Special rules per KP tenets:
    # Saturn or Ketu in sub-lord positions naturally induces delay or deep introspection
    is_delay_planet = csl in ("Saturn", "Ketu", "Rahu")

    if matched_support and not matched_challenge:
        if is_delay_planet and cusp in (2, 7, 10):
            return (
                "delayed_fruition",
                "Delayed with Eventual Fruition",
                "தாமதமான பலன் (முயற்சிக்குப்பின் வெற்றி)",
            )
        return (
            "strongly_promised",
            "Strongly Promised",
            "உறுதியான வாக்குறுதி (பூரண வெற்றி)",
        )
    elif matched_support and matched_challenge:
        # If supportive exceeds challenging, it yields success after hurdles
        if len(matched_support) >= len(matched_challenge):
            return (
                "delayed_fruition",
                "Delayed with Eventual Fruition",
                "தாமதமான பலன் (முயற்சிக்குப்பின் வெற்றி)",
            )
        else:
            return (
                "denied_or_caution",
                "Denied or Requires Caution",
                "விழிப்புணர்வு தேவை / சவாலான சூழல்",
            )
    elif matched_challenge and not matched_support:
        return (
            "denied_or_caution",
            "Denied or Requires Caution",
            "விழிப்புணர்வு தேவை / சவாலான சூழல்",
        )
    else:
        # Moderate default
        return (
            "delayed_fruition",
            "Delayed with Eventual Fruition",
            "தாமதமான பலன் (முயற்சிக்குப்பின் வெற்றி)",
        )


def _generate_plain_narrative(
    cusp: int,
    csl: str,
    star_lord: str,
    verdict: str,
    supportive_matched: List[int],
    challenging_matched: List[int],
) -> Tuple[str, str, str, str, str, str]:
    """Generates structured, plain-language English & Tamil narratives without astrology jargon.

    Returns: (summary_en, summary_ta, plain_narrative_en, plain_narrative_ta, practical_takeaway_en, practical_takeaway_ta)
    """
    csl_ta = PLANET_NAMES_TA.get(csl, csl)
    star_ta = PLANET_NAMES_TA.get(star_lord, star_lord)

    if cusp == 1:
        if verdict == "strongly_promised":
            sum_en = "Robust vitality, natural charisma, and strong self-healing capacity are assured throughout life."
            sum_ta = "சிறப்பான தேக ஆரோக்கியம், நற்பெயர் மற்றும் சவால்களை வெல்லும் மன உறுதி ஜாதகத்தில் உறுதியாக உள்ளது."
            narr_en = (
                f"Your life blueprint indicates an exceptionally resilient physical constitution and natural leadership ability. "
                f"Governed by {csl} operating through {star_lord}, your body quickly recuperates from fatigue, and your mind carries "
                f"the persistence needed to overcome early obstacles. Opportunities for personal recognition will open naturally when you take initiative."
            )
            narr_ta = (
                f"உங்கள் ஜாதகத்தில் முதலாம் பாவக உப-அதிபதி {csl_ta} மற்றும் நட்சத்திர அதிபதி {star_ta} அமைப்பானது சிறந்த நோய் எதிர்ப்புச் சக்தியையும், "
                f"தனித்தன்மை கொண்ட ஆளுமைத் திறனையும் வழங்குகிறது. எத்தகைய கடினமான சூழ்நிலைகளிலும் தளர்ந்து போகாமல் மீண்டு வரும் தேக பலமும், "
                f"சமூகத்தில் தங்களுக்கு என்று ஒரு தனி அங்கீகாரத்தைப் பெறும் நல்வாய்ப்பும் உறுதியாக வாக்குறுதி அளிக்கப்பட்டுள்ளது."
            )
            take_en = "Prioritize clean daily routines and trust your instinctive drive when taking leadership roles."
            take_ta = "தவறாமல் முறையான உடற்பயிற்சி மற்றும் ஆரோக்கியமான உணவுப் பழக்கங்களை கடைப்பிடித்து, தைரியமாக முன்முயற்சிகளை எடுக்கவும்."
        elif verdict == "delayed_fruition":
            sum_en = "Vitality and personal recognition develop steadily over time through disciplined self-care."
            sum_ta = "ஆரம்ப காலத்தில் உடல் அயர்ச்சி அல்லது தாமதங்கள் இருந்தாலும், அனுபவ முதிர்ச்சியால் நற்பெயரும் ஆரோக்கியமும் நிலைக்கும்."
            narr_en = (
                f"Your vital energy is grounded but demands conscious pacing. With {csl} as the primary sub-lord, early years may feature "
                f"occasional energy dips or self-doubt. However, as maturity builds, your mental resilience and physical stamina steadily strengthen, "
                f"leading to lasting respect in your middle and senior years."
            )
            narr_ta = (
                f"உங்கள் முதலாம் பாவக உப-அதிபதி {csl_ta} அமைப்பின்படி, ஆரம்ப காலங்களில் தேக அயர்ச்சியோ அல்லது முன்னேற்றத்தில் சிறு தாமதங்களோ "
                f"இருந்தாலும், வயது ஏற ஏற மன உறுதியும் உடல் வலிமையும் சீராக உயரும். ஒழுக்கமான வாழ்க்கை முறையைக் கடைப்பிடிக்கும் போது சமூக மதிப்பும் நீண்ட ஆயுளும் கிட்டும்."
            )
            take_en = "Avoid exhausting yourself with irregular sleep; sustainable pacing is your key to lifelong vitality."
            take_ta = "முறையற்ற தூக்கத்தையும் மன அழுத்தத்தையும் தவிர்த்து, மிதமான ஓய்வும் ஒழுக்கமும் பேணினால் ஆயுள் பலம் மிகும்."
        else:
            sum_en = "Health and stamina require vigilant attention and proactive medical management."
            sum_ta = "உடல் ஆரோக்கியத்தில் அலட்சியம் காட்டாமல் முன்எச்சரிக்கையுடனும் கவனத்துடனும் இருக்க வேண்டும்."
            narr_en = (
                f"Your life foundation asks for conscious preservation. The sub-lord connection warns against chronic overwork, sedentary habits, "
                f"or ignoring early bodily warning signals. Proactive preventive health checks and mindfulness will serve as your best armor."
            )
            narr_ta = (
                f"ஜாதக அமைப்பின்படி உடல் ஆரோக்கியத்தில் கூடுதல் விழிப்புணர்வு தேவைப்படுகிறது. நீண்ட நேரம் அமர்ந்து வேலை செய்தல், அதிக வேலைப்பளு "
                f"காரணமாக அயர்ச்சி ஏற்படலாம். சிறிய உபாதைகளையும் தள்ளிப்போடாமல் உடனடியாக மருத்துவ கவனிப்பும் யோகா போன்ற அமைதியான பயிற்சிகளும் மேற்கொள்வது நல்லது."
            )
            take_en = "Schedule regular annual medical screenings and strictly avoid unmanaged stress."
            take_ta = "ஆண்டுதோறும் முழு உடல் பரிசோதனை செய்துகொள்வதும், தியானம் மற்றும் சாத்வீக உணவு முறையைக் கடைப்பிடிப்பதும் நன்மை தரும்."

    elif cusp == 2:
        if verdict == "strongly_promised":
            sum_en = "Strong capital accumulation, steady cash flow, and reliable family financial support."
            sum_ta = "தொடர்ச்சியான பணப்புழக்கம், சொத்துச் சேர்க்கை மற்றும் குடும்பத்தின் வழியே நிரந்தர பொருளாதார வளர்ச்சி உண்டு."
            narr_en = (
                f"Financial security is one of the pillars of your horoscope. Guided by {csl}, your financial instincts are sound. "
                f"You possess the natural ability to convert modest earnings into growing assets and reliable liquid reserves. Family members "
                f"provide meaningful encouragement, and sudden financial dry spells will be brief and easily overcome."
            )
            narr_ta = (
                f"இரண்டாம் பாவக உப-அதிபதி {csl_ta} மூலம் உங்கள் ஜாதகத்தில் நிலையான பொருளாதார யோகம் சுட்டிக்காட்டப்படுகிறது. உழைப்பிற்கேற்ற வருமானம், "
                f"வங்கியில் சேமிப்பு உயர்வு மற்றும் அசையா சொத்துக்கள் சேரும் பாக்கியம் உண்டு. குடும்பத்தாரின் ஆதரவும் தகுந்த நேரத்தில் உங்களுக்கு பக்கபலமாக அமையும்."
            )
            take_en = "Channel your liquid surpluses into appreciating tangible assets like real estate or gold."
            take_ta = "உபரி பணத்தை வீண் செலவு செய்யாமல் நிலம், கட்டிடம் அல்லது தங்கத்தில் சேமித்து வைத்தால் பல மடங்கு பெருகும்."
        elif verdict == "delayed_fruition":
            sum_en = "Wealth builds through steady, patient compounding rather than quick windfalls."
            sum_ta = "பொருளாதார வளர்ச்சி ஆரம்பத்தில் நிதானமாக இருந்தாலும், கடின உழைப்பால் பிற்காலத்தில் பெரிய செல்வம் சேரும்."
            narr_en = (
                f"Your financial path requires patience in your early adulthood. Under {csl}, money may flow out as fast as it comes in during early phases. "
                f"However, financial discipline and systematic savings will turn the tide around your late 20s or 30s, culminating in dependable long-term security."
            )
            narr_ta = (
                f"இரண்டாம் பாவக அமைப்பில் {csl_ta} தொடர்பு காரணமாக, இளமைக்காலத்தில் வரவுக்கு மிஞ்சிய செலவுகள் அல்லது குடும்பச் சுமைகள் இருக்கலாம். "
                f"ஆனால் முறையான வரவு-செலவு திட்டமிடலும் பொறுமையும் இருந்தால், 30 வயதுக்கு மேல் உங்கள் நிதி நிலைமை அசுர வேகத்தில் முன்னேற்றம் அடையும்."
            )
            take_en = "Commit to automated monthly recurring savings and steer clear of speculative schemes."
            take_ta = "மாதாந்திர முறையான தொடர் சேமிப்பு திட்டங்களில் முதலீடு செய்து, விரைவு பண ஆசைகளை தவிர்ப்பது நலம்."
        else:
            sum_en = "Financial fluctuations require conservative budgeting and protective wealth barriers."
            sum_ta = "பண பரிவர்த்தனைகளிலும் குடும்ப நிதி விவகாரங்களிலும் மிகுந்த கவனமும் எச்சரிக்கையும் தேவை."
            narr_en = (
                f"The financial sub-lord highlights susceptibility to sudden family expenditures, impulsive lending, or disputed assets. "
                f"You should never sign personal financial guarantees for acquaintances or leave capital unprotected without proper documentation."
            )
            narr_ta = (
                f"இரண்டாம் பாவக உப-அதிபதி அமைப்பானது வீண் செலவுகள் மற்றும் கடன் விவகாரங்களில் எச்சரிக்கையுடன் இருக்க அறிவுறுத்துகிறது. "
                f"யாருக்கும் ஜாமீன் கையெழுத்து போடுவதையோ, ஆவணங்கள் இல்லாத கடன் கொடுப்பதையோ முற்றிலும் தவிர்க்க வேண்டும்."
            )
            take_en = "Keep separate emergency reserves in fixed deposits and never guarantee other people's loans."
            take_ta = "அவசர கால நிதிக்கு நிரந்தர வைப்பு நிதியில் பணம் ஒதுக்குங்கள்; மற்றவர்கள் கடனுக்கு உத்தரவாதமாக நிற்க வேண்டாம்."

    elif cusp == 5:
        if verdict == "strongly_promised":
            sum_en = "Gifted creative intelligence, fruitful investments, and joyful relationship with children."
            sum_ta = "சிறந்த படைப்பாற்றல் அறிவு, புத்திர பாக்கியம் மற்றும் பிள்ளைகளால் குடும்பத்திற்கு பெருமை சேரும்."
            narr_en = (
                f"Your chart reflects deep intellectual foresight and good fortune through creative or educational endeavors. "
                f"Sub-lord {csl} ensures that children bring warmth, pride, and happiness into your household. Your analytical instincts "
                f"in investments and strategic projects are naturally sharp."
            )
            narr_ta = (
                f"ஐந்தாம் பாவக உப-அதிபதி {csl_ta} வழியாக நுண்ணறிவும் புத்திர பாக்கியமும் மிகச் சிறப்பாக வாக்களிக்கப்பட்டுள்ளது. பிள்ளைகளின் படிப்பு "
                f"மற்றும் நற்பண்புகளால் குடும்பத்தின் பெருமை உயரும். கலை, இலக்கியம், ஆலோசனை அல்லது புத்தி கூர்மை சார்ந்த பணிகளில் அபார வெற்றி கிட்டும்."
            )
            take_en = "Cultivate your creative or analytical passions; they hold potential for supplemental prestige and income."
            take_ta = "உங்கள் தனித்திறன்களையும் அறிவு சார்ந்த திட்டங்களையும் தொடர்ந்து வளர்த்துக் கொள்ளுங்கள்."
        elif verdict == "delayed_fruition":
            sum_en = "Childbirth or speculative rewards materialize with delay and dedicated medical/spiritual care."
            sum_ta = "குழந்தை பாக்கியம் அல்லது முதலீடுகளில் ஆரம்ப தடைகளுக்குப் பின் நல்ல தீர்வு கிடைக்கும்."
            narr_en = (
                f"Matters concerning children or creative projects may experience some initial waiting period or medical interventions under {csl}. "
                f"Patience and modern guidance will yield success. Avoid emotional gambling in volatile stock trading."
            )
            narr_ta = (
                f"ஐந்தாம் பாவகத்தில் {csl_ta} அமைப்பால் குழந்தை பாக்கியத்தில் அல்லது முதலீடுகளில் ஆரம்பத்தில் காலதாமதம் ஏற்படலாம். "
                f"தகுந்த மருத்துவ வழிகாட்டுதலும், இறை வழிபாடும் மேற்கொள்ளும் போது நன்மக்கள் பாக்கியமும், அமைதியும் நிச்சயமாக கைகூடும்."
            )
            take_en = "Consult trustworthy specialists for fertility planning without anxiety; avoid day-trading risks."
            take_ta = "பதற்றமின்றி தகுந்த மருத்துவ ஆலோசனைகளை நாடுங்கள்; பங்குச்சந்தையில் அவசர முதலீடுகளை தவிர்க்கவும்."
        else:
            sum_en = "Progeny and high-risk investments demand heightened caution and deliberate preparation."
            sum_ta = "பிள்ளைகளின் உடல் நலம் மற்றும் யூக வணிக முதலீடுகளில் மிகுந்த விழிப்புணர்வு அவசியம்."
            narr_en = (
                f"The 5th sub-lord warns against speculative gambling, high-leverage trading, or excessive emotional turbulence in love affairs. "
                f"For family planning, timely professional medical checks and stress-free living will help navigate challenges."
            )
            narr_ta = (
                f"ஐந்தாம் பாவக தொடர்பு யூக வணிகம் (Speculation) மற்றும் தேவையற்ற காதல் விவகாரங்களில் நஷ்டத்தை தரக்கூடும் என்பதால் விழிப்புணர்வு தேவை. "
                f"பிள்ளைகளின் ஆரோக்கியத்தில் கூடுதல் கவனமும், முதலீடுகளில் பாதுகாப்பு முறைகளும் அவசியம்."
            )
            take_en = "Completely avoid speculative financial gambles; focus on secure guaranteed returns."
            take_ta = "அதிக லாபத்திற்கு ஆசைப்பட்டு பணத்தை முதலீடு செய்யாமல் அரசு சார்ந்த பாதுகாப்பான திட்டங்களில் சேமிக்கவும்."

    elif cusp == 7:
        if verdict == "strongly_promised":
            sum_en = "Harmonious marital union, supportive life partner, and fruitful social/business alliances."
            sum_ta = "அன்பும் பாசமும் நிறைந்த வாழ்க்கை துணை, மன மகிழ்ச்சியான இல்லறம் மற்றும் கூட்டாண்மையில் வெற்றி."
            narr_en = (
                f"Matrimony and meaningful partnerships are strongly blessed in your destiny. Ruled by {csl} linked with {star_lord}, "
                f"your spouse will bring companionship, emotional grounding, and mutual respect. Commercial alliances and contractual agreements "
                f"will flourish with fairness."
            )
            narr_ta = (
                f"ஏழாம் பாவக உப-அதிபதி {csl_ta} அமைப்பு நல்ல குணமும், குடும்பப் பாசமும் கொண்ட சிறந்த வாழ்க்கை துணையை உறுதி செய்கிறது. "
                f"இருவருக்கிடையே பரஸ்பர புரிதலும் அன்பும் நிலைத்து நிற்கும். சமூக உறவுகளிலும், கூட்டுத் தொழில்களிலும் நற்பெயர் கிட்டும்."
            )
            take_en = "Foster open and empathetic dialogue in marriage; your partner will be your most dependable counselor."
            take_ta = "வாழ்க்கைத் துணையுடன் வெளிப்படையான கருத்துப் பரிமாற்றங்களை மேற்கொள்ளுங்கள்; குடும்ப அமைதி தழைக்கும்."
        elif verdict == "delayed_fruition":
            sum_en = "Marriage settles after some delays, matching search, or later age maturity."
            sum_ta = "திருமண அமைப்பில் ஆரம்ப வரன் தேடுதலில் தாமதம் ஏற்பட்டாலும், உரிய காலத்தில் நல்ல துணை அமையும்."
            narr_en = (
                f"Marriage discussions may face initial delays, horoscope matching re-checks, or career-related postponements under {csl}. "
                f"Do not rush; the union that takes root after maturity will be stable, mature, and deeply grounded against life's storms."
            )
            narr_ta = (
                f"ஏழாம் பாவக உப-அதிபதி {csl_ta} காரணமாக திருமணப் பேச்சுகளில் ஆரம்பத்தில் தடைகளும் காலதாமதமும் ஏற்படலாம். "
                f"ஆனால் அவசரப்படாமல் நிதானமாக தேர்ந்தெடுக்கும் வரன், காலமெல்லாம் உங்கள் மேல் உண்மையான அன்புடன் துணை நிற்கும்."
            )
            take_en = "Do not compromise on core shared values under pressure; patience guarantees a harmonious partner."
            take_ta = "அவசரப்பட்டு சமரசம் செய்யாமல், குணநலன்களும் எண்ணங்களும் ஒத்துப்போகும் நல்ல வரனைத் தேர்ந்தெடுக்கவும்."
        else:
            sum_en = "Marital harmony demands active compromise, patience, and clear boundary management."
            sum_ta = "தாம்பத்திய உறவில் விட்டுக்கொடுத்து போவதும், ஈகோ இன்றி பேசி தீர்ப்பதும் குடும்ப அமைதிக்கு மிகவும் அவசியம்."
            narr_en = (
                f"The 7th sub-lord indicates periods of friction, differing expectations, or interference from external relations. "
                f"Clear emotional boundaries, avoiding hasty accusations, and prioritizing calm mutual respect will safeguard marital bliss."
            )
            narr_ta = (
                f"ஏழாம் பாவக அமைப்பில் மாற்றுக் கருத்துக்களும் வீண் பிடிவாதங்களும் எழ வாய்ப்புள்ளது. வெளி மனிதர்களின் தலையீட்டை அனுமதிக்காமல், "
                f"இருவரும் மனம் விட்டுப் பேசி சின்னச் சின்ன தவறுகளை மன்னித்து வாழ்வது திருமண வாழ்க்கையை மகிழ்ச்சியாக வைத்திருக்கும்."
            )
            take_en = "Never let workplace stress spill over into domestic conversations; practice active listening with your spouse."
            take_ta = "வேலைப்பளு கோபத்தை இல்லத்தில் காட்டாதீர்கள்; வாழ்க்கைத் துணையின் உணர்வுகளுக்கு முன்னுரிமை கொடுங்கள்."

    elif cusp == 10:
        if verdict == "strongly_promised":
            sum_en = "High professional status, steady promotions, executive authority, and respected public reputation."
            sum_ta = "உயர்ந்த உத்தியோகப் பதவி, சமூக கௌரவம், தொழில் முன்னேற்றம் மற்றும் அதிகார யோகம் உறுதியாக உண்டு."
            narr_en = (
                f"Your professional sphere is fortified with tremendous potential. With {csl} shaping your 10th house, you possess the work ethic, "
                f"strategic competence, and leadership authority that attract commendations and executive responsibilities. Whether in employment or business, "
                f"your name will carry weight and credibility."
            )
            narr_ta = (
                f"பத்தாம் பாவக உப-அதிபதி {csl_ta} உங்கள் ஜாதகத்தில் சிறந்த தொழில் மேன்மையை வாக்குறுதி அளிக்கிறது. செய்யும் தொழிலில் அல்லது பார்க்கும் வேலையில் "
                f"முன்னேற்றம், மேலதிகாரிகளின் பாராட்டு, பதவி உயர்வுகள் மற்றும் சமூகத்தில் நல்ல பெயர் உங்களுக்கு நிச்சயம் வந்து சேரும்."
            )
            take_en = "Step forward for higher responsibilities and continuous skill upgrades; promotions will follow your competence."
            take_ta = "நிர்வாகப் பொறுப்புகளை தயங்காமல் ஏற்கவும்; புதிய தொழில் நுட்பங்களையும் திறன்களையும் வளர்த்துக்கொண்டால் வெற்றி நிச்சயம்."
        elif verdict == "delayed_fruition":
            sum_en = "Career breakthrough consolidates after establishing foundational experience and overcoming early trials."
            sum_ta = "தொழில் வாழ்வில் ஆரம்பத்தில் அதிக உழைப்பும் குறைந்த அங்கீகாரமும் இருந்தாலும், பின்னாளில் உன்னத நிலையை அடைவீர்கள்."
            narr_en = (
                f"Career success does not arrive on an effortless silver platter, but it builds into an unshakeable fortress under {csl}. "
                f"Initial jobs may feel underpaid or demanding. However, every ounce of effort builds irreplaceable expertise, triggering "
                f"major professional breakthroughs in your 30s and 40s."
            )
            narr_ta = (
                f"பத்தாம் பாவக உப-அதிபதி {csl_ta} அமைப்பால் ஆரம்பத்தில் உங்கள் திறமைக்கேற்ற பதவி உயர்வில் தாமதம் இருக்கலாம். ஆனால் நீங்கள் பெறும் "
                f"அனுபவங்களும் கடுமையான உழைப்பும் உங்களை பிற்காலத்தில் யாராலும் அசைக்க முடியாத ஒரு வல்லுநராகவும் தலைவராகவும் உயர்த்தும்."
            )
            take_en = "Remain loyal to mastering your craft without getting discouraged by short-term recognition delays."
            take_ta = "உடனடி பலனை எதிர்பார்க்காமல் உங்கள் துறையில் ஆழ்ந்த நிபுணத்துவத்தை வளர்த்துக் கொள்ளுங்கள்; வெற்றி தானாக தேடி வரும்."
        else:
            sum_en = "Career stability requires adaptable skills and careful navigation around organizational politics."
            sum_ta = "பணியிடத்தில் அதிகாரிகளுடன் வீண் விவாதங்களை தவிர்த்து, மாற்றுத் தொழில் வழிகளையும் தயாராக வைத்திருக்க வேண்டும்."
            narr_en = (
                f"The 10th sub-lord warns of workplace restructuring, abrupt shifts in management, or interpersonal friction with superiors. "
                f"Focus strictly on high-quality deliverables, keep official documentation impeccable, and avoid engaging in office gossip or factionalism."
            )
            narr_ta = (
                f"பத்தாம் பாவக அமைப்பு பணியிடத்தில் திடீர் மாற்றங்கள் அல்லது மேலிடத்துடன் கருத்து வேறுபாடுகளை ஏற்படுத்தக்கூடும். அலுவலக அரசியலில் "
                f"ஈடுபடாமல், உங்கள் பணியை துல்லியமாகவும் நேர்மையாகவும் செய்து வந்தால் எவ்வித சிக்கலும் இன்றி தற்காத்துக் கொள்ளலாம்."
            )
            take_en = "Maintain an updated resume and emergency savings; steer clear of office power struggles."
            take_ta = "பணியிடத்தில் வீண் வாக்குவாதங்களை தவிர்த்து, உங்கள் பொறுப்புகளில் மட்டும் கவனம் செலுத்துங்கள்."

    else: # cusp 11
        if verdict == "strongly_promised":
            sum_en = "Fulfillment of key lifelong dreams, lucrative windfalls, and high-value social alliances."
            sum_ta = "எண்ணிய காரியங்கள் இனிதே ஈடேறும்; தொடர் லாபங்கள் மற்றும் நண்பர்களால் பெரும் ஆதாயம் உண்டு."
            narr_en = (
                f"The 11th cusp is the crown of fulfillment in KP astrology. With {csl} favorably positioned, your core ambitions are destined "
                f"to bear fruit. Beneficial mentors, prosperous networks, and multiple income channels will step forward at critical junctures "
                f"to lift you toward your dreams."
            )
            narr_ta = (
                f"பதினொன்றாம் பாவக உப-அதிபதி {csl_ta} உங்கள் ஜாதகத்தில் லாப ஸ்தானத்தை வலுப்படுத்துகிறது. நீங்கள் திட்டமிடும் சுப காரியங்களும், "
                f"வாழ்க்கை இலக்குகளும் ஒவ்வொன்றாக நிறைவேறும். நல்ல நண்பர்கள் மற்றும் நலம் விரும்பிகளின் வழியே எதிர்பார்த்த நன்மைகள் கைகூடும்."
            )
            take_en = "Maintain your network of respected colleagues and never hesitate to articulate ambitious life aspirations."
            take_ta = "நற்பண்புகள் கொண்ட நண்பர்களுடனான தொடர்பை பேணி, உங்கள் இலக்குகளை உறுதியுடன் தொடர்ந்து பின்தொடருங்கள்."
        elif verdict == "delayed_fruition":
            sum_en = "Major ambitions fulfill sequentially after steady groundwork and structured effort."
            sum_ta = "நீண்ட நாள் ஆசைகள் சற்று நிதானமாகவே நிறைவேறும்; முறையான திட்டமிடுதல் பெரும் வெற்றியைத் தரும்."
            narr_en = (
                f"Your desires are not denied, but they follow a structured timetable under {csl}. Projects take longer to blossom than initially "
                f"forecast, but once established, their rewards are sustainable and immune to abrupt setbacks."
            )
            narr_ta = (
                f"பதினொன்றாம் பாவக அமைப்பில் {csl_ta} தொடர்பு காரணமாக உங்கள் திட்டங்கள் சற்று தாமதமாகவே முடிவுக்கு வரும். இருப்பினும் "
                f"கிடைக்கும் வெற்றி மிக உறுதியானதாகவும் நிரந்தரமானதாகவும் இருக்கும் என்பதால் பொறுமையுடன் உழைப்பது அவசியம்."
            )
            take_en = "Break big lifelong goals into measurable quarterly milestones and celebrate incremental wins."
            take_ta = "பெரிய இலக்குகளை சிறு சிறு படிகளாக பிரித்து, நிதானமான முன்னேற்றத்தை நோக்கி நடைபோடுங்கள்."
        else:
            sum_en = "Expectations must be managed realistically; guard against unfulfilled promises from peers."
            sum_ta = "நண்பர்கள் அல்லது கூட்டாளிகளை குருட்டுத்தனமாக நம்பாமல், எதிர்பார்ப்புகளை நிதானமாக வைத்துக்கொள்ள வேண்டும்."
            narr_en = (
                f"The 11th sub-lord warns that relying on verbal promises from acquaintances or overestimating immediate profits can lead to disappointments. "
                f"Base all business agreements on formal written contracts rather than informal camaraderie."
            )
            narr_ta = (
                f"பதினொன்றாம் பாவக அமைப்பு நண்பர்கள் அல்லது வெளி நபர்கள் மூலம் ஏமாற்றங்கள் ஏற்பட வாய்ப்புள்ளதை காட்டுகிறது. "
                f"பண விவகாரங்களில் எவரையும் வாய்மொழியாக நம்பாமல், எழுத்துப்பூர்வமான ஒப்பந்தங்களை மட்டும் நம்பி செயல்படுவது நல்லது."
            )
            take_en = "Never lend money based on informal social ties; keep financial expectations grounded in verified reality."
            take_ta = "நட்பு ரீதியான கடன் கொடுப்பதையோ அல்லது வாய்மொழி ஒப்பந்தங்களையோ தவிர்ப்பது உங்கள் முதலீடுகளை பாதுகாக்கும்."

    return sum_en, sum_ta, narr_en, narr_ta, take_en, take_ta


def evaluate_natal_event_promise(kp_chart: Any) -> NatalPromiseSection:
    """Evaluates all 6 primary cuspal sub-lords and synthesizes overall life promise."""
    items: List[CuspalPromiseItem] = []
    strong_cnt = 0
    delayed_cnt = 0
    caution_cnt = 0

    cusps_data = getattr(kp_chart, "cusps", [])
    cusp_map: Dict[int, Any] = {}
    for c in cusps_data:
        h = getattr(c, "house", None)
        if h is not None:
            cusp_map[int(h)] = c

    for cusp_num in PRIMARY_PROMISE_CUSPS:
        domain_info = CUSP_DOMAINS[cusp_num]
        c_obj = cusp_map.get(cusp_num)

        if c_obj:
            csl = getattr(c_obj, "sub_lord", "Jupiter")
            star_l = getattr(c_obj, "star_lord", "Sun")
            ssl = getattr(c_obj, "sub_sub_lord", "Venus")
        else:
            csl = "Jupiter"
            star_l = "Sun"
            ssl = "Venus"

        signified = _get_planet_signified_houses(csl, kp_chart)
        supp = sorted(list(set(signified) & CUSP_SUPPORTIVE_HOUSES.get(cusp_num, set())))
        chal = sorted(list(set(signified) & CUSP_CHALLENGING_HOUSES.get(cusp_num, set())))

        verdict_key, v_label_en, v_label_ta = _evaluate_cusp_verdict(cusp_num, csl, signified)

        if verdict_key == "strongly_promised":
            strong_cnt += 1
        elif verdict_key == "delayed_fruition":
            delayed_cnt += 1
        else:
            caution_cnt += 1

        sum_en, sum_ta, narr_en, narr_ta, take_en, take_ta = _generate_plain_narrative(
            cusp=cusp_num,
            csl=csl,
            star_lord=star_l,
            verdict=verdict_key,
            supportive_matched=supp,
            challenging_matched=chal,
        )

        items.append(
            CuspalPromiseItem(
                cusp=cusp_num,
                domain_en=domain_info["domain_en"],
                domain_ta=domain_info["domain_ta"],
                cusp_sub_lord=csl,
                star_lord=star_l,
                sub_sub_lord=ssl,
                signified_houses=signified,
                supporting_houses=supp,
                challenging_houses=chal,
                verdict=verdict_key,
                verdict_label_en=v_label_en,
                verdict_label_ta=v_label_ta,
                summary_en=sum_en,
                summary_ta=sum_ta,
                plain_narrative_en=narr_en,
                plain_narrative_ta=narr_ta,
                practical_takeaway_en=take_en,
                practical_takeaway_ta=take_ta,
            )
        )

    # Generate overarching natal synthesis narrative
    if strong_cnt >= 4:
        syn_en = (
            f"Your astrological blueprint possesses exceptional foundational strength with {strong_cnt} out of 6 major life pillars "
            f"strongly promised. Career elevation, wealth accumulation, and life aspirations are anchored on rock-solid planetary foundations. "
            f"With disciplined effort, major milestones will materialize with enduring success."
        )
        syn_ta = (
            f"உங்கள் ஜாதகத்தில் 6 முக்கிய பாவகங்களில் {strong_cnt} பாவகங்கள் உறுதியான யோக வாக்குறுதியைப் பெற்றுள்ளன. "
            f"தொழில் உயர்வு, தன சேர்க்கை மற்றும் ஆசைகள் நிறைவேறும் பாக்கியம் மிகச் சிறப்பாக அமைந்துள்ளது. நற்சிந்தனையும் விடாமுயற்சியும் "
            f"உங்களை சமூகத்தில் ஒரு உன்னதமான இடத்திற்கு கொண்டு செல்லும்."
        )
    elif strong_cnt + delayed_cnt >= 5:
        syn_en = (
            f"Your chart reflects a classic 'Progress Through Perseverance' life pattern. While some life milestones involve patience "
            f"and initial trials ({delayed_cnt} delayed fruition indicators), the eventual outcome is robust and fruitful. "
            f"You will achieve lasting stability in your middle and mature years."
        )
        syn_ta = (
            f"உங்கள் ஜாதக அமைப்பானது 'விடாமுயற்சியால் படிப்படியான முன்னேற்றம்' தரும் உன்னத அமைப்பாகும். சில முக்கிய வாழ்க்கை காரியங்களில் "
            f"ஆரம்பத்தில் பொறுமையும் தடைகளும் இருந்தாலும் ({delayed_cnt} தாமதப் பலன்கள்), இறுதியில் வெற்றி உங்களையே வந்தடையும். "
            f"நடுத்தர வயதில் அசைக்க முடியாத திடமான நிலைமையை அடைவீர்கள்."
        )
    else:
        syn_en = (
            f"Your chart calls for strategic self-management and mindful decision-making. Certain life areas require proactive caution "
            f"({caution_cnt} caution areas), but through ethical discipline, proper risk-hedging, and perseverance, challenges can be turned "
            f"into foundational life lessons."
        )
        syn_ta = (
            f"உங்கள் ஜாதகமானது விழிப்புணர்வுடனும் திட்டமிடலுடனும் வாழ வேண்டிய அவசியத்தை உணர்த்துகிறது. சில வாழ்க்கை துறைகளில் விழிப்புணர்வு "
            f"தேவைப்பட்டாலும் ({caution_cnt} எச்சரிக்கை அம்சங்கள்), நேர்மறையான எண்ணங்களுடனும், முறையான நிதி மற்றும் சுகாதார ஒழுக்கத்துடனும் "
            f"செயல்பட்டால் அனைத்து சவால்களையும் வெற்றியாக மாற்றலாம்."
        )

    return NatalPromiseSection(
        overall_synthesis_en=syn_en,
        overall_synthesis_ta=syn_ta,
        items=items,
        strong_promises_count=strong_cnt,
        delayed_count=delayed_cnt,
        caution_count=caution_cnt,
    )
