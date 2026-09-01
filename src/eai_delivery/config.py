from __future__ import annotations
from pathlib import Path
import json
import yaml
from jsonschema import Draft202012Validator

def load_yaml(path: str | Path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def load_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate_contract(contract_path: str | Path, schema_path: str | Path):
    contract = load_yaml(contract_path)
    schema = load_json(schema_path)
    errors = sorted(Draft202012Validator(schema).iter_errors(contract), key=lambda e: list(e.path))
    return contract, errors

def load_profile(spec: str):
    # format: path.yaml:key
    if ":" not in spec:
        raise ValueError("Profile must be path.yaml:key")
    path, key = spec.rsplit(":", 1)
    data = load_yaml(path)
    if key not in data:
        raise KeyError(f"Profile '{key}' not found in {path}")
    return data[key]
