from __future__ import annotations

from typing import Protocol

from ..models import WatermarkVerification


class ProviderDetector(Protocol):
    provider_name: str

    def verify(self, text: str) -> WatermarkVerification:
        ...
