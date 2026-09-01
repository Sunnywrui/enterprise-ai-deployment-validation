import tempfile
from pathlib import Path
from eai_delivery.config import load_profile
from eai_delivery.runner import compare_profiles

ROOT = Path(__file__).resolve().parents[1]

def test_offline_compare_detects_regression():
    with tempfile.TemporaryDirectory() as td:
        decision = compare_profiles(
            load_profile(str(ROOT/"examples"/"execution_profiles.yaml")+":reference"),
            load_profile(str(ROOT/"examples"/"execution_profiles.yaml")+":customer"),
            str(ROOT/"examples"/"golden_cases.csv"),
            str(ROOT/"examples"/"thresholds.yaml"),
            td,
        )
        assert decision["overall_verdict"] == "FAIL"
