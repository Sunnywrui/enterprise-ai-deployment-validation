#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"
rm -rf out
python -m eai_delivery.cli validate-contract examples/reference_contract.yaml --schema examples/deployment_contract.schema.json
python -m eai_delivery.cli diff-contracts examples/reference_contract.yaml examples/customer_contract.yaml || true
python -m eai_delivery.cli compare \
  --reference-profile examples/execution_profiles.yaml:reference \
  --target-profile examples/execution_profiles.yaml:customer \
  --golden examples/golden_cases.csv \
  --thresholds examples/thresholds.yaml \
  --out out || true
echo
cat out/release_decision.md
