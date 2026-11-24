import re
from typing import Any

DISCLOSURE_REPLACEMENTS = [
    # Engine & Library terms
    (re.compile(r'\bxalen\b', re.IGNORECASE), "GAI Astronomical Core"),
    (re.compile(r'\bswiss\s+ephemeris\b', re.IGNORECASE), "High-Precision Ephemeris"),
    (re.compile(r'\bswisseph\b', re.IGNORECASE), "High-Precision Ephemeris"),
    (re.compile(r'\bpyswisseph\b', re.IGNORECASE), "High-Precision Ephemeris"),
    (re.compile(r'\bkp\s+engine\b', re.IGNORECASE), "KP Astrological System"),

    # Author terms
    (re.compile(r'Siddhayogi\s+Sivadasan\s+Ravi\s*\([^\)]*\)', re.IGNORECASE), "GAI Astrology Research Council"),
    (re.compile(r'\bSivadasan\s+Ravi\b', re.IGNORECASE), "Classical Astrology"),
    (re.compile(r'\(Sannu\s+Ahmed\s+Tradition\)', re.IGNORECASE), "(Classical Vedic Tradition)"),
    (re.compile(r'\bSannu\s+Ahmed\b', re.IGNORECASE), "Classical Vedic"),
    (re.compile(r'\bMarc\s+Boney\b', re.IGNORECASE), "Classical Scholar"),
    (re.compile(r'\bMark\s+Boney\b', re.IGNORECASE), "Classical Scholar"),
    (re.compile(r'Dr\.?\s*S\.?\s*Krishna\s*Kumar', re.IGNORECASE), "Classical Medical Astrologer"),
    (re.compile(r'Heinrich\s+D[aä]ath', re.IGNORECASE), "Classical Astrologer"),
    (re.compile(r'\bPicatrix\b', re.IGNORECASE), "Classical Astrological Hermeticum"),

    # Code Identifiers
    (re.compile(r'REM_BPHS_', re.IGNORECASE), "REM_VEDIC_"),

    # Book / Treatise Titles & Chapter Citations
    (re.compile(r'Thirumana\s+Yoga\s+Porutha\s+Thiravukol', re.IGNORECASE), "Classical Marriage Compatibility Analysis"),
    (re.compile(r'திருமண\s+யோக\s+திருமணப்\s+பொருத்த\s+திறவுகோல்'), "பாரம்பரிய திருமணப் பொருத்த ஆய்வு"),
    (re.compile(r'Brihat\s+Parashara\s+Hora\s+Shastra\s*\(BPHS\)', re.IGNORECASE), "Classical Vedic Shastra"),
    (re.compile(r'Brihat\s+Parashara\s+Hora\s+Shastra', re.IGNORECASE), "Classical Vedic Shastra"),
    (re.compile(r'Brihat\s+Parasara\s+Hora\s+Shastra\s*\(BPHS\)', re.IGNORECASE), "Classical Vedic Shastra"),
    (re.compile(r'Brihat\s+Parasara\s+Hora\s+Shastra', re.IGNORECASE), "Classical Vedic Shastra"),
    (re.compile(r'BPHS\s+Ch\.\s*\d+[^;,\)"]*', re.IGNORECASE), "Classical Vedic Shastra"),
    (re.compile(r'\bBPHS\b', re.IGNORECASE), "Classical Vedic"),
    (re.compile(r'Phaladeepika\s+Ch\.\s*\d+[^;,\)"]*', re.IGNORECASE), "Classical Jyotish Shastra"),
    (re.compile(r'\bPhaladeepika\b', re.IGNORECASE), "Classical Jyotish"),
    (re.compile(r'Muhurta\s+Chintamani\s+Ch\.\s*\d+[^;,\)"]*', re.IGNORECASE), "Classical Vivaha Shastra"),
    (re.compile(r'\bMuhurta\s+Chintamani\b', re.IGNORECASE), "Classical Vivaha Shastra"),
    (re.compile(r'Kalaprakasika\s+Ch\.\s*\d+[^;,\)"]*', re.IGNORECASE), "Classical Porutham Shastra"),
    (re.compile(r'\bKalaprakasika\b', re.IGNORECASE), "Classical Porutham Shastra"),
    (re.compile(r'\bSaravali\s+Ch\.\s*\d+[^;,\)"]*', re.IGNORECASE), "Classical Shastra"),
    (re.compile(r'\bSaravali\b', re.IGNORECASE), "Classical Jyotish"),
]

def sanitize_value(val: Any) -> Any:
    if isinstance(val, str):
        for pattern, repl in DISCLOSURE_REPLACEMENTS:
            val = pattern.sub(repl, val)
        return val
    elif isinstance(val, dict):
        return {k: sanitize_value(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [sanitize_value(v) for v in val]
    return val
