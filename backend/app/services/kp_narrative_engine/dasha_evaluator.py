"""Running Dasha-Bhukti-Antara Evaluator for KP Predictive Narrative Engine.

Breaks down currently running Mahadasha, Bhukti, and Antara lords, their star lords,
sub-lords, and analyzes their real-world impact across Career, Finance, Relationships, and Health.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.kp_narrative import (
    DashaPeriodDetail,
    RunningDashaImpactSection,
)
from app.services.kp_engine.dasha import (
    current_periods,
    format_days,
)
from .constants import (
    PLANET_NAMES_TA,
)
from .natal_evaluator import _get_planet_signified_houses


def _format_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def evaluate_running_dasha_impact(
    kp_chart: Any,
    birth_dt: datetime,
    target_dt: datetime,
) -> RunningDashaImpactSection:
    """Evaluates currently running Dasha-Bhukti-Antara hierarchy and produces plain-language impact analysis."""
    moon_lon = 0.0
    planets_dict = getattr(kp_chart, "planets", {})
    if isinstance(planets_dict, dict) and "Moon" in planets_dict:
        m_obj = planets_dict["Moon"]
        moon_lon = getattr(m_obj, "longitude", 0.0)
    elif hasattr(kp_chart, "planet_lon") and isinstance(kp_chart.planet_lon, dict):
        moon_lon = kp_chart.planet_lon.get("Moon", 0.0)

    # 1. Resolve current active periods up to depth 3 (Mahadasha, Bhukti, Antara)
    active_periods = current_periods(moon_lon, birth_dt, target_dt, depth=3)
    p_md = active_periods.get(1)
    p_ad = active_periods.get(2)
    p_pd = active_periods.get(3)

    def _make_detail(p: Any, lvl: int, name_en: str, name_ta: str) -> DashaPeriodDetail:
        lord = getattr(p, "lord", "Jupiter")
        s_dt = birth_dt + timedelta(days=p.start_days)
        e_dt = birth_dt + timedelta(days=p.end_days)
        dur_str = format_days(p.duration_days)

        # Retrieve star_lord and sub_lord of this planet from kp_chart
        star_l = "Sun"
        sub_l = "Venus"
        if isinstance(planets_dict, dict) and lord in planets_dict:
            pl_info = planets_dict[lord]
            star_l = getattr(pl_info, "star_lord", "Sun")
            sub_l = getattr(pl_info, "sub_lord", "Venus")

        sig_houses = _get_planet_signified_houses(lord, kp_chart)

        return DashaPeriodDetail(
            level=lvl,
            level_name_en=name_en,
            level_name_ta=name_ta,
            lord=lord,
            lord_ta=PLANET_NAMES_TA.get(lord, lord),
            star_lord=star_l,
            star_lord_ta=PLANET_NAMES_TA.get(star_l, star_l),
            sub_lord=sub_l,
            sub_lord_ta=PLANET_NAMES_TA.get(sub_l, sub_l),
            start_date=_format_date(s_dt),
            end_date=_format_date(e_dt),
            duration_formatted=dur_str,
            signified_houses=sig_houses,
        )

    md_detail = _make_detail(p_md, 1, "Mahadasha", "மகா திசை")
    ad_detail = _make_detail(p_ad, 2, "Bhukti (Antardasha)", "புக்தி")
    pd_detail = _make_detail(p_pd, 3, "Antara (Pratyantardasha)", "அந்தரம்")

    md_lord = md_detail.lord
    ad_lord = ad_detail.lord
    pd_lord = pd_detail.lord

    md_ta = PLANET_NAMES_TA.get(md_lord, md_lord)
    ad_ta = PLANET_NAMES_TA.get(ad_lord, ad_lord)
    pd_ta = PLANET_NAMES_TA.get(pd_lord, pd_lord)

    all_sig_houses = set(md_detail.signified_houses) | set(ad_detail.signified_houses) | set(pd_detail.signified_houses)

    # Calculate overall favorability score (0-100)
    fav_houses = {1, 2, 3, 5, 9, 10, 11}
    unfav_houses = {6, 8, 12}
    fav_count = len(all_sig_houses & fav_houses)
    unfav_count = len(all_sig_houses & unfav_houses)
    score = max(20, min(95, 50 + (fav_count * 8) - (unfav_count * 10)))

    # Phase title
    phase_title_en = f"{md_lord} Mahadasha – {ad_lord} Bhukti – {pd_lord} Antara"
    phase_title_ta = f"{md_ta} மகா திசை – {ad_ta} புக்தி – {pd_ta} அந்தரம்"

    # Phase Theme
    if score >= 70:
        theme_en = (
            f"You are navigating an active expansion phase where your efforts meet supportive circumstances. "
            f"Under {md_lord} and {ad_lord}, doors open for progressive development and long-term positioning."
        )
        theme_ta = (
            f"தற்போது உங்களுக்கு முன்னேற்றகரமான மற்றும் வளர்ச்சி தரும் காலகட்டம் நடைபெறுகிறது. "
            f"{md_ta} மற்றும் {ad_ta} கிரக அமைப்புகள் நீங்கள் எடுக்கும் முயற்சிகளுக்கு உரிய நற்பலன்களை பெற்றுத்தரும்."
        )
    elif score >= 50:
        theme_en = (
            f"A transitional consolidation period requiring systematic effort and balanced priorities. "
            f"Under {md_lord}-{ad_lord}, steady persistence is rewarded while hasty decisions should be kept in check."
        )
        theme_ta = (
            f"தற்போது நீங்கள் நிதானமாக அடித்தளம் அமைக்க வேண்டிய காலகட்டத்தில் உள்ளீர்கள். "
            f"{md_ta}-{ad_ta} அமைப்பால் கடின உழைப்புக்கு ஏற்ற பலன்கள் கிடைக்கும்; அவசர முடிவுகளை தவிர்ப்பது நல்லது."
        )
    else:
        theme_en = (
            f"A reflective testing period asking for prudence, emotional calm, and protective boundary management. "
            f"Avoid over-extending finances or engaging in avoidable conflicts during this {ad_lord} Bhukti."
        )
        theme_ta = (
            f"தற்போது எச்சரிக்கையுடனும் கவனத்துடனும் நகர்த்த வேண்டிய காலமாகும். "
            f"நிதி விவகாரங்களிலும் உறவுகளிலும் வீண் வாக்குவாதங்களை தவிர்த்து, விழிப்புணர்வுடன் செயல்பட வேண்டும்."
        )

    # 1. Career Impact
    career_sig = all_sig_houses & {2, 6, 10, 11}
    career_chal = all_sig_houses & {5, 8, 12}
    if career_sig and not career_chal:
        c_en = (
            f"Strong positive career momentum. The current {ad_lord} Bhukti enhances your standing at work, "
            f"making this a prime window to request promotions, take on strategic initiatives, or close lucrative business deals."
        )
        c_ta = (
            f"தொழில் மற்றும் உத்தியோகத்தில் சிறப்பான வளர்ச்சி உண்டாகும். {ad_ta} புக்தி அமைப்பானது பணியிடத்தில் மேலதிகாரிகளின் பாராட்டு, "
            f"பதவி உயர்வு மற்றும் புதிய வர்த்தக வாய்ப்புகளை பெற்றுத்தரும் பொன்னான நேரமாகும்."
        )
    elif career_sig and career_chal:
        c_en = (
            f"High activity with heavy workloads. You will achieve commendable career breakthroughs, but they will come with "
            f"stiff deadlines or organizational restructuring. Stay organized and avoid taking disagreements personally."
        )
        c_ta = (
            f"தொழிலில் அதிக பணிச்சுமையும் அலைச்சலும் இருக்கும். உழைப்புக்குரிய அங்கீகாரம் படிப்படியாக கிடைத்தாலும், "
            f"பணியிடத்து வீண் சர்ச்சைகளில் தலையிடாமல் உங்கள் வேலையில் மட்டும் கவனமாக இருப்பது நல்லது."
        )
    else:
        c_en = (
            f"Maintain steady performance without making radical or impulsive career leaps. "
            f"Focus on upskilling and consolidating your current role rather than quitting abruptly."
        )
        c_ta = (
            f"தொழிலில் அவசர மாற்றங்களை செய்யாமல் உள்ள வேலையிலேயே நிலைத்து நிற்பது நல்லது. "
            f"புதிய தொழில் நுட்பங்களையும் திறமைகளையும் கற்றுக்கொண்டு உங்களை தயார்படுத்திக் கொள்ளுங்கள்."
        )

    # 2. Finance Impact
    fin_sig = all_sig_houses & {2, 6, 11}
    fin_chal = all_sig_houses & {5, 8, 12}
    if fin_sig and not fin_chal:
        f_en = (
            f"Healthy cash liquidity and steady capital growth. Incoming receivables and investment gains remain stable, "
            f"giving you room to build robust long-term emergency reserves or acquire appreciating assets."
        )
        f_ta = (
            f"பணப்புழக்கம் திருப்திகரமாக இருக்கும். எதிர்பார்த்த பண வரவுகள் தடையின்றி கைக்கு வந்து சேரும். "
            f"சேமிப்பை உயர்த்தவும், நிலம் அல்லது தங்கத்தில் முதலீடு செய்யவும் இது மிகச் சிறந்த காலகட்டம்."
        )
    elif fin_sig and fin_chal:
        f_en = (
            f"Good earnings offset by elevated family or domestic expenditures. Money will flow in steadily, but prompt "
            f"outflows may tempt you to overspend. Stick rigidly to your monthly budget and postpone luxury purchases."
        )
        f_ta = (
            f"வரவுக்கு ஏற்ற செலவுகள் வரிசையாக வந்து நிற்கும். பண வரவு இருந்தாலும் குடும்ப சுபநிகழ்ச்சிகள் அல்லது சுபச் செலவுகள் "
            f"ஏற்படலாம். ஆடம்பரச் செலவுகளை தவிர்த்து வரவுக்கேற்ற திட்டமிடலுடன் இருப்பது நிதி ஸ்திரத்தன்மையை காக்கும்."
        )
    else:
        f_en = (
            f"Exercise strict financial caution. Avoid speculative stock bets, unauthorized lending, or making high-stakes purchases. "
            f"Focus strictly on preserving your existing capital."
        )
        f_ta = (
            f"நிதி விவகாரங்களில் மிகுந்த விழிப்புணர்வு தேவை. யூக வணிகம், பிறருக்கு கடன் கொடுப்பது அல்லது புதிய கடன் வாங்குவதை "
            f"தவிர்த்து, கையில் உள்ள பணத்தை பாதுகாப்பதே இப்போதைய முக்கிய கடமையாகும்."
        )

    # 3. Relationship Impact
    rel_sig = all_sig_houses & {2, 7, 11}
    rel_chal = all_sig_houses & {1, 6, 10, 12}
    if rel_sig and not rel_chal:
        r_en = (
            f"Warm domestic harmony and emotional fulfillment. Your relationships with your spouse, family members, and friends "
            f"are supportive. For unmarried natives, this running period provides pleasant matrimonial talks and meaningful bonding."
        )
        r_ta = (
            f"குடும்பத்தில் மகிழ்ச்சியும் அன்பும் தழைக்கும். வாழ்க்கைத் துணையுடன் பரஸ்பர புரிதலும் அமைதியும் நிலவும். "
            f"திருமணம் ஆகாதவர்களுக்கு நல்ல வரன் பேச்சுகள் முடிவாகி சுபகாரியங்கள் கைகூடும் இனிய நேரமாகும்."
        )
    elif rel_sig and rel_chal:
        r_en = (
            f"Relationships are active but require patient communication. Minor ego clashes or differing opinions on family expenses "
            f"may surface. Approach discussions with compassion and avoid letting third-party relatives dictate terms."
        )
        r_ta = (
            f"குடும்ப விவகாரங்களில் சிறு சிறு கருத்து வேறுபாடுகள் தோன்றலாம். ஈகோ பார்க்காமல் மனம் விட்டுப் பேசுவதும், "
            f"வெளி நபர்களின் பேச்சைக் கேட்டு வாழ்க்கைத் துணையை சந்தேகப்படாமல் இருப்பதும் குடும்ப அமைதியை நிலைநாட்டும்."
        )
    else:
        r_en = (
            f"Guard against misunderstandings. Give your partner breathing space, listen attentively without defensive reactions, "
            f"and avoid making permanent relationship decisions during temporary emotional arguments."
        )
        r_ta = (
            f"உறவுகளில் பொறுமையும் நிதானமும் மிக அவசியம். அவசரப்பட்டு வார்த்தைகளை விடாமல், "
            f"வாழ்க்கைத் துணையின் உணர்வுகளை மதித்து நடப்பது தேவையற்ற விரிசல்களைத் தவிர்க்கும்."
        )

    # 4. Health Impact
    health_chal = all_sig_houses & {6, 8, 12}
    if not health_chal:
        h_en = (
            f"Strong physical stamina and mental equilibrium. Energy levels are buoyant, allowing you to take on demanding tasks "
            f"with enthusiasm. Keep up daily physical fitness to sustain this rhythm."
        )
        h_ta = (
            f"உடல் நலம் சிறந்து விளங்கும்; மன அமைதியும் உற்சாகமும் கூடும். நாள்பட்ட உபாதைகள் விலகி உடல் புத்துணர்ச்சி பெறும். "
            f"முறையான உடற்பயிற்சியும் தியானமும் இந்த நற்பலனை மேலும் அதிகரிக்கும்."
        )
    elif len(health_chal) == 1:
        h_en = (
            f"Moderate fatigue from mental exertion or disrupted sleep schedules. While no major illnesses are indicated, "
            f"taking regular screen breaks and staying hydrated will preserve your vitality."
        )
        h_ta = (
            f"அதிக வேலை காரணமாக கண் எரிச்சல், தலைவலி அல்லது தூக்கமின்மை ஏற்படலாம். "
            f"நேரத்திற்கு உணவு உட்கொள்வதும், போதுமான தண்ணீர் குடிப்பதும் நலம் பயக்கும்."
        )
    else:
        h_en = (
            f"Prioritize health proactively. Do not ignore digestive discomfort, joint aches, or chronic stress. "
            f"Follow medical instructions promptly and avoid irregular late-night habits."
        )
        h_ta = (
            f"உடல் நலத்தில் கூடுதல் கவனம் தேவை. அஜீரணம், சோர்வு அல்லது மன அழுத்தம் இருந்தால் அலட்சியம் செய்யாமல் மருத்துவ பரிசோதனை செய்துகொள்ளவும். "
            f"இரவு நேர விழிப்பு மற்றும் எண்ணெய் உணவுகளை தவிர்க்கவும்."
        )

    return RunningDashaImpactSection(
        mahadasha=md_detail,
        bhukti=ad_detail,
        antara=pd_detail,
        phase_title_en=phase_title_en,
        phase_title_ta=phase_title_ta,
        phase_theme_en=theme_en,
        phase_theme_ta=theme_ta,
        career_impact_en=c_en,
        career_impact_ta=c_ta,
        finance_impact_en=f_en,
        finance_impact_ta=f_ta,
        relationship_impact_en=r_en,
        relationship_impact_ta=r_ta,
        health_impact_en=h_en,
        health_impact_ta=h_ta,
        favorable_score=score,
    )
