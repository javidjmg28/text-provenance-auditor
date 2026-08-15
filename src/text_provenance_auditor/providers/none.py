from __future__ import annotations

from ..models import WatermarkVerification


class NoProviderDetector:
    provider_name = "none"

    def verify(self, text: str) -> WatermarkVerification:
        return WatermarkVerification(
            provider="none",
            status="not_requested",
            verified=None,
            reason="Provider watermark verification was not requested.",
            method="none",
            evidence_level="unavailable",
        )
