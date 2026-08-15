from __future__ import annotations

from .external import ExternalCommandDetector, ExternalVerifierConfig


class AnthropicDetector(ExternalCommandDetector):
    """Anthropic detector boundary.

    Anthropic publicly confirms embedded text watermarks and says third-party
    detection details are forthcoming. The auditor therefore supports an opt-in authorised
    verifier command without inventing an API contract or watermark algorithm.
    """

    def __init__(self) -> None:
        super().__init__(
            ExternalVerifierConfig(
                provider="anthropic",
                env_var="PROVENANCE_ANTHROPIC_VERIFIER_CMD",
                method="authorised_anthropic_verifier",
            )
        )
