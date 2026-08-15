from __future__ import annotations

from .anthropic import AnthropicDetector
from .google import GoogleSynthIDDetector
from .none import NoProviderDetector


def get_detector(provider: str):
    provider = provider.lower().strip()
    if provider in {"anthropic", "claude"}:
        return AnthropicDetector()
    if provider in {"google", "gemini", "synthid", "google_synthid"}:
        return GoogleSynthIDDetector()
    if provider in {"none", "auto"}:
        return NoProviderDetector()
    raise ValueError(f"Unsupported provider: {provider}")


__all__ = ["AnthropicDetector", "GoogleSynthIDDetector", "NoProviderDetector", "get_detector"]
