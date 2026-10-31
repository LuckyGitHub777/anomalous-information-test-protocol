from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .core import PROTOCOL_VERSION, sha256_file, write_json, load_json


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def freeze_artifact(file_path: str | Path, kind: str, out_path: str | Path) -> dict:
    p = Path(file_path)
    record = {
        "protocol_version": PROTOCOL_VERSION,
        "artifact_kind": kind,
        "artifact_name": p.name,
        "artifact_bytes": p.stat().st_size,
        "artifact_sha256": sha256_file(p),
        "frozen_at_utc": utc_now(),
    }
    write_json(out_path, record)
    return record


def verify_freeze(file_path: str | Path, freeze_path: str | Path) -> bool:
    p = Path(file_path)
    record = load_json(freeze_path)
    return (
        record.get("artifact_name") == p.name
        and record.get("artifact_bytes") == p.stat().st_size
        and record.get("artifact_sha256") == sha256_file(p)
    )
