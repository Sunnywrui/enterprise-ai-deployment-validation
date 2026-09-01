# Enterprise AI Deployment Release Decision

- Reference: `DEP-REF-001`
- Target: `DEP-CUSTOMER-001`
- Overall verdict: **FAIL**
- Mandatory metric failures: **4**

## Metric gates

| Metric | Reference | Target | Delta | Gate | Mandatory | Verdict |
|---|---:|---:|---:|---|---|---|
| task_completion_rate | 1.0 | 0.5454545454545454 | -0.4545454545454546 | min_delta -0.05 | True | **FAIL** |
| human_acceptance_rate | 1.0 | 0.5454545454545454 | -0.4545454545454546 | min_delta -0.05 | True | **FAIL** |
| semantic_acceptance_rate | 1.0 | 1.0 | 0.0 | min_delta -0.1 | False | **PASS** |
| tool_call_accuracy | 1.0 | 1.0 | 0.0 | min_delta -0.03 | True | **PASS** |
| argument_accuracy | 1.0 | 0.0 | -1.0 | min_delta -0.03 | True | **FAIL** |
| argument_schema_validity | 1.0 | 0.0 | -1.0 | min_delta -0.03 | True | **FAIL** |
| schema_validity | 1.0 | 1.0 | 0.0 | min_value 0.97 | True | **PASS** |
| permission_compliance | 1.0 | 1.0 | 0.0 | min_value 1.0 | True | **PASS** |
| p95_latency_ms | 900.0 | 1400.0 | 500.0 | max_value 3000 | True | **PASS** |
| cost_per_accepted_workflow | 0.03944444444444444 | 9.733076923076924 | 9.693632478632479 | max_value 10.0 | False | **PASS** |

## Release rule

Any mandatory FAIL or INCONCLUSIVE blocks automatic release. Residual risk requires explicit owner acceptance and compensating controls.