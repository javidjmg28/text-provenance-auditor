from __future__ import annotations

from .external import ExternalCommandDetector, ExternalVerifierConfig


class GoogleSynthIDDetector(ExternalCommandDetector):
    """Google SynthID-Text verification boundary.

    Google publishes a SynthID-Text reference implementation for model owners.
    Verification of arbitrary Gemini text still requires the relevant watermark
    configuration / authorised mechanism, so this adapter remains opt-in.
    """

    def __init__(self) -> None:
        super().__init__(
            ExternalVerifierConfig(
                provider="google",
                env_var="PROVENANCE_GOOGLE_SYNTHID_VERIFIER_CMD",
                method="authorised_google_synthid_verifier",
            )
        )
