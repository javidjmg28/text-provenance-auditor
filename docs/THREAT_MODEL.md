# Threat Model

## What V3 is intended to detect

V3 surfaces evidence that can be inspected and explained:

- authorised provider watermark verification results;
- signed C2PA provenance attached to supported assets;
- invisible or unusual Unicode channels;
- bidirectional text controls;
- mixed-script homoglyph substitutions;
- document sections with concentrated observable anomalies;
- weak style regularities, clearly labelled as heuristics.

## What V3 does not claim to detect

V3 does not claim to identify AI authorship from prose style alone.

A clean report does not establish that text was written by a human. Reasons include:

- the provider verifier may be unavailable;
- a watermark may not be present in the source model;
- a mark may be too weak to verify in a short passage;
- content may have been edited or transformed;
- file metadata may have been removed;
- a different model or system may use a different marking technique.

## False-positive considerations

Observable anomalies can be legitimate.

Examples:

- zero-width joiners are used in some writing systems and emoji sequences;
- non-breaking spaces are common in typography;
- bidirectional controls can support multilingual layouts;
- NFKC changes can arise from ligatures or compatibility characters;
- mixed scripts can occur in names, transliteration and technical notation.

The report should therefore say what was observed rather than assign malicious intent.

## Local web interface

The V3 web UI binds to `127.0.0.1` by default and has no application authentication layer. This is appropriate for a local utility, not a public internet service.

Risks introduced by intentionally binding the server to another interface include:

- unauthorised users submitting files or text;
- exposure of audit results;
- denial-of-service through repeated requests;
- processing of untrusted files through optional extraction or C2PA libraries.

If exposing V3 beyond localhost, place it behind appropriate authentication, TLS, request limits and network controls.

The UI caps uploads at 25 MB. Temporary files are deleted after each request, including failure paths handled by the application.

## Adversarial considerations

This project does not contain watermark-removal or detector-evasion logic.

The external verifier interface is designed for authorised detectors. No secret keys are bundled and no provider algorithm is reverse-engineered.

## Trust boundary

C2PA validation depends on the configured verification backend and trust settings. A manifest with validation issues remains useful forensic information, but it should not be represented as fully trusted signed provenance.
