# V3 Architecture

## Goals

Text Provenance Auditor V3 answers a narrow question accurately: **what provenance evidence is actually present and verifiable?**

It deliberately avoids a universal AI-detector claim and adds a local human-facing interface without changing the underlying evidence model.

## Layers

```text
+-------------------------------------------------------------+
| Interfaces                                                  |
| Local web UI | CLI | Python API | Agent skill              |
+-----------------------------+-------------------------------+
                              |
+-----------------------------v-------------------------------+
| Audit engine                                                |
| extraction | provider adapter | C2PA | Unicode | stylometry |
| segmentation | evidence summary + independent scores        |
+-----------------------------+-------------------------------+
                              |
+-----------------------------v-------------------------------+
| Structured AuditReport JSON                                |
+-------------------------------------------------------------+
```

The web interface never reimplements detector logic. It calls `audit_text()` and `audit_file()` and renders their structured report.

## Local web server

`provenance-audit web` launches a FastAPI/Uvicorn application.

Default binding:

```text
127.0.0.1:8765
```

Endpoints:

- `GET /` browser application;
- `GET /health` health and version;
- `GET /api/capabilities` current capability declaration;
- `POST /api/scan-text` raw text audit;
- `POST /api/scan-file` local file audit.

Uploaded files are written to a temporary local path only because existing extraction and C2PA backends are path-oriented. The temporary file is removed in a `finally` block after the report is produced.

The local UI limits uploads to 25 MB. This is an application guardrail rather than a format guarantee.

## Provider adapters

Provider detection uses an interface boundary instead of embedding a guessed detector.

Current adapters:

- `AnthropicDetector`
- `GoogleSynthIDDetector`
- `NoProviderDetector`

Anthropic and Google adapters support an opt-in external command contract. This allows future official or authorised detection mechanisms to be connected without rewriting the audit pipeline.

The verifier command receives candidate text on stdin and returns structured JSON.

## C2PA backend selection

`inspect_c2pa()` uses this order:

1. import and use `c2pa-python` when available;
2. use `c2patool` from `PATH` when available;
3. return `unavailable` if neither backend is present.

This keeps the base package dependency-free while allowing cryptographic provenance inspection when official tooling is installed.

## Observable text forensics

The scanner classifies suspicious characters into families and severity levels.

High-value families include:

- zero-width characters;
- bidirectional controls;
- Unicode tags;
- invisible operators.

Medium or notice-level observations include:

- variation selectors;
- soft hyphens;
- unusual whitespace;
- Unicode normalisation differences.

Mixed-script token detection is intentionally simple and transparent. It identifies tokens containing two or more recognised scripts, which can help surface homoglyph substitutions.

## Stylometry

Stylometry is not part of provider verification.

Metrics include:

- type-token ratio;
- sentence-length coefficient of variation;
- repeated trigram counts.

Weak flags are only raised when thresholds are crossed. They remain separate from provider and C2PA evidence.

## Evidence scoring

There is no combined AI score.

Each channel has its own scale:

- provider evidence: 0, 100 or unavailable;
- signed provenance: 0, 55, 100 or unavailable;
- observable anomalies: weighted by direct forensic observations;
- style heuristics: capped at 60.

The absence of a provider score means the verifier was not available or was inconclusive, not that the text is human-written.
