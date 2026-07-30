"""Canonical content identity and synthetic gateway attestation helpers."""

import hashlib
import hmac
import json
from pathlib import Path
from typing import Any, Dict


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest(value: Any) -> str:
    return sha256_bytes(canonical(value).encode("utf-8"))


def attest(body: Dict[str, Any], key: bytes) -> str:
    value = hmac.new(key, canonical(body).encode("utf-8"), hashlib.sha256).hexdigest()
    return "hmac-sha256:" + value


def verify_attestation(receipt: Dict[str, Any], key: bytes) -> bool:
    if not isinstance(receipt, dict):
        return False
    body = dict(receipt)
    actual = body.pop("attestation", None)
    if not isinstance(actual, str):
        return False
    return hmac.compare_digest(actual, attest(body, key))


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_fsynced(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        import os

        os.fsync(handle.fileno())


def append_fsynced(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        import os

        os.fsync(handle.fileno())
