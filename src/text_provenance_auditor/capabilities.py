from __future__ import annotations

from . import __version__


def get_capabilities() -> dict:
    return {
        "version": __version__,
        "providers": {
            "anthropic": {
                "text_marking": "confirmed_by_anthropic",
                "public_detector_contract": "forthcoming",
                "optional_authorised_verifier_env": "PROVENANCE_ANTHROPIC_VERIFIER_CMD",
            },
            "google": {
                "text_marking": "SynthID-Text documented and open-source reference available",
                "generic_gemini_text_verification": "requires relevant authorised/configured detector",
                "optional_authorised_verifier_env": "PROVENANCE_GOOGLE_SYNTHID_VERIFIER_CMD",
            },
        },
        "file_provenance": {
            "standard": "C2PA",
            "backends": ["c2pa-python", "c2patool"],
            "optional_dependency": "c2pa-python",
        },
        "forensics": [
            "zero_width_characters",
            "bidi_controls",
            "unicode_tag_characters",
            "variation_selectors",
            "invisible_operators",
            "unusual_spaces",
            "mixed_script_tokens",
            "unicode_normalisation_delta",
            "document_segmentation",
        ],
        "interfaces": ["python_api", "cli", "local_web_ui"],
        "heuristics": ["transparent_stylometry"],
        "watermark_evasion_or_removal": False,
    }
