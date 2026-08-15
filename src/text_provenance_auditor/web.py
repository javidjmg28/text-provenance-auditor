from __future__ import annotations

import tempfile
import threading
import webbrowser
from importlib.resources import files
from pathlib import Path
from typing import Any

from .audit import audit_file, audit_text
from .capabilities import get_capabilities

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_UPLOAD_BYTES = 4_000_000
ALLOWED_PROVIDERS = {"anthropic", "google", "none", "auto"}


def _require_web_dependencies():
    try:
        from fastapi import FastAPI, File, Form, HTTPException, UploadFile
        from fastapi.responses import HTMLResponse
    except ImportError as exc:  # pragma: no cover - depends on installation extras
        raise RuntimeError(
            "The web interface requires optional dependencies. "
            "Install them with: python -m pip install -e '.[web]'"
        ) from exc
    return FastAPI, File, Form, HTTPException, UploadFile, HTMLResponse


def _validate_provider(provider: str) -> str:
    provider = (provider or "anthropic").strip().lower()
    if provider not in ALLOWED_PROVIDERS:
        raise ValueError(f"Unsupported provider: {provider}")
    return provider


def _load_index_html() -> str:
    return (
        files("text_provenance_auditor")
        .joinpath("web_assets", "index.html")
        .read_text(encoding="utf-8")
    )


def create_app():
    FastAPI, File, Form, HTTPException, UploadFile, HTMLResponse = _require_web_dependencies()

    app = FastAPI(
        title="Text Provenance Auditor",
        version=get_capabilities()["version"],
        description="Evidence-based provenance inspection for text and supported files.",
    )

    @app.get("/", response_class=HTMLResponse)
    async def index():
        return HTMLResponse(_load_index_html())

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": get_capabilities()["version"]}

    @app.get("/api/capabilities")
    async def capabilities() -> dict[str, Any]:
        return get_capabilities()

    @app.post("/api/scan-text")
    async def scan_text(payload: dict[str, Any]) -> dict[str, Any]:
        text = str(payload.get("text", ""))
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text is required.")
        try:
            provider = _validate_provider(str(payload.get("provider", "anthropic")))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        include_segments = bool(payload.get("include_segments", True))
        report = audit_text(
            text,
            source="web:inline",
            provider=provider,
            include_segments=include_segments,
        )
        return report.to_dict()

    @app.post("/api/scan-file")
    async def scan_file(
        file: Any = File(...),
        provider: str = Form("anthropic"),
        include_segments: bool = Form(True),
        inspect_c2pa: bool = Form(True),
    ) -> dict[str, Any]:
        try:
            provider = _validate_provider(provider)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        data = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="File exceeds the 4 MB hosted upload limit.")

        safe_name = Path(file.filename or "upload").name
        suffix = Path(safe_name).suffix
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(prefix="provenance-audit-", suffix=suffix, delete=False) as tmp:
                tmp.write(data)
                temp_path = Path(tmp.name)
            report = audit_file(
                temp_path,
                provider=provider,
                include_segments=include_segments,
                inspect_file_provenance=inspect_c2pa,
            )
            result = report.to_dict()
            result["source"] = safe_name
            return result
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    return app


def run_web(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    *,
    open_browser: bool = True,
) -> None:
    _require_web_dependencies()
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "The web interface requires uvicorn. Install with: python -m pip install -e '.[web]'"
        ) from exc

    if open_browser and host in {"127.0.0.1", "localhost"}:
        url = f"http://{host}:{port}"
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    uvicorn.run(create_app(), host=host, port=port, log_level="info")
