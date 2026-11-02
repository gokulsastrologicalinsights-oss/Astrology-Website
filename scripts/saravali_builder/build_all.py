# scripts/saravali_builder/build_all.py
"""Master Builder Script for Kalyana Varma's Saravali Rules.
Combines all sections and outputs directly to backend/app/services/prediction_rules/saravali_rules.py.
"""

import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from saravali_builder.bhava_phala import get_bhava_phala_rules
from saravali_builder.conjunctions import get_conjunction_rules
from saravali_builder.angles_and_worldly import get_angles_and_worldly_rules
from saravali_builder.raja_and_bhanga import get_raja_and_bhanga_rules
from saravali_builder.dignities_stri_longevity_ashtakavarga import get_dignities_stri_longevity_ashtakavarga_rules

OUTPUT_FILE = os.path.abspath("backend/app/services/prediction_rules/saravali_rules.py")

def main():
    print("Collecting Saravali rules from all sub-builders...")
    bhava_rules = get_bhava_phala_rules()
    conj_rules = get_conjunction_rules()
    angle_rules = get_angles_and_worldly_rules()
    raja_rules = get_raja_and_bhanga_rules()
    dignity_rules = get_dignities_stri_longevity_ashtakavarga_rules()

    all_rules = bhava_rules + conj_rules + angle_rules + raja_rules + dignity_rules
    print(f"Total rules gathered: {len(all_rules)}")
    print(f"  - Bhava Phala (Ch. 30): {len(bhava_rules)}")
    print(f"  - Conjunctions (Ch. 15, 16): {len(conj_rules)}")
    print(f"  - Angles & Worldly Affairs (Ch. 31-34): {len(angle_rules)}")
    print(f"  - Raja Yogas & Bhanga (Ch. 35, 39): {len(raja_rules)}")
    print(f"  - Dignities, Stri, Longevity, Ashtakavarga (Ch. 45, 46, 47, 54): {len(dignity_rules)}")

    header = '''"""Kalyana Varma's Saravali Classical Rules Registry.

Authoritative codification of classical astrological rules from the sacred
treatise 'Saravali' authored by King Kalyana Varma of Vyaghrapada (Ch. 1 to 55).

Includes:
- Bhava Phala of 7 classical grahas across all 12 houses (Ch. 30, v. 2-86)
- Conjunctions of Two Planets (Ch. 15, v. 2-22)
- Conjunctions of Three Planets (Ch. 16, v. 1-38)
- Two Planets in Angles / Kendras (Ch. 31, v. 1-86)
- 9th House Fortunes & Foreign Travel (Ch. 32, v. 1-29)
- 10th House Livelihood from Moon and Signs (Ch. 33, v. 1-65)
- Worldly Affairs, 2nd House Wealth & 11th House Gains (Ch. 34, v. 1-67)
- Raja Yogas, Pushkala Yoga & Chandradhi Yoga (Ch. 35, v. 1-145)
- Obstructions to Raja Yogas / Raja Yoga Bhanga (Ch. 39, v. 1-23)
- Multi-Planet Dignities (Ch. 45, v. 23-45)
- Female Horoscopy / Stri Jataka (Ch. 46, v. 1-31)
- Aphorisms of Death & 8th House Indications (Ch. 47, v. 1-22 & Ch. 10, v. 111-114)
- Ashtakavarga Bindu Predictions (Ch. 54, v. 1-9)
"""

from typing import List
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
    SeverityLevel,
)

SARAVALI_RULES: List[AstrologicalRuleDefinition] = [
'''

    footer = ''']
'''

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header)
        for r in all_rules:
            f.write(r + "\n")
        f.write(footer)

    print(f"Successfully generated {OUTPUT_FILE} with {len(all_rules)} rules.")

if __name__ == "__main__":
    main()
