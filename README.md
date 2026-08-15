# Text Provenance Auditor V2

A provider-aware provenance inspector for text, documents and C2PA-capable assets. It is designed for ChatGPT skills, other LLM agents, local CLI workflows and CI pipelines.

V2 is built around one principle: **do not confuse evidence with guesses**.

The tool keeps four evidence channels separate:

1. **Provider verification**: an authorised provider detector returns a result.
2. **Signed file provenance**: C2PA Content Credentials are read and validated where supported.
3. **Observable text forensics**: hidden or unusual Unicode channels, bidirectional controls, mixed-script tokens and normalisation differences are reported directly.
4. **Stylometric heuristics**: weak writing-pattern indicators are shown separately and never treated as proof of AI authorship or a provider watermark.

## Why V2 exists

AI provenance is becoming a mix of text watermarks, signed asset metadata and platform-specific verification systems. A single "AI detector score" hides important differences between these signals.

V2 therefore produces a structured evidence report rather than a binary claim.

```text
Input
  |
  +-- Provider verifier adapter
  |
  +-- C2PA Content Credentials inspection
  |
  +-- Unicode and steganography forensics
  |
  +-- Stylometric diagnostics
  |
  +-- Long-document segment analysis
  |
  `-- Evidence summary + separate channel scores
```

## Anthropic and Claude

Anthropic's current support documentation confirms that supported Claude models use embedded text watermarks and signed C2PA provenance metadata for supported file types. Anthropic also states that third-party detection details will be published in forthcoming technical documentation.

This repository therefore **does not invent Claude's watermark algorithm** and does not claim that Claude uses Google SynthID-Text. Until an authorised detector is available, Claude provider verification correctly returns `unavailable`.

You can wire an authorised detector into V2 later without changing the core code:

```bash
export PROVENANCE_ANTHROPIC_VERIFIER_CMD="/path/to/authorised-claude-verifier"
```

The command receives text on stdin and returns JSON. See [`examples/authorised_verifier_stub.py`](examples/authorised_verifier_stub.py).

## Google SynthID-Text

Google DeepMind publishes SynthID-Text documentation and an open-source reference implementation. Detection depends on the relevant watermark configuration and detector. V2 does not pretend that an arbitrary Gemini passage can be verified from style alone.

An authorised or model-owner detector can be wired in through:

```bash
export PROVENANCE_GOOGLE_SYNTHID_VERIFIER_CMD="/path/to/authorised-synthid-verifier"
```

## C2PA Content Credentials

V2 can inspect C2PA provenance through either:

- the official `c2pa-python` package, preferred when installed; or
- the official `c2patool` CLI when it is available on `PATH`.

The adapter reports:

- whether a manifest is present;
- whether validation completed without reported validation issues;
- the active manifest ID;
- claim generator information;
- detected C2PA assertion labels;
- digital source type references;
- provider-related metadata hints;
- validation status entries.

A provider hint inside a manifest is labelled as a hint. It is not silently upgraded into proof of authorship.

## Unicode and steganography forensics

V2 scans for observable text channels including:

- zero-width characters;
- bidirectional controls and overrides;
- Unicode tag characters;
- variation selectors;
- invisible mathematical operators;
- soft hyphens;
- unusual whitespace characters;
- mixed Latin/Cyrillic/Greek or other script tokens;
- NFC and NFKC normalisation differences.

These are useful for finding hidden text, copy-and-paste artefacts, homoglyph substitutions and unusual formatting. They are **not** assumed to be Claude, Gemini or any other provider's watermark.

## Document-level analysis

Long text is split into roughly 400-word segments. Each segment records:

- word count;
- suspicious Unicode count;
- mixed-script count;
- number of weak stylometric flags.

This makes it easier to locate anomalies in a large document instead of treating the whole file as one opaque score.

## Evidence scores

V2 outputs four independent channel scores:

```json
{
  "provider_evidence": null,
  "signed_provenance": 100,
  "observable_text_anomalies": 20,
  "style_heuristics": 0
}
```

These scores **must not be added together**. They are not an AI-authorship probability.

For example:

- `provider_evidence: 100` means an authorised provider detector returned positive verification;
- `signed_provenance: 100` means a C2PA manifest was present and no validation issues were reported by the backend;
- `observable_text_anomalies` measures directly observable unusual text features;
- `style_heuristics` reflects weak pattern flags and is capped well below provider evidence.

## Deploy to Vercel

V3 includes a FastAPI entrypoint at `app.py` and is ready to deploy from GitHub to Vercel.

1. Import this repository into Vercel.
2. Keep the framework preset on automatic detection.
3. Deploy. Vercel will detect the Python/FastAPI application.
4. The root URL serves the browser UI and `/api/*` routes perform audits.

The hosted direct-upload limit is 4 MB because Vercel Functions enforce a 4.5 MB request payload ceiling. For larger files, use the local CLI/web interface or add a direct object-storage upload flow later.

The hosted app does not intentionally persist uploaded files. Uploaded assets are written only to temporary function storage for the duration of analysis. Do not use the public demo for confidential documents.

## Installation

Base installation:

```bash
python -m pip install -e .
```

DOCX and PDF text extraction:

```bash
python -m pip install -e '.[documents]'
```

C2PA inspection through Python:

```bash
python -m pip install -e '.[provenance]'
```

Everything for local development:

```bash
python -m pip install -e '.[all]'
```

## CLI

Audit pasted text:

```bash
provenance-audit scan-text "Paste the text here" --pretty
```

Audit a document:

```bash
provenance-audit scan report.docx --pretty
provenance-audit scan paper.pdf --pretty
```

Use the Google/SynthID provider adapter:

```bash
provenance-audit scan-text "..." --provider google --pretty
```

Inspect only C2PA provenance:

```bash
provenance-audit verify-c2pa image.png --pretty
provenance-audit verify-c2pa document.pdf --pretty
```

Show capabilities:

```bash
provenance-audit capabilities --pretty
```

Disable document segmentation or C2PA checks when required:

```bash
provenance-audit scan report.pdf --no-segments --no-c2pa --pretty
```

## Example report structure

```json
{
  "version": "0.2.0",
  "watermark_verification": {
    "provider": "anthropic",
    "status": "unavailable",
    "verified": null,
    "method": "authorised_anthropic_verifier"
  },
  "c2pa": {
    "status": "unavailable",
    "manifest_present": null
  },
  "unicode_forensics": {
    "suspicious_count": 0,
    "mixed_script_count": 0
  },
  "stylometry": {
    "classification": "heuristic_only",
    "flagged_signal_count": 0
  },
  "evidence_summary": {
    "overall_level": "no_positive_evidence"
  },
  "evidence_scores": {
    "provider_evidence": null,
    "signed_provenance": null,
    "observable_text_anomalies": 0,
    "style_heuristics": 0
  }
}
```

## Provider verifier contract

An external authorised detector receives the text through stdin and should return:

```json
{
  "verified": true,
  "score": 0.97,
  "reason": "Provider detector matched the configured watermark.",
  "metadata": {
    "detector_version": "example"
  }
}
```

`verified` may be `true`, `false` or `null` when inconclusive.

## Supported text extraction

Built in:

- `.txt`
- `.md`
- `.rst`
- `.csv`
- `.json`
- `.yaml`
- `.yml`

With the `documents` extra:

- `.docx`
- text-based `.pdf`

Non-text C2PA assets can still be inspected with `verify-c2pa`, or with `scan` where the text analysis section will simply contain no extracted words.

## What this project does not do

- remove or defeat provider watermarks;
- paraphrase text to evade provenance detection;
- reverse-engineer secret watermark keys;
- claim "Claude watermark detected" from writing style;
- claim "Gemini/SynthID detected" without the relevant verifier;
- turn stylistic regularity into a fake AI probability.

Ordinary editorial rewriting for clarity, tone, grammar or brand voice is separate from provenance detection and should not be represented as watermark removal.

## Tests

```bash
python -m pytest -q
```

V2 currently includes tests for provider boundaries, Unicode channels, mixed-script detection, C2PA parsing, document segmentation and evidence scoring.

## Project layout

```text
src/text_provenance_auditor/
  audit.py
  c2pa_forensics.py
  cli.py
  evidence.py
  extract.py
  models.py
  segments.py
  stylometry.py
  unicode_forensics.py
  providers/
    anthropic.py
    base.py
    external.py
    google.py
    none.py

docs/
  ARCHITECTURE.md
  THREAT_MODEL.md

examples/
  authorised_verifier_stub.py
```

## References

Primary references used for V2:

- Anthropic Help Center, "How Claude marks AI-generated content": https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content
- Google DeepMind, SynthID: https://deepmind.google/models/synthid/
- Google DeepMind SynthID-Text reference implementation: https://github.com/google-deepmind/synthid-text
- C2PA Specification: https://spec.c2pa.org/specifications/
- Content Authenticity Initiative, c2pa-python: https://github.com/contentauth/c2pa-python
- Content Authenticity Initiative, c2pa-rs / c2patool: https://github.com/contentauth/c2pa-rs

## Licence

MIT
