"""Centralized PDF Design Tokens and Layout Standards for Gokul's Astrological Insights (GAI).

Provides reusable design tokens across all PDF reports:
1. Page Dimensions and Calibrated Content-Safe Area Margins (A4).
2. Vedic Branding Color Palette.
3. Target Typography Scales and Calibrated Leading for Tamil & English.
4. Component Padding, Border Radii, and Spacing Tokens.
"""

from typing import Tuple, Dict
from reportlab.lib.units import mm
from reportlab.lib import colors

# =============================================================================
# 1. Page Dimensions & Safe-Area Margins (A4 Portrait)
# =============================================================================
PAGE_WIDTH: float = 210.0 * mm   # 595.2755 pt
PAGE_HEIGHT: float = 297.0 * mm  # 841.8898 pt
PAGE_SIZE: Tuple[float, float] = (PAGE_WIDTH, PAGE_HEIGHT)

# Calibrated Safe-Area Margins for Official GAI Letterpad:
# - Header: Blue banner, Gokul's portrait, Logo, and Tamil prayer ribbon ("ஓம் ஸ்ரீ கணேஷாய நமஹ | ஓம் குருப்யோ நமஹ")
#   terminate at y = 53.7 mm from top edge (with flourish at y=55mm confined within 10.7mm of left border).
#   TOP_MARGIN_MM = 55.0 mm guarantees generous clearance with 0% text overlay on branding.
# - Footer: Golden temple gopuram with trees on the right terminates at y = 46.5 mm from bottom edge,
#   golden wave ribbon extends up to y = 45.0 mm, and blue address banner sits at y = 0 to 27.3 mm.
#   BOTTOM_MARGIN_MM = 46.0 mm guarantees report flowables never overlap temple or address graphics.
# - Left/Right margins: 12.0 mm ensures ample breathing room inside borders.
TOP_MARGIN_MM: float = 55.0
BOTTOM_MARGIN_MM: float = 46.0
LEFT_MARGIN_MM: float = 12.0
RIGHT_MARGIN_MM: float = 12.0

TOP_MARGIN: float = TOP_MARGIN_MM * mm        # 155.91 pt (distance from top edge)
BOTTOM_MARGIN: float = BOTTOM_MARGIN_MM * mm  # 130.39 pt (distance from bottom edge)
LEFT_MARGIN: float = LEFT_MARGIN_MM * mm      # 34.02 pt
RIGHT_MARGIN: float = RIGHT_MARGIN_MM * mm    # 34.02 pt

USABLE_WIDTH: float = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN    # 186.0 mm = 527.24 pt
USABLE_HEIGHT: float = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN  # 196.0 mm = 555.59 pt

# Running Page Number Position:
# Placed at y = 42.0 mm (~119.0 pt), safely in the clean white horizontal central zone:
# - In the horizontal gap between the blue address banner on the left (which clears at x=65mm)
#   and the temple structure on the right (which starts at x=172mm).
# - 4.0 mm below the story flowables (which terminate at y >= 46.0 mm)
# - Centered or inset from right edge to stay 100% clear of graphics
PAGE_NUMBER_Y_MM: float = 42.0
PAGE_NUMBER_Y: float = PAGE_NUMBER_Y_MM * mm

# =============================================================================
# 2. Brand Color Palette (Vedic Gold, Royal Midnight & Crimson)
# =============================================================================
GOLD_PRIMARY = colors.HexColor("#8B6914")       # Rich Vedic Gold / Saffron
GOLD_ACCENT = colors.HexColor("#B8860B")        # Dark Goldenrod
GOLD_LIGHT_BG = colors.HexColor("#FFFDF5")      # Warm Ivory / Light Gold Tint
GOLD_BORDER = colors.HexColor("#D4AF37")        # Regal Gold Border

NAVY_PRIMARY = colors.HexColor("#0F172A")       # Deep Slate / Midnight
NAVY_SECONDARY = colors.HexColor("#1E293B")     # Charcoal Slate
TEXT_BODY = colors.HexColor("#334155")          # Dark Muted Slate for Body
TEXT_MUTED = colors.HexColor("#475569")         # Muted Slate for Subtitles & Hints
TEXT_DISCLAIMER = colors.HexColor("#64748B")    # Subtle Slate for Disclaimers

CRIMSON_ACCENT = colors.HexColor("#991B1B")     # Deep Vedic Red / Lagna
COLOR_LOVE = colors.HexColor("#BE123C")         # Rose / Passion (Love)
COLOR_ARRANGED = colors.HexColor("#1D4ED8")     # Royal Blue (Arranged / Tradition)
COLOR_BLESSING = colors.HexColor("#047857")     # Emerald Green (Auspicious Family Blessing)

BG_HEADER = colors.HexColor("#F8FAFC")          # Light Slate Tint
BG_ZEBRA = colors.HexColor("#F1F5F9")           # Table Zebra stripe
BORDER_SUBTLE = colors.HexColor("#CBD5E1")      # Subtle Slate Border
BORDER_INNER = colors.HexColor("#E2E8F0")       # Table Inner Grid Border

# Badges and Cards Backgrounds & Borders
CARD_BG_LOVE = colors.HexColor("#FFF1F2")
CARD_BORDER_LOVE = colors.HexColor("#FDA4AF")
CARD_BG_BLEND = colors.HexColor("#FAF5FF")
CARD_BORDER_BLEND = colors.HexColor("#D8B4FE")
CARD_BG_ARRANGED = colors.HexColor("#EFF6FF")
CARD_BORDER_ARRANGED = colors.HexColor("#93C5FD")
CARD_BG_NEUTRAL = colors.HexColor("#F8FAFC")
CARD_BORDER_NEUTRAL = colors.HexColor("#CBD5E1")
CARD_BG_GOLD = colors.HexColor("#FFFDF5")
CARD_BORDER_GOLD = GOLD_PRIMARY

# =============================================================================
# 3. Target Typography Scales (A4 Standardized)
# =============================================================================
# Target sizes calibrated for Tamil ascenders/descenders and English legibility
TYPO_REPORT_TITLE = {"fontSize": 17.0, "leading": 21.0}
TYPO_PRIMARY_PREDICTION = {"fontSize": 14.5, "leading": 18.0}
TYPO_SECTION_HEADING = {"fontSize": 11.0, "leading": 14.5}
TYPO_BODY_STANDARD = {"fontSize": 8.8, "leading": 12.2}
TYPO_BODY_COMPACT = {"fontSize": 8.2, "leading": 11.5}
TYPO_TABLE_HEADER = {"fontSize": 8.2, "leading": 10.8}
TYPO_TABLE_CONTENT = {"fontSize": 7.8, "leading": 10.5}
TYPO_FOOTER = {"fontSize": 8.0, "leading": 10.5}
TYPO_DISCLAIMER = {"fontSize": 7.3, "leading": 10.0}

# =============================================================================
# 4. Spacing & Padding Tokens
# =============================================================================
PAD_CARD_H: float = 8.0
PAD_CARD_V: float = 4.5
PAD_TABLE_H: float = 4.0
PAD_TABLE_V: float = 3.0
SPACER_SECTION: float = 5.0
SPACER_TITLE: float = 3.0
