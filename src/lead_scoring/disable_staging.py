#!/usr/bin/env python3
"""
Immediate revocation of the Lead Scoring staging installation — requirement
#9 (must be disable-able immediately). Also used directly as negative test
"disabled/uninstalled agent must fail closed".

    VITRINA_ENV=staging python -m src.lead_scoring.disable_staging
"""
from __future__ import annotations

import sys

sys.path.insert(0, ".")

from .. import env  # noqa: E402


def main() -> None:
    env.require(env.DEV, env.STAGING)
    from . import kernel_registry
    result = kernel_registry.disable(reason="manual revocation via disable_staging.py")
    print(f"Disabled: {result}")


if __name__ == "__main__":
    main()
