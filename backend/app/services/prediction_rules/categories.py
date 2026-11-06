"""Prediction Categories Registry.

Defines the 8 classical and modern life categories with groups, subcategories,
Tamil translations, and metadata.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SubcategoryItem(BaseModel):
    slug: str
    name_en: str
    name_ta: str
    description_en: str
    description_ta: str


class CategoryGroup(BaseModel):
    group_code: str
    group_name_en: str
    group_name_ta: str
    display_order: int
    subcategories: List[SubcategoryItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Canonical Categories Registry (8 Groups, 67 Subcategories)
# ---------------------------------------------------------------------------

PREDICTION_CATEGORY_GROUPS: List[CategoryGroup] = [
    CategoryGroup(
        group_code="marriage_relationships",
        group_name_en="Marriage & Relationships",
        group_name_ta="திருமணம் மற்றும் உறவுகள்",
        display_order=1,
        subcategories=[
            SubcategoryItem(
                slug="marriage_prospects",
                name_en="Marriage Prospects",
                name_ta="திருமண வாய்ப்புகள்",
                description_en="General promise and nature of marriage in the horoscope.",
                description_ta="ஜாதகத்தில் திருமண பாக்கியம் மற்றும் அமைவு பற்றிய பொதுவான விதிகள்.",
            ),
            SubcategoryItem(
                slug="marriage_timing",
                name_en="Marriage Timing",
                name_ta="திருமண கால நிர்ணயம்",
                description_en="Astrological timing indicators and Dasa-Bhukti influences for marriage.",
                description_ta="திருமணம் கைகூடும் காலம் மற்றும் தசா-புக்தி அமைப்புகள்.",
            ),
            SubcategoryItem(
                slug="first_marriage",
                name_en="First Marriage",
                name_ta="முதல் திருமணம்",
                description_en="Specific indicators governing the primary marriage union.",
                description_ta="முதல் திருமண பந்தம் மற்றும் அதன் இயல்புகள்.",
            ),
            SubcategoryItem(
                slug="second_marriage",
                name_en="Second Marriage",
                name_ta="இரண்டாம் திருமணம்",
                description_en="Indicators of multiple unions or remarriage from 2nd/8th/7th/11th houses.",
                description_ta="இரண்டாம் திருமணம் மற்றும் மறுமணத்திற்கான பாரம்பரிய ஜோதிட விதிகள்.",
            ),
            SubcategoryItem(
                slug="delayed_marriage",
                name_en="Delayed Marriage",
                name_ta="திருமணத் தடை மற்றும் காலதாமதம்",
                description_en="Saturn, Sun, or nodal afflictions causing delayed marital timing.",
                description_ta="சனி, சூரியன், ராகு-கேது தாக்கங்களால் ஏற்படும் தாமத திருமண யோகங்கள்.",
            ),
            SubcategoryItem(
                slug="love_marriage",
                name_en="Love Marriage",
                name_ta="காதல் திருமணம்",
                description_en="5th and 7th house lord connections, Venus-Mars or Rahu influences.",
                description_ta="5 மற்றும் 7-ஆம் அதிபதிகள் தொடர்பு, சுக்கிரன்-செவ்வாய், ராகு சேர்க்கைகள்.",
            ),
            SubcategoryItem(
                slug="arranged_marriage",
                name_en="Arranged Marriage",
                name_ta="பெரியோர்களால் நிச்சயிக்கப்பட்ட திருமணம்",
                description_en="Traditional arranged marriage alignments involving 2nd, 9th, and 7th lords.",
                description_ta="குடும்பத்தினரால் பேசி முடிக்கப்படும் திருமணத்திற்கான கிரக நிலைகள்.",
            ),
            SubcategoryItem(
                slug="spouse_characteristics",
                name_en="Spouse Characteristics",
                name_ta="வாழ்க்கைத் துணையின் குணநலன்கள்",
                description_en="7th house, 7th lord, Venus, and Navamsa D9 indicators of spouse's persona.",
                description_ta="7-ஆம் பாவம், நவாம்ச லக்னம் மூலம் துணையின் குணம் மற்றும் தோற்றம்.",
            ),
            SubcategoryItem(
                slug="relationship_compatibility",
                name_en="Relationship Compatibility",
                name_ta="உறவுப் பொருத்தம்",
                description_en="Interplanetary harmony, mutual trines, and synastry foundations.",
                description_ta="தம்பதியர் இடையே பரஸ்பர இணக்கம் மற்றும் பொருத்தம்.",
            ),
            SubcategoryItem(
                slug="marital_harmony",
                name_en="Marital Harmony",
                name_ta="தாம்பத்திய ஒற்றுமை",
                description_en="Factors promoting domestic peace, emotional closeness, and mutual respect.",
                description_ta="குடும்ப அமைதி, மகிழ்ச்சி மற்றும் மனஒற்றுமைக்கான விதிகள்.",
            ),
            SubcategoryItem(
                slug="separation_divorce",
                name_en="Separation & Divorce Indicators",
                name_ta="பிரிவினை மற்றும் முறிவு அறிகுறிகள்",
                description_en="Afflictions to 7th/8th/12th houses, Upapada Lagna, and 6th lord ties.",
                description_ta="7, 8, 12-ஆம் பாவ பாதிப்புகள் மற்றும் மனக்கசப்புக்கான காரணிகள்.",
            ),
            SubcategoryItem(
                slug="reconciliation_indicators",
                name_en="Reconciliation Indicators",
                name_ta="மீண்டும் இணைதல் அறிகுறிகள்",
                description_en="Benefic aspects from Jupiter or Venus facilitating dispute resolution.",
                description_ta="குருவின் சுபப் பார்வை மூலம் கருத்து வேறுபாடுகள் நீங்கி இணையும் யோகம்.",
            ),
            SubcategoryItem(
                slug="multiple_marriages",
                name_en="Multiple Marriage Indicators",
                name_ta="பல திருமண யோகம்",
                description_en="Dual signs on 7th cusp or multiple planets influencing 7th/2nd/11th.",
                description_ta="உபய ராசிகள் 7-ல் அமைதல் மற்றும் பல கிரக தாக்கங்கள்.",
            ),
        ],
    ),
    CategoryGroup(
        group_code="career_profession",
        group_name_en="Career & Profession",
        group_name_ta="தொழில் மற்றும் உத்தியோகம்",
        display_order=2,
        subcategories=[
            SubcategoryItem(
                slug="job_prospects",
                name_en="Job Prospects",
                name_ta="வேலை வாய்ப்புகள்",
                description_en="General employment promise, 6th and 10th house strength.",
                description_ta="உத்தியோக யோகம் மற்றும் வேலை வாய்ப்புகள்.",
            ),
            SubcategoryItem(
                slug="government_employment",
                name_en="Government Employment",
                name_ta="அரசுப் பணி யோகம்",
                description_en="Sun, Mars, Jupiter, and 10th lord associations with 1st or 9th house.",
                description_ta="சூரியன், செவ்வாய் பலம் மற்றும் அரசு உத்தியோக யோகங்கள்.",
            ),
            SubcategoryItem(
                slug="private_employment",
                name_en="Private Employment",
                name_ta="தனியார் துறை வேலைவாய்ப்பு",
                description_en="Corporate, technical, and service sector indicators via Saturn and Mercury.",
                description_ta="தனியார் துறை மற்றும் தகவல் தொழில்நுட்ப உத்தியோக அமைப்புகள்.",
            ),
            SubcategoryItem(
                slug="business_entrepreneurship",
                name_en="Business & Entrepreneurship",
                name_ta="சுயதொழில் மற்றும் வணிகம்",
                description_en="3rd, 7th, 10th, and 11th house strong placements, Mercury-Venus yogas.",
                description_ta="வியாபாரம், சுயதொழில் மற்றும் வர்த்தகத் துறை அமைப்புகள்.",
            ),
            SubcategoryItem(
                slug="promotion_advancement",
                name_en="Promotion & Advancement",
                name_ta="பதவி உயர்வு மற்றும் வளர்ச்சி",
                description_en="Planetary triggers indicating elevated rank, authority, and status.",
                description_ta="தொழிலில் பதவி உயர்வு மற்றும் அங்கீகாரம் கிடைக்கும் காலங்கள்.",
            ),
            SubcategoryItem(
                slug="career_changes",
                name_en="Career Changes",
                name_ta="தொழில் மாற்றம்",
                description_en="Dasa transitions, node influences, and 8th/10th house interactions.",
                description_ta="துறை மாற்றம் மற்றும் உத்தியோக இடப்பெயர்ச்சி விதிகள்.",
            ),
            SubcategoryItem(
                slug="foreign_employment",
                name_en="Foreign Employment",
                name_ta="வெளிநாட்டு வேலைவாய்ப்பு",
                description_en="9th and 12th house connections with 10th house and moveable signs.",
                description_ta="10-ஆம் அதிபதி 9, 12-ல் இருத்தல் மற்றும் வெளிநாட்டு வேலை யோகம்.",
            ),
            SubcategoryItem(
                slug="professional_recognition",
                name_en="Professional Recognition",
                name_ta="தொழில் அங்கீகாரம் மற்றும் விருதுகள்",
                description_en="Digbala Sun/Mars in 10th, Raja Yogas, and Amatyakaraka disposition.",
                description_ta="திக்கதிப பலம், ராஜயோகங்கள் மற்றும் தொழிலில் சிறப்புப் புகழ்.",
            ),
            SubcategoryItem(
                slug="employment_difficulties",
                name_en="Employment Difficulties",
                name_ta="வேலையில் ஏற்படும் தடைகள்",
                description_en="Afflictions to 10th house or 6th lord causing instability or stress.",
                description_ta="தொழில் மந்தம், அதிகாரிகளுடன் முரண்பாடுகள் மற்றும் சிக்கல்கள்.",
            ),
            SubcategoryItem(
                slug="income_from_profession",
                name_en="Income from Profession",
                name_ta="தொழில் வழி வருமானம்",
                description_en="Interlocking of 2nd (wealth), 10th (karma), and 11th (gains) houses.",
                description_ta="2, 10, 11-ஆம் பாவக தொடர்புகளால் உருவாகும் வருமான யோகம்.",
            ),
        ],
    ),
    CategoryGroup(
        group_code="personality_birth",
        group_name_en="Personality & Birth Characteristics",
        group_name_ta="சுய ஆளுமை மற்றும் பிறப்புக் குணங்கள்",
        display_order=3,
        subcategories=[
            SubcategoryItem(
                slug="nakshatra_characteristics",
                name_en="Nakshatra Characteristics",
                name_ta="நட்சத்திர குணநலன்கள்",
                description_en="Core temperament and archetypal tendencies governed by birth star.",
                description_ta="ஜென்ம நட்சத்திரத்தின் அடிப்படை குணாதிசயங்கள்.",
            ),
            SubcategoryItem(
                slug="nakshatra_pada_characteristics",
                name_en="Nakshatra Pada Characteristics",
                name_ta="நட்சத்திர பாத குணங்கள்",
                description_en="Specific nuances revealed by the 4 quarters of birth Nakshatra.",
                description_ta="நட்சத்திரத்தின் 4 பாதங்களின் தனித்துவ பலன்கள்.",
            ),
            SubcategoryItem(
                slug="lagna_characteristics",
                name_en="Lagna Characteristics",
                name_ta="லக்ன குணநலன்கள்",
                description_en="Ascendant sign physical traits, natural disposition, and core outlook.",
                description_ta="பிறந்த லக்னத்தின் இயல்புகள், உடல் அமைப்பு மற்றும் பொது நடத்தை.",
            ),
            SubcategoryItem(
                slug="moon_sign_characteristics",
                name_en="Moon Sign Characteristics",
                name_ta="ராசி குணநலன்கள்",
                description_en="Emotional reactions, mind patterns, and instinctual temperament.",
                description_ta="சந்திர ராசியின் மனோபாவம் மற்றும் உணர்வுபூர்வ இயல்பு.",
            ),
            SubcategoryItem(
                slug="ascendant_lord",
                name_en="Ascendant Lord Placement",
                name_ta="லக்னாதிபதி நிலை",
                description_en="Vitality, resilience, and general fortune from Lagnadhipati placement.",
                description_ta="லக்னாதிபதி நின்ற பாவத்தின் மூலம் அறியப்படும் வாழ்வின் போக்கு.",
            ),
            SubcategoryItem(
                slug="atmakaraka",
                name_en="Atmakaraka Indicators",
                name_ta="ஆத்மகாரகன் பலன்கள்",
                description_en="The soul's primary life purpose and spiritual orientation per Jaimini.",
                description_ta="ஜைமினி முறைப்படி அதிக பாகை பெற்ற ஆத்மகாரகனின் ஆன்ம இலக்கு.",
            ),
            SubcategoryItem(
                slug="planetary_strengths",
                name_en="Planetary Strengths",
                name_ta="கிரகங்களின் பலம் மற்றும் வீரியம்",
                description_en="High Shadbala, exaltation, and Vargottama influences on behavior.",
                description_ta="ஷட்பல பலம், உச்சம், வர்கோத்தம அமைப்புகளின் தாக்கங்கள்.",
            ),
            SubcategoryItem(
                slug="planetary_debilitation_aspects",
                name_en="Planetary Debilitation & Aspect Loss",
                name_ta="கிரக நீசம் மற்றும் பார்வை இழப்பு நிலைகள்",
                description_en="Classical debilitation effects from Adhirshta Jothida Kalanjiyam and the 3 conditions where a planet completely loses aspectual potency (Avastha, Combustion, Graha Yuddha).",
                description_ta="அதிர்ஷ்ட ஜோதிடக் களஞ்சியத்தின் 9 கிரக நீச பலன்கள் மற்றும் பார்வை வலுவை முழுதாக இழக்கும் 3 நிலைகள் (அவஸ்தை, அஸ்தங்கம், கிரக யுத்தம்).",
            ),
            SubcategoryItem(
                slug="traditional_temperament",
                name_en="Traditional Temperament",
                name_ta="பாரம்பரிய மனோநிலை",
                description_en="Ayurvedic Pitta, Vata, and Kapha astrological correlations.",
                description_ta="வாத, பித்த, சிலேத்தும சுபாவங்கள் மற்றும் இயற்கை குணம்.",
            ),
            SubcategoryItem(
                slug="leadership_communication",
                name_en="Leadership & Communication Tendencies",
                name_ta="தலைமைத்துவம் மற்றும் பேச்சுத் திறன்",
                description_en="Mars, Sun, and Mercury configurations guiding speech and initiative.",
                description_ta="தலைமை தாங்கும் திறன், வீரம் மற்றும் நாவன்மை யோகங்கள்.",
            ),
        ],
    ),
    CategoryGroup(
        group_code="sexuality_intimacy",
        group_name_en="Sexuality & Intimacy",
        group_name_ta="ஈர்ப்பு மற்றும் தாம்பத்திய அந்தரங்கம்",
        display_order=4,
        subcategories=[
            SubcategoryItem(
                slug="attraction_interpretations",
                name_en="Traditional Attraction Interpretations",
                name_ta="பாரம்பரிய ஈர்ப்பு விளக்கங்கள்",
                description_en="Classical principles of physical magnetism, Venus-Mars associations.",
                description_ta="கவர்ச்சி மற்றும் ஈர்ப்பு தொடர்பான பாரம்பரிய ஜோதிட விதிகள்.",
            ),
            SubcategoryItem(
                slug="intimacy_themes",
                name_en="Intimacy-Related Themes",
                name_ta="தாம்பத்திய நெருக்கக் கூறுகள்",
                description_en="8th and 12th house indicators of bedroom comfort and shared trust.",
                description_ta="8 மற்றும் 12-ஆம் பாவங்கள் வழி அமையும் சயன சுகம் மற்றும் ரகசிய ஈடுபாடு.",
            ),
            SubcategoryItem(
                slug="romantic_inclination",
                name_en="Romantic Inclination",
                name_ta="காதல் உணர்வு மற்றும் நாட்டம்",
                description_en="5th house, Venus, and Moon alignments reflecting romantic temperament.",
                description_ta="5-ஆம் பாவம் மற்றும் சுக்கிரன் தரும் கலை, காதல் ஆர்வம்.",
            ),
            SubcategoryItem(
                slug="emotional_intimacy",
                name_en="Emotional Intimacy",
                name_ta="உணர்வுபூர்வ நெருக்கம்",
                description_en="4th and 7th house connection fostering deep emotional bonds.",
                description_ta="மனப்பூர்வமான அன்பும் பாசமும் பெருகும் ஜோதிட அமைப்புகள்.",
            ),
            SubcategoryItem(
                slug="marital_intimacy",
                name_en="Marital Intimacy",
                name_ta="தாம்பத்திய சுக யோகம்",
                description_en="Venus, 7th lord, and 12th house dignity regarding physical harmony.",
                description_ta="சுக்கிரன் மற்றும் 7, 12-ஆம் அதிபதிகளின் சுப நிலை.",
            ),
            SubcategoryItem(
                slug="relationship_satisfaction",
                name_en="Relationship Satisfaction",
                name_ta="திருமண வாழ்வில் திருப்தி",
                description_en="Benefic presence in Kendra houses supporting marital fulfillment.",
                description_ta="கேந்திர சுப கிரகங்களால் ஏற்படும் குடும்ப மனநிறைவு.",
            ),
            SubcategoryItem(
                slug="boundaries_challenges",
                name_en="Relationship Boundaries & Challenges",
                name_ta="உறவு எல்லைகள் மற்றும் சவால்கள்",
                description_en="Saturn or Ketu in 7th/12th calling for patience and mature communication.",
                description_ta="சனி, கேது அமைப்புகளால் தேவைப்படும் பக்குவம் மற்றும் பொறுமை.",
            ),
            SubcategoryItem(
                slug="classical_adultery_unions",
                name_en="Classical Unconventional & Extramarital Yogas",
                name_ta="பாரம்பரிய திருமணத்திற்கு வெளியேயான உறவு யோகங்கள்",
                description_en="Classical combinations from Jataka Tatva and ancient canons on unconventional relationships and societal boundaries.",
                description_ta="ஜாதக தத்துவம் மற்றும் பாரம்பரிய நூல்களில் விவரிக்கப்பட்டுள்ள திருமணத்திற்கு வெளியேயான உறவு யோகங்கள்.",
            ),
            SubcategoryItem(
                slug="stri_jataka_principles",
                name_en="Stri Jataka Female Horoscopy Principles",
                name_ta="ஸ்திரீ ஜாதகம் - பெண் ஜாதக தாம்பத்திய யோகங்கள்",
                description_en="Classical Brihat Jataka Stri Jataka Adhyaya guidelines on 7th house configurations, marital bonds, and independence.",
                description_ta="பிருஹத் ஜாதகத்தின் ஸ்திரீ ஜாதக அத்தியாயத்தில் கூறப்படும் 7-ஆம் பாவ அமைப்புகள் மற்றும் பெண்கள் திருமண விதிகள்.",
            ),
        ],
    ),
    CategoryGroup(
        group_code="money_assets",
        group_name_en="Money & Assets",
        group_name_ta="தனம் மற்றும் சொத்துக்கள்",
        display_order=5,
        subcategories=[
            SubcategoryItem(
                slug="wealth_yogas",
                name_en="Wealth & Dhana Yogas",
                name_ta="தன யோகங்கள் மற்றும் செல்வம்",
                description_en="Classical combinations of 1st, 2nd, 5th, 9th, and 11th lords.",
                description_ta="1, 2, 5, 9, 11-ஆம் அதிபதிகளால் ஏற்படும் லட்சுமி மற்றும் தன யோகங்கள்.",
            ),
            SubcategoryItem(
                slug="regular_income",
                name_en="Regular Income",
                name_ta="நிலையான வருமானம்",
                description_en="Strength of 11th house, 11th lord, and ongoing favorable Dasa periods.",
                description_ta="11-ஆம் பாவம் மற்றும் லாபாதிபதி பலம் தரும் தொடர் வருவாய்.",
            ),
            SubcategoryItem(
                slug="savings_accumulation",
                name_en="Savings & Accumulation",
                name_ta="சேமிப்பு மற்றும் தன இருப்பு",
                description_en="2nd house from Lagna and Moon, Jupiter's aspect on 2nd.",
                description_ta="2-ஆம் பாவம் மற்றும் தனகாரகன் குருவின் பார்வையால் சேரும் நிதி.",
            ),
            SubcategoryItem(
                slug="debt_obligations",
                name_en="Debt & Financial Obligations",
                name_ta="கடன் மற்றும் நிதிச்சுமை",
                description_en="6th house, 6th lord, and Daridra yoga factors to be monitored.",
                description_ta="6-ஆம் பாவம் மற்றும் ருண ஸ்தானம் சார்ந்த எச்சரிக்கை விதிகள்.",
            ),
            SubcategoryItem(
                slug="property_land",
                name_en="Property & Real Estate",
                name_ta="நிலம் மற்றும் பூமி யோகம்",
                description_en="4th house, Mars, and Saturn in fixed signs indicating landed property.",
                description_ta="4-ஆம் பாவம், செவ்வாய் பலம் தரும் பூமி, நிலம், வீடு யோகங்கள்.",
            ),
            SubcategoryItem(
                slug="vehicles_conveyances",
                name_en="Vehicles & Conveyances",
                name_ta="வாகன யோகம்",
                description_en="4th house and Venus configurations indicating vehicle acquisitions.",
                description_ta="சுக்கிரன் மற்றும் 4-ஆம் அதிபதியால் கிட்டும் வாகன சுகம்.",
            ),
            SubcategoryItem(
                slug="inheritance_unearned_wealth",
                name_en="Inheritance & Unearned Wealth",
                name_ta="பூர்வீகச் சொத்து மற்றும் எதிர்பாராத தனவரவு",
                description_en="8th house, 8th lord, and 9th house connections for ancestral gains.",
                description_ta="8-ஆம் பாவம், பூர்வீக புண்ணியம் மூலம் எதிர்பாராமல் வரும் செல்வம்.",
            ),
            SubcategoryItem(
                slug="business_gains",
                name_en="Business Gains",
                name_ta="வியாபார லாபம்",
                description_en="Mercury, 7th lord, and 11th house synergy in commercial activities.",
                description_ta="வர்த்தகம் மற்றும் கூட்டுத் தொழில் வழி பெருகும் வருவாய்.",
            ),
            SubcategoryItem(
                slug="financial_fluctuations",
                name_en="Financial Fluctuations",
                name_ta="பொருளாதார ஏற்ற இறக்கங்கள்",
                description_en="Rahu, Ketu, or 12th lord interactions creating income volatility.",
                description_ta="விரயாதிபதி மற்றும் ராகு-கேதுவால் ஏற்படும் வரவு-செலவு மாற்றங்கள்.",
            ),
        ],
    ),
    CategoryGroup(
        group_code="family_children",
        group_name_en="Family & Children",
        group_name_ta="குடும்பம் மற்றும் குழந்தைகள்",
        display_order=6,
        subcategories=[
            SubcategoryItem(
                slug="children_prospects",
                name_en="Children Prospects",
                name_ta="புத்திர பாக்கியம்",
                description_en="5th house, 5th lord, Jupiter (Putrakaraka), and Saptamsha (D7).",
                description_ta="5-ஆம் பாவம், புத்திரகாரகன் குரு மற்றும் நற்புத்திர யோகங்கள்.",
            ),
            SubcategoryItem(
                slug="childbirth_indicators",
                name_en="Traditional Childbirth Indicators",
                name_ta="மகப்பேறு அமைப்புகள்",
                description_en="Classical timing indicators and benefic transits over 5th house.",
                description_ta="குழந்தை பிறப்பு மற்றும் அதற்கான தசா-புக்தி சாதகங்கள்.",
            ),
            SubcategoryItem(
                slug="sibling_relationships",
                name_en="Sibling Relationships",
                name_ta="சகோதர உறவுகள்",
                description_en="3rd house (younger) and 11th house (elder siblings), Mars strength.",
                description_ta="3 மற்றும் 11-ஆம் பாவங்கள், செவ்வாய் மூலம் சகோதர ஒற்றுமை.",
            ),
            SubcategoryItem(
                slug="parents_lineage",
                name_en="Parents & Ancestry",
                name_ta="பெற்றோர் மற்றும் முன்னோர்கள்",
                description_en="9th house/Sun for father; 4th house/Moon for mother.",
                description_ta="சூரியன், 9-ஆம் பாவம் (தந்தை); சந்திரன், 4-ஆம் பாவம் (தாய்).",
            ),
            SubcategoryItem(
                slug="family_environment",
                name_en="Family Environment",
                name_ta="குடும்பச் சூழல்",
                description_en="2nd house harmony, Kutumba sthana benefic occupants.",
                description_ta="2-ஆம் பாவம் மற்றும் குடும்பத்தில் நிலவும் நிம்மதி.",
            ),
            SubcategoryItem(
                slug="domestic_harmony",
                name_en="Domestic Harmony",
                name_ta="இல்லற அமைதி",
                description_en="4th house Sukhastana and Moon dignity supporting peace of mind.",
                description_ta="4-ஆம் பாவம் சுகஸ்தானம் தரும் மனநிறைவு மற்றும் அமைதி.",
            ),
        ],
    ),
    CategoryGroup(
        group_code="education_travel",
        group_name_en="Education & Travel",
        group_name_ta="கல்வி மற்றும் பயணங்கள்",
        display_order=7,
        subcategories=[
            SubcategoryItem(
                slug="basic_education",
                name_en="Basic & School Education",
                name_ta="ஆரம்பக் கல்வி",
                description_en="4th house, Mercury, and Vidyakaraka Jupiter for foundation studies.",
                description_ta="4-ஆம் பாவம், புதன், குரு அருளால் அமையும் அடிப்படைக் கல்வி.",
            ),
            SubcategoryItem(
                slug="higher_education",
                name_en="Higher Education & Degrees",
                name_ta="உயர்கல்வி மற்றும் பட்டப் படிப்பு",
                description_en="5th and 9th houses, Jupiter, and Sun indicating specialized research.",
                description_ta="5 மற்றும் 9-ஆம் அதிபதிகள் தரும் உயர்கல்வி, கல்லூரிப் படிப்பு யோகம்.",
            ),
            SubcategoryItem(
                slug="competitive_examinations",
                name_en="Competitive Examinations",
                name_ta="போட்டித் தேர்வுகள்",
                description_en="6th house of competition, Mars, and Mercury sharp intellect.",
                description_ta="6-ஆம் பாவம், செவ்வாய் தரும் விடாமுயற்சியால் தேர்வுகளில் வெற்றி.",
            ),
            SubcategoryItem(
                slug="foreign_travel",
                name_en="Foreign Travel & Journeys",
                name_ta="வெளிநாட்டுப் பயணம்",
                description_en="9th house long voyages, 12th house foreign lands, moveable signs.",
                description_ta="9, 12-ஆம் பாவங்கள் மற்றும் சர ராசிகளால் உருவாகும் தூர தேசப் பயணம்.",
            ),
            SubcategoryItem(
                slug="settlement_abroad",
                name_en="Settlement Abroad",
                name_ta="வெளிநாட்டு குடியுரிமை",
                description_en="12th house strong presence, 4th house lord in 12th or movable signs.",
                description_ta="12-ஆம் பாவக பலத்தால் வெளிநாட்டில் நிரந்தரமாக வசிக்கும் யோகம்.",
            ),
            SubcategoryItem(
                slug="relocation_city_change",
                name_en="Relocation & Residence Change",
                name_ta="ஊர் மாற்றம் மற்றும் இடப்பெயர்ச்சி",
                description_en="3rd house short moves and 4th house shifting indicators.",
                description_ta="3-ஆம் பாவம் மூலம் நிகழும் உள்ளூர் இடமாற்றங்கள்.",
            ),
            SubcategoryItem(
                slug="spiritual_studies",
                name_en="Spiritual & Occult Studies",
                name_ta="ஆன்மீக மற்றும் ஜோதிடக் கல்வி",
                description_en="8th house occult, 9th house dharma, 5th house mantra, Jupiter-Ketu.",
                description_ta="8, 9-ஆம் பாவங்கள் மற்றும் கேது தரும் வேத, சாஸ்திர ஞானம்.",
            ),
        ],
    ),
    CategoryGroup(
        group_code="other_life_themes",
        group_name_en="Other Life Themes",
        group_name_ta="பிற முக்கிய வாழ்க்கை நிகழ்வுகள்",
        display_order=8,
        subcategories=[
            SubcategoryItem(
                slug="health_vitality",
                name_en="Health & Traditional Vitality",
                name_ta="உடல் நலம் மற்றும் ஆரோக்கியம்",
                description_en="Lagna lord strength, 6th house monitoring, and Ayurdaya indicators.",
                description_ta="லக்னாதிபதி பலம் மற்றும் நோய் எதிர்ப்பு சக்தி அமைப்புகள்.",
            ),
            SubcategoryItem(
                slug="spirituality_moksha",
                name_en="Spirituality & Moksha",
                name_ta="ஆன்மீகம் மற்றும் முக்தி நாட்டம்",
                description_en="12th house, Ketu, Jupiter, and 9th lord guiding spiritual surrender.",
                description_ta="12-ஆம் பாவம், கேது பகவான் தரும் ஆன்மீக பக்குவம் மற்றும் முக்தி யோகம்.",
            ),
            SubcategoryItem(
                slug="legal_disputes",
                name_en="Legal Disputes & Litigation",
                name_ta="நீதிமன்ற வழக்குகள் மற்றும் தீர்வுகள்",
                description_en="6th house litigation, 6th vs 8th lord dignity, and resolution factors.",
                description_ta="6-ஆம் பாவம் மற்றும் சட்டப் போராட்டங்களில் கிடைக்கும் வெற்றி.",
            ),
            SubcategoryItem(
                slug="public_recognition",
                name_en="Public Recognition & Fame",
                name_ta="மக்கள் செல்வாக்கு மற்றும் புகழ்",
                description_en="Sun, Moon, 10th house, and Raja Yogas conferring renown.",
                description_ta="சூரியன், சந்திரன், 10-ஆம் பாவம் தரும் சமூகப் புகழ் மற்றும் செல்வாக்கு.",
            ),
            SubcategoryItem(
                slug="partnerships_alliances",
                name_en="Business Partnerships & Alliances",
                name_ta="கூட்டு வணிகம் மற்றும் ஒப்பந்தங்கள்",
                description_en="7th house commercial alliances and 11th house collaborative gains.",
                description_ta="7-ஆம் பாவம் மூலம் அமையும் கூட்டுத் தொழில் மற்றும் ஒப்பந்த பலன்கள்.",
            ),
            SubcategoryItem(
                slug="general_life_themes",
                name_en="General Life Themes",
                name_ta="பொதுவான வாழ்க்கை அம்சங்கள்",
                description_en="Comprehensive life indicators, destiny milestones, and karmic flow.",
                description_ta="வாழ்வின் முக்கிய திருப்பங்கள் மற்றும் பொதுவான பலன்கள்.",
            ),
        ],
    ),
    CategoryGroup(
        group_code="saravali_classics",
        group_name_en="Kalyana Varma's Saravali",
        group_name_ta="கல்யாண வர்மாவின் சாராவளி",
        display_order=9,
        subcategories=[
            SubcategoryItem(
                slug="saravali_bhava_phala",
                name_en="Planets in Bhavas (Ch. 30)",
                name_ta="சாராவளி பாவ பலன்கள் (அத். 30)",
                description_en="Planetary placements from 1st to 12th houses strictly per Saravali Chapter 30.",
                description_ta="சாராவளி 30-ம் அத்தியாயத்தின்படி 1 முதல் 12 பாவங்களில் கிரகங்களின் பலன்கள்.",
            ),
            SubcategoryItem(
                slug="saravali_graha_yogas",
                name_en="Conjunctions & Angular Pairs (Ch. 15, 16, 31)",
                name_ta="சாராவளி கிரக சேர்க்கைகள் (அத். 15, 16, 31)",
                description_en="Two-planet and multi-planet conjunctions and angular dispositions per Saravali.",
                description_ta="சாராவளி முறைப்படி இரண்டு மற்றும் பல கிரக சேர்க்கைகள் மற்றும் கேந்திர அமைப்புகள்.",
            ),
            SubcategoryItem(
                slug="saravali_raja_yogas",
                name_en="Raja Yogas & Royal Status (Ch. 35)",
                name_ta="சாராவளி ராஜ யோகங்கள் (அத். 35)",
                description_en="High status, ministerial authority, and kingly yogas per Saravali Chapter 35.",
                description_ta="சாராவளி 35-ம் அத்தியாயத்தின்படி அரசு அதிகாரம், தலைமை மற்றும் ராஜ யோகங்கள்.",
            ),
            SubcategoryItem(
                slug="saravali_raja_yoga_bhanga",
                name_en="Raja Yoga Obstructions (Ch. 39)",
                name_ta="சாராவளி ராஜயோக பங்கங்கள் (அத். 39)",
                description_en="Nullifications and obstructions preventing Raja Yoga realization per Saravali Chapter 39.",
                description_ta="சாராவளி 39-ம் அத்தியாயத்தின்படி ராஜயோகங்களை முறிக்கும் கிரக அமைப்புகள்.",
            ),
            SubcategoryItem(
                slug="saravali_longevity_death",
                name_en="Longevity & Death Causes (Ch. 10, 40, 47)",
                name_ta="சாராவளி ஆயுள் & மரண நிர்ணயம் (அத். 10, 40, 47)",
                description_en="8th house indications, fatal degrees, and Khara Drekkana per Saravali Chapters 10, 40 & 47.",
                description_ta="சாராவளி முறைப்படி ஆயுள், மரண காரணங்கள் மற்றும் 22-வது திரேக்காணம்.",
            ),
            SubcategoryItem(
                slug="saravali_stri_jataka",
                name_en="Female Horoscopy (Ch. 46)",
                name_ta="சாராவளி ஸ்திரீ ஜாதகம் (அத். 46)",
                description_en="Female horoscopy, 7th house husband indicators, and Trimsamsa rules per Saravali Chapter 46.",
                description_ta="சாராவளி 46-ம் அத்தியாயத்தின்படி பெண் ஜாதக பலன்கள், கணவர் லட்சணம் மற்றும் திரிம்சாம்சம்.",
            ),
            SubcategoryItem(
                slug="saravali_ashtakavarga",
                name_en="Ashtakavarga Bindu Predictions (Ch. 54)",
                name_ta="சாராவளி அஷ்டகவர்க்க பலன்கள் (அத். 54)",
                description_en="Specific predictive effects of 0 to 8 bindus per planet per Saravali Chapter 54.",
                description_ta="சாராவளி 54-ம் அத்தியாயத்தின்படி ஒவ்வொரு கிரகத்திற்கும் 0 முதல் 8 பிந்து பலன்கள்.",
            ),
            SubcategoryItem(
                slug="saravali_dignities",
                name_en="Multi-Planet Dignities (Ch. 45)",
                name_ta="சாராவளி கிரக பலன்கள் & உச்ச நீச பலன் (அத். 45)",
                description_en="Effects of multiple planets in exaltation, moolatrikona, own sign, or fall per Saravali Chapter 45.",
                description_ta="சாராவளி 45-ம் அத்தியாயத்தின்படி பல கிரகங்கள் உச்சம், மூலத்திரிகோணம், ஆட்சி, நீசம் பெற்ற பலன்கள்.",
            ),
            SubcategoryItem(
                slug="saravali_worldly_affairs",
                name_en="Worldly Affairs & Fortunes (Ch. 32-34)",
                name_ta="சாராவளி பாக்கியம் & ஜீவனம் (அத். 32-34)",
                description_en="9th house fortunes, 10th house livelihoods, 2nd house wealth, and 11th house gains per Saravali.",
                description_ta="சாராவளி 32-34 அத்தியாயங்களின்படி பாக்கியம், தொழில் ஜீவனம், தன யோகம் மற்றும் லாப ஸ்தான பலன்கள்.",
            ),
        ],
    ),
    CategoryGroup(
        group_code="bphs_classics",
        group_name_en="Brihat Parashara Hora Shastra",
        group_name_ta="பிருஹத் பராசர ஹோரா சாஸ்திரம்",
        display_order=10,
        subcategories=[
            SubcategoryItem(
                slug="bphs_bhava_lords",
                name_en="Bhava Lords in 12 Houses (Ch. 24)",
                name_ta="12 பாவங்களில் பாவாதிபதிகள் பலன் (அத். 24)",
                description_en="Comprehensive effects of each of the 12 bhava lords positioned in each of the 12 bhavas (144 combinations) strictly per BPHS Ch. 24.",
                description_ta="பிருஹத் பராசர ஹோரா சாஸ்திரம் அத்தியாயம் 24-ன்படி 1 முதல் 12 பாவாதிபதிகள் 12 பாவங்களில் அமர்வதால் உண்டாகும் 144 பூரண பலன்கள்.",
            ),
            SubcategoryItem(
                slug="bphs_yogakarakas",
                name_en="Yogakarakas & Lagna Lords (Ch. 34)",
                name_ta="யோககாரகர்கள் & லக்ன சுபாசுப கிரகங்கள் (அத். 34)",
                description_en="Functional benefics, functional malefics, Yogakarakas, and Marakas for all 12 ascendants per BPHS Ch. 34.",
                description_ta="பிருஹத் பராசர ஹோரா சாஸ்திரம் 34-ம் அத்தியாயத்தின்படி 12 லக்னங்களுக்கும் இயற்கை மற்றும் காரக சுப, அசுப, யோககாரக, மாரக கிரக விதிகள்.",
            ),
            SubcategoryItem(
                slug="bphs_dhana_yogas",
                name_en="Special Dhana Yogas (Ch. 41)",
                name_ta="சிறப்பு தன யோகங்கள் (அத். 41)",
                description_en="Canonical combinations for extreme wealth, royal fortune, and sovereign riches per BPHS Ch. 41.",
                description_ta="பிருஹத் பராசர ஹோரா சாஸ்திரம் 41-ம் அத்தியாயத்தின்படி அளப்பரிய செல்வம் மற்றும் அரச யோகத்தை வழங்கும் தன யோகங்கள்.",
            ),
            SubcategoryItem(
                slug="bphs_daridra_yogas",
                name_en="Daridra Yogas & Penury (Ch. 42)",
                name_ta="தரித்திர யோகங்கள் & வறுமை நிலைகள் (அத். 42)",
                description_en="Classical combinations producing financial distress, debt, and penury per BPHS Ch. 42.",
                description_ta="பிருஹத் பராசர ஹோரா சாஸ்திரம் 42-ம் அத்தியாயத்தின்படி தனநாசம் மற்றும் வறுமையை ஏற்படுத்தும் தரித்திர யோகங்கள்.",
            ),
            SubcategoryItem(
                slug="bphs_special_yogas",
                name_en="Special Yogas & Characters (Ch. 36)",
                name_ta="பராசர சிறப்பு யோகங்கள் (அத். 36)",
                description_en="Special Yogas (Parvata, Kahala, Chamara, Shankha, Bheri, Shrinatha, etc.) per BPHS Ch. 36.",
                description_ta="பிருஹத் பராசர ஹோரா சாஸ்திரம் 36-ம் அத்தியாயத்தின்படி பர்வத, காகள, சாமர, சங்க, பேரி முதலான விசேஷ யோகங்கள்.",
            ),
            SubcategoryItem(
                slug="bphs_stri_jataka",
                name_en="Stri Jataka & Visha Kanya (Ch. 80)",
                name_ta="ஸ்திரீ ஜாதகம் & விஷ கன்யா (அத். 80)",
                description_en="Female horoscopy, chastity, marital longevity, and Visha Kanya afflictions & cancellations per BPHS Ch. 80.",
                description_ta="பிருஹத் பராசர ஹோரா சாஸ்திரம் 80-ம் அத்தியாயத்தின்படி பெண் ஜாதக விதிகள் மற்றும் விஷ கன்யா யோக அமைப்புகளும் பரிகாரங்களும்.",
            ),
            SubcategoryItem(
                slug="bphs_shapas_curses",
                name_en="Curses from Past Lives & Remedies (Ch. 83)",
                name_ta="முற்பிறவி சாபங்கள் & சாந்தி பரிகாரங்கள் (அத். 83)",
                description_en="8 Curses of past lives (Sarpa, Pitru, Matru, Bhratri, Matula, Brahmana, Patni, Pretha) causing childlessness and their classical prayaschittas per BPHS Ch. 83.",
                description_ta="பிருஹத் பராசர ஹோரா சாஸ்திரம் 83-ம் அத்தியாயத்தின்படி புத்திர தோஷத்தை உண்டாக்கும் 8 முற்பிறவி சாபங்களும் அவற்றிற்கான வேத பரிகாரங்களும்.",
            ),
            SubcategoryItem(
                slug="bphs_inauspicious_births",
                name_en="Inauspicious Births & Gandanta (Ch. 85-94)",
                name_ta="அசுப ஜனனங்கள் & கண்டாந்த தோஷங்கள் (அத். 85-94)",
                description_en="Amavasya, Krishna Chaturdashi portions, Nakshatra Gandanta, Lagna Gandanta, and Trik Prasava per BPHS Ch. 85-94.",
                description_ta="பிருஹத் பராசர ஹோரா சாஸ்திரம் 85-94 அத்தியாயங்களின்படி அமாவாசை, கிருஷ்ண சதுர்த்தசி பாகங்கள், கண்டாந்தம் மற்றும் திரிக பிரசவ பலன்கள்.",
            ),
            SubcategoryItem(
                slug="bphs_upagrahas_arudhas",
                name_en="Arudha Padas & Upagrahas (Ch. 29-30)",
                name_ta="ஆரூட பாதங்கள் & உபகிரகங்கள் (அத். 29-30)",
                description_en="Arudha Lagna, Upapada Lagna, and manifestation of bhava padas per BPHS Ch. 29-30.",
                description_ta="பிருஹத் பராசர ஹோரா சாஸ்திரம் 29-30 அத்தியாயங்களின்படி ஆரூட லக்னம், உபபதம் மற்றும் பாவக ஆரூடங்களின் பலன்கள்.",
            ),
        ],
    ),
    CategoryGroup(
        group_code="deva_keralam_classics",
        group_name_en="Deva Keralam (Chandra Kala Nadi)",
        group_name_ta="தேவ கேரளம் (சந்திர கலா நாடி)",
        display_order=11,
        subcategories=[
            SubcategoryItem(
                slug="deva_keralam_nadiamsas",
                name_en="150 Nadiamsas Micro-Zodiac Predictions",
                name_ta="150 நாடியம்ச நுண்பிரிவு பலன்கள்",
                description_en="Micro-zodiac predictions based on 150 Nadiamsas (12' arc each) across movable, fixed, and dual signs per Deva Keralam Book 1.",
                description_ta="தேவ கேரளம் முதல் பாகத்தின்படி சர, ஸ்திர, உபய ராசிகளில் 150 நாடியம்சங்களின் (12 கலை அளவு) அடிப்படையில் கூறப்பட்ட நுட்பமான பலன்கள்.",
            ),
            SubcategoryItem(
                slug="deva_keralam_raja_yogas",
                name_en="Sovereign & Koorma Yogas",
                name_ta="ராஜ யோகங்கள் மற்றும் கூர்ம யோகம்",
                description_en="Sovereign combinations including Matanga, Koorma, Rudrasana, and Chakra Yogas from Deva Keralam.",
                description_ta="மாதங்க யோகம், கூர்ம யோகம், சக்ர யோகம் உள்ளிட்ட அரச யோகங்கள் மற்றும் உயர் பதவிகளைத் தரும் தேவ கேரள யோகங்கள்.",
            ),
            SubcategoryItem(
                slug="deva_keralam_gochara_navamsa",
                name_en="Saturn Transits over Navamsa Dispositors",
                name_ta="நவாம்ச அதிபதிகள் மீது சனியின் கோசார விதிகள்",
                description_en="Timing critical life events, family loss, and prosperity when transit Saturn aspects or enters Navamsa dispositor Rasis.",
                description_ta="2, 8, 11-ஆம் அதிபதிகளின் நவாம்ச அதிபதி மீது கோசார சனி சஞ்சரிக்கும் காலத்தில் நிகழும் விபத்து, தன நஷ்டம் மற்றும் மரண கண்டக் கால நிர்ணயம்.",
            ),
            SubcategoryItem(
                slug="deva_keralam_karma_remedies",
                name_en="Karma-Vipaka Diagnostic & Remedial Science",
                name_ta="கர்ம விபாக சாப ஆய்வு & பரிகார சாஸ்திரம்",
                description_en="Specific past-life curses causing childlessness and their exact remedies: Setu snanam, Nageswara Pradosha worship, and Santana Gopala Dana.",
                description_ta="முற்பிறவி சாபங்களால் ஏற்படும் புத்திர தோஷங்கள் மற்றும் அதற்கான ராமேஸ்வர சேது ஸ்நானம், நாகேஸ்வர சிவபூஜை, சந்தான கோபால தான பரிகாரங்கள்.",
            ),
            SubcategoryItem(
                slug="deva_keralam_bhava_phala",
                name_en="Bhava Indications & Longevity",
                name_ta="பாவ பலன்கள் மற்றும் ஆயுள் நிர்ணயம்",
                description_en="Detailed horoscopic manifestations for Taurus, Aquarius, and Sagittarius Ascendants across Purvardha and Uttarardha.",
                description_ta="ரிஷபம், கும்பம், தனுசு லக்னங்களின் பூர்வார்த்த மற்றும் உத்தரார்த்த பாவ பலன்கள் மற்றும் குடும்பத்தாரின் ஆயுள் சூத்திரங்கள்.",
            ),
        ],
    ),
]


def get_all_category_groups() -> List[Dict[str, Any]]:
    """Return serialized list of all category groups and subcategories."""
    return [g.model_dump() for g in PREDICTION_CATEGORY_GROUPS]


def get_category_by_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Find category/subcategory metadata by slug."""
    for group in PREDICTION_CATEGORY_GROUPS:
        if group.group_code == slug:
            return group.model_dump()
        for sub in group.subcategories:
            if sub.slug == slug:
                res = sub.model_dump()
                res["group_code"] = group.group_code
                res["group_name_en"] = group.group_name_en
                res["group_name_ta"] = group.group_name_ta
                return res
    return None
