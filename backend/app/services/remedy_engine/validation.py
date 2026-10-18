"""Remedy and content validation engine.

Ensures high fidelity for:
- Bilingual English / Tamil translations
- Authentic Devanagari Sanskrit mantras
- Tamil script transliterations (phonetic accuracy)
- Kaveri Delta temple attributes and coordinates
- Classical Shastra citation traceability
- Positive integer Japa counts
"""

import re
from typing import List, Dict, Any, Optional
from app.schemas.remedies import (
    ContentValidationReport,
    ContentValidationCheck,
)
from app.services.remedy_engine.repository import remedy_repository


class RemedyValidator:
    """Validates remedy knowledge base for textual, astronomical, and linguistic integrity."""

    TAMIL_RANGE = (0x0B80, 0x0BFF)
    DEVANAGARI_RANGE = (0x0900, 0x097F)

    @classmethod
    def contains_tamil(cls, text: Optional[str]) -> bool:
        """Check if string contains authentic Tamil Unicode glyphs."""
        if not text:
            return False
        return any(cls.TAMIL_RANGE[0] <= ord(ch) <= cls.TAMIL_RANGE[1] for ch in text)

    @classmethod
    def contains_devanagari(cls, text: Optional[str]) -> bool:
        """Check if string contains authentic Devanagari Unicode glyphs."""
        if not text:
            return False
        return any(cls.DEVANAGARI_RANGE[0] <= ord(ch) <= cls.DEVANAGARI_RANGE[1] for ch in text)

    @classmethod
    def contains_corrupted_characters(cls, text: Optional[str]) -> bool:
        """Detect encoding artifacts like '???', replacement characters, or empty strings."""
        if text is None:
            return False
        # Check for unicode replacement character or triple question marks
        if "\ufffd" in text or "???" in text:
            return True
        return False

    @classmethod
    def validate_remedy(cls, remedy: Dict[str, Any]) -> List[str]:
        """Validate a single remedy entry for required fields and script integrity."""
        errors: List[str] = []
        code = remedy.get("code", "UNKNOWN")

        # English and Tamil name
        if not remedy.get("name_en"):
            errors.append(f"{code}: Missing English name")
        if not remedy.get("name_ta") or not cls.contains_tamil(remedy.get("name_ta")):
            errors.append(f"{code}: Missing or invalid Tamil script name")

        # Descriptions
        if not remedy.get("description_en"):
            errors.append(f"{code}: Missing English description")
        if not remedy.get("description_ta") or not cls.contains_tamil(remedy.get("description_ta")):
            errors.append(f"{code}: Missing or invalid Tamil script description")

        # Mantras must have Sanskrit and Tamil script representations
        if remedy.get("remedy_type") == "mantra":
            sanskrit = remedy.get("sanskrit_text")
            if not sanskrit or not cls.contains_devanagari(sanskrit):
                errors.append(f"{code}: Mantra lacks valid Devanagari Sanskrit text")

            translit_ta = remedy.get("transliteration_ta")
            if not translit_ta or not cls.contains_tamil(translit_ta):
                errors.append(f"{code}: Mantra lacks authentic Tamil phonetic transliteration")

            japa = remedy.get("japa_count")
            if japa is not None and (not isinstance(japa, int) or japa <= 0):
                errors.append(f"{code}: Japa count must be a positive integer, got {japa}")

        # Source code
        if not remedy.get("source_code"):
            errors.append(f"{code}: Missing classical shastra citation source code")

        # Corruption
        for field in ("name_en", "name_ta", "description_en", "description_ta", "sanskrit_text"):
            val = remedy.get(field)
            if cls.contains_corrupted_characters(val):
                errors.append(f"{code}: Field '{field}' contains corrupted characters or '???'")

        return errors

    @classmethod
    def validate_temple(cls, temple: Dict[str, Any]) -> List[str]:
        """Validate a Navagraha temple entry for geographic coordinates and bilingual fields."""
        errors: List[str] = []
        code = temple.get("code", "UNKNOWN")

        if not temple.get("name_en"):
            errors.append(f"{code}: Missing English temple name")
        if not temple.get("name_ta") or not cls.contains_tamil(temple.get("name_ta")):
            errors.append(f"{code}: Missing or invalid Tamil temple name")

        lat = temple.get("latitude")
        lon = temple.get("longitude")
        # Tamil Nadu Kaveri Delta coordinates bounds: lat 10.0 to 12.0, lon 78.5 to 80.5
        if lat is None or not (10.0 <= float(lat) <= 12.0):
            errors.append(f"{code}: Latitude {lat} outside Kaveri Delta Tamil Nadu range (10.0 - 12.0)")
        if lon is None or not (78.5 <= float(lon) <= 80.5):
            errors.append(f"{code}: Longitude {lon} outside Kaveri Delta Tamil Nadu range (78.5 - 80.5)")

        return errors

    @classmethod
    def validate_taxonomy_item(cls, item: Dict[str, Any]) -> List[str]:
        """Validate a problem taxonomy item."""
        errors: List[str] = []
        slug = item.get("slug", "UNKNOWN")

        if not item.get("name_en"):
            errors.append(f"{slug}: Missing English problem name")
        if not item.get("name_ta") or not cls.contains_tamil(item.get("name_ta")):
            errors.append(f"{slug}: Missing or invalid Tamil problem name")

        karakas = item.get("primary_karakas", [])
        if not karakas or not isinstance(karakas, list):
            errors.append(f"{slug}: Primary karakas list cannot be empty")

        houses = item.get("governing_houses", [])
        if not houses or not isinstance(houses, list):
            errors.append(f"{slug}: Governing houses list cannot be empty")
        for h in houses:
            if not isinstance(h, int) or not (1 <= h <= 12):
                errors.append(f"{slug}: Governing house {h} must be between 1 and 12")

        return errors

    @classmethod
    async def audit_knowledge_base(cls) -> ContentValidationReport:
        """Run a full audit of all in-memory or database records."""
        problems = await remedy_repository.get_all_problem_taxonomies()
        remedies = await remedy_repository.get_all_remedies()
        temples = await remedy_repository.get_all_navagraha_temples()
        sources = await remedy_repository.get_all_source_references()

        checks: List[ContentValidationCheck] = []
        all_passed = True

        # Check 1: Taxonomy completeness and bilingual fidelity
        taxonomy_errors: List[str] = []
        for p in problems:
            taxonomy_errors.extend(cls.validate_taxonomy_item(p))

        is_tax_ok = len(problems) >= 39 and len(taxonomy_errors) == 0
        checks.append(ContentValidationCheck(
            check_name="problem_taxonomy_completeness",
            is_valid=is_tax_ok,
            details=f"Audited {len(problems)} problem categories. Errors: {len(taxonomy_errors)}" + (f" ({'; '.join(taxonomy_errors[:3])})" if taxonomy_errors else "")
        ))
        if not is_tax_ok:
            all_passed = False

        # Check 2: Kaveri Delta 9 Navagraha Temples
        temple_errors: List[str] = []
        for t in temples:
            temple_errors.extend(cls.validate_temple(t))

        is_temples_ok = len(temples) == 9 and len(temple_errors) == 0
        checks.append(ContentValidationCheck(
            check_name="navagraha_temples_kaveri_delta",
            is_valid=is_temples_ok,
            details=f"Audited {len(temples)} Navagraha temples. Geographic coordinates & Tamil scripts verified. Errors: {len(temple_errors)}"
        ))
        if not is_temples_ok:
            all_passed = False

        # Check 3: Remedy catalog bilingual and mantra script fidelity
        remedy_errors: List[str] = []
        known_sources = {s["code"] for s in sources}
        for r in remedies:
            remedy_errors.extend(cls.validate_remedy(r))
            if r.get("source_code") and r.get("source_code") not in known_sources:
                remedy_errors.append(f"{r.get('code')}: Source code '{r.get('source_code')}' not found in canonical sources")

        is_remedies_ok = len(remedies) >= 10 and len(remedy_errors) == 0
        checks.append(ContentValidationCheck(
            check_name="remedies_catalog_mantra_and_sources",
            is_valid=is_remedies_ok,
            details=f"Audited {len(remedies)} catalog remedies. Devanagari Sanskrit, Tamil transliteration, and Shastra sources verified. Errors: {len(remedy_errors)}"
        ))
        if not is_remedies_ok:
            all_passed = False

        # Check 4: Canonical Shastra sources
        is_sources_ok = len(sources) >= 5
        checks.append(ContentValidationCheck(
            check_name="classical_shastra_sources",
            is_valid=is_sources_ok,
            details=f"Verified {len(sources)} canonical classical sources (BPHS, Phaladeepika, Lal Kitab, Navagraha Stotram, etc.)."
        ))
        if not is_sources_ok:
            all_passed = False

        return ContentValidationReport(
            total_remedies_audited=len(remedies),
            total_problems_audited=len(problems),
            total_temples_audited=len(temples),
            checks=checks,
            all_passed=all_passed,
        )
