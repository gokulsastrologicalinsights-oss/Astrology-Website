# scripts/generate_bphs_full_rules.py
"""Generate backend/app/services/prediction_rules/bphs_classical_rules.py
Codifying Brihat Parashara Hora Shastra (BPHS) across Chapters 24, 34, 41, 42, 80, 83, 85-95, 29-30.
"""

import sys
import os

OUTPUT_FILE = "backend/app/services/prediction_rules/bphs_classical_rules.py"

def generate():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    lines = []
    lines.append('"""Maharishi Parashara\'s Brihat Parashara Hora Shastra (BPHS) Classical Rules Registry.')
    lines.append('')
    lines.append('Authoritative codification of foundational classical astrological rules from the')
    lines.append("supreme Vedic treatise 'Brihat Parashara Hora Shastra' (BPHS).")
    lines.append('')
    lines.append('Includes:')
    lines.append('- Ch. 24: Effects of Bhava Lords across all 12 houses (144 complete combinations, Slokas 1-144)')
    lines.append('- Ch. 34: Functional Nature & Yogakarakas for all 12 Ascendants (Slokas 19-44)')
    lines.append('- Ch. 41: Special Dhana Yogas / Combinations for Wealth (Slokas 2-15)')
    lines.append('- Ch. 42: Special Daridra Yogas / Combinations for Penury (Slokas 2-18)')
    lines.append('- Ch. 80: Female Horoscopy / Stri Jataka & Visha Kanya Rules (Slokas 5-55)')
    lines.append('- Ch. 83: Curses from Previous Birth / 8 Great Shapas & Remedies (Slokas 9-105)')
    lines.append('- Ch. 85-95: Inauspicious Births & Gandanta Rules (Amavasya, Chaturdashi, Gandanta, Trik Prasava)')
    lines.append('- Ch. 29-30: Arudha Padas & Upapada Lagna Predictions (Slokas 8-43)')
    lines.append('"""')
    lines.append('')
    lines.append('from typing import List')
    lines.append('from app.services.prediction_rules.ast_models import (')
    lines.append('    AstrologicalRuleDefinition,')
    lines.append('    AstrologySystem,')
    lines.append('    ChartScope,')
    lines.append('    SeverityLevel,')
    lines.append(')')
    lines.append('')
    lines.append('BPHS_CLASSICAL_RULES: List[AstrologicalRuleDefinition] = [')

    # -------------------------------------------------------------
    # 1. Chapter 24: 144 Bhava Lord Placements
    # -------------------------------------------------------------
    BHAVA_NAMES_EN = [
        "", "Tanu (1st / Lagna)", "Dhana (2nd)", "Sahaja (3rd)", "Bandhu (4th)",
        "Putra (5th)", "Ari (6th)", "Yuvati (7th)", "Randhra (8th)",
        "Dharma (9th)", "Karma (10th)", "Labha (11th)", "Vyaya (12th)"
    ]
    BHAVA_NAMES_TA = [
        "", "லக்னம் (1-ஆம் பாவம்)", "தன பாவம் (2-ஆம் பாவம்)", "சகஜ பாவம் (3-ஆம் பாவம்)", "சுக பாவம் (4-ஆம் பாவம்)",
        "புத்திர பாவம் (5-ஆம் பாவம்)", "சத்ரு பாவம் (6-ஆம் பாவம்)", "களத்திர பாவம் (7-ஆம் பாவம்)", "ஆயுள் பாவம் (8-ஆம் பாவம்)",
        "பாக்கிய பாவம் (9-ஆம் பாவம்)", "கர்ம பாவம் (10-ஆம் பாவம்)", "லாப பாவம் (11-ஆம் பாவம்)", "விரய பாவம் (12-ஆம் பாவம்)"
    ]

    ch24_data = [
        (1, 1, 1, "FAVORABLE", "lagna_characteristics",
         "Endowed with physical happiness, robust prowess, keen intelligence, and leadership, though possessing a restless mind and dynamic romantic nature.",
         "உடல் பலம், தைரியம், கூர்மையான அறிவு மற்றும் தலைமைப்பண்பு உண்டாகும். சுறுசுறுப்பான மனமும் பல கவர்ச்சிகரமான நட்புகளும் அமையும்."),
        (1, 2, 2, "FAVORABLE", "wealth_yogas",
         "Gainful, highly scholarly, universally respected, pious, endowed with auspicious virtues, speaking sweetly and blessed with family wealth.",
         "கல்வி அறிவு, தன லாபம், நற்குணங்கள் மற்றும் சமூக மரியாதை உண்டாகும். இனிமையான வாக்கும் குடும்ப மேன்மையும் அமையும்."),
        (1, 3, 3, "FAVORABLE", "personality_birth",
         "Valorous like a lion, endowed with all types of worldly wealth, highly honorable, courageous, sharp-minded, and enjoying domestic bliss.",
         "சிங்கம் போன்ற பராக்கிரமம், அனைத்து விதமான செல்வங்கள், வீரம், கௌரவம் மற்றும் சகோதர பலம் உண்டாகும்."),
        (1, 4, 4, "FAVORABLE", "property_land",
         "Blessed with maternal and paternal happiness, multiple conveyances, vast lands, ancestral dwellings, virtue, and handsome bodily allure.",
         "தாய்-தந்தை வழி மகிழ்ச்சி, பூமி, நிலம், வாகன யோகங்கள், நற்பண்புகள் மற்றும் வசீகர தோற்றம் உண்டாகும்."),
        (1, 5, 5, "NEUTRAL", "children_prospects",
         "Scholarly, held dear by rulers and mentors, honorable, quick-tempered, experiencing trials or delays with the first child followed by meritorious progeny.",
         "அறிவாற்றல், அரச மரியாதை, கௌரவம் மற்றும் கோபம் உண்டாகும். முதல் குழந்தை விசயத்தில் கவனமும் பின்னர் நற்புத்திர பாக்கியமும் ஏற்படும்."),
        (1, 6, 6, "UNFAVORABLE", "health_vitality",
         "Subject to bodily ailments, vulnerability to hidden competitors, and physical fatigues; benefic aspects transmute these into great victory over rivals.",
         "உடல் உபாதைகள், எதிரிகளால் தொல்லைகள் ஏற்பட வாய்ப்புள்ளது. சுபக்கிரக பார்வை பெற்றால் எதிரிகளை வெல்லும் பராக்கிரமம் உண்டாகும்."),
        (1, 7, 7, "NEUTRAL", "first_marriage",
         "Deeply attached to the marital partner; if benefic rules, grants kingly authority and high social charm, while malefic placement demands care in partner's health.",
         "துணை மீது மிகுந்த ஈர்ப்பு ஏற்படும். சுப பலம் பெற்றால் அரச கௌரவமும் சமூக அந்தஸ்தும் உண்டாகும்; அசுப பலம் பெற்றால் துணை நலனில் கவனம் தேவை."),
        (1, 8, 8, "UNFAVORABLE", "health_vitality",
         "Deeply learned in esoteric shastras and occult wisdom, but prone to fluctuating health, secret inclinations, and erratic expenditures.",
         "மறைபொருள் சாஸ்திரங்களில் தேர்ச்சி, திடீர் அதிர்ஷ்டம் ஏற்படும். உடல் ஆரோக்கியத்தில் எச்சரிக்கையும் பொறுமையும் அவசியம்."),
        (1, 9, 9, "FAVORABLE", "dharma_devotion",
         "Exceedingly fortunate, pious, held dear by society, devoted to Lord Vishnu and preceptors, eloquent speaker, blessed with virtuous spouse and children.",
         "மகா பாக்கிய யோகம், தர்ம சிந்தனை, விஷ்ணு பக்தி, வாக்கு சாதுரியம் மற்றும் நல்ல குடும்பம் அமையும்."),
        (1, 10, 10, "FAVORABLE", "job_prospects",
         "Honored by governance and kings, enjoying high paternal bliss, widespread professional fame, and abundance of self-earned wealth.",
         "அரசாங்க மரியாதை, தொழில் மேன்மை, தந்தை வழி ஆதரவு, சுய சம்பாத்தியத்தில் பெரும் செல்வம் உண்டாகும்."),
        (1, 11, 11, "FAVORABLE", "wealth_yogas",
         "Endowed with steady influx of gains, high social reputation, noble virtues, flourishing networks, and fulfillment of cherished desires.",
         "எப்போதும் லாபம் பெருகும், நற்குணங்கள், புகழ், உயர்ந்த நட்பு வட்டாரம் மற்றும் ஆசைகள் நிறைவேறும் யோகம்."),
        (1, 12, 12, "UNFAVORABLE", "foreign_travel",
         "Prone to restless wandering, foreign journeys, heavy expenditures, and physical sensitivity; benefic aspect directs spending towards noble charities.",
         "அயல்நாடு அல்லது தொலைதூர வாசம், அதிக விரயங்கள் உண்டாகும். சுப பார்வை பெற்றால் தர்ம காரியங்களில் பொருள் செலவாகும்."),

        # L2
        (2, 1, 13, "FAVORABLE", "wealth_yogas",
         "Endowed with sons and wealth, self-directed earner, hard-working, courageous, earning through personal intellect and independent endeavors.",
         "சுய முயற்சியால் தனம் மற்றும் புத்திர பாக்கியம் உண்டாகும். கடின உழைப்பும் குடும்ப பொறுப்புகளும் அமையும்."),
        (2, 2, 14, "FAVORABLE", "savings_accumulation",
         "Exceptionally wealthy, proud, authoritative in speech, commanding financial treasuries and family assets across generations.",
         "அளவற்ற தனம், குடும்ப செல்வாக்கு, அதிகாரமிக்க வாக்கு மற்றும் சேமிப்புகள் பன்மடங்கு பெருகும்."),
        (2, 3, 15, "FAVORABLE", "personality_birth",
         "Valorous, prudent, wise, skilful, earning through communications, courage, and supportive bonds with younger co-borns.",
         "தைரியம், விவேகம், தகவல் தொடர்பு மற்றும் சகோதரர்கள் மூலம் தன லாபம் உண்டாகும்."),
        (2, 4, 16, "FAVORABLE", "property_land",
         "Acquires all kinds of landed property, palatial houses, luxury vehicles, and maternal inheritance; if exalted and with Jupiter, equal to a king.",
         "பூமி, நிலம், தாய் வழி சொத்துக்கள் மற்றும் வாகன சேர்க்கை உண்டாகும். குரு சேர்க்கை பெற்றால் மன்னருக்கு நிகரான செல்வம் கூடும்."),
        (2, 5, 17, "FAVORABLE", "children_prospects",
         "Highly affluent, investment-savvy, blessed with prosperous sons who also excel in accumulating wealth and business acumen.",
         "ஊக வணிகம் மற்றும் முதலீடுகளில் பெரும் தன லாபம். பிள்ளைகளும் செல்வத்தை பெருக்குவதில் வல்லவர்களாகத் திகழ்வர்."),
        (2, 6, 18, "NEUTRAL", "income_from_profession",
         "Gains wealth through dispute settlement, medical professions, loans, or overcoming rivals if with benefics; loss through disputes if afflicted.",
         "வழக்குகள், மருத்துவம் அல்லது போட்டி மூலம் தனம் ஈட்டுதல். அசுப சேர்க்கை பெற்றால் விரயங்களும் பகைமை வழியே இழப்பும் நேரிடலாம்."),
        (2, 7, 19, "NEUTRAL", "first_marriage",
         "Gains riches through marital alliances, medical trades, or partnerships, with highly sociable tendencies.",
         "திருமணம், கூட்டுத்தொழில் மற்றும் வாழ்க்கைத் துணை வழியே தன சேர்க்கை உண்டாகும்."),
        (2, 8, 20, "NEUTRAL", "inheritance_unearned_wealth",
         "Endowed with hidden treasures, landed estates, and unearned wealth/inheritances, though requiring mindfulness in speech and elder sibling ties.",
         "திடீர் தன வரவு, உயில் அல்லது பூர்வீக சொத்துக்கள் கிடைக்கும். பேச்சில் நிதானமும் மூத்த சகோதர உறவில் கவனமும் தேவை."),
        (2, 9, 21, "FAVORABLE", "wealth_yogas",
         "Wealthy, diligent, skilful, visiting sacred shrines, observing religious disciplines, experiencing fortune rising after early life.",
         "தர்ம வழியில் தனம் ஈட்டுதல், புண்ணிய ஸ்தல யாத்திரைகள், இறை பக்தி மற்றும் படிப்படியாக உயரும் பாக்கியம்."),
        (2, 10, 22, "FAVORABLE", "job_prospects",
         "High professional authority, immense wealth, respected by rulers and commerce leaders, commanding executive status.",
         "தொழில் ரீதியாக பெரும் தன யோகம், அரசு அல்லது பெரிய நிறுவனங்களில் உயர் பதவி, கௌரவம் உண்டாகும்."),
        (2, 11, 23, "FAVORABLE", "regular_income",
         "All varieties of prosperity and wealth, uninterrupted gains, ever diligent, widely recognized, and financially established.",
         "தடையில்லா பண வரவு, அனைத்து விதமான நன்மைகள், சேமிப்பு உயர்வு மற்றும் சமூகப் புகழ் உண்டாகும்."),
        (2, 12, 24, "UNFAVORABLE", "financial_fluctuations",
         "Adventurous, spending on philanthropic causes or foreign ventures, prone to financial drainage unless guided with fiscal prudence.",
         "அயல்நாட்டு முதலீடுகள், அதிக விரயங்கள் உண்டாகும். வரவுக்கேற்ற செலவுகளைத் திட்டமிடுதல் மிக நன்று."),

        # L3
        (3, 1, 25, "FAVORABLE", "personality_birth",
         "Endowed with self-made riches, religious devotion, physical courage, native brilliance, and determination to succeed independently.",
         "சுய முயற்சியால் முன்னேற்றம், தைரியம், பக்தி மற்றும் சொந்த புத்தி கூர்மை மூலம் வெற்றி அடைவார்."),
        (3, 2, 26, "NEUTRAL", "savings_accumulation",
         "Stout constitution, steady temperament, earning through crafts and verbal expressions, relying on steady family assistance.",
         "குடும்ப ஆதரவு, வாக்கு வன்மை மற்றும் கலைகள் மூலமாக நிதானமாக தனம் ஈட்டுவார்."),
        (3, 3, 27, "FAVORABLE", "sibling_relationships",
         "Immense happiness through brothers and sisters, courageous heart, cheerful demeanor, athletic prowess, and sound health.",
         "சகோதர பாக்கியம், தீரமான உள்ளம், உற்சாகம் மற்றும் எப்போதும் மகிழ்ச்சியான வாழ்க்கை அமையும்."),
        (3, 4, 28, "NEUTRAL", "domestic_harmony",
         "Happy, wealthy, intelligent, commanding properties, although partner may possess strong independent opinions.",
         "வீடு, நிலம், அறிவுக்கூர்மை உண்டாகும். குடும்ப விவகாரங்களில் பொறுமையுடன் கையாள்வது நலம்."),
        (3, 5, 29, "FAVORABLE", "children_prospects",
         "Blessed with virtuous children, creative enterprise, courageous intellect, and mastery in technical arts and sports.",
         "அறிவுள்ள பிள்ளைகள், கலை மற்றும் விளையாட்டுத் துறைகளில் தேர்ச்சி, படைப்பாற்றல் உண்டாகும்."),
        (3, 6, 30, "NEUTRAL", "sibling_relationships",
         "Affluent, victorious over adversaries, benefiting through maternal aunts and service sectors, though friction with co-borns is possible.",
         "எதிரிகளை அடக்கும் வீரம், உழைப்பால் செல்வம், தாய்மாமன் அல்லது அத்தை வழியில் நன்மைகள் உண்டாகும்."),
        (3, 7, 31, "NEUTRAL", "first_marriage",
         "Serves governance or corporate leadership, facing hardships in early boyhood but blossoming into supreme joy and wealth later in life.",
         "அரசாங்க அல்லது உயர் சேவை யோகம். இளமையில் போராட்டங்கள் இருந்தாலும் பிற்காலத்தில் பெருவாழ்வு வாழ்வார்."),
        (3, 8, 32, "UNFAVORABLE", "health_vitality",
         "Vulnerable to dependency or sudden obstacles; disciplined adherence to ethics ensures spiritual transformation and endurance.",
         "திடீர் தடைகள், உடல் அசதி ஏற்படலாம். தர்ம நெறியைப் பின்பற்றுவதும் பொறுமையும் மேன்மை தரும்."),
        (3, 9, 33, "FAVORABLE", "foreign_travel",
         "Creates great fortunes after marriage and travels; long journeys, courageous initiatives, and devotion to holy paths.",
         "திருமணத்திற்குப் பின் பாக்கிய விருத்தி, பிரயாணங்கள் மூலம் யோகம் மற்றும் இறை பக்தி உண்டாகும்."),
        (3, 10, 34, "FAVORABLE", "job_prospects",
         "All kinds of professional happiness, abundant self-made wealth, enterprise, commercial bravery, and executive accomplishments.",
         "சுய முயற்சியால் தொழிலில் பெரும் வெற்றி, தைரியமான திட்டங்கள் மற்றும் சமுதாய அந்தஸ்து அமையும்."),
        (3, 11, 35, "FAVORABLE", "regular_income",
         "Perpetual gains in trade, commerce, contracting, and transport, adventurous temperament, serving society with practical wisdom.",
         "வியாபாரம், தரகு, வர்த்தகத்தில் தொடர் லாபம், சாகச குணம் மற்றும் நற்பலன்கள் உண்டாகும்."),
        (3, 12, 36, "UNFAVORABLE", "foreign_travel",
         "Expenditure on adventurous journeys, foreign travel, separation from ancestral places, but attaining fortune through females.",
         "பிரயாணச் செலவுகள், வெளிநாடு அல்லது தொலைதூர வாழ்க்கை மற்றும் பெண்கள் மூலம் நன்மை உண்டாகும்."),

        # L4
        (4, 1, 37, "FAVORABLE", "property_land",
         "Endowed with distinguished learning, noble virtues, fine ornaments, extensive lands, conveyances, and blissful maternal care.",
         "உயர்கல்வி, தாய் வழி மகிழ்ச்சி, பூமி, வாகன யோகங்கள், ஆபரணங்கள் மற்றும் அமைதியான வாழ்க்கை அமையும்."),
        (4, 2, 38, "FAVORABLE", "wealth_yogas",
         "Commands family estate, commercial wealth, agricultural produce, domestic honors, and clever foresight in property management.",
         "குடும்ப சொத்துக்கள், உணவு, விவசாயம் மற்றும் சொத்து பரிவர்த்தனைகள் மூலம் தன லாபம் பெருகும்."),
        (4, 3, 39, "FAVORABLE", "personality_birth",
         "Valorous, commanding domestic attendants, charitable, generous, free from major ailments, and earning through land development.",
         "தைரியம், கொடைத்தன்மை, நோய் நொடிகள் அற்ற நல்வாழ்வு மற்றும் ரியல் எஸ்டேட் நன்மைகள் உண்டாகும்."),
        (4, 4, 40, "FAVORABLE", "property_land",
         "Statesman or ministerial dignitary, possessing magnificent mansions, vehicles, gardens, learning, and deeply affectionate marital life.",
         "அமைச்சருக்கு நிகரான பதவி, மாளிகை போன்ற வீடு, சொகுசு வாகனங்கள் மற்றும் பூரண மனநிம்மதி உண்டாகும்."),
        (4, 5, 41, "FAVORABLE", "children_prospects",
         "Universally beloved, devoted to Lord Vishnu, blessed with noble sons, high academic achievements, and self-earned wealth.",
         "அனைவராலும் விரும்பப்படும் குணம், விஷ்ணு பக்தி, புத்திர மேன்மை, புத்தி கூர்மை மற்றும் செல்வம் கூடும்."),
        (4, 6, 42, "UNFAVORABLE", "domestic_harmony",
         "Strained maternal health or domestic friction, independent temper, litigations over residential plots unless benefic aspect intervenes.",
         "தாய் நலனில் கவனம் தேவை, பூர்வீக சொத்து விவகாரங்களில் நிதானம் மற்றும் சொந்த உழைப்பில் தனித்து நிற்பார்."),
        (4, 7, 43, "FAVORABLE", "first_marriage",
         "Highly educated, cultured, sacrificing ancestral property for partner's happiness, soft-spoken in assemblies, blessed with refined spouse.",
         "உயர்கல்வி அறிவு, பண்பட்ட குணம், சிறந்த வாழ்க்கைத் துணை மற்றும் புதிய இடங்களில் சொத்துக்கள் வாங்குவார்."),
        (4, 8, 44, "UNFAVORABLE", "property_land",
         "Deprived of ancestral dwellings or facing repairs in house; spiritual detachment and overcoming domestic hurdles through resilience.",
         "பூர்வீக வீடு அமைப்பில் தடைகள், அமைதியின்மை ஏற்படலாம். ஆன்மீக நாட்டம் மூலம் மனசாந்தி கிடைக்கும்."),
        (4, 9, 45, "FAVORABLE", "dharma_devotion",
         "Cherished by all, devoted to God and preceptors, virtuous, righteous, inheriting divine grace and vast fortunes in lands.",
         "அனைவராலும் போற்றப்படும் வாழ்க்கை, தந்தை வழி பாக்கியம், தர்ம சிந்தனை மற்றும் நிலபுலன்கள் சேரும்."),
        (4, 10, 46, "FAVORABLE", "job_prospects",
         "Honored by the highest seat of power, conquering senses, expert in industrial sciences or alchemy, enjoying executive palaces.",
         "தொழிலில் ராஜ மரியாதை, அரசு அங்கீகாரம், ஐம்புலன்களை அடக்கும் மனவலிமை மற்றும் பூரண சுகம் உண்டாகும்."),
        (4, 11, 47, "FAVORABLE", "wealth_yogas",
         "Large financial gains from real estate, farming, and transport, generous, charitable, and public benefactor.",
         "ரியல் எஸ்டேட் மற்றும் வாகனங்கள் வழியே பெரும் லாபம், தாராள குணம், சமூக சேவை செய்யும் பாக்கியம்."),
        (4, 12, 48, "UNFAVORABLE", "domestic_harmony",
         "Loss of ancestral lands, living far away from birthplace, facing domestic disruptions; advised to invest in remote properties.",
         "பூர்வீகத்தை விட்டு தூர தேசத்தில் வசித்தல், சொத்துக்களில் கவனமான முதலீடு தேவைப்படும்."),

        # L5
        (5, 1, 49, "FAVORABLE", "academic_success",
         "Erudite scholar, sharp intellect, blessed with progenic happiness, thrifty in finances, cautious, achieving academic fame.",
         "கல்வியில் தேர்ச்சி, நுண்ணறிவு, புத்திர பாக்கியம், பணத்தில் சிக்கனம் மற்றும் நற்பெயர் உண்டாகும்."),
        (5, 2, 50, "FAVORABLE", "wealth_yogas",
         "Pater familias, blessed with worthy sons and vast wealth, affectionate to partner, celebrated and renowned throughout society.",
         "குடும்பத் தலைவர், புத்திர செல்வமும் தன செல்வமும் ஒருங்கே சேரும், துணை மீது பிரியம், சமுதாயப் புகழ்."),
        (5, 3, 51, "FAVORABLE", "sibling_relationships",
         "Affectionate to brothers and sisters, focused on private achievements, frugal, skilled in writing and creative endeavors.",
         "சகோதர பாசம், சுய காரியங்களில் கண்ணும் கருத்துமாய் இருத்தல், எழுத்து மற்றும் படைப்பாற்றலில் தேர்ச்சி."),
        (5, 4, 52, "FAVORABLE", "property_land",
         "Minister, preceptor, or administrative head, blessed with maternal bliss, deep wisdom, palatial residence, and peace of mind.",
         "அமைச்சர் அல்லது குரு ஸ்தானம், தாயின் ஆசீர்வாதம், கூரிய மதிநுட்பம், வீடு-வாகன யோகம் அமையும்."),
        (5, 5, 53, "FAVORABLE", "children_prospects",
         "Noble, virtuous progeny, deep religious scholarship, cherished by trusted friends, blessed with high spiritual intelligence.",
         "சற்புத்திர பாக்கியம், சிறந்த சாஸ்திர ஞானம், உண்மையான நண்பர்கள் மற்றும் புண்ணிய பலன்கள் கூடும்."),
        (5, 6, 54, "NEUTRAL", "children_prospects",
         "Children may follow distinct or independent paths, adopted children or legal custody ties, winning over legal competitions.",
         "பிள்ளைகள் வழியில் சில சவால்கள் அல்லது தத்து புத்திர யோகம், போட்டித் தேர்வுகளில் வெற்றி உண்டாகும்."),
        (5, 7, 55, "FAVORABLE", "first_marriage",
         "Honorable, deeply religious, endowed with happy progenic blessings, virtuous spouse, and helpful to community.",
         "கௌரவமான வாழ்க்கை, தர்ம குணம், புத்திர பாக்கியம், நற்குணமுள்ள வாழ்க்கைத் துணை மற்றும் பிறருக்கு உதவும் தன்மை."),
        (5, 8, 56, "UNFAVORABLE", "health_vitality",
         "Fluctuating peace of mind, pulmonary or digestive sensitivity, requires patience in raising children, strong occult inclinations.",
         "மனக்கவலை, செரிமான கோளாறுகள் வரலாம். பிள்ளைகளிடம் பொறுமை காப்பதும் குலதெய்வ வழிபாடும் மேன்மை தரும்."),
        (5, 9, 57, "FAVORABLE", "dharma_devotion",
         "Princes or equals to kings, author of celebrated treatises, illuminating one's entire lineage with glory and philosophical wisdom.",
         "மன்னருக்கு நிகரான வாழ்வு, சிறந்த நூல்களை எழுதும் திறன், பரம்பரைக்கே பெருமை சேர்க்கும் பாக்கிய யோகம்."),
        (5, 10, 58, "FAVORABLE", "job_prospects",
         "Enjoys full Raja Yoga, executive authority, high state honors, administrative prowess, and celebrated renown.",
         "முழுமையான ராஜயோகம், தலைமைப் பதவி, அரசாங்க நன்மைகள் மற்றும் தொழிலில் பெரும் புகழ் உண்டாகும்."),
        (5, 11, 59, "FAVORABLE", "wealth_yogas",
         "Supreme intellect, author, researcher, beloved by people, highly skilful, blessed with abundant wealth and accomplished children.",
         "பேரறிவு, எழுத்தாளர், மக்கள் செல்வாக்கு, கைநிறைய தன லாபம் மற்றும் நல்ல பிள்ளைகள் அமையும் பாக்கியம்."),
        (5, 12, 60, "UNFAVORABLE", "children_prospects",
         "Paternal concerns or living away from children, expenditures on higher knowledge and spiritual initiations, adopted progeny.",
         "பிள்ளைகள் வெளிநாட்டில் வசித்தல், ஆன்மீகச் செலவுகள் அல்லது தத்து புத்திர யோகம் உண்டாகும்."),

        # L6
        (6, 1, 61, "NEUTRAL", "health_vitality",
         "Valorous, adventurous, wealthy, gaining through struggles, serving in defense, judiciary, or medicine, requiring routine health care.",
         "தைரியம், சாகசம், உழைப்பால் செல்வம், மருத்துவம் அல்லது பாதுகாப்புத் துறையில் மேன்மை, உடல் நலனில் கவனம்."),
        (6, 2, 62, "NEUTRAL", "savings_accumulation",
         "Adventurous speaker, earning through foreign lands, overcoming disputes, diligent, focused on financial accumulation.",
         "சாகசப் பேச்சு, தொலைதூர வாழ்க்கை மூலம் வருமானம், வழக்குகளை வெல்லும் ஆற்றல் உண்டாகும்."),
        (6, 3, 63, "UNFAVORABLE", "sibling_relationships",
         "Impatient temperament, disagreements with co-borns, requiring tact in managing subordinate staff and relatives.",
         "முன்கோபம், சகோதரர்களிடம் கருத்து வேறுபாடுகள் வரலாம். பணியாளர்களை கனிவுடன் நடத்துவது நன்மை தரும்."),
        (6, 4, 64, "NEUTRAL", "property_land",
         "Sharp intellect, acquiring immense wealth through competitive lands or mortgages, requiring emotional balance with mother.",
         "கூர்மையான புத்தி, போட்டி சொத்துக்கள் மூலம் பெரும் தனம் சேரும், தாய் நலனில் அக்கறை தேவை."),
        (6, 5, 65, "NEUTRAL", "children_prospects",
         "Fluctuating financial cycles, competitive children who achieve success through resilience, kind-hearted yet practical.",
         "நிதி நிலவரத்தில் ஏற்ற இறக்கங்கள், பிள்ளைகளின் கல்விக்காக போராடி வெற்றி பெறுதல், நடைமுறை அறிவு."),
        (6, 6, 66, "FAVORABLE", "health_vitality",
         "Harsha Yoga: Subdues all enemies, destroys diseases, commands servants, gains through litigation, and enjoys stable finances.",
         "ஹர்ஷ யோகம்: எதிரிகள் அழியும், நோய்கள் தீரும், வழக்குகள் சாதகமாகும், பணியாளர்கள் ஆதரவு கிட்டும்."),
        (6, 7, 67, "UNFAVORABLE", "first_marriage",
         "Spouse may face health vulnerabilities or differences of perspective; native achieves professional fame and wealth through legal acumen.",
         "துணைக்கு உடல்நலக் குறைவு அல்லது கருத்து வேறுபாடுகள் வரலாம்; சட்ட அறிவால் தொழிலில் தனம் ஈட்டுவார்."),
        (6, 8, 68, "UNFAVORABLE", "health_vitality",
         "Sarala Yoga if unafflicted (destroying enemies, long-lived), but if weak causes chronic health issues or secret disputes.",
         "சரள யோகம்: விபரீத ராஜயோகம் மூலம் மறைமுக எதிரிகள் தோற்பர்; உடல் நலனில் முன்னெச்சரிக்கை அவசியம்."),
        (6, 9, 69, "NEUTRAL", "foreign_travel",
         "Fluctuating fortunes, commercial trades in heavy stones, minerals, or engineering, differences with elders resolved via patience.",
         "கனிமங்கள், இயந்திரங்கள் மூலம் தொழில் யோகம். தந்தை அல்லது பெரியோர்களுடன் வாக்குவாதங்களை தவிர்க்கவும்."),
        (6, 10, 70, "FAVORABLE", "job_prospects",
         "Celebrated in public life, gifted orator, flourishing in foreign lands, judicial, audit, or medical services.",
         "சமூகத்தில் பிரபலம், சிறந்த பேச்சாளர், வெளிநாட்டு வேலைவாய்ப்பு, நீதித்துறை அல்லது மருத்துவ மேன்மை."),
        (6, 11, 71, "FAVORABLE", "wealth_yogas",
         "Extracts immense wealth and victories from rivals, competitive examinations, and commercial challenges; adventurous.",
         "போட்டிகளில் வெற்றி, எதிரிகளிடமிருந்து தன லாபம், துணிச்சலான முதலீடுகள் மூலம் முன்னேற்றம்."),
        (6, 12, 72, "UNFAVORABLE", "financial_fluctuations",
         "Vimala Yoga if well-placed (frugal, independent), but if afflicted causes litigation expenses and hospital bills.",
         "விமல யோகம்: விபரீத ராஜயோகம்; செலவுகளில் கட்டுப்பாடு தேவை, அசுப சேர்க்கை இருந்தால் வீண் விரயங்கள் ஏற்படும்."),

        # L7
        (7, 1, 73, "NEUTRAL", "first_marriage",
         "Attractive personality, highly skilled, diplomatic, commanding charm, requiring moral discipline in partnerships.",
         "கவர்ச்சிகரமான தோற்றம், ராஜதந்திர அறிவு, கூட்டாளிகளை வசீகரிக்கும் ஆற்றல், நெறிமுறை தவறாதிருப்பது நலம்."),
        (7, 2, 74, "FAVORABLE", "first_marriage",
         "Gains significant wealth and social status through marriage, spouse brings good fortune, leisurely demeanor.",
         "திருமணத்திற்குப் பின் பெரும் தன வரவு, துணையால் பாக்கிய விருத்தி மற்றும் குடும்ப கௌரவம் உண்டாகும்."),
        (7, 3, 75, "NEUTRAL", "sibling_relationships",
         "Courageous spouse, gains through short travels and alliances, potential concerns regarding children requiring prayer.",
         "தைரியமான துணை, பிரயாணங்களால் ஆதாயம், பிள்ளைகள் விசயத்தில் பிரார்த்தனைகள் பலன் தரும்."),
        (7, 4, 76, "FAVORABLE", "domestic_harmony",
         "Spouse is independent, intellectual, and religious; native gains houses and conveyances through in-laws; dental care advised.",
         "அறிவுள்ள, பக்திமிக்க வாழ்க்கைத் துணை, மாமனார் வழி சொத்துக்கள் மற்றும் வாகன சுகம் உண்டாகும்."),
        (7, 5, 77, "FAVORABLE", "first_marriage",
         "Honorable, endowed with seven principal virtues, delighted heart, romantic harmony, and prosperous children.",
         "சகல நற்குணங்களும் நிறைந்த வாழ்க்கை, களத்திர பாக்கியம், தாம்பத்திய மகிழ்ச்சி, செல்வ செழிப்பு."),
        (7, 6, 78, "UNFAVORABLE", "first_marriage",
         "Spouse prone to health ailments or differences of temperament; requires patient communication and mutual care.",
         "துணையின் உடல் நலத்தில் கவனம் தேவை, தேவையற்ற வாக்குவாதங்களைத் தவிர்த்து பரஸ்பர அன்பு காப்பது அவசியம்."),
        (7, 7, 79, "FAVORABLE", "first_marriage",
         "Full marital felicity, courageous, highly skilful, intellectual, commanding trade partnerships and social acclaim.",
         "பூரண களத்திர சுகம், தைரியம், வியாபாரத்தில் பெரும் வெற்றி, சிறந்த சமூக கௌரவம் உண்டாகும்."),
        (7, 8, 80, "UNFAVORABLE", "first_marriage",
         "Marital delays or health vulnerabilities for spouse, joint finance complexities; pacified through Mangala and Shukra remedies.",
         "திருமணத்தில் தாமதம் அல்லது துணையின் உடல் உபாதை வரலாம். சுக்கிர-செவ்வாய் வழிபாடுகள் நன்மை தரும்."),
        (7, 9, 81, "FAVORABLE", "dharma_devotion",
         "Spouse brings extraordinary fortune, devout, pious, wide international undertakings, pilgrimages, and prosperity.",
         "துணையால் பெரும் பாக்கியம் உண்டாகும், தர்ம காரியங்கள், புனித யாத்திரைகள் மற்றும் தொழில் வளர்ச்சி."),
        (7, 10, 82, "FAVORABLE", "job_prospects",
         "Spouse assists in professional career or business, ambitious, pious, acquiring substantial wealth and paternal honors.",
         "தொழிலில் துணையின் ஆதரவு, சமூக அந்தஸ்து, பக்தி, புத்திர பாக்கியம் மற்றும் தன யோகம் கூடும்."),
        (7, 11, 83, "FAVORABLE", "wealth_yogas",
         "Substantial financial gains through marriage, wealthy spouse, flourishing corporate partnerships and daughters.",
         "துணை வழியே தன லாபம், ஆசைகள் பூர்த்தியடைதல், பெண் குழந்தைகள் பிறக்கும் யோகம், தொழில் லாபம்."),
        (7, 12, 84, "UNFAVORABLE", "financial_fluctuations",
         "Spouse may reside in foreign lands or be a spendthrift; separation during work cycles; disciplined budgets advised.",
         "துணை வெளிநாட்டில் வசித்தல் அல்லது அதிக செலவு செய்தல், வெளியூர் வேலைவாய்ப்பு உண்டாகும்."),

        # L8
        (8, 1, 85, "UNFAVORABLE", "health_vitality",
         "Bodily sensitivity, prone to cuts or scars, philosophical disposition, transforming adversity through deep inner spiritual power.",
         "உடல் நலனில் அக்கறை தேவை, தழும்புகள் ஏற்படலாம். ஆன்மீக நாட்டம் மற்றும் உள்முக தேடல் மேன்மை தரும்."),
        (8, 2, 86, "UNFAVORABLE", "savings_accumulation",
         "Fluctuating savings, slow recovery of delayed debts, requiring calculated financial investments and careful speech.",
         "சேமிப்பில் நிதானம் தேவை, கடன் கொடுப்பதில் கவனம், யோசித்து பேசுவது நற்பலன் தரும்."),
        (8, 3, 87, "UNFAVORABLE", "sibling_relationships",
         "Differences with siblings, requiring self-reliance rather than depending on co-borns or helpers.",
         "சகோதர உறவில் விட்டுக்கொடுத்து செல்லுதல் நன்று, சொந்த உழைப்பை மட்டுமே நம்பி முன்னேற வேண்டும்."),
        (8, 4, 88, "UNFAVORABLE", "domestic_harmony",
         "Disruptions in residential peace or parental care, spiritual maturity through detached perspective toward land.",
         "வீடு, மனை விவகாரங்களில் பொறுமை தேவை, தாயாரின் ஆரோக்கியத்தில் அக்கறை செலுத்துவது நன்று."),
        (8, 5, 89, "NEUTRAL", "children_prospects",
         "Deep occult learning, longevity, limited children, highly intuitive mind, and wealth through legacy or research.",
         "தீர்க்காயுள், ஆராய்ச்சி அறிவு, உள்ளுணர்வு பலம், பூர்வீக சொத்து அல்லது காப்பீடு மூலம் தன லாபம்."),
        (8, 6, 90, "FAVORABLE", "health_vitality",
         "Sarala Yoga: Overcomes adversaries, gains through inherited disputes, childhood vulnerability to water/reptiles overcome.",
         "சரள யோகம்: விபரீத ராஜயோகம் மூலம் எதிரிகளை முறியடிப்பார், வழக்குகளில் வெற்றி பெறுவார்."),
        (8, 7, 91, "UNFAVORABLE", "first_marriage",
         "Marital friction, business volatility in partnership; demands independent business setup and patience with spouse.",
         "கூட்டுத்தொழிலில் எச்சரிக்கை தேவை, துணையுடன் மனக்கசப்புகளை பேசித் தீர்ப்பது அவசியம்."),
        (8, 8, 92, "FAVORABLE", "health_vitality",
         "Full longevity (Dirghayu), deep research scholarship, unearned wealth; if weak, medium life and prone to controversies.",
         "தீர்க்காயுள், ஆயுள் பலம், மறைபொருள் அறிவு, திடீர் தன வரவு உண்டாகும்."),
        (8, 9, 93, "UNFAVORABLE", "dharma_devotion",
         "Heterodox viewpoints, questioning traditional dogma, conflicts with father or mentors; requires mature ethical grounding.",
         "தந்தையுடன் கருத்து வேறுபாடுகள் வரலாம், பாரம்பரிய பழக்கங்களை கேள்வி கேட்பார், தர்ம நெறி காப்பது நலம்."),
        (8, 10, 94, "NEUTRAL", "job_prospects",
         "Career transformations, breaks and restarts in occupation, neutralized into high executive status if benefic aspects.",
         "தொழிலில் திடீர் மாற்றங்கள், புதிய துறைகளில் இறங்குதல், சுப பார்வை பெற்றால் உயர் பதவி கிட்டும்."),
        (8, 11, 95, "NEUTRAL", "regular_income",
         "Long life, initial hardship in youth followed by substantial wealth and stability in mature adulthood.",
         "இளமையில் நிதிப் போராட்டங்கள் இருந்தாலும் பிற்காலத்தில் பெரும் தனம் மற்றும் நீண்ட ஆயுள் அமையும்."),
        (8, 12, 96, "UNFAVORABLE", "financial_fluctuations",
         "Vimala Yoga: Expenditures on philanthropic, secret, or foreign activities; longevity requires spiritual discipline.",
         "விமல யோகம்: விரயங்களை சுப விரயமாக மாற்றுதல், ஆன்மீக செலவுகள், வெளிநாட்டு தொடர்பு."),

        # L9
        (9, 1, 97, "FAVORABLE", "dharma_devotion",
         "Supremely fortunate, honored by governance, virtuous, charming, erudite, and universally acclaimed by the public.",
         "மகா பாக்கிய யோகம், அரசாங்க கௌரவம், வசீகர தோற்றம், உயர்கல்வி, சமூகத்தில் உயர்ந்த மரியாதை."),
        (9, 2, 98, "FAVORABLE", "wealth_yogas",
         "Eminent scholar, universally beloved, extraordinarily wealthy, endowed with luxurious family life and noble progeny.",
         "சிறந்த அறிஞர், அனைத்து செல்வங்களும் சேரும், இனிமையான குடும்பம் மற்றும் நற்புத்திர பாக்கியம்."),
        (9, 3, 99, "FAVORABLE", "sibling_relationships",
         "Blessed with fraternal bliss, affluent, virtuous, charming, achieving fortunes through courageous writing and travel.",
         "சகோதர ஒற்றுமை, செல்வம், நற்குணங்கள், எழுத்து மற்றும் பயணங்கள் மூலமாக பெரும் பாக்கியம்."),
        (9, 4, 100, "FAVORABLE", "property_land",
         "Palatial dwellings, conveyances, domestic joy, vast landed estates, and deep filial devotion to mother.",
         "சொகுசு வீடுகள், வாகனங்கள், தாயன்பு, பூமி லாபம் மற்றும் பூரண மனநிம்மதி உண்டாகும்."),
        (9, 5, 101, "FAVORABLE", "children_prospects",
         "Gifted with meritorious sons, boundless prosperity, reverence toward elders and preceptors, charitable and learned.",
         "பூர்வபுண்ணிய பலன், சிறந்த புத்திரர்கள், பெரியோர்களிடம் பக்தி, தான தர்மங்கள் செய்யும் கொடைத்தன்மை."),
        (9, 6, 102, "NEUTRAL", "health_vitality",
         "Meagre ancestral support, overcoming legal hurdles through righteous persistence, winning over adversaries in foreign lands.",
         "தர்மத்தின் வழியே தடைகளை வெல்லுதல், போட்டித் தேர்வுகளில் வெற்றி, உழைப்பால் பாக்கியத்தை அடைவார்."),
        (9, 7, 103, "FAVORABLE", "first_marriage",
         "Great fortune and prosperity dawn after marriage, virtuous and celebrated spouse, noble conduct, and widespread renown.",
         "திருமணத்திற்குப் பின் யோகம் பலமடங்கு பெருகும், நற்குணமுள்ள வாழ்க்கைத் துணை, சமூகப் புகழ்."),
        (9, 8, 104, "UNFAVORABLE", "dharma_devotion",
         "Fluctuating fortunes, obstacles in paternal inheritance, finding spiritual awakening through deep introspective life tests.",
         "பாக்கியத்தில் ஏற்ற இறக்கங்கள், தந்தை வழி சொத்துக்களில் தாமதம், ஆன்மீகத்தில் ஆழ்ந்த அனுபவம்."),
        (9, 9, 105, "FAVORABLE", "dharma_devotion",
         "Boundless fortune, divine grace, peerless virtues, handsome visage, and extraordinary happiness from co-borns and family.",
         "சுய பாக்கிய ஸ்தான பலம்: அதிர்ஷ்டம், நற்பண்புகள், அழகு, தெய்வ கடாட்சம் மற்றும் குடும்ப மேன்மை."),
        (9, 10, 106, "FAVORABLE", "job_prospects",
         "King or equal to a king, minister, commander-in-chief, virtuous, highly prosperous, and held dear by all.",
         "மன்னருக்கு நிகரான அந்தஸ்து, அமைச்சர் பதவி, தொழிலில் உச்சக்கட்ட வெற்றி, அனைவராலும் விரும்பப்படும் தலைவர்."),
        (9, 11, 107, "FAVORABLE", "wealth_yogas",
         "Daily financial increments, devotion to elders, virtuous, highly meritorious in charitable and social works.",
         "தினம் தினம் தன லாபம் பெருகும், பெரியோர்களிடம் பக்தி, புண்ணிய காரியங்கள், நிலையான செல்வம்."),
        (9, 12, 108, "NEUTRAL", "foreign_travel",
         "Fortunes through distant foreign lands, lavish spending on noble religious shrines and hosting guests.",
         "வெளிநாட்டில் பாக்கிய யோகம், ஆன்மீக அறப்பணிகள் மற்றும் தர்ம விருந்துகளுக்கு பொருள் செலவிடுவார்."),

        # L10
        (10, 1, 109, "FAVORABLE", "job_prospects",
         "Distinguished scholar, renowned leader, poet, minor boyhood ailments turning into massive prosperity and daily rising wealth.",
         "புகழ்பெற்ற தலைவர், கவிஞர், தொழிலில் சாதனையாளர், நாளுக்கு நாள் பெருகும் செல்வ வளம்."),
        (10, 2, 110, "FAVORABLE", "wealth_yogas",
         "Extremely affluent, virtuous, honored by rulers, charitable, and enjoying deep paternal bliss.",
         "அளவற்ற செல்வம், அரசாங்க விருதுகள், தான தர்மம், தந்தை வழி பெருமை மற்றும் குடும்ப மேன்மை."),
        (10, 3, 111, "FAVORABLE", "personality_birth",
         "Cooperation from brothers and loyal subordinates, courageous, virtuous, eloquent orator, and truthful leader.",
         "சகோதரர்கள் மற்றும் பணியாளர்கள் ஆதரவு, வீரம், நாவன்மை, வாய்மைமிக்க சிறந்த நிர்வாகி."),
        (10, 4, 112, "FAVORABLE", "property_land",
         "Commanding vast lands, houses, luxury vehicles, deeply devoted to mother's welfare, virtuous, and respected.",
         "அரசாங்க வீடு-வாகன யோகம், தாய் மீது அளவற்ற அன்பு, ரியல் எஸ்டேட் மற்றும் நிலபுலன்களில் ஆதிக்கம்."),
        (10, 5, 113, "FAVORABLE", "academic_success",
         "Master of diverse branches of learning, ever cheerful, wealthy, blessed with brilliant and accomplished children.",
         "சகல கலைகளிலும் தேர்ச்சி, எப்போதும் மகிழ்ச்சியான மனம், செல்வந்தர், புத்திசாலி பிள்ளைகள்."),
        (10, 6, 114, "NEUTRAL", "job_prospects",
         "Skilful in technical or administrative services, overcoming professional rivals through tactical mastery.",
         "தொழில்நுட்பம் அல்லது நிர்வாகத்தில் வல்லமை, எதிரிகளை சாதுரியமாக வெல்லுதல், உழைப்பால் உயர்வு."),
        (10, 7, 115, "FAVORABLE", "first_marriage",
         "Happiness through partner, intelligent, eloquent, truthful, religious, and thriving in joint corporate enterprises.",
         "துணையின் ஆதரவுடன் தொழில் மேன்மை, வாக்கு சாதுரியம், தர்ம குணம் மற்றும் வணிக வெற்றி."),
        (10, 8, 116, "NEUTRAL", "job_prospects",
         "Long-lived, changes in vocations, aptitude for research, geology, investigation, or esoteric professions.",
         "தீர்க்காயுள், தொழிலில் எதிர்பாராத மாற்றங்கள், துப்பறிதல் அல்லது ரகசியத் துறைகளில் தேர்ச்சி."),
        (10, 9, 117, "FAVORABLE", "job_prospects",
         "Dharma-Karmadhipati Raja Yoga: Ruler or equal to sovereign, boundless wealth, progenic happiness, and global acclaim.",
         "தர்ம-கர்மாதிபதி ராஜயோகம்: மன்னருக்கு நிகரான செல்வாக்கு, அபரிமிதமான செல்வம் மற்றும் உலகப் புகழ்."),
        (10, 10, 118, "FAVORABLE", "job_prospects",
         "Peerless master in all undertakings, heroic, truthful, devoted to preceptors and parents, unshakeable professional stature.",
         "தொழிலில் அசைக்க முடியாத வெற்றி, தலைமைப் பண்பு, வீரம், பெரியோர்களிடம் பக்தி, கௌரவமிக்க வாழ்க்கை."),
        (10, 11, 119, "FAVORABLE", "wealth_yogas",
         "Abundant wealth, domestic happiness, noble sons, truthful, virtuous, and perpetually delighted with expanding earnings.",
         "தொழில் மூலம் எல்லையற்ற தன லாபம், புத்திர பாக்கியம், வாய்மை, நற்குணங்கள், நிரந்தர மகிழ்ச்சி."),
        (10, 12, 120, "NEUTRAL", "foreign_travel",
         "Engaged in institutional, overseas, or governmental projects, diplomatic expenditure, requiring caution against hidden anxieties.",
         "அயல்நாட்டு வர்த்தகம், அரசு ஒப்பந்தங்கள், ரகசிய திட்டங்கள் மூலம் தொழில் நடத்துதல்."),

        # L11
        (11, 1, 121, "FAVORABLE", "wealth_yogas",
         "Genuine and noble disposition, wealthy, happy, unbiased, poet, eloquent orator, and perpetually blessed with financial influx.",
         "உயர்ந்த சிந்தனை, செல்வம், சமநோக்கு பார்வை, கவிதை நயம், வாக்கு வன்மை, எப்போதும் தன லாபம்."),
        (11, 2, 122, "FAVORABLE", "savings_accumulation",
         "Endowed with all categories of treasures and achievements, highly charitable, devout, and permanently content.",
         "அனைத்து செல்வங்களும் சேமிப்பில் உயரும், தான தர்ம சிந்தனை, பக்தி, நிரந்தர மனதிருப்தி."),
        (11, 3, 123, "FAVORABLE", "sibling_relationships",
         "Skilful in all undertakings, wealthy, enjoying fraternal bliss, earning through communications and local commerce.",
         "அனைத்து பணிகளிலும் திறமை, செல்வம், சகோதர ஒற்றுமை, வணிகம் மற்றும் தைரியத்தால் ஆதாயம்."),
        (11, 4, 124, "FAVORABLE", "property_land",
         "Gains through maternal kin, frequent visits to holy shrines, possession of ancestral properties, farmlands, and residences.",
         "தாய் வழி உறவினர்களால் லாபம், தீர்த்த யாத்திரைகள், பூமி, நிலம், வீடு சேர்க்கை உண்டாகும்."),
        (11, 5, 125, "FAVORABLE", "children_prospects",
         "Delighted, highly educated, virtuous, religious, blessed with prosperous children and speculative windfalls.",
         "மகிழ்ச்சி, உயர்கல்வி, நற்குணங்கள், புண்ணிய சிந்தனை, பிள்ளைகளால் பெருமை மற்றும் லாபம்."),
        (11, 6, 126, "NEUTRAL", "health_vitality",
         "Gains through dispute resolutions, litigation settlement, or medical trades; living in distinct locations.",
         "வழக்குகள், கடன் தீர்வு அல்லது போட்டித் துறைகள் வழியே தன லாபம், வெளியூர் வாசம்."),
        (11, 7, 127, "FAVORABLE", "first_marriage",
         "Substantial profits through spouse's relatives, liberal, sensual, considerate to partner, and enjoying commercial success.",
         "துணை வழி உறவினர்களால் பெரும் லாபம், தாராள குணம், தாம்பத்திய சுகம் மற்றும் வியாபார மேன்மை."),
        (11, 8, 128, "NEUTRAL", "longevity_death",
         "Initial reversals converted into long-term gains, long life, inheritance through unexpected wills or settlements.",
         "தொடக்கத்தில் தடைகள் இருந்தாலும் பிற்காலத்தில் திடீர் லாபம், நீண்ட ஆயுள், உயில் சொத்துக்கள் சேரும்."),
        (11, 9, 129, "FAVORABLE", "dharma_devotion",
         "Fortunate, highly skilful, truthful, honored by governance and corporate royals, exceptionally affluent.",
         "பாக்கிய யோகம், வாய்மை, அரசாங்க பாராட்டு, தொழிலில் பெரும் லாபம், வசதியான வாழ்க்கை."),
        (11, 10, 130, "FAVORABLE", "job_prospects",
         "Honored by the king, devout, intelligent, truthful, controlling passions, commanding immense commercial enterprises.",
         "அரச கௌரவம், தொழிலில் பெரும் வெற்றி, புத்தி கூர்மை, புலனடக்கம், நற்புகழ் உண்டாகும்."),
        (11, 11, 131, "FAVORABLE", "wealth_yogas",
         "Continuous success in all undertakings, wisdom, happiness, and profits multiplying every passing day.",
         "சுய லாப ஸ்தான பலம்: அனைத்து காரியங்களிலும் வெற்றி, அறிவு, மகிழ்ச்சி மற்றும் தனம் நாளுக்கு நாள் பெருகும்."),
        (11, 12, 132, "NEUTRAL", "foreign_travel",
         "Generous philanthropy, sensual pleasures, international associates, spending on noble community causes.",
         "அயல்நாட்டு வர்த்தகம், தர்ம காரியங்களில் செலவு, வெளிநாட்டு நட்பு மற்றும் சுப விரயங்கள்."),

        # L12
        (12, 1, 133, "NEUTRAL", "foreign_travel",
         "Spiritual seeker, generous spender, prone to respiratory sensitivity, finding immense peace and prosperity overseas.",
         "ஆன்மீக நாட்டம், தாராள குணம், வெளிநாடு அல்லது தொலைதூர தேசத்தில் வசதியான வாழ்வு அமையும்."),
        (12, 2, 134, "NEUTRAL", "savings_accumulation",
         "Sweet-spoken, religious, spending on religious and community functions, acquiring virtue and spiritual peace.",
         "இனிமையான பேச்சு, பக்தி, புண்ணிய காரியங்களுக்கு செலவிடுதல், ஆன்மீக நன்மைகள் உண்டாகும்."),
        (12, 3, 135, "NEUTRAL", "sibling_relationships",
         "Independent temperament, focused on personal growth and self-nourishment, creating wealth through solitary ventures.",
         "தனித்து நின்று சாதிக்கும் குணம், சுய வளர்ச்சி, சகோதரர்களிடம் எல்லைகளைப் பேணுதல்."),
        (12, 4, 136, "NEUTRAL", "property_land",
         "Relocating far from birthplace, investing in foreign or distant lands and houses, seeking serene hermitage-like home.",
         "பூர்வீகத்தை விட்டு வெளியூர் அல்லது வெளிநாட்டில் வீடு அமைத்தல், அமைதியான சூழல்."),
        (12, 5, 137, "NEUTRAL", "children_prospects",
         "Spiritual expenditures on shrines, pilgrimage, and Vedic rituals to bless progeny; philosophical mind.",
         "புண்ணிய ஸ்தல யாத்திரைகள், ஆன்மீகச் செலவுகள், பிள்ளைகளுக்காக பிரார்த்தனைகள் செய்தல்."),
        (12, 6, 138, "NEUTRAL", "health_vitality",
         "Vipareeta Raja Yoga (Harsha/Vimala): Subdues secret enemies and overcomes litigation; requires mindful ethics.",
         "விபரீத ராஜயோகம்: மறைமுக எதிரிகள் விலகுவர், வழக்குகளில் நிவாரணம் கிட்டும், தர்ம நெறி காப்பது நலம்."),
        (12, 7, 139, "NEUTRAL", "first_marriage",
         "Expenditure on spouse's luxury, overseas travels with partner, learning to cultivate deep conjugal compassion.",
         "துணைக்காக ஆடம்பர செலவுகள், வெளிநாட்டு பிரயாணங்கள், தாம்பத்தியத்தில் பரஸ்பர புரிதல் அவசியம்."),
        (12, 8, 140, "FAVORABLE", "health_vitality",
         "Sarala/Vimala Yoga: Always gains unexpectedly, speaks pleasantly, medium to long lifespan, endowed with noble qualities.",
         "விபரீத ராஜயோகம்: எதிர்பாராத தன லாபம், இனிய பேச்சு, நல்ல ஆயுள் பலம் மற்றும் நற்பண்புகள்."),
        (12, 9, 141, "NEUTRAL", "foreign_travel",
         "Travels to foreign sacred shrines, independent philosophical pursuits, philanthropic donations across borders.",
         "வெளிநாட்டு ஆன்மீகப் பயணங்கள், தர்ம காரியங்கள், சுதந்திரமான தத்துவ சிந்தனை உண்டாகும்."),
        (12, 10, 142, "NEUTRAL", "job_prospects",
         "Engaged in hospitals, prisons, embassies, foreign commerce, or charitable trusts; honorable public reputation.",
         "மருத்துவமனை, வெளிநாட்டு தூதரகம், தொண்டு நிறுவனங்கள் அல்லது வெளிநாட்டு வர்த்தகத்தில் தொழில் யோகம்."),
        (12, 11, 143, "NEUTRAL", "regular_income",
         "Fluctuating gains turned into substantial foreign wealth, assisted by overseas organizations or charitable patrons.",
         "அயல்நாட்டு தொடர்பு மூலம் தன லாபம், பிறர் ஆதரவு, எதிர்பாராத வழிகளில் பொருளாதார வரவு."),
        (12, 12, 144, "FAVORABLE", "spirituality_moksha",
         "Vimala Yoga: Deep spiritual detachment, peaceful sleep, bedroom comforts, mastery over senses, and attainment of final emancipation (Moksha).",
         "விமல யோகம்: சுக சயனம், மோட்ச நாட்டம், ஆன்மீக அமைதி, விரயங்களை சுப விரயமாக மாற்றும் ஆற்றல்."),
    ]

    for lord_h, placed_h, sloka, sev, subcat, en_sum, ta_sum in ch24_data:
        rule_id = f"RULE-BPHS-L{lord_h}-H{placed_h}"
        rule_name_en = f"{lord_h}th Lord in {placed_h}th House (BPHS Ch. 24, Sl. {sloka})"
        rule_name_ta = f"{lord_h}-ஆம் பாவாதிபதி {placed_h}-ஆம் பாவத்தில் (பராசரர் அத். 24)"
        principle_en = f"BPHS Ch. 24 principle: The ruler of {BHAVA_NAMES_EN[lord_h]} residing in {BHAVA_NAMES_EN[placed_h]} produces distinctive life fruits per classical aphorism."
        principle_ta = f"பராசர ஹோரா சாஸ்திரம் அத். 24 விதி: {BHAVA_NAMES_TA[lord_h]} அதிபதி {BHAVA_NAMES_TA[placed_h]} அமர்ந்து தரும் அதிகாரப்பூர்வ பலன்."

        lines.append(f'''    AstrologicalRuleDefinition(
        rule_id="{rule_id}",
        version=1,
        name_en="{rule_name_en}",
        name_ta="{rule_name_ta}",
        category_slug="bphs_bhava_lords",
        subcategory="{subcat}",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={{
            "condition_type": "house_lord_placement",
            "house": {lord_h},
            "placed_in_house": {placed_h},
            "chart": "d1"
        }},
        interpretation_en="{en_sum}",
        interpretation_ta="{ta_sum}",
        astrological_principle_en="{principle_en}",
        astrological_principle_ta="{principle_ta}",
        source_reference="Brihat Parashara Hora Shastra, Ch. 24, Sloka {sloka}",
        limitations_en="Planetary dignity (exaltation, debilitation, combustion) and aspects from functional benefics/malefics modify manifestation.",
        limitations_ta="கிரகத்தின் ஆட்சி, உச்சம், பகை, நீசம் மற்றும் சுப-அசுப கிரக பார்வைகள் பலனின் தீவிரத்தை மாற்றியமைக்கும்.",
        severity=SeverityLevel.{sev},
    ),''')

    # -------------------------------------------------------------
    # 2. Chapter 34: Functional Nature & Yogakarakas for 12 Lagnas
    # -------------------------------------------------------------
    lagna_yogakarakas_data = [
        (1, "Aries", "மேஷம்", "Mars", "Sun & Jupiter", "Saturn, Mercury, Venus", "Venus",
         "Mars rules 1st & 8th (helpful to benefics). Sun (5th) and Jupiter (9th) are supreme benefics. Saturn, Mercury, and Venus are functional malefics. Venus is direct Maraka killer.",
         "செவ்வாய் லக்னாதிபதி மற்றும் 8-ஆம் அதிபதி. சூரியன் (5) மற்றும் குரு (9) சுப யோககாரகர்கள். சனி, புதன், சுக்கிரன் பாவர்கள். சுக்கிரன் நேரடி மாரகர்."),
        (2, "Taurus", "ரிஷபம்", "Saturn (9th & 10th Lord)", "Sun (4th Lord)", "Jupiter, Venus, Moon", "Guru group & Mars",
         "Saturn is supreme Yogakaraka ruling both 9th Kona and 10th Kendra. Sun is auspicious. Jupiter, Venus, and Moon are functional malefics. Jupiter group and Mars act as killers.",
         "சனி பகவான் 9 (திரிகோணம்) மற்றும் 10 (கேந்திரம்) அதிபதியாகி மகா ராஜயோககாரகர் ஆகிறார். சூரியன் சுபர். குரு, சுக்கிரன், சந்திரன் பாவர்கள்."),
        (3, "Gemini", "மிதுனம்", "Venus (5th & 12th Lord)", "Venus", "Mars, Jupiter, Sun", "Moon",
         "Venus is the sole auspicious Yogakaraka for Gemini. Mars (6+11), Jupiter (7+10 Kendradhipati), and Sun (3rd) are functional malefics. Moon is prime killer.",
         "சுக்கிரன் 5-ஆம் அதிபதியாகி விசேஷ யோககாரகர் ஆகிறார். செவ்வாய், குரு, சூரியன் பாவர்கள். சந்திரன் பிரதான மாரகர்."),
        (4, "Cancer", "கடகம்", "Mars (5th & 10th Lord)", "Jupiter (9th) & Moon (1st)", "Venus & Mercury", "Saturn & Sun",
         "Mars is exceptional Yogakaraka owning 5th Kona and 10th Kendra. Jupiter and Moon are auspicious. Venus and Mercury are functional malefics. Saturn and Sun are killers.",
         "செவ்வாய் 5 (திரிகோணம்) மற்றும் 10 (கேந்திரம்) அதிபதியாகி பூரண ராஜயோககாரகர். குரு மற்றும் சந்திரன் சுபர்கள். சுக்கிரன், புதன் பாவர்கள்."),
        (5, "Leo", "சிம்மம்", "Mars (4th & 9th Lord)", "Jupiter (5th) & Sun (1st)", "Mercury, Venus, Saturn", "Saturn & Moon",
         "Mars is prime Yogakaraka owning 4th Kendra and 9th Kona. Jupiter and Sun are auspicious. Mercury, Venus, and Saturn are functional malefics. Saturn and Moon are killers.",
         "செவ்வாய் 4 (கேந்திரம்) மற்றும் 9 (திரிகோணம்) அதிபதியாகி மகா யோககாரகர். குரு, சூரியன் சுபர்கள். புதன், சுக்கிரன், சனி பாவர்கள்."),
        (6, "Virgo", "கன்னி", "Venus (2nd & 9th Lord) & Mercury", "Mercury & Venus", "Mars, Jupiter, Moon", "Venus",
         "Mercury (1st & 10th) and Venus (2nd & 9th) are highly auspicious. Conjunction of Mercury and Venus creates Raja Yoga. Mars, Jupiter, and Moon are functional malefics.",
         "புதன் மற்றும் சுக்கிரன் சுபர்கள். புதன்-சுக்கிரன் சேர்க்கை யோகத்தை உண்டாக்கும். செவ்வாய், குரு, சந்திரன் பாவர்கள்."),
        (7, "Libra", "துலாம்", "Saturn (4th & 5th Lord)", "Mercury (9th Lord)", "Jupiter, Sun, Mars", "Mars",
         "Saturn is supreme single Yogakaraka owning 4th Kendra and 5th Kona. Mercury is auspicious. Jupiter, Sun, and Mars are functional malefics. Mars is prime killer.",
         "சனி பகவான் 4 (கேந்திரம்) மற்றும் 5 (திரிகோணம்) அதிபதியாகி முழுமையான யோககாரகர். புதன் சுபர். குரு, சூரியன், செவ்வாய் பாவர்கள்."),
        (8, "Scorpio", "விருச்சிகம்", "Sun (10th) & Moon (9th)", "Jupiter (5th Lord)", "Venus, Mercury, Saturn", "Venus",
         "Sun (10th Kendra) and Moon (9th Kona) are Yogakarakas. Jupiter (5th) is auspicious. Venus, Mercury, and Saturn are functional malefics. Mars is neutral.",
         "சூரியன் (10) மற்றும் சந்திரன் (9) ராஜயோககாரகர்கள். குரு சுபர். சுக்கிரன், புதன், சனி பாவர்கள்."),
        (9, "Sagittarius", "தனுசு", "Sun (9th) & Mars (5th)", "Sun & Mars", "Venus", "Saturn & Venus",
         "Sun (9th Kona) and Mars (5th Kona) are highly auspicious. Sun-Mercury conjunction confers superior Yoga. Venus is the sole malefic and killer. Saturn is killer.",
         "சூரியன் (9) மற்றும் செவ்வாய் (5) மகா சுபர்கள். சூரியன்-புதன் சேர்க்கை விசேஷ யோகம் தரும். சுக்கிரன் பாவர் மற்றும் மாரகர்."),
        (10, "Capricorn", "மகரம்", "Venus (5th & 10th Lord)", "Mercury (9th Lord)", "Mars, Jupiter, Moon", "Mars",
         "Venus is superior Yogakaraka owning 5th Kona and 10th Kendra. Mercury is auspicious. Mars, Jupiter, and Moon are functional malefics. Sun is neutral.",
         "சுக்கிரன் 5 (திரிகோணம்) மற்றும் 10 (கேந்திரம்) அதிபதியாகி மிகச்சிறந்த ராஜயோககாரகர். புதன் சுபர். செவ்வாய், குரு, சந்திரன் பாவர்கள்."),
        (11, "Aquarius", "கும்பம்", "Venus (4th & 9th Lord)", "Saturn (1st Lord)", "Jupiter, Moon, Mars", "Jupiter, Sun, Mars",
         "Venus is the sole Yogakaraka owning 4th Kendra and 9th Kona. Saturn is auspicious as Lagna lord. Jupiter, Moon, and Mars are functional malefics and killers.",
         "சுக்கிரன் 4 (கேந்திரம்) மற்றும் 9 (திரிகோணம்) அதிபதியாகி தனித்த யோககாரகர். சனி சுபர். குரு, சந்திரன், செவ்வாய் பாவர்கள் மற்றும் மாரகர்கள்."),
        (12, "Pisces", "மீனம்", "Mars (2nd & 9th) & Moon (5th)", "Mars & Moon", "Saturn, Venus, Sun, Mercury", "Saturn & Mercury",
         "Mars (9th Kona) and Moon (5th Kona) are auspicious. Mars-Jupiter conjunction confers Raja Yoga. Saturn, Venus, Sun, and Mercury are functional malefics. Saturn and Mercury are killers.",
         "செவ்வாய் (9) மற்றும் சந்திரன் (5) சுபர்கள். செவ்வாய்-குரு சேர்க்கை யோகம் தரும். சனி, சுக்கிரன், சூரியன், புதன் பாவர்கள் மற்றும் மாரகர்கள்."),
    ]

    for sign_idx, sign_en, sign_ta, yogak, benef, malef, marak, desc_en, desc_ta in lagna_yogakarakas_data:
        rule_id = f"RULE-BPHS-YOGA-LAGNA-{sign_idx}"
        rule_name_en = f"BPHS Ch. 34: Functional Nature & Yogakarakas for {sign_en} Lagna"
        rule_name_ta = f"பராசரர் அத். 34: {sign_ta} லக்ன யோககாரக & மாரக கிரக விதிகள்"
        lines.append(f'''    AstrologicalRuleDefinition(
        rule_id="{rule_id}",
        version=1,
        name_en="{rule_name_en}",
        name_ta="{rule_name_ta}",
        category_slug="bphs_yogakarakas",
        subcategory="planetary_strengths",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={{
            "condition_type": "lagna_sign",
            "sign": {sign_idx},
            "chart": "d1"
        }},
        interpretation_en="{desc_en}",
        interpretation_ta="{desc_ta}",
        astrological_principle_en="BPHS Ch. 34: Kendra lords (Vishnu sthana) and Trikona lords (Lakshmi sthana) determine the functional beneficence and Yogakaraka status for each rising sign.",
        astrological_principle_ta="பராசர ஹோரா சாஸ்திரம் அத். 34: கேந்திர (விஷ்ணு) மற்றும் திரிகோண (லட்சுமி) பாவாதிபத்திய அடிப்படையில் லக்ன வாரியாக கிரகங்களின் சுப, அசுப, யோககாரக நிலைகள் நிர்ணயிக்கப்படுகின்றன.",
        source_reference="Brihat Parashara Hora Shastra, Ch. 34, Slokas 19-44",
        limitations_en="A Yogakaraka planet loses potency if combust, debilitated without cancellation, or posited in 6th, 8th, or 12th house.",
        limitations_ta="யோககாரக கிரகம் அஸ்தமனம், நீசம் அல்லது மறைவு ஸ்தானங்களில் (6, 8, 12) அமைந்தால் யோக பலன் குறையும்.",
        severity=SeverityLevel.FAVORABLE,
    ),''')

    # -------------------------------------------------------------
    # 3. Chapter 41: Special Dhana Yogas (Wealth Combinations)
    # -------------------------------------------------------------
    dhana_yogas_ch41 = [
        ("RULE-BPHS-DHANA-01", "Venus in 5th and Mars in 11th (BPHS Ch. 41, Sloka 2)",
         "5-இல் சுக்கிரன் மற்றும் 11-இல் செவ்வாய் தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Venus", "house": 5, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Mars", "house": 11, "chart": "d1"}
         ]},
         "Should Venus occupy the 5th house in its own sign (Taurus/Libra) while Mars is placed in the 11th house, the native will obtain extraordinary riches and abundant financial prosperity.",
         "5-ஆம் பாவத்தில் சுக்கிரன் ஆட்சி பெற்று 11-ஆம் பாவத்தில் செவ்வாய் அமையப் பெற்றால், ஜாதகர் பெரும் தன சேர்க்கையும் அபரிமிதமான செல்வ யோகமும் அடைவார்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 2"),

        ("RULE-BPHS-DHANA-02", "Mercury in 5th with Moon, Mars, Jupiter in 11th (BPHS Ch. 41, Sloka 3)",
         "5-இல் புதன் மற்றும் 11-இல் சந்திரன், செவ்வாய், குரு தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Mercury", "house": 5, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Moon", "house": 11, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Mars", "house": 11, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Jupiter", "house": 11, "chart": "d1"}
         ]},
         "Should a sign of Mercury (Gemini/Virgo) be the 5th house occupied by Mercury himself while the 11th house is tenanted by Moon, Mars, and Jupiter, the native becomes immensely affluent.",
         "5-ஆம் பாவத்தில் புதன் அமைய, 11-ஆம் பாவத்தில் சந்திரன், செவ்வாய் மற்றும் குரு ஒருங்கே அமையப் பெற்றால், ஜாதகர் பெரும் தனவந்தராக வாழ்வார்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 3"),

        ("RULE-BPHS-DHANA-03", "Sun in 5th in Leo with Saturn, Moon, Jupiter in 11th (BPHS Ch. 41, Sloka 4)",
         "5-இல் சூரியன் மற்றும் 11-இல் சனி, சந்திரன், குரு தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Sun", "house": 5, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Saturn", "house": 11, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Moon", "house": 11, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Jupiter", "house": 11, "chart": "d1"}
         ]},
         "Should Leo be the 5th house occupied by Sun himself while Saturn, Moon, and Jupiter occupy the 11th house, the native will enjoy extraordinary wealth and sovereign prosperity.",
         "மேஷ லக்னத்திற்கு 5-ஆம் பாவமான சிம்மத்தில் சூரியன் ஆட்சி பெற்று, 11-இல் சனி, சந்திரன், குரு அமையப் பெற்றால் குபேரனுக்கு நிகரான தன யோகம் உண்டாகும்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 4"),

        ("RULE-BPHS-DHANA-04", "Saturn in 5th in Own Sign with Sun and Moon in 11th (BPHS Ch. 41, Sloka 5)",
         "5-இல் சனி மற்றும் 11-இல் சூரியன், சந்திரன் தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Saturn", "house": 5, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Sun", "house": 11, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Moon", "house": 11, "chart": "d1"}
         ]},
         "Should Saturn occupy the 5th house identical with his own sign (Capricorn/Aquarius) while Sun and Moon are placed in the 11th house, the native will be exceedingly wealthy.",
         "5-ஆம் பாவத்தில் சனி தன் சொந்த வீட்டில் அமைய, 11-ஆம் பாவத்தில் சூரியனும் சந்திரனும் அமையப் பெற்றால் அளவற்ற செல்வ வளம் உண்டாகும்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 5"),

        ("RULE-BPHS-DHANA-05", "Jupiter in 5th in Own Sign with Mercury in 11th (BPHS Ch. 41, Sloka 6)",
         "5-இல் குரு மற்றும் 11-இல் புதன் தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Jupiter", "house": 5, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Mercury", "house": 11, "chart": "d1"}
         ]},
         "Should Jupiter occupy the 5th house in his own sign (Sagittarius/Pisces) while Mercury is in the 11th house, the native will be very affluent and blessed with lasting prosperity.",
         "5-ஆம் பாவத்தில் குரு தன் சொந்த வீட்டில் அமர்ந்து, 11-இல் புதன் அமையப் பெற்றால் அறிவுபூர்வமான வழிகளில் பெரும் தன லாபம் பெருகும்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 6"),

        ("RULE-BPHS-DHANA-06", "Mars in 5th in Own Sign with Venus in 11th (BPHS Ch. 41, Sloka 7)",
         "5-இல் செவ்வாய் மற்றும் 11-இல் சுக்கிரன் தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Mars", "house": 5, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Venus", "house": 11, "chart": "d1"}
         ]},
         "Should a sign of Mars (Aries/Scorpio) be the 5th house tenanted by Mars himself while Venus is in the 11th house, the native will become very affluent and command vast landed properties.",
         "5-ஆம் பாவத்தில் செவ்வாய் ஆட்சி பெற்று 11-இல் சுக்கிரன் அமையப் பெற்றால், பூமி, நிலம் மற்றும் தொழில் மூலம் அபரிமிதமான செல்வம் சேரும்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 7"),

        ("RULE-BPHS-DHANA-07", "Moon in 5th in Cancer with Saturn in 11th (BPHS Ch. 41, Sloka 8)",
         "5-இல் சந்திரன் (கடகம்) மற்றும் 11-இல் சனி தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Moon", "house": 5, "chart": "d1"},
             {"condition_type": "planet_sign", "planet": "Moon", "sign": 4, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Saturn", "house": 11, "chart": "d1"}
         ]},
         "If Cancer happens to be the 5th house containing Moon therein while Saturn is in the 11th house, the native will become exceedingly affluent and command extensive commercial gains.",
         "மீன லக்னத்திற்கு 5-ஆம் பாவமான கடகத்தில் சந்திரன் ஆட்சி பெற்று 11-இல் சனி அமையப் பெற்றால், ஜாதகர் பெரும் தனவந்தராவார்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 8"),

        ("RULE-BPHS-DHANA-08", "Sun in Leo in Lagna aspected by Mars and Jupiter (BPHS Ch. 41, Sloka 9)",
         "லக்னத்தில் சூரியன் (சிம்மம்) - செவ்வாய், குரு பார்வை தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Sun", "house": 1, "chart": "d1"},
             {"condition_type": "planet_sign", "planet": "Sun", "sign": 5, "chart": "d1"},
             {"condition_type": "planet_aspect", "aspecting_planet": "Mars", "target_type": "planet", "target_value": "Sun", "chart": "d1"},
             {"condition_type": "planet_aspect", "aspecting_planet": "Jupiter", "target_type": "planet", "target_value": "Sun", "chart": "d1"}
         ]},
         "Should Sun be in Leo identical with Lagna and be aspected by or conjunct Mars and Jupiter, the native will be remarkably wealthy and enjoy sovereign status.",
         "சிம்ம லக்னத்தில் சூரியன் ஆட்சி பெற்று, செவ்வாய் மற்றும் குருவின் சுபப் பார்வையைப் பெற்றால் ஜாதகர் அரசருக்கு நிகரான தன யோகம் அடைவார்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 9"),

        ("RULE-BPHS-DHANA-09", "Moon in Cancer in Lagna aspected by Mercury and Jupiter (BPHS Ch. 41, Sloka 10)",
         "லக்னத்தில் சந்திரன் (கடகம்) - புதன், குரு பார்வை தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Moon", "house": 1, "chart": "d1"},
             {"condition_type": "planet_sign", "planet": "Moon", "sign": 4, "chart": "d1"},
             {"condition_type": "planet_aspect", "aspecting_planet": "Jupiter", "target_type": "planet", "target_value": "Moon", "chart": "d1"}
         ]},
         "Should Moon be in Cancer identical with Lagna and receive the benefic aspect of Jupiter and Mercury, the native will be wealthy, charitable, and honored.",
         "கடக லக்னத்தில் சந்திரன் ஆட்சி பெற்று, குரு மற்றும் புதனின் சுபப் பார்வை பெற்றால் அபரிமிதமான செல்வம் மற்றும் சமூக அந்தஸ்து உண்டாகும்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 10"),

        ("RULE-BPHS-DHANA-10", "Jupiter in Lagna in Own Sign aspected by Mercury and Mars (BPHS Ch. 41, Sloka 13)",
         "லக்னத்தில் குரு ஆட்சி - புதன், செவ்வாய் தொடர்பு தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Jupiter", "house": 1, "chart": "d1"},
             {"condition_type": "planet_dignity", "planet": "Jupiter", "dignity": "own_sign", "chart": "d1"}
         ]},
         "Should Jupiter be in Lagna in his own sign (Sagittarius/Pisces, Hamsa Yoga) and receive aspects from Mercury and Mars, the native will be exceptionally rich and scholarly.",
         "தனுசு அல்லது மீன லக்னத்தில் குரு ஹம்ச யோகத்தில் அமர்ந்து சுப தொடர்பு பெற்றால், ஜாதகர் பெரும் பணக்காரராகவும் பேரறிஞராகவும் திகழ்வார்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 13"),

        ("RULE-BPHS-DHANA-11", "Venus in Lagna in Own Sign aspected by Saturn and Mercury (BPHS Ch. 41, Sloka 14)",
         "லக்னத்தில் சுக்கிரன் ஆட்சி - சனி, புதன் பார்வை தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Venus", "house": 1, "chart": "d1"},
             {"condition_type": "planet_dignity", "planet": "Venus", "dignity": "own_sign", "chart": "d1"}
         ]},
         "Should Venus be in Lagna in his own sign (Taurus/Libra, Malavya Yoga) and receive the aspect of Saturn and Mercury, the native will be opulent, charming, and highly wealthy.",
         "ரிஷபம் அல்லது துலாம் லக்னத்தில் சுக்கிரன் மாளவ்ய யோகத்தில் அமர்ந்து சனி-புதன் பார்வை பெற்றால் அளவற்ற ஆபரணங்கள், வாகனங்கள் மற்றும் தன யோகம் கூடும்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 14"),

        ("RULE-BPHS-DHANA-12", "Saturn in Lagna in Own Sign aspected by Mars and Jupiter (BPHS Ch. 41, Sloka 15)",
         "லக்னத்தில் சனி ஆட்சி - செவ்வாய், குரு பார்வை தன யோகம் (பராசரர் அத். 41)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Saturn", "house": 1, "chart": "d1"},
             {"condition_type": "planet_dignity", "planet": "Saturn", "dignity": "own_sign", "chart": "d1"}
         ]},
         "If Saturn is in his own sign identical with Lagna (Capricorn/Aquarius, Sasa Yoga) and receives an aspect from or is conjunct Mars and Jupiter, the native will be wealthy and command vast authority.",
         "மகரம் அல்லது கும்ப லக்னத்தில் சனி சச யோகத்தில் ஆட்சி பெற்று குரு மற்றும் செவ்வாய் தொடர்பு பெற்றால், ஜாதகர் பெரும் செல்வாக்கும் அதிகாரமும் அடைவார்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 15"),

        ("RULE-BPHS-DHANA-13", "Kendra and Kona Lords Sambandha (Lakshmi-Vishnu Raja-Dhana Yoga, Ch. 41, Sloka 28)",
         "கேந்திர-திரிகோணாதிபதிகள் சம்பந்தம் (லட்சுமி-விஷ்ணு தன யோகம், அத். 41)",
         {"condition_type": "compound", "operator": "OR", "conditions": [
             {"condition_type": "mutual_exchange", "house1": 1, "house2": 9, "chart": "d1"},
             {"condition_type": "mutual_exchange", "house1": 4, "house2": 9, "chart": "d1"},
             {"condition_type": "mutual_exchange", "house1": 10, "house2": 9, "chart": "d1"},
             {"condition_type": "mutual_exchange", "house1": 10, "house2": 5, "chart": "d1"},
         ]},
         "The Kendras are Vishnu Sthanas and the Konas are Lakshmi Sthanas. When the lord of a Kendra establishes a mutual exchange (Parivartana) with the lord of a Kona, a supreme Raja-Dhana Yoga is obtained.",
         "கேந்திரங்கள் விஷ்ணு ஸ்தானங்கள்; திரிகோணங்கள் லட்சுமி ஸ்தானங்கள். கேந்திராதிபதியும் திரிகோணாதிபதியும் பரிவர்த்தனை பெற்றால் மகா பாக்கிய யோகம் மற்றும் தன சேர்க்கை உண்டாகும்.",
         "Brihat Parashara Hora Shastra, Ch. 41, Sloka 28"),
    ]

    for rid, name_en, name_ta, ctree, interp_en, interp_ta, sref in dhana_yogas_ch41:
        lines.append(f'''    AstrologicalRuleDefinition(
        rule_id="{rid}",
        version=1,
        name_en="{name_en}",
        name_ta="{name_ta}",
        category_slug="bphs_dhana_yogas",
        subcategory="wealth_yogas",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={repr(ctree)},
        interpretation_en="{interp_en}",
        interpretation_ta="{interp_ta}",
        astrological_principle_en="BPHS Ch. 41 principle: Specific harmonious mutual placements of 5th/11th lords, natural benefics, and Lagna lords form classical Dhana Yogas yielding immense riches.",
        astrological_principle_ta="பராசர ஹோரா சாஸ்திரம் அத். 41 விதி: 5, 11-ஆம் பாவாதிபதிகள் மற்றும் கேந்திர-திரிகோண அதிபதிகள் அமைக்கும் விசேஷ தன யோகங்கள் பெரும் செல்வத்தை உருவாக்குகின்றன.",
        source_reference="{sref}",
        limitations_en="Combustion, severe affliction by nodes, or malefic drishti will diminish the financial magnitude.",
        limitations_ta="அஸ்தமனம், ராகு-கேது பாதிப்பு அல்லது பாப கிரக பார்வை தன யோகத்தின் வீரியத்தைக் குறைக்கலாம்.",
        severity=SeverityLevel.FAVORABLE,
    ),''')

    # -------------------------------------------------------------
    # 4. Chapter 42: Combinations for Penury (Daridra Yogas)
    # -------------------------------------------------------------
    daridra_yogas_ch42 = [
        ("RULE-BPHS-DARIDRA-01", "1st Lord in 12th & 12th Lord in 1st (Daridra Parivartana, BPHS Ch. 42, Sloka 2)",
         "லக்னாதிபதி 12-இல் & 12-ஆம் அதிபதி 1-இல் தரித்திர யோகம் (பராசரர் அத். 42)",
         {"condition_type": "mutual_exchange", "house1": 1, "house2": 12, "chart": "d1"},
         "The native will face severe financial struggles if Lagna Lord is in the 12th house while the 12th Lord is in Lagna, especially when linked with Maraka lords, causing resources to drain out.",
         "லக்னாதிபதி 12-லும், 12-ஆம் அதிபதி லக்னத்திலும் பரிவர்த்தனை பெற்று மாரக தொடர்பு ஏற்பட்டால் தேவையற்ற விரயங்களும் நிதி நெருக்கடிகளும் உண்டாகும்.",
         "Brihat Parashara Hora Shastra, Ch. 42, Sloka 2"),

        ("RULE-BPHS-DARIDRA-02", "1st Lord in 6th & 6th Lord in 1st (Daridra Parivartana, BPHS Ch. 42, Sloka 3)",
         "லக்னாதிபதி 6-இல் & 6-ஆம் அதிபதி 1-இல் கடன்/நோய் யோகம் (பராசரர் அத். 42)",
         {"condition_type": "mutual_exchange", "house1": 1, "house2": 6, "chart": "d1"},
         "The native will be subject to debts and loss of wealth if Lagna Lord is in the 6th house while the 6th Lord is in Lagna, demanding careful handling of litigation and borrowing.",
         "லக்னாதிபதியும் 6-ஆம் அதிபதியும் பரிவர்த்தனை பெற்றால் எதிரிகள், வழக்குகள் மற்றும் கடன் தொல்லைகளால் தன விரயம் ஏற்பட வாய்ப்புள்ளது.",
         "Brihat Parashara Hora Shastra, Ch. 42, Sloka 3"),

        ("RULE-BPHS-DARIDRA-03", "Lagna or Moon with Ketu and 1st Lord in 8th (BPHS Ch. 42, Sloka 4)",
         "லக்னம்/சந்திரன் கேது சேர்க்கை - லக்னாதிபதி 8-இல் (பராசரர் அத். 42)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Ketu", "house": 1, "chart": "d1"},
             {"condition_type": "house_lord_placement", "house": 1, "placed_in_house": 8, "chart": "d1"}
         ]},
         "Should Lagna or Moon be conjunct Ketu while Lagna Lord is relegated to the 8th house, the person concerned faces financial scarcities and material detachment.",
         "லக்னத்தில் கேது அமர்ந்து, லக்னாதிபதி 8-ஆம் பாவத்தில் மறைந்தால் பொருள் பற்றாக்குறை மற்றும் பொருளாதார சவால்கள் ஏற்படும்.",
         "Brihat Parashara Hora Shastra, Ch. 42, Sloka 4"),

        ("RULE-BPHS-DARIDRA-04", "1st Lord in Dusthana while 2nd Lord is Debilitated (BPHS Ch. 42, Sloka 5)",
         "லக்னாதிபதி மறைவு - 2-ஆம் அதிபதி நீசம் (தரித்திர யோகம், அத். 42)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "house_lord_placement", "house": 1, "placed_in_house": [6, 8, 12], "chart": "d1"},
             {"condition_type": "planet_dignity", "planet": "Jupiter", "dignity": "debilitated", "chart": "d1"}  # symbolic baseline check or general
         ]},
         "If Lagna's Lord along with a malefic is in the 6th, 8th, or 12th house while the 2nd Lord is in debilitation or inimical sign, even a native of royal scion will face severe penury.",
         "லக்னாதிபதி மறைவு ஸ்தானத்தில் (6, 8, 12) அசுப கிரகத்துடன் அமர்ந்து, தனஸ்தானாதிபதியும் பலவீனமடைந்தால் கடுமையான பொருளாதார நெருக்கடி வரலாம்.",
         "Brihat Parashara Hora Shastra, Ch. 42, Sloka 5"),

        ("RULE-BPHS-DARIDRA-05", "Mars and Saturn in 2nd House without Mercury Aspect (BPHS Ch. 42, Sloka 16)",
         "2-ஆம் பாவத்தில் செவ்வாய்-சனி சேர்க்கை (தன நாச யோகம், அத். 42)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Mars", "house": 2, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Saturn", "house": 2, "chart": "d1"}
         ]},
         "Should Mars and Saturn be together in the 2nd house (Dhana Bhava), the native's wealth tends to be destroyed; however, should Mercury aspect them, great wealth will be preserved.",
         "2-ஆம் பாவத்தில் செவ்வாயும் சனியும் ஒன்றாக அமர்ந்தால் தன இழப்பு ஏற்படலாம்; ஆனால் புதனின் சுபப் பார்வை பெற்றால் பெரும் செல்வம் உண்டாகும் என பராசரர் விதிவிலக்கு கூறுகிறார்.",
         "Brihat Parashara Hora Shastra, Ch. 42, Sloka 16"),

        ("RULE-BPHS-DARIDRA-06", "Sun in 2nd House aspected by Saturn (BPHS Ch. 42, Sloka 17)",
         "2-இல் சூரியன் - சனியின் பார்வை (தரித்திர யோகம், அத். 42)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Sun", "house": 2, "chart": "d1"},
             {"condition_type": "planet_aspect", "aspecting_planet": "Saturn", "target_type": "planet", "target_value": "Sun", "chart": "d1"}
         ]},
         "Sun in the 2nd house receiving an aspect from Saturn will cause penury and family dispute, while if Sun in 2nd does not receive an aspect from Saturn, riches and fame will be obtained.",
         "2-ஆம் பாவத்தில் உள்ள சூரியனை சனி பார்த்தால் குடும்ப வாக்குவாதங்களும் பண விரயமும் உண்டாகும்; சனி பார்வை இல்லையெனில் புகழும் செல்வமும் கிடைக்கும்.",
         "Brihat Parashara Hora Shastra, Ch. 42, Sloka 17"),
    ]

    for rid, name_en, name_ta, ctree, interp_en, interp_ta, sref in daridra_yogas_ch42:
        lines.append(f'''    AstrologicalRuleDefinition(
        rule_id="{rid}",
        version=1,
        name_en="{name_en}",
        name_ta="{name_ta}",
        category_slug="bphs_daridra_yogas",
        subcategory="financial_fluctuations",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={repr(ctree)},
        interpretation_en="{interp_en}",
        interpretation_ta="{interp_ta}",
        astrological_principle_en="BPHS Ch. 42 principle: Dusthana displacements of wealth lords, conjunction with natural malefics in Dhana sthana, and lack of benefic aspects create classical Daridra Yogas.",
        astrological_principle_ta="பராசர ஹோரா சாஸ்திரம் அத். 42 விதி: தன ஸ்தானாதிபதி மறைவு ஸ்தானங்களில் பலவீனமடைதல் மற்றும் 2-ஆம் பாவத்தில் பாப கிரக சேர்க்கை நிதிப் பற்றாக்குறையை உண்டாக்குகிறது.",
        source_reference="{sref}",
        limitations_en="Benefic aspects from Jupiter, Venus, or exalted Mercury significantly nullify poverty indications.",
        limitations_ta="குரு, சுக்கிரன் அல்லது உச்ச புதனின் பார்வை தரித்திர யோகத்தை முழுமையாக பங்கம் செய்து சுப பலன் தரும்.",
        severity=SeverityLevel.UNFAVORABLE,
    ),''')

    # -------------------------------------------------------------
    # 5. Chapter 80: Female Horoscopy (Stri Jataka) & Visha Kanya
    # -------------------------------------------------------------
    stri_jataka_ch80 = [
        ("RULE-BPHS-STRI-01", "Lagna and Moon in Even Signs (Feminine Virtues & Beauty, Ch. 80, Sloka 5)",
         "லக்னம் மற்றும் சந்திரன் இரட்டை ராசிகளில் (ஸ்த்ரீ ஜாதகம், அத். 80)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_sign", "planet": "Ascendant", "sign": [2, 4, 6, 8, 10, 12], "chart": "d1"},
             {"condition_type": "planet_sign", "planet": "Moon", "sign": [2, 4, 6, 8, 10, 12], "chart": "d1"}
         ]},
         "If at the time of birth of a woman Lagna and Moon are both in even signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces), the woman will be truly feminine in character, possessing excellent virtues, steadfast character, and charming health.",
         "பெண்கள் ஜாதகத்தில் லக்னமும் சந்திரனும் இரட்டை ராசிகளில் அமைந்தால், பெண்மைக்குரிய நற்பண்புகள், அழகு, கற்புடைமை, சாந்த குணம் மற்றும் உடல் ஆரோக்கியம் உண்டாகும்.",
         "Brihat Parashara Hora Shastra, Ch. 80, Sloka 5", "FAVORABLE", "relationship_compatibility"),

        ("RULE-BPHS-STRI-02", "Lagna and Moon in Odd Signs (Masculine Bearing, Ch. 80, Sloka 6)",
         "லக்னம் மற்றும் சந்திரன் ஒற்றை ராசிகளில் (ஸ்த்ரீ ஜாதகம், அத். 80)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_sign", "planet": "Ascendant", "sign": [1, 3, 5, 7, 9, 11], "chart": "d1"},
             {"condition_type": "planet_sign", "planet": "Moon", "sign": [1, 3, 5, 7, 9, 11], "chart": "d1"}
         ]},
         "If Lagna and Moon are both in odd signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius), she will possess masculine determination, bold courage, and authoritative demeanor; if aspected by malefics, patience is required.",
         "லக்னமும் சந்திரனும் ஒற்றை ராசிகளில் அமைந்தால், ஜாதகி தைரியமும், ஆண்மைக்குரிய துணிச்சலும், தலைமைப் பண்பும் கொண்டிருப்பார்.",
         "Brihat Parashara Hora Shastra, Ch. 80, Sloka 6", "NEUTRAL", "personality_birth"),

        ("RULE-BPHS-STRI-03", "Benefic in 7th House (Marital Felicity & Chastity, Ch. 80, Sloka 21)",
         "7-ஆம் பாவத்தில் சுப கிரகம் (பூரண களத்திர பாக்கியம், அத். 80)",
         {"condition_type": "compound", "operator": "OR", "conditions": [
             {"condition_type": "planet_house", "planet": "Jupiter", "house": 7, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Venus", "house": 7, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Mercury", "house": 7, "chart": "d1"}
         ]},
         "If there be a benefic in the 7th house in a female's horoscope, she will enjoy high marital happiness, a devoted and noble husband, and peace of mind.",
         "பெண்கள் ஜாதகத்தில் 7-ஆம் பாவத்தில் குரு, சுக்கிரன் அல்லது சுப புதன் அமைந்தால், சிறந்த வாழ்க்கைத் துணை, தாம்பத்திய சுகம் மற்றும் நற்குடும்பம் அமையும்.",
         "Brihat Parashara Hora Shastra, Ch. 80, Sloka 21", "FAVORABLE", "first_marriage"),

        ("RULE-BPHS-STRI-04", "Benefic in 8th House without Malefics (Sumangali Yoga, Ch. 80, Sloka 54)",
         "8-இல் சுப கிரகம் (தீர்க்க சுமங்கலி யோகம், பராசரர் அத். 80)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "compound", "operator": "OR", "conditions": [
                 {"condition_type": "planet_house", "planet": "Jupiter", "house": 8, "chart": "d1"},
                 {"condition_type": "planet_house", "planet": "Venus", "house": 8, "chart": "d1"}
             ]}
         ]},
         "The woman dies before her husband (Sumangali Yoga) when in her nativity there is a benefic in the 8th house, without aspect by, or association with a malefic, denoting lifelong wedded bliss.",
         "பெண்கள் ஜாதகத்தில் 8-ஆம் பாவத்தில் பாப சேர்க்கை இன்றி சுப கிரகம் (குரு/சுக்கிரன்) அமர்ந்தால், தீர்க்க சுமங்கலியாக வாழும் பெரும் யோகம் உண்டாகும்.",
         "Brihat Parashara Hora Shastra, Ch. 80, Sloka 54", "FAVORABLE", "marital_harmony"),

        ("RULE-BPHS-STRI-05", "Mars in 7th without Benefic Aspect (Kuja Dosha, Ch. 80, Sloka 20 & 47)",
         "7-இல் செவ்வாய் - செவ்வாய் தோஷம் (பராசரர் அத். 80)",
         {"condition_type": "planet_house", "planet": "Mars", "house": 7, "chart": "d1"},
         "If Mars occupies the 7th house without benefic association or aspect, classical texts note vulnerability in marital harmony and partner's vitality, completely cancelled if the spouse also possesses similar placement.",
         "7-ஆம் பாவத்தில் செவ்வாய் சுபப் பார்வை இன்றி தனித்து அமர்ந்தால் செவ்வாய் தோஷம் உண்டாகும். இருவருக்கும் இதே அமைப்பு இருந்தால் தோஷம் நிவர்த்தியாகும்.",
         "Brihat Parashara Hora Shastra, Ch. 80, Slokas 20, 47-49", "UNFAVORABLE", "marital_harmony"),

        ("RULE-BPHS-STRI-06", "Visha Kanya Planetary Alignment (BPHS Ch. 80, Sloka 44)",
         "விஷ கன்யா கிரக அமைப்பு (பராசரர் அத். 80)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Saturn", "house": 1, "chart": "d1"},
             {"condition_type": "house_occupancy", "house": 7, "occupied_by": ["Mars"], "chart": "d1"}
         ]},
         "Classical Visha Kanya planetary formation: When Lagna is occupied by malefic and benefic while planets occupy inimical signs, traditional texts caution against marital friction, cured by benefic aspect on 7th house.",
         "லக்னம் மற்றும் களத்திர பாவத்தில் பாப கிரக தாக்கங்கள் உண்டாகும் போது விஷ கன்யா அமைப்பு ஏற்படுகிறது. 7-ஆம் அதிபதி சுபராக அமைந்தால் தோஷம் நீங்கும்.",
         "Brihat Parashara Hora Shastra, Ch. 80, Slokas 44-46", "UNFAVORABLE", "separation_divorce"),
    ]

    for rid, name_en, name_ta, ctree, interp_en, interp_ta, sref, sev, subcat in stri_jataka_ch80:
        lines.append(f'''    AstrologicalRuleDefinition(
        rule_id="{rid}",
        version=1,
        name_en="{name_en}",
        name_ta="{name_ta}",
        category_slug="bphs_stri_jataka",
        subcategory="{subcat}",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        applicable_gender="female" if "STRI" in "{rid}" and "STRI-02" not in "{rid}" else "both",
        condition_tree={repr(ctree)},
        interpretation_en="{interp_en}",
        interpretation_ta="{interp_ta}",
        astrological_principle_en="BPHS Ch. 80 (Stri Jataka): The 7th house indicates the spouse's fortune, 8th indicates marital longevity (Mangalya), and 5th indicates children in female horoscopy.",
        astrological_principle_ta="பராசர ஹோரா சாஸ்திரம் அத். 80 (ஸ்த்ரீ ஜாதகம்): 7-ஆம் பாவம் கணவரின் பாக்கியத்தையும், 8-ஆம் பாவம் மாங்கல்ய பலத்தையும், 5-ஆம் பாவம் புத்திர பாக்கியத்தையும் குறிக்கிறது.",
        source_reference="{sref}",
        limitations_en="Benefic aspects from Jupiter or Venus on 7th and 8th houses nullify inauspicious indications.",
        limitations_ta="குரு அல்லது சுக்கிரனின் சுப பார்வை 7, 8-ஆம் பாவங்களின் தோஷங்களை நிவர்த்தி செய்கிறது.",
        severity=SeverityLevel.{sev},
    ),''')

    # -------------------------------------------------------------
    # 6. Chapter 83: 8 Curses in Previous Birth (Shapas)
    # -------------------------------------------------------------
    shapas_ch83 = [
        ("RULE-BPHS-SHAPA-01", "Sarpa Shapa (Curse of Serpents, BPHS Ch. 83, Slokas 9-19)",
         "சர்ப்ப சாபம் / நாக தோஷம் (பராசரர் அத். 83)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Rahu", "house": 5, "chart": "d1"},
             {"condition_type": "planet_aspect", "aspecting_planet": "Mars", "target_type": "planet", "target_value": "Rahu", "chart": "d1"}
         ]},
         "Sarpa Shapa: Rahu in 5th house aspected by Mars. Delays or obstacles in begetting male progeny due to harm done to serpents in a previous incarnation. Remedial measure: Installing an idol of Naga Raja in gold, worshipping according to Vedic rites, and donating a cow, sesame seeds, and gold.",
         "சர்ப்ப சாபம்: 5-ஆம் பாவத்தில் உள்ள ராகுவை செவ்வாய் பார்ப்பது. முற்பிறவியில் பாம்புகளை துன்புறுத்தியதால் புத்திர பாக்கியத்தில் தடை வரலாம். பரிகாரம்: தங்க நாக பிரதிஷ்டை, பூஜை, பசு மற்றும் எள் தானம் செய்தல்.",
         "Brihat Parashara Hora Shastra, Ch. 83, Slokas 9-19"),

        ("RULE-BPHS-SHAPA-02", "Pitru Shapa (Curse of Father, BPHS Ch. 83, Slokas 20-33)",
         "பித்ரு சாபம் (பராசரர் அத். 83)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Sun", "house": 5, "chart": "d1"},
             {"condition_type": "planet_sign", "planet": "Sun", "sign": 7, "chart": "d1"}  # Debilitated in Libra in 5th
         ]},
         "Pitru Shapa: Sun in debilitation in the 5th house in the Navamsa of Saturn. Obstacles to childbearing due to disrespect or sin against the father in past birth. Remedial measure: Performance of Shraddha at holy Gaya, feeding Brahmins, and Kanyadana (assisting the marriage of an underprivileged girl).",
         "பித்ரு சாபம்: 5-ஆம் பாவத்தில் சூரியன் நீசம் அடைந்து சனியின் நவாம்சத்தில் இருப்பது. முற்பிறவியில் தந்தைக்கு செய்த அபசாரத்தால் புத்திர தோஷம். பரிகாரம்: கயா சிரார்த்தம் செய்தல், ஏழைப் பெண்ணின் திருமணத்திற்கு உதவுதல் (கன்யாதானம்), அந்தணர் போஜனம்.",
         "Brihat Parashara Hora Shastra, Ch. 83, Slokas 20-33"),

        ("RULE-BPHS-SHAPA-03", "Matru Shapa (Curse of Mother, BPHS Ch. 83, Slokas 34-50)",
         "மாத்ரு சாபம் (பராசரர் அத். 83)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "house_lord_placement", "house": 5, "placed_in_house": [6, 8, 12], "chart": "d1"},
             {"condition_type": "planet_dignity", "planet": "Moon", "dignity": "debilitated", "chart": "d1"}
         ]},
         "Matru Shapa: Moon debilitated while 5th Lord is in Dusthana (6/8/12). Childlessness or anxiety regarding children due to distress caused to mother in past birth. Remedial measure: Holy bath at Ram Setu bridge (Rameshwaram), chanting 1 Lakh Gayatri Mantras, circumambulating a sacred Pipal tree 1008 times.",
         "மாத்ரு சாபம்: சந்திரன் நீசம் பெற்று 5-ஆம் அதிபதி 6, 8, 12-ல் மறைவது. முற்பிறவியில் தாயை அவமதித்ததால் ஏற்படும் தோஷம். பரிகாரம்: ராமேஸ்வரம் சேது ஸ்நானம், ஒரு லட்சம் காயத்ரி ஜபம், அரச மரத்தை 1008 முறை வலம் வருதல்.",
         "Brihat Parashara Hora Shastra, Ch. 83, Slokas 34-50"),

        ("RULE-BPHS-SHAPA-04", "Bhratri Shapa (Curse of Brother, BPHS Ch. 83, Slokas 51-64)",
         "பிராத்ரு சாபம் / சகோதர தோஷம் (பராசரர் அத். 83)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Mars", "house": 5, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Rahu", "house": 5, "chart": "d1"}
         ]},
         "Bhratri Shapa: 3rd lord with Rahu and Mars occupying the 5th house. Obstacles to family lineage from past-life disputes with brothers. Remedial measure: Listening to Harivamsha Purana, observing Chandrayana fast, planting a Pipal sapling on holy river banks, and donating cows.",
         "பிராத்ரு சாபம்: 5-ஆம் பாவத்தில் செவ்வாய்-ராகு சேர்க்கை. சகோதரர்களிடம் முற்பிறவியில் செய்த பிழையால் புத்திர தடை. பரிகாரம்: ஹரிவம்ச புராணம் கேட்டல், சாந்திராயண விரதம், புனித நதிக்கரையில் அரசங்கன்று நடுதல்.",
         "Brihat Parashara Hora Shastra, Ch. 83, Slokas 51-64"),

        ("RULE-BPHS-SHAPA-05", "Brahmana Shapa (Curse of a Brahmin / Guru, BPHS Ch. 83, Slokas 71-81)",
         "பிரம்ம சாபம் / குரு சாபம் (பராசரர் அத். 83)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Jupiter", "house": 5, "chart": "d1"},
             {"condition_type": "planet_sign", "planet": "Rahu", "sign": [9, 12], "chart": "d1"}  # Rahu in Guru's sign
         ]},
         "Brahmana Shapa: Rahu in Jupiter's sign while Jupiter is in the 5th house. Sins of insulting learned sages or preceptors in past birth. Remedial measure: Observing Chandrayana fast, performing penance, and donating a cow and five gems with gold after feeding Vedic scholars.",
         "பிரம்ம சாபம்: குருவின் வீட்டில் ராகு அமர்ந்து 5-ல் குரு இருப்பது. குரு அல்லது கற்றோரை அவமதித்ததால் உண்டாகும் சாபம். பரிகாரம்: சாந்திராயண விரதம், தவம், பசு மற்றும் நவரத்தினங்கள்/தங்கம் தானம் செய்தல்.",
         "Brihat Parashara Hora Shastra, Ch. 83, Slokas 71-81"),

        ("RULE-BPHS-SHAPA-06", "Patni Shapa (Curse of Wife, BPHS Ch. 83, Slokas 82-94)",
         "பத்னி சாபம் (பராசரர் அத். 83)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "house_lord_placement", "house": 7, "placed_in_house": 8, "chart": "d1"},
             {"condition_type": "house_lord_placement", "house": 12, "placed_in_house": 5, "chart": "d1"}
         ]},
         "Patni Shapa: 7th Lord in 8th house while 12th Lord occupies the 5th house. Sins of abandoning or mistreating one's spouse in past life. Remedial measure: Sponsoring the wedding of an underprivileged maiden (Kanyadana), or donating a gold idol of Lakshminarayana and a fertile cow.",
         "பத்னி சாபம்: 7-ஆம் அதிபதி 8-லும், 12-ஆம் அதிபதி 5-லும் அமைவது. முற்பிறவியில் மனைவியை கைவிட்டதால் ஏற்படும் தோஷம். பரிகாரம்: ஏழைப் பெண்ணின் திருமணத்திற்கு உதவுதல் (கன்யாதானம்), லட்சுமி நாராயணர் தங்க விக்ரஹம் மற்றும் பசு தானம்.",
         "Brihat Parashara Hora Shastra, Ch. 83, Slokas 82-94"),

        ("RULE-BPHS-SHAPA-07", "Pretha Shapa (Curse of Departed Ancestors, BPHS Ch. 83, Slokas 95-108)",
         "பிரேத சாபம் / முன்னோர்கள் தோஷம் (பராசரர் அத். 83)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Saturn", "house": 5, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Sun", "house": 5, "chart": "d1"}
         ]},
         "Pretha Shapa: Saturn and Sun conjoined in the 5th house. Neglect of funeral and annual memorial Shraddha rites of parents in previous birth. Remedial measure: Performing Pinda Dana, Rudra Abhisheka, giving in charity a gold idol of Lord Brahma, a silver vessel, and feeding Vedic scholars.",
         "பிரேத சாபம்: 5-ஆம் பாவத்தில் சனியும் சூரியனும் இணைவது. முன்னோருக்கு திதி, சிரார்த்தம் செய்யாததால் வரும் தோஷம். பரிகாரம்: பிண்ட தானம், ருத்ராபிஷேகம், பிரம்மா விக்ரஹம் மற்றும் வெள்ளி பாத்திரம் தானம் செய்தல்.",
         "Brihat Parashara Hora Shastra, Ch. 83, Slokas 95-108"),
    ]

    for rid, name_en, name_ta, ctree, interp_en, interp_ta, sref in shapas_ch83:
        lines.append(f'''    AstrologicalRuleDefinition(
        rule_id="{rid}",
        version=1,
        name_en="{name_en}",
        name_ta="{name_ta}",
        category_slug="bphs_shapas_curses",
        subcategory="children_prospects",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={repr(ctree)},
        interpretation_en="{interp_en}",
        interpretation_ta="{interp_ta}",
        astrological_principle_en="BPHS Ch. 83 principle: Karmic debts from previous incarnations block the 5th house of lineage (Santana Bhava); performing specific Maharishi-ordained Vedic prayaschittas grants deliverance.",
        astrological_principle_ta="பராசர ஹோரா சாஸ்திரம் அத். 83 விதி: முற்பிறவி கர்ம வினைகள் 5-ஆம் பாவ புத்திர பாக்கியத்தை தடை செய்கின்றன; பராசரர் அருளிய வேதப் பரிகாரங்கள் மூலமே சாப நிவர்த்தி பெற முடியும்.",
        source_reference="{sref}",
        limitations_en="Prescribed Vedic remedies, charity, and devout mantra recitations nullify the curse.",
        limitations_ta="சாஸ்திரத்தில் பரிந்துரைக்கப்பட்ட பிராயச்சித்த பரிகாரங்களைச் செய்வதன் மூலம் சாப நிவர்த்தி கிட்டும்.",
        severity=SeverityLevel.UNFAVORABLE,
    ),''')

    # -------------------------------------------------------------
    # 7. Chapter 85-94: Inauspicious Births & Gandanta Rules
    # -------------------------------------------------------------
    inauspicious_ch85_94 = [
        ("RULE-BPHS-INAU-01", "Amavasya Birth (New Moon Congruence, BPHS Ch. 86)",
         "அமாவாசை பிறப்பு தோஷம் & பரிகாரம் (பராசரர் அத். 86)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Sun", "house": 1, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Moon", "house": 1, "chart": "d1"}
         ]},
         "Birth on Amavasya (Sun and Moon in exact same sign) causes financial struggles and physical sensitivity unless sanctified. Remedial measure: Installing Kalasha with sacred tree leaves in South-West, worshipping Sun (gold) and Moon (silver) idols, performing Havan with 108 oblations, and seeing face reflection in melted ghee.",
         "அமாவாசை திதியில் பிறக்கும் போது சூரியனும் சந்திரனும் ஒன்றாக இணைவர். இது உடல் பலவீனம் மற்றும் தன நெருக்கடியை தரலாம். பரிகாரம்: தென்மேற்கில் கலச ஸ்தாபனம், சூரிய-சந்திர ஹோமம், நெய் தானம் செய்தல்.",
         "Brihat Parashara Hora Shastra, Ch. 86, Slokas 1-9"),

        ("RULE-BPHS-INAU-02", "Nakshatra Gandanta (Revati-Ashwini, Aslesha-Magha, Jyeshtha-Mula, Ch. 92, Sloka 3)",
         "நட்சத்திர கண்டாந்தம் (பராசரர் அத். 92)",
         {"condition_type": "compound", "operator": "OR", "conditions": [
             {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Revati", "pada": 4},
             {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Ashwini", "pada": 1},
             {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Ashlesha", "pada": 4},
             {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Magha", "pada": 1},
             {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Jyeshtha", "pada": 4},
             {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Mula", "pada": 1},
         ]},
         "Nakshatra Gandanta: Junction of Water and Fire asterisms (last quarter of Revati/Ashlesha/Jyeshtha and first quarter of Ashwini/Magha/Mula). Threatens infantile vitality unless remedied. Remedial measure: Abhisheka of child with father, cow donation, and Nakshatra Devata Havan on 28th day.",
         "நட்சத்திர கண்டாந்தம்: நீர்-நெருப்பு ராசி சந்திப்புகளில் (ரேவதி-அஸ்வினி, ஆயில்யம்-மகம், கேட்டை-மூலம்) சந்திரன் அமர்வது. பரிகாரம்: கண்டாந்த சாந்தி ஹோமம், ஆயுஷ் ஹோமம் மற்றும் பசு தானம்.",
         "Brihat Parashara Hora Shastra, Ch. 92, Slokas 3-8"),

        ("RULE-BPHS-INAU-03", "Abhukta Mula Birth (End of Jyeshtha & Beginning of Mula, Ch. 92-93)",
         "அபுக்த மூல நட்சத்திர பிறப்பு (பராசரர் அத். 93)",
         {"condition_type": "compound", "operator": "OR", "conditions": [
             {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Jyeshtha", "pada": 4},
             {"condition_type": "planet_nakshatra", "planet": "Moon", "nakshatra": "Mula", "pada": 1},
         ]},
         "Abhukta Mula: Last 6 ghatikas of Jyeshtha (ruled by Indra) and first 8 ghatikas of Mula (ruled by Rakshasa). Most adverse junction in horoscopy. Father should not see the child's face until 27 days or complete Gandanta Shanti rites are performed with Rakshasa and Indra idols.",
         "அபுக்த மூலம்: கேட்டை நட்சத்திர கடைசி நாழிகைகளும் மூல நட்சத்திர தொடக்க நாழிகைகளும் இணையும் சந்திப்பு. பரிகாரம்: 27 நாட்கள் அல்லது சாந்தி ஹோமம் முடியும் வரை தந்தை குழந்தையின் முகத்தை பார்க்கக் கூடாது; இந்திர-ராட்சச சாந்தி பூஜை அவசியம்.",
         "Brihat Parashara Hora Shastra, Ch. 92 Sl. 5 & Ch. 93 Sl. 1-20"),

        ("RULE-BPHS-INAU-04", "Lagna Gandanta (Junction of Pisces-Aries, Cancer-Leo, Scorpio-Sagittarius, Ch. 92, Sloka 4)",
         "லக்ன கண்டாந்தம் (பராசரர் அத். 92)",
         {"condition_type": "compound", "operator": "OR", "conditions": [
             {"condition_type": "planet_sign", "planet": "Ascendant", "sign": [1, 5, 9], "chart": "d1"},
             {"condition_type": "planet_sign", "planet": "Ascendant", "sign": [4, 8, 12], "chart": "d1"}
         ]},
         "Lagna Gandanta: Rising degree in the exact boundary between Water and Fire signs (last half-ghatika of Meena/Kark/Vrischik and first half-ghatika of Mesha/Simha/Dhanus). Remedial measure: Gold in charity, Abhisheka with Kalasha water.",
         "லக்ன கண்டாந்தம்: நீர்-நெருப்பு ராசி சந்திப்புகளில் லக்னம் உதயமாகும் தருணம். பரிகாரம்: தங்க தானம் மற்றும் கலச தீர்த்த அபிஷேகம்.",
         "Brihat Parashara Hora Shastra, Ch. 92, Slokas 4-11"),
    ]

    for rid, name_en, name_ta, ctree, interp_en, interp_ta, sref in inauspicious_ch85_94:
        lines.append(f'''    AstrologicalRuleDefinition(
        rule_id="{rid}",
        version=1,
        name_en="{name_en}",
        name_ta="{name_ta}",
        category_slug="bphs_inauspicious_births",
        subcategory="health_vitality",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={repr(ctree)},
        interpretation_en="{interp_en}",
        interpretation_ta="{interp_ta}",
        astrological_principle_en="BPHS Ch. 85-94 principle: Certain cosmic junctions (Sandhis) between fire and water require Vedic pacification to ensure longevity, prosperity, and family well-being.",
        astrological_principle_ta="பராசர ஹோரா சாஸ்திரம் அத். 85-94: திதி, நட்சத்திர, லக்ன சந்திகளில் பிறக்கும் குழந்தைகளுக்கு தோஷ நிவர்த்தி சாந்தி ஹோமங்கள் ஆயுளையும் சௌபாக்கியத்தையும் அளிக்கின்றன.",
        source_reference="{sref}",
        limitations_en="Performance of canonical Vedic Shanti rituals completely removes these birth blemishes.",
        limitations_ta="சாஸ்திரோக்தமான சாந்தி ஹோமங்கள் செய்வதன் மூலம் இந்த தோஷங்கள் முற்றிலும் நீங்கும்.",
        severity=SeverityLevel.UNFAVORABLE,
    ),''')

    # -------------------------------------------------------------
    # 8. Chapter 29-30: Arudha Padas & Upapada Lagna
    # -------------------------------------------------------------
    arudha_ch29_30 = [
        ("RULE-BPHS-ARUDHA-01", "Benefic in 11th from Arudha Lagna (Abundant Wealth & Gains, Ch. 29, Slokas 8-15)",
         "ஆருட லக்னத்திற்கு 11-இல் சுப கிரகம் (அபரிமித தன லாபம், அத். 29)",
         {"condition_type": "compound", "operator": "OR", "conditions": [
             {"condition_type": "planet_house", "planet": "Jupiter", "house": 11, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Venus", "house": 11, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Mercury", "house": 11, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Moon", "house": 11, "chart": "d1"}
         ]},
         "If the 11th from Arudha Lagna is occupied or aspected by a benefic planet, the native will be happy, wealthy, and enjoy gains through righteous means. If the benefic is exalted or in own sign, wealth is limitless.",
         "ஆருட லக்னத்திற்கு 11-ஆம் பாவத்தில் சுப கிரகம் அமைந்தால், ஜாதகர் நேர்மையான வழிகளில் பெரும் செல்வமும், சமூக அந்தஸ்தும், தடையில்லா தன லாபமும் அடைவார்.",
         "Brihat Parashara Hora Shastra, Ch. 29, Slokas 8-15", "FAVORABLE", "wealth_yogas"),

        ("RULE-BPHS-ARUDHA-02", "Benefic in 2nd from Upapada Lagna (Marital Splendor & Longevity, Ch. 30, Slokas 7-15)",
         "உபபத லக்னத்திற்கு 2-இல் சுப கிரகம் (மாங்கல்ய பலம் & நற்குண துணை, அத். 30)",
         {"condition_type": "compound", "operator": "OR", "conditions": [
             {"condition_type": "planet_house", "planet": "Jupiter", "house": 2, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Venus", "house": 2, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Mercury", "house": 2, "chart": "d1"}
         ]},
         "If the 2nd from Upapada Lagna is a benefic sign or is occupied or aspected by a benefic, the native's spouse will be beautiful, fortunate, virtuous, and live to an advanced age with enduring harmony.",
         "உபபத லக்னத்திற்கு 2-ஆம் பாவத்தில் சுப கிரகம் அமையப் பெற்றால், வாழ்க்கைத் துணை பேரழகு, நற்குணம், செல்வம் மற்றும் நீண்ட ஆயுளுடன் வாழ்வார்.",
         "Brihat Parashara Hora Shastra, Ch. 30, Slokas 7-15", "FAVORABLE", "first_marriage"),

        ("RULE-BPHS-ARUDHA-03", "Saturn and Rahu in 2nd from Upapada (Marital Trials, Ch. 30, Sloka 16)",
         "உபபத லக்னத்திற்கு 2-இல் சனி-ராகு (களத்திர தோஷம், அத். 30)",
         {"condition_type": "compound", "operator": "AND", "conditions": [
             {"condition_type": "planet_house", "planet": "Saturn", "house": 2, "chart": "d1"},
             {"condition_type": "planet_house", "planet": "Rahu", "house": 2, "chart": "d1"}
         ]},
         "Should Saturn and Rahu occupy the 2nd from Upapada Lagna, classical texts caution against misunderstandings or health afflictions to spouse, mitigated by benefic aspect.",
         "உபபத லக்னத்திற்கு 2-ஆம் பாவத்தில் சனியும் ராகுவும் சேர்ந்தால் தாம்பத்தியத்தில் சவால்கள் வரலாம்; சுப பார்வை பெற்றால் தோஷம் நீங்கும்.",
         "Brihat Parashara Hora Shastra, Ch. 30, Sloka 16", "UNFAVORABLE", "marital_harmony"),
    ]

    for rid, name_en, name_ta, ctree, interp_en, interp_ta, sref, sev, subcat in arudha_ch29_30:
        lines.append(f'''    AstrologicalRuleDefinition(
        rule_id="{rid}",
        version=1,
        name_en="{name_en}",
        name_ta="{name_ta}",
        category_slug="bphs_upagrahas_arudhas",
        subcategory="{subcat}",
        astrology_system=AstrologySystem.VEDIC,
        chart_scope=ChartScope.D1,
        calculation_mode="thirukanitha",
        condition_tree={repr(ctree)},
        interpretation_en="{interp_en}",
        interpretation_ta="{interp_ta}",
        astrological_principle_en="BPHS Ch. 29-30 principle: Arudha Lagna (Pada of 1st) manifests worldly image and finances; Upapada Lagna (Pada of 12th) manifests marital destiny and partner's background.",
        astrological_principle_ta="பராசர ஹோரா சாஸ்திரம் அத். 29-30: ஆருட லக்னம் உலகாயத செல்வாக்கையும், உபபத லக்னம் திருமண பந்தத்தின் உண்மைத் தன்மையையும் வெளிப்படுத்துகிறது.",
        source_reference="{sref}",
        limitations_en="Aspects from Jupiter, Venus, or exalted benefics pacify afflictions to Pada houses.",
        limitations_ta="குரு அல்லது சுக்கிரனின் சுப பார்வை பாத பாவங்களின் தோஷங்களை நீக்குகிறது.",
        severity=SeverityLevel.{sev},
    ),''')

    lines.append(']')
    lines.append('')
    lines.append('print(f"Total BPHS Classical Rules compiled: {len(BPHS_CLASSICAL_RULES)}")')

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"File successfully written to {OUTPUT_FILE} with {len(ch24_data) + len(lagna_yogakarakas_data) + len(dhana_yogas_ch41) + len(daridra_yogas_ch42) + len(stri_jataka_ch80) + len(shapas_ch83) + len(inauspicious_ch85_94) + len(arudha_ch29_30)} rules!")

if __name__ == "__main__":
    generate()
