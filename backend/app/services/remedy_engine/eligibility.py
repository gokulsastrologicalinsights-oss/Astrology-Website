"""Classical Vedic Astrology Remedy Eligibility Engine.

Implements Shastra safeguards according to Brihat Parashara Hora Shastra (BPHS):
1. Functional Nature Assessment: Determines whether a planet is a Yogakaraka,
   Functional Benefic, or Functional Malefic for each of the 12 Lagnas (Ascendants).
2. Yogakaraka Protection Rule: Strict prohibition on Daan (charity/donation) for
   Yogakaraka planets (e.g. Saturn for Taurus/Libra, Mars for Cancer/Leo, Venus for Capricorn/Aquarius).
   Daan pacifies and dissipates the planet's energy, which diminishes its capacity
   to confer Raja Yoga, status, and prosperity.
3. Safe Alternative Recommendations: Redirects users toward Sattvic strengthening
   remedies (Gayatri mantra, stotras, temple worship) instead of pacifying donations.
"""

from typing import Dict, Any, Optional, Set
from app.schemas.remedies import RemedyEligibilityResponse


# Mapping of 12 Ascendants to their Yogakaraka, Functional Benefics, and Functional Malefics
# Standard classical Parashari principles (BPHS Ch. 34)
LAGNA_PLANETARY_NATURE: Dict[str, Dict[str, Any]] = {
    "aries": {
        "yogakaraka": None,
        "benefics": {"sun", "jupiter", "mars"},
        "malefics": {"mercury", "saturn", "venus"},
        "neutral": {"moon"},
    },
    "taurus": {
        "yogakaraka": "saturn",  # 9th (Trikona) & 10th (Kendra) lord
        "benefics": {"saturn", "mercury", "sun"},
        "malefics": {"jupiter", "mars", "venus"},
        "neutral": {"moon"},
    },
    "gemini": {
        "yogakaraka": None,
        "benefics": {"venus", "mercury"},
        "malefics": {"mars", "jupiter", "sun"},
        "neutral": {"moon", "saturn"},
    },
    "cancer": {
        "yogakaraka": "mars",  # 5th (Trikona) & 10th (Kendra) lord
        "benefics": {"mars", "moon", "jupiter"},
        "malefics": {"mercury", "venus", "saturn"},
        "neutral": {"sun"},
    },
    "leo": {
        "yogakaraka": "mars",  # 4th (Kendra) & 9th (Trikona) lord
        "benefics": {"mars", "sun", "jupiter"},
        "malefics": {"saturn", "venus", "mercury"},
        "neutral": {"moon"},
    },
    "virgo": {
        "yogakaraka": None,
        "benefics": {"venus", "mercury"},
        "malefics": {"mars", "jupiter", "moon"},
        "neutral": {"sun", "saturn"},
    },
    "libra": {
        "yogakaraka": "saturn",  # 4th (Kendra) & 5th (Trikona) lord
        "benefics": {"saturn", "mercury", "venus"},
        "malefics": {"jupiter", "sun", "mars"},
        "neutral": {"moon"},
    },
    "scorpio": {
        "yogakaraka": None,  # Sun (10th) & Moon (9th) form yoga, but no single planet
        "benefics": {"sun", "moon", "jupiter", "mars"},
        "malefics": {"mercury", "venus"},
        "neutral": {"saturn"},
    },
    "sagittarius": {
        "yogakaraka": None,
        "benefics": {"sun", "mars", "jupiter"},
        "malefics": {"venus", "saturn"},
        "neutral": {"moon", "mercury"},
    },
    "capricorn": {
        "yogakaraka": "venus",  # 5th (Trikona) & 10th (Kendra) lord
        "benefics": {"venus", "mercury", "saturn"},
        "malefics": {"mars", "jupiter", "moon"},
        "neutral": {"sun"},
    },
    "aquarius": {
        "yogakaraka": "venus",  # 4th (Kendra) & 9th (Trikona) lord
        "benefics": {"venus", "saturn"},
        "malefics": {"jupiter", "moon", "mars"},
        "neutral": {"sun", "mercury"},
    },
    "pisces": {
        "yogakaraka": None,
        "benefics": {"moon", "mars", "jupiter"},
        "malefics": {"venus", "sun", "saturn"},
        "neutral": {"mercury"},
    },
}

# English and Sanskrit canonical names for planets
PLANET_CANONICAL_NAMES = {
    "sun": "Surya",
    "moon": "Chandra",
    "mars": "Mangala (Angaraka)",
    "mercury": "Budha",
    "jupiter": "Guru (Brihaspati)",
    "venus": "Shukra",
    "saturn": "Shani",
    "rahu": "Rahu",
    "ketu": "Ketu",
}


class RemedyEligibilityEngine:
    """Evaluates remedy eligibility ensuring classical Parashari safeguards are not breached."""

    @classmethod
    def normalize_key(cls, value: str) -> str:
        """Standardize ascendant sign or planet input."""
        return value.strip().lower()

    @classmethod
    def evaluate_eligibility(
        cls,
        ascendant_sign: str,
        graha: str,
        remedy_type: str,
    ) -> RemedyEligibilityResponse:
        """
        Evaluate if a proposed remedy type (mantra, worship, charity, fasting, temple)
        is astrologically sound for a specific Ascendant and Planet.
        """
        lagna = cls.normalize_key(ascendant_sign)
        planet = cls.normalize_key(graha)
        rem_type = cls.normalize_key(remedy_type)

        chart_nature = LAGNA_PLANETARY_NATURE.get(lagna)
        if not chart_nature:
            # Fallback if unknown ascendant
            return RemedyEligibilityResponse(
                graha=graha,
                ascendant_sign=ascendant_sign,
                remedy_type=remedy_type,
                is_eligible=True,
                is_yogakaraka=False,
                is_functional_benefic=False,
                is_functional_malefic=False,
                restriction_reason=f"Unknown ascendant sign '{ascendant_sign}'. Standard safety guidelines apply.",
                safe_alternative_recommendation="Recitation of universal mantras (e.g., Gayatri or Maha Mrityunjaya) or temple visits.",
            )

        is_yogakaraka = (chart_nature["yogakaraka"] == planet)
        is_benefic = planet in chart_nature["benefics"]
        is_malefic = planet in chart_nature["malefics"]

        # Universal / Shadow planets (Rahu / Ketu)
        if planet in ("rahu", "ketu"):
            # Rahu/Ketu are natural malefics, charity and pacification are always safe
            return RemedyEligibilityResponse(
                graha=graha,
                ascendant_sign=ascendant_sign,
                remedy_type=remedy_type,
                is_eligible=True,
                is_yogakaraka=False,
                is_functional_benefic=False,
                is_functional_malefic=True,
                restriction_reason=None,
                safe_alternative_recommendation=None,
            )

        # SAFEGUARD 1: Strict Yogakaraka Protection Rule against Daan (Charity)
        if is_yogakaraka and rem_type in ("charity", "daan", "donation"):
            graha_display = PLANET_CANONICAL_NAMES.get(planet, planet.capitalize())
            return RemedyEligibilityResponse(
                graha=graha,
                ascendant_sign=ascendant_sign,
                remedy_type=remedy_type,
                is_eligible=False,
                is_yogakaraka=True,
                is_functional_benefic=True,
                is_functional_malefic=False,
                restriction_reason=(
                    f"{graha_display} is the supreme Yogakaraka (Kendra-Trikona lord) for {ascendant_sign} Lagna. "
                    "Classical Jyotish (BPHS Ch. 34) strictly warns against Daan (charity) for Yogakaraka planets, "
                    "as donating planetary items dissipates and pacifies the planet's auspicious raja yoga power."
                ),
                safe_alternative_recommendation=(
                    f"Instead of charity, strengthen {graha_display} through Sattvic worship: recite its Vedic/Puranic "
                    "Gayatri or Moola Mantra (108 times), perform Archana at its consecrated Navagraha Sthalam, "
                    "or worship its presiding deity (Shiva / Vishnu / Devi / Murugan)."
                ),
            )

        # SAFEGUARD 2: Functional Benefic Protection against Daan
        if is_benefic and rem_type in ("charity", "daan", "donation") and not is_yogakaraka:
            graha_display = PLANET_CANONICAL_NAMES.get(planet, planet.capitalize())
            return RemedyEligibilityResponse(
                graha=graha,
                ascendant_sign=ascendant_sign,
                remedy_type=remedy_type,
                is_eligible=False,
                is_yogakaraka=False,
                is_functional_benefic=True,
                is_functional_malefic=False,
                restriction_reason=(
                    f"{graha_display} is a Functional Benefic for {ascendant_sign} Lagna. "
                    "Daan (donation) is primarily prescribed for pacifying afflicted functional malefics, "
                    "not for auspicious lords whose strength supports your Lagna, intelligence, or fortunes."
                ),
                safe_alternative_recommendation=(
                    f"Honor {graha_display} via Japa (mantra chanting) or temple darshan rather than discarding its items."
                ),
            )

        # SAFEGUARD 3: Mantras, Temples, and Worship are universally eligible and safe
        if rem_type in ("mantra", "worship", "temple", "prayer"):
            return RemedyEligibilityResponse(
                graha=graha,
                ascendant_sign=ascendant_sign,
                remedy_type=remedy_type,
                is_eligible=True,
                is_yogakaraka=is_yogakaraka,
                is_functional_benefic=is_benefic,
                is_functional_malefic=is_malefic,
                restriction_reason=None,
                safe_alternative_recommendation=None,
            )

        # Daan for Functional Malefics is highly eligible
        if rem_type in ("charity", "daan", "donation") and is_malefic:
            return RemedyEligibilityResponse(
                graha=graha,
                ascendant_sign=ascendant_sign,
                remedy_type=remedy_type,
                is_eligible=True,
                is_yogakaraka=False,
                is_functional_benefic=False,
                is_functional_malefic=True,
                restriction_reason=None,
                safe_alternative_recommendation=None,
            )

        # SAFEGUARD 4: Gemstone (Ratna) Safeguard & Mandatory Manual Astrologer Review Gate
        if rem_type in ("gemstone", "ratna", "gem"):
            graha_display = PLANET_CANONICAL_NAMES.get(planet, planet.capitalize())
            if is_malefic or planet in ("rahu", "ketu"):
                return RemedyEligibilityResponse(
                    graha=graha,
                    ascendant_sign=ascendant_sign,
                    remedy_type=remedy_type,
                    is_eligible=False,
                    is_yogakaraka=False,
                    is_functional_benefic=False,
                    is_functional_malefic=True,
                    restriction_reason=(
                        f"{graha_display} is a Functional Malefic for {ascendant_sign} Lagna. "
                        "Classical Jyotish (Jataka Parijata Ch. 2, Mani Mala) strictly forbids wearing gemstones "
                        "for functional malefics. Gemstones amplify incoming planetary radiation; wearing a stone for a "
                        "malefic lord intensifies diseases, accidents, debts, and mental strife."
                    ),
                    safe_alternative_recommendation=(
                        f"Do not wear {graha_display}'s gemstone. Instead, pacify {graha_display} via Sattvic "
                        "mantra recitation, Archana at its Kaveri Delta temple, or prescribed charity."
                    ),
                    requires_manual_astrologer_review=True,
                    is_review_gated=True,
                )
            else:
                return RemedyEligibilityResponse(
                    graha=graha,
                    ascendant_sign=ascendant_sign,
                    remedy_type=remedy_type,
                    is_eligible=True,
                    is_yogakaraka=is_yogakaraka,
                    is_functional_benefic=is_benefic,
                    is_functional_malefic=False,
                    restriction_reason=(
                        f"{graha_display} is auspicious for {ascendant_sign} Lagna, but gemstone prescription "
                        "strictly requires manual certified astrologer review. Factors such as degree of dignity, "
                        "combustion, Maraka/Badhaka lordship, and transit sensitivities must be verified in person."
                    ),
                    safe_alternative_recommendation=(
                        "Prioritize recitation of Moola Mantras and Archana at consecrated temples, which are "
                        "universally safe and sattvic without the physical and psychological risks of untreated gemstones."
                    ),
                    requires_manual_astrologer_review=True,
                    is_review_gated=True,
                )

        # Default fallback
        return RemedyEligibilityResponse(
            graha=graha,
            ascendant_sign=ascendant_sign,
            remedy_type=remedy_type,
            is_eligible=True,
            is_yogakaraka=is_yogakaraka,
            is_functional_benefic=is_benefic,
            is_functional_malefic=is_malefic,
            restriction_reason=None,
            safe_alternative_recommendation=None,
        )
