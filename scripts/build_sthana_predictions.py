# -*- coding: utf-8 -*-
"""
Full Generator for 108 Planetary House Placements (9 Planets x 12 Houses)
Authoritative Vedic Astrological synthesis based on:
- Dr. B. V. Raman: 'How to Judge a Horoscope' (Vol 1 & 2)
- Kalyana Varma: 'Saravali' (Ch. 30)
- Maharishi Parashara: 'Brihat Parashara Hora Shastra' (Ch. 24)
- Tamil Classical Texts: 'Jathaka Alankaram' & 'Pulippani'
"""

import json

PLANETS = [
    {"id": "Sun", "name_en": "Sun", "name_ta": "சூரியன்", "symbol": "☀️", "element": "Agni (தீ)"},
    {"id": "Moon", "name_en": "Moon", "name_ta": "சந்திரன்", "symbol": "🌙", "element": "Jala (நீர்)"},
    {"id": "Mars", "name_en": "Mars", "name_ta": "செவ்வாய்", "symbol": "🔴", "element": "Agni (தீ)"},
    {"id": "Mercury", "name_en": "Mercury", "name_ta": "புதன்", "symbol": "🟢", "element": "Prithvi (நிலம்)"},
    {"id": "Jupiter", "name_en": "Jupiter", "name_ta": "குரு", "symbol": "🟡", "element": "Akasha (ஆகாயம்)"},
    {"id": "Venus", "name_en": "Venus", "name_ta": "சுக்கிரன்", "symbol": "✨", "element": "Jala (நீர்)"},
    {"id": "Saturn", "name_en": "Saturn", "name_ta": "சனி", "symbol": "🪐", "element": "Vayu (காற்று)"},
    {"id": "Rahu", "name_en": "Rahu", "name_ta": "ராகு", "symbol": "🐉", "element": "Vayu (சாயா)"},
    {"id": "Ketu", "name_en": "Ketu", "name_ta": "கேது", "symbol": "☄️", "element": "Moksha (சாயா)"},
]

HOUSES = [
    {
        "house": 1,
        "name_en": "1st House (Lagna / Tanu Bhava)",
        "name_ta": "1-ஆம் பாவம் - லக்னம் (தனு பாவம்)",
        "significance_en": "Self, physical body, complexion, health, personality, self-respect, innate temperament",
        "significance_ta": "சுய அடையாளம், உடல் கட்டமைப்பு, தோற்றம், ஆரோக்கியம், தன்னம்பிக்கை, மானமரியாதை, சுபாவம்",
        "category": "kendra"
    },
    {
        "house": 2,
        "name_en": "2nd House (Dhana Bhava)",
        "name_ta": "2-ஆம் பாவம் - தன பாவம் (வாக்கு & குடும்பம்)",
        "significance_en": "Wealth, liquid money, speech, family, right eye, food habits, initial education",
        "significance_ta": "செல்வம், பண வரவு, பேச்சாற்றல், வாக்கு நாணயம், குடும்ப நலம், வலது கண், உணவுப் பழக்கம்",
        "category": "panaphara"
    },
    {
        "house": 3,
        "name_en": "3rd House (Sahaja & Dhairya Bhava)",
        "name_ta": "3-ஆம் பாவம் - சகஜ பாவம் (தைரியம் & இளைய சகோதரம்)",
        "significance_en": "Courage, valor, younger siblings, fine arts, short journeys, writing, communication",
        "significance_ta": "தைரியம், வீரம், இளைய சகோதரர்கள், கலைத் திறன், குறுகிய பயணங்கள், எழுத்து, தகவல் தொடர்பு",
        "category": "apoklima"
    },
    {
        "house": 4,
        "name_en": "4th House (Sukha & Matru Bhava)",
        "name_ta": "4-ஆம் பாவம் - சுக பாவம் (தாய், நிலம் & வாகனம்)",
        "significance_en": "Mother, domestic happiness, immovable property, vehicles, primary education, peace of mind",
        "significance_ta": "தாய் நலம், வீட்டு சுகம், பூமி & அசையா சொத்துகள், வாகனங்கள், கல்வி, மன நிம்மதி",
        "category": "kendra"
    },
    {
        "house": 5,
        "name_en": "5th House (Putra & Poorvapunya Bhava)",
        "name_ta": "5-ஆம் பாவம் - புத்திர பாவம் (பூர்வ புண்ணியம் & புத்தி)",
        "significance_en": "Children, intellect, past life merit, devotion, mantra siddhi, speculation, romance",
        "significance_ta": "குழந்தை பாக்கியம், கூர்மையான புத்தி, பூர்வ புண்ணியம், தெய்வ பக்தி, மந்திர சித்தி, உல்லாசம்",
        "category": "trikona"
    },
    {
        "house": 6,
        "name_en": "6th House (Rina, Roga, Satru Bhava)",
        "name_ta": "6-ஆம் பாவம் - ரண ருண ரோக பாவம் (எதிரி, கடன் & நோய்)",
        "significance_en": "Debts, diseases, adversaries, legal disputes, maternal uncle, daily work, service",
        "significance_ta": "கடன், வியாதிகள், எதிரிகள், வழக்குகள், தாய்மாமன், தினசரி உழைப்பு, அடிமைத் தொழில்",
        "category": "dusthana"
    },
    {
        "house": 7,
        "name_en": "7th House (Kalathra Bhava)",
        "name_ta": "7-ஆம் பாவம் - களத்திர பாவம் (வாழ்க்கைத் துணை & கூட்டு)",
        "significance_en": "Spouse, marriage, conjugal harmony, business partnerships, public relations, foreign residence",
        "significance_ta": "வாழ்க்கைத் துணை, திருமண வாழ்க்கை, தாம்பத்திய சுகம், தொழில் கூட்டாளிகள், பொதுத் தொடர்பு, தூரப் பயணம்",
        "category": "kendra"
    },
    {
        "house": 8,
        "name_en": "8th House (Ayur & Randhra Bhava)",
        "name_ta": "8-ஆம் பாவம் - ஆயுள் பாவம் (அஷ்டம பாவம் & மறைவு)",
        "significance_en": "Longevity, sudden events, unearned wealth, legacies, occult wisdom, humiliation, chronic illness",
        "significance_ta": "ஆயுள் பலம், திடீர் விபத்துகள்/அதிர்ஷ்டம், எதிர்பாராத தன வரவு, மறைமுக ஞானம், அவமானம், தீராத பிணிகள்",
        "category": "dusthana"
    },
    {
        "house": 9,
        "name_en": "9th House (Bhagya & Dharma Bhava)",
        "name_ta": "9-ஆம் பாவம் - பாக்கிய பாவம் (தர்மம் & தந்தை)",
        "significance_en": "Fortune, father, higher spiritual wisdom, pilgrimages, divine grace, guru, righteous deeds",
        "significance_ta": "பாக்கியம், தந்தை நலம், ஆன்மீக நாட்டம், திருத்தலப் பயணம், குருவருள், தர்ம சிந்தனை, நற்பெயர்",
        "category": "trikona"
    },
    {
        "house": 10,
        "name_en": "10th House (Karma & Rajya Bhava)",
        "name_ta": "10-ஆம் பாவம் - ஜீவன பாவம் (தொழில், அதிகாரம் & கர்மம்)",
        "significance_en": "Career, worldly status, authority, fame, government favors, executive power, public reputation",
        "significance_ta": "தொழில் மேன்மை, பதவி, அரசு கௌரவம், சமுதாய அதிகாரம், கீர்த்தி, செயல்களில் வெற்றி, தலைமைத்துவம்",
        "category": "kendra"
    },
    {
        "house": 11,
        "name_en": "11th House (Labha Bhava)",
        "name_ta": "11-ஆம் பாவம் - லாப பாவம் (ஆசை நிறைவேறுதல் & மூத்த சகோதரம்)",
        "significance_en": "Gains from all sources, fulfillment of aspirations, elder siblings, friends network, prosperity",
        "significance_ta": "பல்வேறு வழிகளில் லாபம், விருப்பங்கள் நிறைவேறுதல், மூத்த சகோதரர், உயர்ந்தோர் நட்பு, பொருளாதார உயர்வு",
        "category": "upachaya"
    },
    {
        "house": 12,
        "name_en": "12th House (Vraya & Moksha Bhava)",
        "name_ta": "12-ஆம் பாவம் - விரய பாவம் (மோட்சம் & அயன சயன சுகம்)",
        "significance_en": "Expenses, losses, foreign settlement, spiritual liberation, bed pleasures, detachment, hospital/jail",
        "significance_ta": "விரயங்கள், நற்செலவுகள், வெளிநாட்டு வாழ்க்கை, ஆன்மீக மோட்சம், சயன சுகம், பற்றற்ற நிலை, தூக்கம்",
        "category": "dusthana"
    },
]

print("Base setup ready.")
