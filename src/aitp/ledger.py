from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .core import canonical_json_bytes, sha256_bytes

GENESIS = "0" * 64
LEDGER_VERSION = "AITP-LEDGER-1.1"
LEGACY_KEYS = {"index", "timestamp_utc_untrusted_local", "event_type", "payload", "prev_hash", "record_hash"}

class LedgerFormatError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def records(path: str | Path) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    out=[]
    for n,line in enumerate(p.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip():
            continue
        try:
            obj=json.loads(line)
        except json.JSONDecodeError as e:
            raise LedgerFormatError(f"malformed ledger record at line {n}: {e.msg}") from None
        if not isinstance(obj,dict):
            raise LedgerFormatError(f"malformed ledger record at line {n}: object required")
        out.append(obj)
    return out


def _new_body(record: dict) -> dict:
    return {k:v for k,v in record.items() if k != "record_hash"}


def _legacy_body(record: dict) -> dict:
    return {k:record[k] for k in ["index","timestamp_utc_untrusted_local","event_type","payload","prev_hash"]}


def append_event(path: str | Path, event_type: str, payload: dict) -> dict:
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    recs=records(p)
    prev_hash=recs[-1]["record_hash"] if recs else GENESIS
    body={
        "ledger_version": LEDGER_VERSION,
        "index": len(recs),
        "timestamp_utc_untrusted_local": utc_now(),
        "event_type": event_type,
        "payload": payload,
        "prev_hash": prev_hash,
    }
    record_hash=sha256_bytes(canonical_json_bytes(body))
    record={**body,"record_hash":record_hash}
    with p.open("a",encoding="utf-8",newline="\n") as fh:
        fh.write(json.dumps(record,sort_keys=True,ensure_ascii=False)+"\n")
    return record


def verify_ledger(path: str | Path) -> tuple[bool,str]:
    try:
        recs=records(path)
    except LedgerFormatError as e:
        return False,str(e)
    prev=GENESIS
    for idx,record in enumerate(recs):
        if record.get("index") != idx:
            return False,f"index mismatch at {idx}"
        if record.get("prev_hash") != prev:
            return False,f"prev_hash mismatch at {idx}"
        if record.get("ledger_version") == LEDGER_VERSION:
            expected=sha256_bytes(canonical_json_bytes(_new_body(record)))
        elif "ledger_version" not in record:
            # v1.0 compatibility: exact legacy shape only, so injected keys fail.
            if set(record) != LEGACY_KEYS:
                return False,f"unexpected legacy record fields at {idx}"
            expected=sha256_bytes(canonical_json_bytes(_legacy_body(record)))
        else:
            return False,f"unsupported ledger_version at {idx}: {record.get('ledger_version')}"
        if record.get("record_hash") != expected:
            return False,f"record_hash mismatch at {idx}"
        prev=expected
    return True,f"{len(recs)} records verified"


def verify_sequence(path: str | Path, required: list[str]) -> tuple[bool,str]:
    try:
        types=[r.get("event_type") for r in records(path)]
    except LedgerFormatError as e:
        return False,str(e)
    pos=-1
    for item in required:
        try:
            pos=types.index(item,pos+1)
        except ValueError:
            return False,f"required event missing/out of order: {item}"
    return True,"required event order verified"
