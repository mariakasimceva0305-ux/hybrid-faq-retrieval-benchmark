from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s]")


COMMON_REWRITES = {
    "signin": "sign in",
    "log in": "login",
    "log-in": "login",
    "mfa": "multi factor authentication",
    "2fa": "multi factor authentication",
    "pwd": "password",
    "acct": "account",
}


def normalize_text(text: str) -> str:
    value = text.lower().strip()
    for source, target in COMMON_REWRITES.items():
        value = value.replace(source, target)
    value = _PUNCT_RE.sub(" ", value)
    value = _WHITESPACE_RE.sub(" ", value).strip()
    return value
