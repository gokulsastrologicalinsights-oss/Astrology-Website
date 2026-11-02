# scripts/build_bphs_rules.py
"""Generate backend/app/services/prediction_rules/bphs_classical_rules.py
Authoritative Codification of Maharishi Parashara's Brihat Parashara Hora Shastra (BPHS).
"""

import sys
import os

OUTPUT_FILE = "backend/app/services/prediction_rules/bphs_classical_rules.py"

def generate():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    # We will assemble code in blocks
    header = '''"""Maharishi Parashara's Brihat Parashara Hora Shastra (BPHS) Classical Rules Registry.

Authoritative codification of foundational classical astrological rules from the
supreme Vedic treatise 'Brihat Parashara Hora Shastra' (BPHS).

Includes:
- Ch. 24: Effects of Bhava Lords across all 12 houses (144 complete combinations, Slokas 1-144)
- Ch. 34: Functional Nature & Yogakarakas for all 12 Ascendants (Slokas 19-44)
- Ch. 41: Special Dhana Yogas / Combinations for Wealth (Slokas 2-15)
- Ch. 42: Special Daridra Yogas / Combinations for Penury (Slokas 2-18)
- Ch. 80: Female Horoscopy / Stri Jataka & Visha Kanya Rules (Slokas 5-55)
- Ch. 83: Curses from Previous Birth / 8 Great Shapas & Remedies (Slokas 9-105)
- Ch. 85-95: Inauspicious Births & Gandanta Rules (Amavasya, Chaturdashi, Gandanta, Trik Prasava)
- Ch. 29-30: Arudha Padas & Upapada Lagna Predictions (Slokas 8-43)
"""

from typing import List
from app.services.prediction_rules.ast_models import (
    AstrologicalRuleDefinition,
    AstrologySystem,
    ChartScope,
    SeverityLevel,
)

BPHS_CLASSICAL_RULES: List[AstrologicalRuleDefinition] = []
'''

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(header)

    print("Header written to", OUTPUT_FILE)

if __name__ == "__main__":
    generate()
