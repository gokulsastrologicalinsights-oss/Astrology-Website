# scripts/update_categories.py
import re

new_group_text = """    CategoryGroup(
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
"""

path = "backend/app/services/prediction_rules/categories.py"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

target = "        ],\n    ),\n]\n"
if target in text:
    updated = text.replace(target, "        ],\n    ),\n" + new_group_text + "]\n", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    print("Categories updated successfully.")
else:
    print("Target string not found in categories.py.")
