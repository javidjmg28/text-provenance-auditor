#!/usr/bin/env python3
"""Example implementation of the external verifier contract.

This file is intentionally a stub. Replace its internals only with an authorised
provider detector or a detector for a watermark configuration you legitimately
control. It does not attempt to infer provider provenance from writing style.
"""

from __future__ import annotations

import json
import sys


def main() -> int:
    _text = sys.stdin.read()
    print(
        json.dumps(
            {
                "verified": None,
                "score": None,
                "reason": "Example stub only. No authorised provider verifier is connected.",
                "metadata": {"detector_version": "stub-0.3.0"},
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
