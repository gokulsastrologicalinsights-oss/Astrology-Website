# scripts/patch_categories.py
from pathlib import Path

path = Path("backend/app/services/prediction_rules/categories.py")
content = path.read_text(encoding="utf-8")

bphs_block = '''    CategoryGroup(
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
'''

if 'bphs_classics' not in content:
    # replace the closing bracket of PREDICTION_CATEGORY_GROUPS
    idx = content.rfind('PREDICTION_CATEGORY_GROUPS: List[CategoryGroup] = [')
    end_bracket_idx = content.find('\n]\n', idx)
    if end_bracket_idx != -1:
        new_content = content[:end_bracket_idx] + '\n' + bphs_block + content[end_bracket_idx:]
        path.write_text(new_content, encoding="utf-8")
        print("Successfully patched categories.py!")
    else:
        print("Could not find closing bracket")
else:
    print("Already patched")
