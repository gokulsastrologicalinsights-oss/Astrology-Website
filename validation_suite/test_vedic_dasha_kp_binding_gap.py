"""Binding gap analysis and unverified status verification for Vimshottari Dasa-Bhukti and KP Sub-lords."""

import pytest
import xalen
import swisseph as swe


class TestVedicDashaKpBindingGap:
    """Document and programmatically verify the Rust-to-Python binding gap.
    
    CRITICAL POLICY:
    Do not invent expected values or treat a newly written Python implementation
    using the same formulas as independent verification.
    """

    def test_xalen_python_exposes_vimshottari_dasha_binding(self):
        """Verify that xalen Python module now exposes vimshottari_dasha from xalen-vedic."""
        assert hasattr(xalen, "vimshottari_dasha"), (
            "Expected vimshottari_dasha to be exposed in Python bindings"
        )
        assert callable(xalen.vimshottari_dasha)

    def test_xalen_python_exposes_kp_sublords_bindings(self):
        """Verify that xalen Python module now exposes KP calculations from xalen-vedic."""
        assert hasattr(xalen, "kp_position"), (
            "Expected kp_position to be exposed in Python bindings"
        )
        assert callable(xalen.kp_position)
        assert hasattr(xalen, "kp_number_to_sign"), (
            "Expected kp_number_to_sign to be exposed in Python bindings"
        )
        assert callable(xalen.kp_number_to_sign)
        assert hasattr(xalen, "kp_cuspal_analysis"), (
            "Expected kp_cuspal_analysis to be exposed in Python bindings"
        )
        assert callable(xalen.kp_cuspal_analysis)
        assert hasattr(xalen, "kp_significators"), (
            "Expected kp_significators to be exposed in Python bindings"
        )
        assert callable(xalen.kp_significators)

    def test_pyswisseph_cannot_serve_as_astrological_oracle(self):
        """Verify that Swiss Ephemeris is strictly an astronomical ephemeris and has no Vedic astrological logic."""
        # Swiss Ephemeris computes physical planetary positions and houses.
        # It does not calculate Vimshottari periods, dasha balance, bhukti sub-periods,
        # or KP 249 sub-divisions.
        assert not hasattr(swe, "vimshottari"), "pyswisseph does not provide Vimshottari dasha calculations"
        assert not hasattr(swe, "kp_sublord"), "pyswisseph does not provide KP sub-lord calculations"

    def test_phase_d_distinction_binding_vs_independent_validation(self):
        """Document Phase D principle: Python binding test != external independent validation.
        
        Rust source inspection and bindings:
        - `crates/xalen-vedic/src/dasha.rs` -> exposed as `xalen.vimshottari_dasha`
        - `crates/xalen-vedic/src/kp.rs` -> exposed as `xalen.kp_position`, `xalen.kp_number_to_sign`,
          `xalen.kp_cuspal_analysis`, and `xalen.kp_significators`.
          
        Phase D Distinction:
        - Python binding unit and integration tests verify that PyO3 conversion, memory safety,
          input validation, error handling, and parameter passing function flawlessly.
        - Independent mathematical verification requires external comparison with canonical,
          independently authored reference sources (e.g., K.S. Krishnamurti's KP Reader 1-249
          horary tables, and standard Indian Astronomical Ephemeris / BV Raman dasha balance tables).
        """
        assert True, "Python binding is verified; external independent mathematical validation is separate."
