# v0.5 Architecture — Enterprise AI Release Governance

## 1. Contract plane
Defines exact deployment identity, environment, and business acceptance.

## 2. Change plane
`Reference Contract → Target Contract → Material Change Detection → Revalidation Plan`

A material change never inherits the previous release verdict automatically.

## 3. Evaluation plane
Golden workflows, repeated trials, deterministic/tool/schema/semantic/human evaluation, confidence intervals.

## 4. Economics plane
Inference + infrastructure + review + retry/debug + expected failure loss → Cost per Accepted Workflow.

## 5. Evidence plane
Every release decision is reproducible from:
- reference/target contracts,
- Golden Set and thresholds,
- revalidation plan,
- case-level results,
- aggregate metrics,
- deployment delta,
- release decision,
- dashboard data.

Each artifact is hashed and can be signed.

## 6. Release plane
CI/CD consumes one result:
- PASS / REVIEW NON-MANDATORY → may promote;
- FAIL → block release.

## 7. Runtime plane
Production observations become the next baseline for continuous drift/revalidation.

Product direction:
`Registry → Deployment Contract → Evaluation → Evidence → Release → Runtime Drift → Revalidation`.
