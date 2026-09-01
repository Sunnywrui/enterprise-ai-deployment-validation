# Contract Change Revalidation Plan

- Material changes: **4**
- Risk level: **HIGH**
- Automatic release allowed: **False**

## Changed domains
- artifact
- runtime

## Required revalidation
- Golden critical-path regression
- Task quality
- Tool calling
- Structured output
- Workflow economics
- P50/P95 latency
- Throughput
- Critical accuracy/tool regression
- Capacity/soak test

## Approvals
- FDE/AI Architect
- QA/Evaluation
- Business/Risk Owner

## Detailed contract changes

| Domain | Field | Reference | Target | Revalidation |
|---|---|---|---|---|
| artifact | `deployment_artifact.artifact_hash` | `sha256:REF` | `sha256:CUSTOMER` | Full critical-path + economics |
| artifact | `deployment_artifact.quantization` | `None` | `{'enabled': True, 'method': 'AWQ', 'bits': 4}` | Full critical-path + economics |
| artifact | `deployment_artifact.precision` | `BF16` | `INT4` | Full critical-path + economics |
| runtime | `serving_runtime.version` | `0.x-ref` | `0.x-customer` | Targeted behavior + performance |