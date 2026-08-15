# Local Web UI

V3 includes a local browser interface for users who prefer not to operate the CLI directly.

## Start

```bash
python -m pip install -e '.[web]'
provenance-audit web
```

Default URL:

```text
http://127.0.0.1:8765
```

## Text workflow

1. Select **Paste text**.
2. Choose the provider adapter.
3. Paste the candidate text.
4. Keep segmentation enabled for long passages.
5. Select **Analyse provenance**.

## File workflow

1. Select **Upload file**.
2. Choose the provider adapter or `Auto from C2PA hints`.
3. Select the local file.
4. Choose whether to inspect C2PA.
5. Select **Analyse provenance**.

## Result cards

The UI shows four independent evidence cards:

- Provider evidence
- Signed provenance
- Observable anomalies
- Style heuristics

Do not combine their numerical values.

## Findings

The findings panel surfaces:

- suspicious Unicode characters and their context;
- mixed-script tokens and their context;
- long-document segments containing anomalies or weak style flags.

## Report export

Use **Download JSON** to save the complete structured report or **Copy JSON** to place it on the clipboard.

## Privacy model

The default interface is local-first. Browser requests go to the local V3 server and uploaded files are processed through a temporary local file that is deleted after the request.

Do not expose the built-in web server publicly without adding a proper deployment security layer.
