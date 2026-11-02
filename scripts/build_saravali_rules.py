# scripts/build_saravali_rules.py
"""Generate backend/app/services/prediction_rules/saravali_rules.py
Authoritative Codification of Kalyana Varma's Saravali (Ch. 1-55).
"""

import sys
import os

OUTPUT_FILE = "backend/app/services/prediction_rules/saravali_rules.py"

def generate():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write('''"""Kalyana Varma's Saravali Classical Rules Registry.

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

SARAVALI_RULES: List[AstrologicalRuleDefinition] = []

''')
    print("Saravali rules base header created successfully.")

if __name__ == "__main__":
    generate()
