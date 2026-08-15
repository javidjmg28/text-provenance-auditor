---
name: text-provenance-auditor
description: Inspect text, documents and supported assets for provider-verifiable watermark evidence, C2PA signed provenance, observable Unicode or steganographic anomalies, and clearly labelled stylometric indicators without presenting heuristics as proof of AI authorship.
---

# Text Provenance Auditor V2

Use this skill when a user wants to inspect text, a document or a supported file for AI provenance, provider watermarks, Content Credentials, hidden text markers or suspicious machine-readable patterns.

## Core rule

Keep these evidence channels separate:

1. authorised provider verification;
2. signed C2PA file provenance;
3. observable text forensics;
4. stylometric heuristics.

Never convert weak style patterns into a claim that a named model generated the text.

## Workflow

### Pasted text

Run:

```bash
provenance-audit scan-text "<text>" --provider anthropic --pretty
```

or:

```bash
provenance-audit scan-text "<text>" --provider google --pretty
```

### Document or file

Run:

```bash
provenance-audit scan <path> --provider anthropic --pretty
```

For C2PA-only inspection:

```bash
provenance-audit verify-c2pa <path> --pretty
```

## Interpret the report

Report the result using the strongest established evidence level:

- `provider_verified`: an authorised provider verifier returned a positive result.
- `signed_provenance_with_provider_hint`: valid C2PA provenance is present and provider-related metadata was observed.
- `signed_provenance_present`: valid C2PA provenance is present but does not establish a model identity.
- `observable_forensics_only`: hidden or unusual text features were directly observed.
- `heuristic_only`: only weak style patterns were flagged.
- `no_positive_evidence`: none of the configured checks established positive provenance evidence.

## Numerical scores

The report contains independent scores for:

- provider evidence;
- signed provenance;
- observable text anomalies;
- style heuristics.

Never add these scores together. Never describe them as the probability that a text is AI-generated.

## Anthropic handling

Anthropic confirms embedded text watermarks for supported Claude models and says third-party detection details are forthcoming.

Unless `PROVENANCE_ANTHROPIC_VERIFIER_CMD` is configured to an authorised detector, report provider verification as unavailable.

Do not claim that Claude uses SynthID-Text unless Anthropic publishes that information in an authoritative source.

## Google SynthID handling

Google publishes SynthID-Text and an open-source reference implementation. Detecting a particular watermark requires the relevant configuration or authorised mechanism.

Unless `PROVENANCE_GOOGLE_SYNTHID_VERIFIER_CMD` is configured, do not claim that arbitrary Gemini text has been verified.

## C2PA handling

C2PA is signed provenance metadata for an asset. A validated C2PA manifest can establish that signed assertions are bound to the asset and have not been altered without detection under the verification model.

Do not interpret a C2PA manifest as proof that every word in a file originated with a particular model. A file can be edited, converted, assembled from ingredients or processed by multiple tools.

## Unicode handling

The scanner may report zero-width characters, bidi controls, variation selectors, Unicode tag characters, unusual spaces, mixed-script tokens and normalisation differences.

Explain that these findings can arise from legitimate typography, language support, copy-and-paste operations or malicious steganography. They are not automatically provider watermarks.

## Safety and provenance integrity

Do not remove, scramble, paraphrase, translate or rewrite text for the purpose of defeating a watermark or provenance detector.

If a user wants normal editorial improvement, it is acceptable to edit for clarity, structure, tone, grammar or brand voice. Do not optimise the edit against a detector and do not represent it as watermark removal.

## Recommended response format

Use a concise structure:

- **Provider verification:** verified / not verified / unavailable
- **C2PA provenance:** valid / validation warnings / absent / unavailable
- **Observable text findings:** count and the most relevant examples
- **Style heuristics:** weak flags only, explicitly labelled as non-proof
- **Conclusion:** strongest evidence level and what it can establish
- **Limitations:** short samples, edited text and unsupported file types where relevant
