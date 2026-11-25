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

# Calibrated Safe-Area Margins:
# - Header: Logo and portrait graphics clear at y = 49.3 mm from top edge
# - Footer: Blue address banner and gold serrated ribbon clear at y = 16.5 mm from bottom edge
# - Left/Right borders clear at 8.0 mm
TOP_MARGIN_MM: float = 50.0
BOTTOM_MARGIN_MM: float = 26.0
LEFT_MARGIN_MM: float = 10.0
RIGHT_MARGIN_MM: float = 10.0

TOP_MARGIN: float = TOP_MARGIN_MM * mm        # 141.73 pt (distance from top edge)
BOTTOM_MARGIN: float = BOTTOM_MARGIN_MM * mm  # 73.70 pt (distance from bottom edge)
LEFT_MARGIN: float = LEFT_MARGIN_MM * mm      # 28.35 pt
RIGHT_MARGIN: float = RIGHT_MARGIN_MM * mm    # 28.35 pt

USABLE_WIDTH: float = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN    # 190.0 mm = 538.58 pt
USABLE_HEIGHT: float = PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN  # 221.0 mm = 626.46 pt

# Running Page Number Position:
# Placed at y = 19.5 mm (~55.3 pt), safely in the white margin:
# - 3.5 mm above the gold letterhead ribbon (which terminates at y = 16.0 mm)
# - 6.5 mm below the lowest story flowable (which terminates at y >= 26.0 mm)
PAGE_NUMBER_Y_MM: float = 19.5
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
