from __future__ import annotations

import secrets
import shutil
from datetime import datetime, timezone
from pathlib import Path
from random import SystemRandom
from typing import Any

from .core import PROTOCOL_VERSION, canonical_json_bytes, content_digest, load_json, sha256_bytes, write_json
from .freeze import verify_freeze

def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def validate_pool(pool: list[dict[str, Any]]) -> None:
    if len(pool) < 2:
        raise ValueError("target pool requires at least two targets")
    ids = [x.get("id") for x in pool]
    if any(not isinstance(x, str) or not x for x in ids):
        raise ValueError("every target requires a non-empty string id")
    if len(set(ids)) != len(ids):
        raise ValueError("target ids must be unique")

def create_trial(pool_path: str | Path, trial_id: str, out_dir: str | Path, candidate_count: int = 4) -> dict[str, Any]:
    pool = load_json(pool_path)
    if not isinstance(pool, list):
        raise ValueError("target pool must be a JSON array")
    validate_pool(pool)
    if candidate_count < 2 or candidate_count > len(pool):
        raise ValueError("candidate_count must be between 2 and pool size")

    rng = SystemRandom()
    candidates = rng.sample(pool, candidate_count)
    true_target = rng.choice(candidates)
    nonce = secrets.token_hex(32)
    pool_sha256 = content_digest(pool)
    candidate_digests = {item["id"]: content_digest(item) for item in candidates}

    private_payload = {
        "protocol_version": PROTOCOL_VERSION,
        "trial_id": trial_id,
        "created_at_utc_untrusted_local": utc_now(),
        "target_pool_sha256": pool_sha256,
        "candidate_ids_ordered": [x["id"] for x in candidates],
        "candidate_sha256": candidate_digests,
        "true_target_id": true_target["id"],
        "nonce": nonce,
    }
    commitment = sha256_bytes(canonical_json_bytes(private_payload))

    public_payload = {
        "protocol_version": PROTOCOL_VERSION,
        "trial_id": trial_id,
        "candidate_count": candidate_count,
        "target_pool_sha256": pool_sha256,
        "commitment_sha256": commitment,
    }
    candidate_payload = {
        "protocol_version": PROTOCOL_VERSION,
        "trial_id": trial_id,
        "target_pool_sha256": pool_sha256,
        "candidates": candidates,
    }

    out = Path(out_dir)
    write_json(out / "custodian" / "PRIVATE_reveal.json", private_payload)
    write_json(out / "custodian" / "PRIVATE_candidates.json", candidate_payload)
    write_json(out / "public" / "PUBLIC_commitment.json", public_payload)
    (out / "evidence").mkdir(parents=True, exist_ok=True)
    return public_payload

def release_candidates(trial_dir: str | Path) -> dict:
    root = Path(trial_dir)
    response = root / "evidence" / "response.raw"
    response_freeze = root / "evidence" / "response.freeze.json"
    if not (response.exists() and response_freeze.exists() and verify_freeze(response, response_freeze)):
        raise ValueError("response must be frozen before candidate release")
    src = root / "custodian" / "PRIVATE_candidates.json"
    dst = root / "judge" / "JUDGE_candidates.json"
    if dst.exists():
        raise ValueError("judge candidate packet already released")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    return load_json(dst)

def reveal_target(trial_dir: str | Path) -> dict:
    root = Path(trial_dir)
    judgment = root / "evidence" / "judgment.json"
    judgment_freeze = root / "evidence" / "judgment.freeze.json"
    if not (judgment.exists() and judgment_freeze.exists() and verify_freeze(judgment, judgment_freeze)):
        raise ValueError("judgment must be frozen before target reveal")
    src = root / "custodian" / "PRIVATE_reveal.json"
    dst = root / "evidence" / "REVEAL.json"
    if dst.exists():
        raise ValueError("target already revealed")
    shutil.copyfile(src, dst)
    return load_json(dst)

def verify_target_packets(trial_dir: str | Path, require_reveal: bool = True) -> dict[str, Any]:
    root = Path(trial_dir)
    public = load_json(root / "public" / "PUBLIC_commitment.json")
    reveal_path = root / "evidence" / "REVEAL.json"
    if not reveal_path.exists() and not require_reveal:
        reveal_path = root / "custodian" / "PRIVATE_reveal.json"
    if not reveal_path.exists():
        raise FileNotFoundError("revealed target packet missing")
    private = load_json(reveal_path)
    judge = load_json(root / "judge" / "JUDGE_candidates.json")

    actual_commitment = sha256_bytes(canonical_json_bytes(private))
    commitment_verified = actual_commitment == public.get("commitment_sha256")
    trial_id_verified = public.get("trial_id") == private.get("trial_id") == judge.get("trial_id")
    pool_verified = public.get("target_pool_sha256") == private.get("target_pool_sha256") == judge.get("target_pool_sha256")

    judge_candidates = judge.get("candidates", [])
    judge_ids = [x.get("id") for x in judge_candidates]
    order_verified = judge_ids == private.get("candidate_ids_ordered")
    digest_map = {x.get("id"): content_digest(x) for x in judge_candidates}
    candidate_content_verified = digest_map == private.get("candidate_sha256")
    true_in_candidates = private.get("true_target_id") in judge_ids
    count_verified = len(judge_ids) == public.get("candidate_count")

    valid = all([
        commitment_verified, trial_id_verified, pool_verified, order_verified,
        candidate_content_verified, true_in_candidates, count_verified,
    ])
    return {
        "trial_id": public.get("trial_id"),
        "commitment_verified": commitment_verified,
        "trial_id_verified": trial_id_verified,
        "target_pool_verified": pool_verified,
        "candidate_order_verified": order_verified,
        "candidate_content_verified": candidate_content_verified,
        "true_target_in_candidates": true_in_candidates,
        "candidate_count_verified": count_verified,
        "target_packets_valid": valid,
        "true_target_id": private.get("true_target_id"),
        "candidate_count": public.get("candidate_count"),
    }
