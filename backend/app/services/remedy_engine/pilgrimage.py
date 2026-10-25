"""Kaveri Delta Navagraha Pilgrimage Circuit Planner & Route Engine.

Provides optimized, authentic pilgrimage circuits connecting all 9 Navagraha temples 
in the Thanjavur / Kumbakonam / Mayiladuthurai Kaveri Delta region of Tamil Nadu.
Features:
- 1-Day Express Circuit (time-optimized day loop starting from Kumbakonam)
- 2-Day Comprehensive Spiritual Circuit (Day 1: East/North Coastal; Day 2: Central/West)
- Chart-Aware Priority Route (tailors priority order to native's afflicted & Dasha planets)
"""

from typing import List, Dict, Any, Optional
from app.schemas.remedies import (
    PilgrimageTempleStop,
    PilgrimageDayPlan,
    PilgrimageCircuitResponse,
)

TEMPLE_METADATA: Dict[str, Dict[str, Any]] = {
    "sun": {
        "code": "TEMPLE_SURYANAR_KOVIL",
        "graha": "sun",
        "graha_name_en": "Sun (Surya)",
        "graha_name_ta": "சூரியன்",
        "name_en": "Suryanar Kovil (Sri Suryanarayana Swamy)",
        "name_ta": "சூரியனார் கோவில் (ஸ்ரீ சூரியநாராயண சுவாமி)",
        "presiding_deity_en": "Sri Suryanarayana Swamy with Usha and Chaya",
        "presiding_deity_ta": "ஸ்ரீ சூரியநாராயண சுவாமி - உஷா, சாயா தேவியர்",
        "place_name_en": "Suryanar Kovil (near Aduthurai)",
        "place_name_ta": "சூரியனார் கோவில் (ஆடுதுறை அருகில்)",
        "district_en": "Thanjavur",
        "district_ta": "தஞ்சாவூர்",
        "latitude": 11.0317,
        "longitude": 79.4678,
        "darshan_timings_en": "6:00 AM – 12:30 PM & 4:00 PM – 8:00 PM",
        "darshan_timings_ta": "காலை 6:00 – மதியம் 12:30 & மாலை 4:00 – இரவு 8:00",
        "special_ritual_en": "Mandatory circumambulation of Guru shrine first, followed by Surya Bhagavan and other 8 grahas in their separate shrines.",
        "special_ritual_ta": "முதலில் குரு பகவானை வணங்கிவிட்டு, பின் சூரிய பகவான் மற்றும் சுற்றியுள்ள மற்ற 8 கிரகங்களை பிரதக்ஷிணம் செய்து வழிபடுதல் மரபு.",
        "remedy_offerings_en": "Wheat grains (godhumai), red cloth, red lotus / arali flowers, jaggery pongal, lighting ghee deepams.",
        "remedy_offerings_ta": "கோதுமை தானம், சிவப்பு வஸ்திரம், செவ்வரளி/செந்தாமரை மாலை, சர்க்கரைப் பொங்கல் படைத்து நெய் தீபம் ஏற்றுதல்.",
    },
    "moon": {
        "code": "TEMPLE_THINGALUR",
        "graha": "moon",
        "graha_name_en": "Moon (Chandra)",
        "graha_name_ta": "சந்திரன்",
        "name_en": "Thingalur Kailasanathar Temple",
        "name_ta": "திங்களூர் கைலாசநாதர் கோவில்",
        "presiding_deity_en": "Sri Kailasanathar and Goddess Periyanayaki",
        "presiding_deity_ta": "ஸ்ரீ கைலாசநாதர் - பெரியநாயகி அம்மன்",
        "place_name_en": "Thingalur (near Thiruvaiyaru)",
        "place_name_ta": "திங்களூர் (திருவையாறு அருகில்)",
        "district_en": "Thanjavur",
        "district_ta": "தஞ்சாவூர்",
        "latitude": 10.8789,
        "longitude": 79.1678,
        "darshan_timings_en": "7:00 AM – 1:00 PM & 4:00 PM – 9:00 PM",
        "darshan_timings_ta": "காலை 7:00 – மதியம் 1:00 & மாலை 4:00 – இரவு 9:00",
        "special_ritual_en": "Lord Chandra worshipped Shiva here to be cured of Daksha's curse. Supreme sthalam for peace of mind, maternal health, and mental focus.",
        "special_ritual_ta": "சந்திரன் தக்ஷனின் சாபத்திலிருந்து விமோசனம் பெற்ற இடம். தாயார் நலம், மன அமைதி மற்றும் கல்வியில் மேன்மை பெற சிறப்பு அர்ச்சனை.",
        "remedy_offerings_en": "White raw rice, milk kheer (payasam), white cloth, white arali flowers, lighting lamps.",
        "remedy_offerings_ta": "பச்சரிசி, பசும்பால் பாயாசம், வெள்ளை வஸ்திரம், வெள்ளை அரளி மலர்கள் சாற்றி வழிபடுதல்.",
    },
    "mars": {
        "code": "TEMPLE_VAITHEESWARAN",
        "graha": "mars",
        "graha_name_en": "Mars (Chevvai / Angarakan)",
        "graha_name_ta": "செவ்வாய் (அங்காரகன்)",
        "name_en": "Vaitheeswaran Kovil (Sri Vaidyanatha Swamy)",
        "name_ta": "வைத்தீஸ்வரன் கோவில் (ஸ்ரீ வைத்தியநாத சுவாமி)",
        "presiding_deity_en": "Sri Vaidyanatha Swamy, Thaiyalnayaki Amman, and Lord Selva Muthukumaraswamy",
        "presiding_deity_ta": "ஸ்ரீ வைத்தியநாத சுவாமி - தையல்நாயகி அம்மன் - செல்வ முத்துக்குமாரசுவாமி",
        "place_name_en": "Vaitheeswaran Kovil (near Sirkazhi)",
        "place_name_ta": "வைத்தீஸ்வரன் கோவில் (சீர்காழி அருகில்)",
        "district_en": "Mayiladuthurai",
        "district_ta": "மயிலாடுதுறை",
        "latitude": 11.2023,
        "longitude": 79.7314,
        "darshan_timings_en": "6:00 AM – 1:00 PM & 4:00 PM – 9:00 PM",
        "darshan_timings_ta": "காலை 6:00 – மதியம் 1:00 & மாலை 4:00 – இரவு 9:00",
        "special_ritual_en": "Holy dip in the miraculous Siddhamrutha Theertham followed by worship at the separate Angaraka shrine to dissolve Kuja / Manglik dosha and chronic blood/skin ailments.",
        "special_ritual_ta": "சித்தாமிர்த தீர்த்தத்தில் நீராடி, அங்காரக பகவானுக்கு சிவப்பு வஸ்திரம் சாற்றி அர்ச்சனை செய்தல். செவ்வாய் தோஷம், திருமணத் தடை, பூமி/சொத்து சிக்கல்கள் தீர்க்கும் தலம்.",
        "remedy_offerings_en": "Red lentils (thoor dal), red cloth, red arali garland, lighting ghee lamps.",
        "remedy_offerings_ta": "துவரம்பருப்பு, சிவப்பு வஸ்திரம், செவ்வரளி மாலை சாற்றி, நெய் தீபமேற்றி வழிபடுதல்.",
    },
    "mercury": {
        "code": "TEMPLE_THIRUVENKADU",
        "graha": "mercury",
        "graha_name_en": "Mercury (Budhan)",
        "graha_name_ta": "புதன்",
        "name_en": "Thiruvenkadu Swetharanyeswarar Temple (Adi Chidambaram)",
        "name_ta": "திருவெண்காடு சுவேதாரண்யேஸ்வரர் கோவில் (ஆதி சிதம்பரம்)",
        "presiding_deity_en": "Sri Swetharanyeswarar, Brahmavidyambigai, and Lord Agora Murthy",
        "presiding_deity_ta": "ஸ்ரீ சுவேதாரண்யேஸ்வரர் - பிரம்மவித்யாம்பிகை - அகோர மூர்த்தி",
        "place_name_en": "Thiruvenkadu (near Poompuhar)",
        "place_name_ta": "திருவெண்காடு (பூம்புகார் அருகில்)",
        "district_en": "Mayiladuthurai",
        "district_ta": "மயிலாடுதுறை",
        "latitude": 11.1789,
        "longitude": 79.8234,
        "darshan_timings_en": "6:00 AM – 12:30 PM & 4:00 PM – 9:00 PM",
        "darshan_timings_ta": "காலை 6:00 – மதியம் 12:30 & மாலை 4:00 – இரவு 9:00",
        "special_ritual_en": "Holy dip in Surya, Chandra, and Agni theerthams. Supreme blessing for academic intellect, oratorical brilliance, commerce, and nervous system vitality.",
        "special_ritual_ta": "முக்குள தீர்த்தம் (சூரிய, சந்திர, அக்னி தீர்த்தங்கள்). கல்வி அறிவு, கணக்கு, வணிக மேன்மை மற்றும் நரம்பு மண்டல ஆரோக்கியம் நல்கும் புதன் சன்னதி.",
        "remedy_offerings_en": "Green gram (moong dal), green cloth, tulasi garland, lighting lamps.",
        "remedy_offerings_ta": "பச்சைப்பயறு, பச்சை வஸ்திரம், துளசி மாலை, வெண்காந்தள் மலர்கள் சாற்றி வழிபடுதல்.",
    },
    "jupiter": {
        "code": "TEMPLE_ALANGUDI",
        "graha": "jupiter",
        "graha_name_en": "Jupiter (Guru / Dakshinamurthy)",
        "graha_name_ta": "குரு (தட்சிணாமூர்த்தி)",
        "name_en": "Alangudi Apatsahayeswarar Temple",
        "name_ta": "ஆலங்குடி ஆபத்சகாயேஸ்வரர் கோவில்",
        "presiding_deity_en": "Sri Apatsahayeswarar and Goddess Elavarkuzhali",
        "presiding_deity_ta": "ஸ்ரீ ஆபத்சகாயேஸ்வரர் - ஏலவார்குழலி அம்மன்",
        "place_name_en": "Alangudi (near Valangaiman)",
        "place_name_ta": "ஆலங்குடி (வலங்கைமான் அருகில்)",
        "district_en": "Tiruvarur",
        "district_ta": "திருவாரூர்",
        "latitude": 10.8256,
        "longitude": 79.4089,
        "darshan_timings_en": "6:00 AM – 1:00 PM & 4:00 PM – 8:30 PM",
        "darshan_timings_ta": "காலை 6:00 – மதியம் 1:00 & மாலை 4:00 – இரவு 8:30",
        "special_ritual_en": "Circumambulating the presiding Lord Dakshinamurthy 24 times and lighting 24 ghee deepams in brass / clay lamps. Foremost shrine for marriage boon, childbirth, and spiritual wisdom.",
        "special_ritual_ta": "ஸ்ரீ தட்சிணாமூர்த்தியை 24 முறை வலம் வந்து, 24 நெய் தீபங்கள் ஏற்றி வழிபடுதல். திருமண யோகம், புத்திர பாக்கியம், கல்வி மற்றும் ஆன்மீக ஞானம் அருள்வது.",
        "remedy_offerings_en": "Yellow split chickpeas (chana dal) garland, yellow cloth, mullai / yellow flowers, lighting 24 ghee lamps.",
        "remedy_offerings_ta": "கொண்டைக்கடலை மாலை, மஞ்சள் வஸ்திரம், முல்லை மலர்கள் சாற்றி 24 நெய் தீபங்கள் ஏற்றுதல்.",
    },
    "venus": {
        "code": "TEMPLE_KANJANUR",
        "graha": "venus",
        "graha_name_en": "Venus (Sukran)",
        "graha_name_ta": "சுக்கிரன்",
        "name_en": "Kanjanur Agneeswarar Temple",
        "name_ta": "கஞ்சனூர் அக்னீஸ்வரர் கோவில்",
        "presiding_deity_en": "Sri Agneeswarar and Goddess Karpagambal",
        "presiding_deity_ta": "ஸ்ரீ அக்னீஸ்வரர் - கற்பகாம்பாள்",
        "place_name_en": "Kanjanur (near Kumbakonam)",
        "place_name_ta": "கஞ்சனூர் (கும்பகோணம் அருகில்)",
        "district_en": "Thanjavur",
        "district_ta": "தஞ்சாவூர்",
        "latitude": 11.0667,
        "longitude": 79.4833,
        "darshan_timings_en": "7:00 AM – 12:30 PM & 4:00 PM – 8:30 PM",
        "darshan_timings_ta": "காலை 7:00 – மதியம் 12:30 & மாலை 4:00 – இரவு 8:30",
        "special_ritual_en": "Lord Shiva himself manifests the luminous benevolence of Sukra here. Blesses with marital harmony, luxury, artistic success, and vehicles.",
        "special_ritual_ta": "சிவபெருமானே சுக்கிரனின் ஜோதி ஸ்வரூபமாக அருளும் தலம். குடும்ப அமைதி, தம்பதியர் ஒற்றுமை, செல்வம், கலை மற்றும் வாகன யோகம் நல்கும் தலம்.",
        "remedy_offerings_en": "White field beans (mochai), white silk cloth, white lotus, offering sweet payasam or milk rice.",
        "remedy_offerings_ta": "மொச்சைப்பயறு, வெண்பட்டு வஸ்திரம், வெண்தாமரை மலர்கள், பால் பாயாசம் படைத்து வழிபடுதல்.",
    },
    "saturn": {
        "code": "TEMPLE_THIRUNALLAR",
        "graha": "saturn",
        "graha_name_en": "Saturn (Saneeswara)",
        "graha_name_ta": "சனீஸ்வரர்",
        "name_en": "Thirunallar Dharbaranyeswarar Temple",
        "name_ta": "திருநள்ளாறு தர்பாரண்யேஸ்வரர் கோவில்",
        "presiding_deity_en": "Sri Dharbaranyeswarar, Goddess Pranambigai, and Sri Saneeswara Bhagavan",
        "presiding_deity_ta": "ஸ்ரீ தர்பாரண்யேஸ்வரர் - பிராணாம்பிகை - ஸ்ரீ சனீஸ்வர பகவான்",
        "place_name_en": "Thirunallar (near Karaikal)",
        "place_name_ta": "திருநள்ளாறு (காரைக்கால் அருகில்)",
        "district_en": "Karaikal / Puducherry-TN Border",
        "district_ta": "காரைக்கால்",
        "latitude": 10.9272,
        "longitude": 79.7911,
        "darshan_timings_en": "5:30 AM – 1:00 PM & 4:00 PM – 9:00 PM",
        "darshan_timings_ta": "காலை 5:30 – மதியம் 1:00 & மாலை 4:00 – இரவு 9:00",
        "special_ritual_en": "Taking a sacred bath in Nala Theertham (leaving the old clothes behind or bathing clean), lighting black sesame oil lamps in clay cups (ellu deepam), and praying for relief from Sade Sati (Ezharai Sani), Ashtama Shani, and chronic hardships.",
        "special_ritual_ta": "நள தீர்த்தத்தில் புனித நீராடுதல், எள் எண்ணெயில் கருப்பு எள் முடிச்சு தீபமிடுதல் (எள்தீபம்). ஏழரைச் சனி, அஷ்டமச் சனி, கண்டகச் சனி மற்றும் தீராத வாத நோய்களின் தாக்கம் தணியும்.",
        "remedy_offerings_en": "Black sesame seeds (ellu), black/dark blue cloth, blue aparajita/neelothpalam flowers, lighting gingelly oil lamps.",
        "remedy_offerings_ta": "கருப்பு எள், நீல நிற வஸ்திரம், நீலோத்பலம்/கருங்குவளை மலர்கள் சாற்றி, நல்லெண்ணெய் எள்தீபம் ஏற்றுதல்.",
    },
    "rahu": {
        "code": "TEMPLE_THIRUNAGESWARAM",
        "graha": "rahu",
        "graha_name_en": "Rahu Bhagavan",
        "graha_name_ta": "ராகு பகவான்",
        "name_en": "Thirunageswaram Naganathaswamy Temple",
        "name_ta": "திருநாகேஸ்வரம் நாகநாதசுவாமி கோவில்",
        "presiding_deity_en": "Sri Naganathaswamy, Pirayanindasoodi Amman, and Sri Rahu Bhagavan with consorts Nagavalli & Nagakanni",
        "presiding_deity_ta": "ஸ்ரீ நாகநாதசுவாமி - பிறையணிந்தசூடி அம்மன் - நாகவல்லி, நாகக்கன்னியுடன் ராகு பகவான்",
        "place_name_en": "Thirunageswaram (near Kumbakonam)",
        "place_name_ta": "திருநாகேஸ்வரம் (கும்பகோணம் அருகில்)",
        "district_en": "Thanjavur",
        "district_ta": "தஞ்சாவூர்",
        "latitude": 10.9633,
        "longitude": 79.4317,
        "darshan_timings_en": "6:00 AM – 12:45 PM & 4:00 PM – 8:30 PM",
        "darshan_timings_ta": "காலை 6:00 – மதியம் 12:45 & மாலை 4:00 – இரவு 8:30",
        "special_ritual_en": "Miraculous Milk Abhishekam during Rahu Kalam, where fresh cow's milk poured over the idol visibly shifts to light blue as it streams across the stone. Removes Sarpa Dosha, Kala Sarpa, and phobias.",
        "special_ritual_ta": "ராகு காலத்தில் செய்யப்படும் பாலாபிஷேகம்: சிலை மீது பால் ஊற்றப்படும் போது நீல நிறமாக மாறும் அற்புதம். நாக தோஷம், காலசர்ப்ப தோஷம், திருமணத் தடை நீங்கும்.",
        "remedy_offerings_en": "Fresh cow's milk for abhishekam, black gram (urad dal), blue/mixed cloth, mandhara flowers, lighting gingelly oil lamps.",
        "remedy_offerings_ta": "பாலாபிஷேகத்திற்கு பசும்பால், உளுந்து தானம், நீல வஸ்திரம், மந்தாரை மலர்கள் சாற்றி வழிபடுதல்.",
    },
    "ketu": {
        "code": "TEMPLE_KEEZHPERUMPALLAM",
        "graha": "ketu",
        "graha_name_en": "Ketu Bhagavan",
        "graha_name_ta": "கேது பகவான்",
        "name_en": "Keezhperumpallam Naganathaswamy Temple",
        "name_ta": "கீழ்ப்பெரும்பள்ளம் நாகநாதசுவாமி கோவில்",
        "presiding_deity_en": "Sri Naganathaswamy and Goddess Soundaranayaki",
        "presiding_deity_ta": "ஸ்ரீ நாகநாதசுவாமி - சௌந்தரநாயகி",
        "place_name_en": "Keezhperumpallam (near Poompuhar)",
        "place_name_ta": "கீழ்ப்பெரும்பள்ளம் (பூம்புகார் அருகில்)",
        "district_en": "Mayiladuthurai",
        "district_ta": "மயிலாடுதுறை",
        "latitude": 11.1436,
        "longitude": 79.8456,
        "darshan_timings_en": "6:00 AM – 12:30 PM & 4:00 PM – 8:30 PM",
        "darshan_timings_ta": "காலை 6:00 – மதியம் 12:30 & மாலை 4:00 – இரவு 8:30",
        "special_ritual_en": "Ketu Bhagavan is depicted here in an unusual posture with a human head, folded hands, and a serpent tail worshiping Lord Shiva. Bestows spiritual liberation, occult wisdom, and freedom from addictions.",
        "special_ritual_ta": "மனித முகத்துடனும், கைகூப்பிய நிலையிலும், பாம்பு உடலுடனும் சிவனை வணங்கும் அபூர்வ கேது சன்னதி. ஆன்மீக மேன்மை, ஞானம், குலதெய்வ அருள் மற்றும் நச்சு பிணிகள் நீங்கும்.",
        "remedy_offerings_en": "Horse gram (kollu), multi-coloured / spotted cloth, red arali garland, lighting ghee lamps.",
        "remedy_offerings_ta": "கொள்ளு தானம், பலவண்ண வஸ்திரம், செவ்வரளி மாலை சாற்றி, நெய் தீபமேற்றி வழிபடுதல்.",
    },
}


class PilgrimageCircuitEngine:
    """Calculates and assembles Kaveri Delta Navagraha Pilgrimage Circuits."""

    @classmethod
    def get_standard_circuits(cls) -> List[PilgrimageCircuitResponse]:
        """Returns the classical 1-Day Express and 2-Day Comprehensive circuits."""
        return [
            cls.build_1_day_express_circuit(),
            cls.build_2_day_comprehensive_circuit(),
        ]

    @classmethod
    def build_1_day_express_circuit(
        cls,
        priority_planets: Optional[List[str]] = None,
        priority_reasons: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> PilgrimageCircuitResponse:
        """Constructs an optimized 1-day express circuit starting and ending in Kumbakonam."""
        priority_planets = priority_planets or []
        priority_reasons = priority_reasons or {}

        # Optimized sequence to minimize zigzagging around Kumbakonam
        sequence = [
            ("moon", "06:00 AM – 07:15 AM", "காலை 06:00 – 07:15", 35.0, 45),
            ("jupiter", "08:00 AM – 09:15 AM", "காலை 08:00 – 09:15", 28.0, 40),
            ("rahu", "10:00 AM – 11:15 AM", "காலை 10:00 – 11:15", 14.0, 25),
            ("sun", "11:45 AM – 12:45 PM", "மதியம் 11:45 – 12:45", 8.0, 15),
            # Break between 12:45 PM and 4:00 PM (Temples closed)
            ("venus", "04:15 PM – 05:15 PM", "மாலை 04:15 – 05:15", 6.0, 15),
            ("mars", "05:45 PM – 06:45 PM", "மாலை 05:45 – 06:45", 22.0, 35),
            ("mercury", "07:15 PM – 08:00 PM", "இரவு 07:15 – 08:00", 12.0, 20),
            ("ketu", "08:15 PM – 09:00 PM", "இரவு 08:15 – 09:00", 6.0, 12),
            ("saturn", "09:30 PM (or next morning)", "இரவு 09:30 (அல்லது மறுநாள் காலை)", 25.0, 35),
        ]

        stops: List[PilgrimageTempleStop] = []
        total_dist = 0.0

        for idx, (graha, time_en, time_ta, dist, mins) in enumerate(sequence, start=1):
            meta = TEMPLE_METADATA[graha]
            is_priority = graha in priority_planets
            reasons = priority_reasons.get(graha, {})
            total_dist += dist

            stop = PilgrimageTempleStop(
                order_in_day=idx,
                code=meta["code"],
                graha=meta["graha"],
                graha_name_en=meta["graha_name_en"],
                graha_name_ta=meta["graha_name_ta"],
                name_en=meta["name_en"],
                name_ta=meta["name_ta"],
                presiding_deity_en=meta["presiding_deity_en"],
                presiding_deity_ta=meta["presiding_deity_ta"],
                place_name_en=meta["place_name_en"],
                place_name_ta=meta["place_name_ta"],
                district_en=meta["district_en"],
                district_ta=meta["district_ta"],
                latitude=meta["latitude"],
                longitude=meta["longitude"],
                visiting_time_window_en=time_en,
                visiting_time_window_ta=time_ta,
                darshan_timings_en=meta["darshan_timings_en"],
                darshan_timings_ta=meta["darshan_timings_ta"],
                special_ritual_en=meta["special_ritual_en"],
                special_ritual_ta=meta["special_ritual_ta"],
                remedy_offerings_en=meta["remedy_offerings_en"],
                remedy_offerings_ta=meta["remedy_offerings_ta"],
                distance_from_previous_km=dist,
                driving_minutes_from_previous=mins,
                is_chart_priority=is_priority,
                priority_level="high" if is_priority else None,
                chart_priority_reason_en=reasons.get("en"),
                chart_priority_reason_ta=reasons.get("ta"),
            )
            stops.append(stop)

        day_plan = PilgrimageDayPlan(
            day_number=1,
            title_en="Kumbakonam 1-Day Express Navagraha Yatra",
            title_ta="கும்பகோணம் 1-நாள் விரைவு நவக்கிரக யாத்திரை",
            base_camp_en="Kumbakonam",
            base_camp_ta="கும்பகோணம்",
            recommended_start_time="05:30 AM",
            total_distance_km=round(total_dist, 1),
            estimated_travel_time_hours=13.5,
            temple_stops=stops,
            practical_tips_en=[
                "Start promptly at 5:30 AM from Kumbakonam to reach Thingalur before 6:30 AM.",
                "All Kaveri Delta temples strictly close between 1:00 PM and 4:00 PM for afternoon uthsavam rest.",
                "Take lunch in Kumbakonam, Mayiladuthurai, or near Aduthurai between 1:00 PM and 3:30 PM.",
                "If Thirunallar darshan cannot be finished before 9:00 PM, stay overnight in Karaikal/Kumbakonam and take Nala Theertham dip the next morning.",
            ],
            practical_tips_ta=[
                "காலை 5:30 மணிக்கே கும்பகோணத்திலிருந்து புறப்பட்டு திங்களூரை 6:30 மணிக்குள் அடைவது உசிதம்.",
                "அனைத்து தலங்களும் மதியம் 1:00 முதல் மாலை 4:00 வரை நடை சாத்தப்பட்டிருக்கும்.",
                "மதிய உணவை கும்பகோணம், மயிலாடுதுறை அல்லது ஆடுதுறையில் முடித்துக் கொள்ளவும்.",
                "திருநள்ளாறு தரிசனம் இரவில் தாமதமானால், காரைக்காலில் தங்கி மறுநாள் அதிகாலை நள தீர்த்தத்தில் நீராடி வழிபடலாம்.",
            ],
        )

        return PilgrimageCircuitResponse(
            circuit_id="1_day_express",
            title_en="1-Day Express Navagraha Circuit (Kumbakonam Hub)",
            title_ta="1-நாள் விரைவு நவக்கிரக யாத்திரை (கும்பகோணம் மையம்)",
            summary_en="Compact 1-day time-synchronized pilgrimage covering all 9 Kaveri Delta temples with scheduled darshan windows around temple closure timings.",
            summary_ta="கோவில் நடை சாத்தப்படும் நேரங்களை கணக்கில் கொண்டு, ஒரே நாளில் 9 நவக்கிரகங்களையும் தரிசிக்கும் துல்லியமான யாத்திரை திட்டம்.",
            base_hub_en="Kumbakonam",
            base_hub_ta="கும்பகோணம்",
            total_temples=9,
            total_distance_km=round(total_dist, 1),
            day_plans=[day_plan],
            chart_priorities_present=bool(priority_planets),
            rahu_kalam_guidelines_en="Check daily Rahu Kalam. For Thirunageswaram, visiting during Rahu Kalam is highly auspicious for milk abhishekam.",
            rahu_kalam_guidelines_ta="தினசரி ராகு காலத்தை சரிபார்க்கவும். திருநாகேஸ்வரத்திற்கு மட்டும் ராகு காலத்தில் செல்வது பாலாபிஷேகத்திற்கு மிகவும் விசேஷம்.",
            dress_code_and_customs_en="Strict traditional attire required: Dhoti/Veshti with Angavastram for men, Sarees/Salwar with Dupatta for women. Leather items strictly prohibited inside sanctum.",
            dress_code_and_customs_ta="பாரம்பரிய ஆடை அணிவது கட்டாயம்: ஆண்கள் வேட்டி-சட்டை அல்லது அங்கவஸ்திரம்; பெண்கள் புடவை அல்லது துப்பட்டாவுடன் சுடிதார்.",
        )

    @classmethod
    def build_2_day_comprehensive_circuit(
        cls,
        priority_planets: Optional[List[str]] = None,
        priority_reasons: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> PilgrimageCircuitResponse:
        """Constructs an unhurried, classical 2-day pilgrimage separating coastal and central sectors."""
        priority_planets = priority_planets or []
        priority_reasons = priority_reasons or {}

        # Day 1: Coastal & Eastern Sector (Mars, Mercury, Ketu, Saturn)
        day1_seq = [
            ("mars", "07:30 AM – 09:30 AM", "காலை 07:30 – 09:30", 50.0, 60),
            ("mercury", "10:15 AM – 11:30 AM", "காலை 10:15 – 11:30", 12.0, 20),
            ("ketu", "11:45 AM – 12:45 PM", "மதியம் 11:45 – 12:45", 6.0, 15),
            # Rest and travel to Karaikal
            ("saturn", "05:00 PM – 08:30 PM", "மாலை 05:00 – இரவு 08:30", 35.0, 50),
        ]

        # Day 2: Central & Southern Sector (Sun, Venus, Rahu, Jupiter, Moon)
        day2_seq = [
            ("sun", "07:00 AM – 08:30 AM", "காலை 07:00 – 08:30", 15.0, 25),
            ("venus", "09:00 AM – 10:15 AM", "காலை 09:00 – 10:15", 6.0, 15),
            ("rahu", "10:45 AM – 12:30 PM", "காலை 10:45 – மதியம் 12:30", 12.0, 20),
            # Rest in Kumbakonam
            ("jupiter", "04:30 PM – 06:15 PM", "மாலை 04:30 – 06:15", 18.0, 30),
            ("moon", "07:00 PM – 08:30 PM", "இரவு 07:00 – 08:30", 32.0, 50),
        ]

        day1_stops: List[PilgrimageTempleStop] = []
        d1_dist = 0.0
        for idx, (graha, t_en, t_ta, dist, mins) in enumerate(day1_seq, start=1):
            meta = TEMPLE_METADATA[graha]
            is_priority = graha in priority_planets
            reasons = priority_reasons.get(graha, {})
            d1_dist += dist
            day1_stops.append(
                PilgrimageTempleStop(
                    order_in_day=idx,
                    code=meta["code"],
                    graha=meta["graha"],
                    graha_name_en=meta["graha_name_en"],
                    graha_name_ta=meta["graha_name_ta"],
                    name_en=meta["name_en"],
                    name_ta=meta["name_ta"],
                    presiding_deity_en=meta["presiding_deity_en"],
                    presiding_deity_ta=meta["presiding_deity_ta"],
                    place_name_en=meta["place_name_en"],
                    place_name_ta=meta["place_name_ta"],
                    district_en=meta["district_en"],
                    district_ta=meta["district_ta"],
                    latitude=meta["latitude"],
                    longitude=meta["longitude"],
                    visiting_time_window_en=t_en,
                    visiting_time_window_ta=t_ta,
                    darshan_timings_en=meta["darshan_timings_en"],
                    darshan_timings_ta=meta["darshan_timings_ta"],
                    special_ritual_en=meta["special_ritual_en"],
                    special_ritual_ta=meta["special_ritual_ta"],
                    remedy_offerings_en=meta["remedy_offerings_en"],
                    remedy_offerings_ta=meta["remedy_offerings_ta"],
                    distance_from_previous_km=dist,
                    driving_minutes_from_previous=mins,
                    is_chart_priority=is_priority,
                    priority_level="high" if is_priority else None,
                    chart_priority_reason_en=reasons.get("en"),
                    chart_priority_reason_ta=reasons.get("ta"),
                )
            )

        day2_stops: List[PilgrimageTempleStop] = []
        d2_dist = 0.0
        for idx, (graha, t_en, t_ta, dist, mins) in enumerate(day2_seq, start=1):
            meta = TEMPLE_METADATA[graha]
            is_priority = graha in priority_planets
            reasons = priority_reasons.get(graha, {})
            d2_dist += dist
            day2_stops.append(
                PilgrimageTempleStop(
                    order_in_day=idx,
                    code=meta["code"],
                    graha=meta["graha"],
                    graha_name_en=meta["graha_name_en"],
                    graha_name_ta=meta["graha_name_ta"],
                    name_en=meta["name_en"],
                    name_ta=meta["name_ta"],
                    presiding_deity_en=meta["presiding_deity_en"],
                    presiding_deity_ta=meta["presiding_deity_ta"],
                    place_name_en=meta["place_name_en"],
                    place_name_ta=meta["place_name_ta"],
                    district_en=meta["district_en"],
                    district_ta=meta["district_ta"],
                    latitude=meta["latitude"],
                    longitude=meta["longitude"],
                    visiting_time_window_en=t_en,
                    visiting_time_window_ta=t_ta,
                    darshan_timings_en=meta["darshan_timings_en"],
                    darshan_timings_ta=meta["darshan_timings_ta"],
                    special_ritual_en=meta["special_ritual_en"],
                    special_ritual_ta=meta["special_ritual_ta"],
                    remedy_offerings_en=meta["remedy_offerings_en"],
                    remedy_offerings_ta=meta["remedy_offerings_ta"],
                    distance_from_previous_km=dist,
                    driving_minutes_from_previous=mins,
                    is_chart_priority=is_priority,
                    priority_level="high" if is_priority else None,
                    chart_priority_reason_en=reasons.get("en"),
                    chart_priority_reason_ta=reasons.get("ta"),
                )
            )

        plan1 = PilgrimageDayPlan(
            day_number=1,
            title_en="Day 1: Eastern & Coastal Delta (Chevvai, Budhan, Ketu, Shani)",
            title_ta="நாள் 1: கிழக்கு & கடற்கரை மண்டலம் (செவ்வாய், புதன், கேது, சனி)",
            base_camp_en="Mayiladuthurai / Karaikal",
            base_camp_ta="மயிலாடுதுறை / காரைக்கால்",
            recommended_start_time="07:00 AM",
            total_distance_km=round(d1_dist, 1),
            estimated_travel_time_hours=8.0,
            temple_stops=day1_stops,
            practical_tips_en=[
                "Vaitheeswaran Kovil is crowded on Tuesdays; allow at least 1.5 hours for darshan.",
                "Bring a change of traditional clothing for Thirunallar's Nala Theertham sacred tank.",
                "Stay overnight in Karaikal or return to Kumbakonam.",
            ],
            practical_tips_ta=[
                "வைத்தீஸ்வரன் கோவிலில் செவ்வாய்க்கிழமைகளில் பக்தர்கள் கூட்டம் அதிகம்; குறைந்தது 1.5 மணி நேரம் ஒதுக்கவும்.",
                "திருநள்ளாறு நள தீர்த்தத்தில் நீராட மாற்று பாரம்பரிய ஆடைகளை உடன் கொண்டு செல்லவும்.",
                "இரவு காரைக்கால் அல்லது கும்பகோணத்தில் தங்கி ஓய்வெடுக்கலாம்.",
            ],
        )

        plan2 = PilgrimageDayPlan(
            day_number=2,
            title_en="Day 2: Central & Southern Delta (Surya, Sukra, Rahu, Guru, Chandra)",
            title_ta="நாள் 2: மத்திய & தெற்கு மண்டலம் (சூரியன், சுக்கிரன், ராகு, குரு, சந்திரன்)",
            base_camp_en="Kumbakonam",
            base_camp_ta="கும்பகோணம்",
            recommended_start_time="06:30 AM",
            total_distance_km=round(d2_dist, 1),
            estimated_travel_time_hours=8.5,
            temple_stops=day2_stops,
            practical_tips_en=[
                "At Suryanar Kovil, remember to pay respects at the Guru shrine before proceeding to Surya.",
                "Coordinate Thirunageswaram timing with the afternoon Rahu Kalam if milk abhishekam is desired.",
                "Thingalur is peaceful in the late evening; ideal concluding shrine for mental calm.",
            ],
            practical_tips_ta=[
                "சூரியனார் கோவிலில் சூரியனை வழிபடும் முன் குரு பகவானை வணங்குவது அவசிய விதி.",
                "பாலாபிஷேகம் செய்ய விரும்புவோர் திருநாகேஸ்வரத்திற்கு ராகு காலத்தில் செல்வதை உறுதி செய்யவும்.",
                "திங்களூர் இரவு வேளையில் அமைதியாக இருக்கும்; மன அமைதிக்கான யாத்திரையின் நிறைவு ஸ்தலம்.",
            ],
        )

        return PilgrimageCircuitResponse(
            circuit_id="2_day_comprehensive",
            title_en="2-Day Comprehensive Spiritual Navagraha Yatra",
            title_ta="2-நாள் முழுமையான ஆன்மீக நவக்கிரக யாத்திரை",
            summary_en="Relaxed 2-day circuit dividing temples into geographical clusters with ample time for personal Archanas, Theertha snanams, and Parikrama.",
            summary_ta="பதற்றமின்றி அர்ச்சனை, தீர்த்த நீராடல் மற்றும் பிரகார பிரதக்ஷிணம் செய்ய உகந்த 2-நாள் புண்ணிய யாத்திரை.",
            base_hub_en="Kumbakonam & Mayiladuthurai",
            base_hub_ta="கும்பகோணம் & மயிலாடுதுறை",
            total_temples=9,
            total_distance_km=round(d1_dist + d2_dist, 1),
            day_plans=[plan1, plan2],
            chart_priorities_present=bool(priority_planets),
            rahu_kalam_guidelines_en="On Day 2, plan Thirunageswaram darshan during Rahu Kalam to witness the sacred milk turning blue during abhishekam.",
            rahu_kalam_guidelines_ta="நாள் 2 இல், திருநாகேஸ்வரம் அபிஷேகத்தை ராகு காலத்தில் தரிசித்து நீல நிறமாகும் அதிசயத்தைக் காணலாம்.",
            dress_code_and_customs_en="Traditional Veshti/Saree attire. Devotees taking a holy dip at Nala Theertham (Thirunallar) should wear clean clothes thereafter and light black sesame lamps.",
            dress_code_and_customs_ta="வேட்டி அல்லது புடவை கட்டாயம். திருநள்ளாற்றில் நீராடிய பின் புதிய/சுத்தமான ஆடை அணிந்து எள்தீபம் ஏற்ற வேண்டும்.",
        )

    @classmethod
    def generate_personalized_circuit(
        cls,
        chart_context: Dict[str, Any],
        circuit_type: str = "2_day",
    ) -> PilgrimageCircuitResponse:
        """Examines chart afflictions and Dasha lords to produce a customized, prioritized pilgrimage circuit."""
        priority_planets: List[str] = []
        priority_reasons: Dict[str, Dict[str, str]] = {}

        # 1. Running Mahadasha & Bhukti
        mahadasha = (chart_context.get("running_mahadasha") or "").lower()
        bhukti = (chart_context.get("running_bhukti") or "").lower()
        if mahadasha in TEMPLE_METADATA:
            priority_planets.append(mahadasha)
            priority_reasons[mahadasha] = {
                "en": f"Active Mahadasha Lord ({mahadasha.capitalize()}). Primary governor of life trends, vitality, and outcomes during this period.",
                "ta": f"தற்போது நடைபெறும் மகாதிசா நாதன் ({TEMPLE_METADATA[mahadasha]['graha_name_ta']}). உங்கள் வாழ்வின் முக்கிய திருப்புமுனைகளை வழிநடத்துபவர்.",
            }
        if bhukti in TEMPLE_METADATA and bhukti != mahadasha:
            priority_planets.append(bhukti)
            priority_reasons[bhukti] = {
                "en": f"Active Antardasha / Bhukti Lord ({bhukti.capitalize()}). Immediate karmic driver operating right now.",
                "ta": f"தற்போது நடைபெறும் அந்தர்திசை / புக்தி நாதன் ({TEMPLE_METADATA[bhukti]['graha_name_ta']}). நிகழ்கால பலன்களை தீர்மானிப்பவர்.",
            }

        # 2. Debilitated planets
        debilitated = chart_context.get("debilitated_planets") or []
        for p in debilitated:
            p_clean = p.lower()
            if p_clean in TEMPLE_METADATA and p_clean not in priority_planets:
                priority_planets.append(p_clean)
                priority_reasons[p_clean] = {
                    "en": f"Debilitated (Neecha) in Rasi. Temple visit strengthens positive dispositor vibrations and alleviates functional weaknesses.",
                    "ta": f"ராசி கட்டத்தில் நீச்சம் பெற்ற கிரகம். தலம் சென்று அர்ச்சனை செய்வது நீச்ச தோஷத்தை போக்கி நற்பலன்களைத் தரும்.",
                }

        # 3. Combust planets
        combust = chart_context.get("combust_planets") or []
        for p in combust:
            p_clean = p.lower()
            if p_clean in TEMPLE_METADATA and p_clean not in priority_planets:
                priority_planets.append(p_clean)
                priority_reasons[p_clean] = {
                    "en": f"Combust (Astangata) by solar heat. Darshan at this consecrated sthalam restores planetary effulgence.",
                    "ta": f"சூரியனால் அஸ்தமனம் (தகனம்) அடைந்த கிரகம். திருத்தல வழிபாடு கிரகத்தின் பலத்தை புதுப்பிக்கும்.",
                }

        # 4. Kuja Dosha (Manglik)
        if chart_context.get("kuja_dosha_status") == "present" and "mars" not in priority_planets:
            priority_planets.append("mars")
            priority_reasons["mars"] = {
                "en": "Kuja / Manglik Dosha detected. Vaitheeswaran Kovil is the supreme classical pariharam sthalam for marital harmony and obstacle clearance.",
                "ta": "செவ்வாய் தோஷம் உள்ளதால், வைத்தீஸ்வரன் கோவில் வழிபாடு திருமணத் தடைகளை நீக்கி சுபகாரியங்களை விரைவில் நடத்தும்.",
            }

        # 5. Sade Sati / Shani Affliction
        # If saturn not in priority, check if saturn is in dusthana or functional malefic
        func_malefics = [m.lower() for m in (chart_context.get("functional_malefics") or [])]
        if "saturn" in func_malefics and "saturn" not in priority_planets:
            priority_planets.append("saturn")
            priority_reasons["saturn"] = {
                "en": "Functional malefic or affliction period. Thirunallar Nala Theertham dip and Ellu Deepam provide essential pacification.",
                "ta": "சனி பகவான் பாதக/மறைவிட தொடர்பு பெற்றுள்ளார். திருநள்ளாறு நள தீர்த்த நீராடலும் எள்தீபமும் அமைதி தரும்.",
            }

        if circuit_type == "1_day_express":
            return cls.build_1_day_express_circuit(priority_planets, priority_reasons)
        return cls.build_2_day_comprehensive_circuit(priority_planets, priority_reasons)
