# scripts/generate_saravali_rules.py
"""Generate backend/app/services/prediction_rules/saravali_rules.py
Codifying Kalyana Varma's Saravali (Chapters 1 to 55).
"""

import sys
import os

OUTPUT_PATH = "backend/app/services/prediction_rules/saravali_rules.py"

def generate():
    lines = []
    lines.append('"""Kalyana Varma\'s Saravali Classical Rules Registry.')
    lines.append('')
    lines.append('Authoritative codification of classical astrological rules from the sacred')
    lines.append("treatise 'Saravali' authored by King Kalyana Varma of Vyaghrapada (Ch. 1-55).")
    lines.append('')
    lines.append('Key Chapters Codified:')
    lines.append('- Ch. 10, 11, 12: Arishta, Fateful Degrees of the Moon, and Arishta Bhanga')
    lines.append('- Ch. 13 & 14: Lunar & Solar Yogas (Sunapha, Anapha, Durudhura, Vesi, Vasi, Ubhayachari)')
    lines.append('- Ch. 15: Conjunction of Two Planets (21 Dvi-Graha Yogas)')
    lines.append('- Ch. 16: Conjunction of Three Planets (Tri-Graha Yogas, 3 Benefics, 3 Malefics)')
    lines.append('- Ch. 20: Combinations for Renunciation (Pravrajya Yogas)')
    lines.append('- Ch. 30: Effects of Planets in Bhavas (Sun to Saturn in 1st through 12th houses)')
    lines.append('- Ch. 31: Two Planets in Angles (Ascendant, 4th, 7th, 10th)')
    lines.append('- Ch. 32-34: 9th House Fortunes, 10th House Livelihood from Moon, 2nd House Wealth, 11th House Gains')
    lines.append('- Ch. 35: Raja Yogas (Pushkala, Chandradhi, Lagnadhi, Royal Combinations)')
    lines.append('- Ch. 39: Obstructions to Raja Yogas (Raja Yoga Bhanga)')
    lines.append('- Ch. 45: Planetary Dignities (2 to 5 planets Exalted, Own House, or Fall)')
    lines.append('- Ch. 46: Female Horoscopy (Stri Jataka, 7th house husband indicators, Trimsamsa)')
    lines.append('- Ch. 47: Aphorisms of Death (8th house occupant causes, sign modality)')
    lines.append('- Ch. 54: Ashtakavarga Bindu Predictions (0 to 8 bindus in occupied sign)')
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
    lines.append('SARAVALI_RULES: List[AstrologicalRuleDefinition] = []')
    lines.append('')

    # We will append groups of rules programmatically
    return lines

if __name__ == "__main__":
    print("Saravali rule generator initialized.")
