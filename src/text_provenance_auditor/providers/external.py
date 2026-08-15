from __future__ import annotations

import json
import os
import shlex
import subprocess
from dataclasses import dataclass

from ..models import WatermarkVerification


@dataclass
class ExternalVerifierConfig:
    provider: str
    env_var: str
    method: str


class ExternalCommandDetector:
    """Opt-in adapter for an authorised provider verifier.

    The configured command receives the candidate text on stdin and must return JSON:
      {"verified": true|false|null, "score": 0.0-1.0|null, "reason": "...", "metadata": {...}}

    This adapter does not ship a detector key or reverse-engineer a provider watermark.
    """

    def __init__(self, config: ExternalVerifierConfig):
        self.config = config
        self.provider_name = config.provider

    def verify(self, text: str) -> WatermarkVerification:
        command = os.getenv(self.config.env_var)
        if not command:
            return WatermarkVerification(
                provider=self.provider_name,
                status="unavailable",
                verified=None,
                reason=f"No authorised verifier command configured in {self.config.env_var}.",
                method=self.config.method,
                evidence_level="unavailable",
            )

        try:
            proc = subprocess.run(
                shlex.split(command),
                input=text,
                text=True,
                capture_output=True,
                timeout=30,
                check=False,
            )
        except Exception as exc:
            return WatermarkVerification(
                provider=self.provider_name,
                status="error",
                verified=None,
                reason=f"Configured verifier could not run: {exc}",
                method=self.config.method,
                evidence_level="unavailable",
            )

        if proc.returncode != 0:
            detail = proc.stderr.strip() or f"exit code {proc.returncode}"
            return WatermarkVerification(
                provider=self.provider_name,
                status="error",
                verified=None,
                reason=f"Configured verifier failed: {detail}",
                method=self.config.method,
                evidence_level="unavailable",
            )

        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return WatermarkVerification(
                provider=self.provider_name,
                status="error",
                verified=None,
                reason="Configured verifier did not return valid JSON.",
                method=self.config.method,
                evidence_level="unavailable",
            )

        verified = data.get("verified")
        if verified not in {True, False, None}:
            verified = None

        return WatermarkVerification(
            provider=self.provider_name,
            status="verified" if verified is True else ("not_verified" if verified is False else "inconclusive"),
            verified=verified,
            score=data.get("score"),
            reason=data.get("reason"),
            method=self.config.method,
            evidence_level="provider_verified" if verified is not None else "unavailable",
            metadata=data.get("metadata") or {},
        )
