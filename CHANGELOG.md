# Changelog

## 0.2.0

### Added

- Google SynthID-Text provider adapter boundary.
- External authorised verifier command contract for provider integrations.
- C2PA inspection through `c2pa-python` or `c2patool`.
- C2PA manifest parsing, validation status, claim generator, source type and provider-hint reporting.
- Unicode tag, variation selector, bidi, invisible-operator and unusual-space scanning.
- Mixed-script token detection for basic homoglyph forensics.
- Unicode NFC/NFKC normalisation-delta reporting.
- Long-document segmentation.
- Evidence-level classification.
- Four separate evidence-channel scores with no combined AI probability.
- `verify-c2pa` CLI command.
- Architecture and threat-model documentation.
- GitHub Actions test workflow.

### Changed

- Corrected the V1 assumption that Anthropic had publicly identified Claude's watermark as SynthID-Text. Anthropic currently confirms an embedded text watermark but has not publicly documented that implementation as SynthID-Text.
- Provider verification now uses pluggable authorised detectors instead of hard-coded unavailable classes.
- Stylometric metrics and weak flags are separated.

### Safety

- V2 does not remove or defeat watermarks.
- V2 does not optimise rewriting against provenance detectors.
