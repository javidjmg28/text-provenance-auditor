from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .models import C2PAReport


SUPPORTED_SUFFIXES = {
    ".avi", ".avif", ".c2pa", ".dng", ".flac", ".gif", ".heic", ".heif",
    ".jpg", ".jpeg", ".jxl", ".m4a", ".mp3", ".mp4", ".mov", ".pdf", ".png",
    ".svg", ".tif", ".tiff", ".wav", ".webp",
}

PROVIDER_TERMS = {
    "anthropic": ("anthropic", "claude"),
    "google": ("google", "gemini", "synthid"),
    "openai": ("openai", "chatgpt", "gpt-"),
    "adobe": ("adobe", "firefly"),
    "microsoft": ("microsoft", "copilot"),
}


def _walk(obj: Any):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key
            yield from _walk(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from _walk(value)
    elif isinstance(obj, (str, int, float, bool)):
        yield obj


def _find_strings(obj: Any, needle: str) -> list[str]:
    found: list[str] = []
    needle = needle.lower()
    for value in _walk(obj):
        if isinstance(value, str) and needle in value.lower():
            found.append(value)
    return found


def _active_manifest(data: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    active_id = data.get("active_manifest")
    manifests = data.get("manifests") or {}
    active = manifests.get(active_id, {}) if active_id else {}
    return active_id, active if isinstance(active, dict) else {}


def parse_manifest_store(data: dict[str, Any], backend: str) -> C2PAReport:
    active_id, active = _active_manifest(data)
    manifests = data.get("manifests") or {}
    manifest_present = bool(active_id or manifests)

    validation = data.get("validation_status") or active.get("validation_status") or []
    if not isinstance(validation, list):
        validation = [validation]
    validation_ok = manifest_present and len(validation) == 0

    claim_generator = active.get("claim_generator")
    if not claim_generator:
        info = active.get("claim_generator_info") or []
        if isinstance(info, list) and info and isinstance(info[0], dict):
            claim_generator = info[0].get("name")

    labels: set[str] = set()
    source_types: set[str] = set()
    for value in _walk(active):
        if isinstance(value, str):
            if value.startswith("c2pa.") or value.startswith("cawg."):
                labels.add(value)
            if "digitalsourcetype" in value.lower() or "algorithmicmedia" in value.lower():
                source_types.add(value)

    # More precise source-type extraction from actions assertions when present.
    assertions = active.get("assertions")
    if isinstance(assertions, list):
        for assertion in assertions:
            if not isinstance(assertion, dict):
                continue
            label = assertion.get("label")
            if isinstance(label, str):
                labels.add(label)
            data_block = assertion.get("data")
            if isinstance(data_block, dict):
                actions = data_block.get("actions")
                if isinstance(actions, list):
                    for action in actions:
                        if isinstance(action, dict) and isinstance(action.get("digitalSourceType"), str):
                            source_types.add(action["digitalSourceType"])

    provider_hints: list[str] = []
    serialised = json.dumps(active, ensure_ascii=False).lower()
    for provider, terms in PROVIDER_TERMS.items():
        if any(term in serialised for term in terms):
            provider_hints.append(provider)

    return C2PAReport(
        status="present_valid" if manifest_present and validation_ok else ("present_with_validation_warnings" if manifest_present else "not_present"),
        manifest_present=manifest_present,
        validation_ok=validation_ok if manifest_present else None,
        active_manifest=active_id,
        claim_generator=claim_generator if isinstance(claim_generator, str) else None,
        digital_source_types=sorted(source_types),
        assertion_labels=sorted(labels),
        provider_hints=provider_hints,
        validation_status=validation,
        backend=backend,
        reason=None if manifest_present else "No C2PA manifest was found in the asset.",
    )


def _inspect_with_python(path: Path) -> C2PAReport | None:
    try:
        from c2pa import Reader  # type: ignore
    except ImportError:
        return None

    try:
        with Reader(str(path)) as reader:
            data = json.loads(reader.json())
        return parse_manifest_store(data, backend="c2pa-python")
    except Exception as exc:
        # The SDK can raise when no manifest exists or if the file is invalid.
        message = str(exc)
        if "manifest" in message.lower() and any(term in message.lower() for term in ("not found", "no ", "none")):
            return C2PAReport(
                status="not_present",
                manifest_present=False,
                validation_ok=None,
                backend="c2pa-python",
                reason=message,
            )
        return C2PAReport(
            status="error",
            manifest_present=None,
            validation_ok=None,
            backend="c2pa-python",
            reason=message,
        )


def _inspect_with_cli(path: Path) -> C2PAReport | None:
    binary = shutil.which("c2patool")
    if not binary:
        return None
    proc = subprocess.run(
        [binary, str(path)],
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.strip() or proc.stdout.strip()
        lowered = stderr.lower()
        if "manifest" in lowered and any(term in lowered for term in ("not found", "no manifest", "none")):
            return C2PAReport(
                status="not_present",
                manifest_present=False,
                validation_ok=None,
                backend="c2patool",
                reason=stderr,
            )
        return C2PAReport(
            status="error",
            manifest_present=None,
            validation_ok=None,
            backend="c2patool",
            reason=stderr or f"c2patool exited with {proc.returncode}",
        )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return C2PAReport(
            status="error",
            manifest_present=None,
            validation_ok=None,
            backend="c2patool",
            reason="c2patool did not return valid JSON.",
        )
    return parse_manifest_store(data, backend="c2patool")


def inspect_c2pa(path: str | Path) -> C2PAReport:
    path = Path(path)
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        return C2PAReport(
            status="unsupported",
            manifest_present=None,
            validation_ok=None,
            reason=f"C2PA inspection is not supported for {path.suffix or '<no extension>'} by this adapter.",
        )

    python_report = _inspect_with_python(path)
    if python_report is not None:
        return python_report

    cli_report = _inspect_with_cli(path)
    if cli_report is not None:
        return cli_report

    return C2PAReport(
        status="unavailable",
        manifest_present=None,
        validation_ok=None,
        reason="Install the optional 'provenance' extra (c2pa-python) or make c2patool available on PATH.",
    )
