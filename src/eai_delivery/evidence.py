from __future__ import annotations
from pathlib import Path
import hashlib, hmac, json, os, zipfile, datetime

EVIDENCE_CANDIDATES = [
    "reference_contract.yaml", "target_contract.yaml", "golden_cases.csv", "thresholds.yaml",
    "human_reviews.csv", "revalidation_plan.md", "reference_case_results.csv",
    "target_case_results.csv", "reference_metrics.json", "target_metrics.json",
    "deployment_delta.json", "deployment_delta.csv", "release_decision.md",
    "dashboard_data.json", "release_dashboard.html"
]

def sha256_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def create_evidence_bundle(evidence_dir, bundle_path, metadata=None, signing_key_env="EVIDENCE_SIGNING_KEY"):
    evidence_dir = Path(evidence_dir)
    bundle_path = Path(bundle_path)
    files = [evidence_dir/name for name in EVIDENCE_CANDIDATES if (evidence_dir/name).exists()]
    manifest = {
        "schema_version": "0.5",
        "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "metadata": metadata or {},
        "files": [
            {"name": p.name, "sha256": sha256_file(p), "bytes": p.stat().st_size}
            for p in sorted(files)
        ]
    }
    manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    key = os.getenv(signing_key_env)
    signature = hmac.new(key.encode(), manifest_bytes, hashlib.sha256).hexdigest() if key else None

    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, arcname=p.name)
        z.writestr("manifest.json", manifest_bytes)
        z.writestr("manifest.sig", signature or "UNSIGNED")
    return manifest, signature

def verify_evidence_bundle(bundle_path, signing_key_env="EVIDENCE_SIGNING_KEY"):
    with zipfile.ZipFile(Path(bundle_path), "r") as z:
        manifest_bytes = z.read("manifest.json")
        manifest = json.loads(manifest_bytes)
        for item in manifest["files"]:
            actual = hashlib.sha256(z.read(item["name"])).hexdigest()
            if actual != item["sha256"]:
                return {"valid": False, "reason": f"hash mismatch: {item['name']}"}
        sig = z.read("manifest.sig").decode().strip()
        if sig != "UNSIGNED":
            key = os.getenv(signing_key_env)
            if not key:
                return {"valid": False, "reason": "signed bundle but signing key unavailable"}
            expected = hmac.new(key.encode(), manifest_bytes, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected):
                return {"valid": False, "reason": "signature mismatch"}
        return {
            "valid": True,
            "signed": sig != "UNSIGNED",
            "file_count": len(manifest["files"]),
            "metadata": manifest.get("metadata", {})
        }
