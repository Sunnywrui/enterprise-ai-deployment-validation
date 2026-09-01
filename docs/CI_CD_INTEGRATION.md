# CI/CD Integration

The release-gate command is pipeline-native:

- exit `0`: no mandatory release failure;
- exit `2`: mandatory release gate failed.

Always publish evidence, including on failure.

## Recommended enterprise flow

1. PR or CHG updates model/artifact/runtime configuration.
2. Validate Deployment Contract schema.
3. Generate Contract Change Revalidation Plan.
4. Execute required Golden workflow tests.
5. Compute Behavioral Equivalence and Workflow Economics.
6. Generate dashboard and evidence bundle.
7. Sign evidence from a vault-backed secret/KMS identity.
8. Block or promote based on release verdict.
9. Retain evidence with change/release records.

`EVIDENCE_SIGNING_KEY` must be stored in a CI secret or vault, never in source control.
