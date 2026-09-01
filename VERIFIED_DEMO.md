# Verified v0.5 Demo

The bundled offline release-governance demo was executed successfully.

## Release result
- Overall release verdict: **FAIL**
- Mandatory metric failures: **4**
- Release ready: **false**

The failure is intentional: the customer deployment contains a tool-argument regression.

## Change governance
- Material contract changes detected: **4**
- Risk level: **HIGH**
- Changed domains: **artifact, runtime**
- Automatic Contract Change Revalidation Plan generated.

## Evidence governance
- Evidence bundle created.
- SHA-256 manifest generated for every included file.
- HMAC-SHA256 signature generated using an ephemeral demo key.
- Bundle integrity/signature verification passed during build.
- Demo signing key is intentionally not distributed.

## Dashboard
- `release_dashboard.html` generated from the same release evidence.
- Companion `Enterprise_AI_Release_Governance_Dashboard_v0.5.xlsx` is included in the Delivery Pack.

## Runtime governance hook
- Production observation schema included for post-release drift monitoring.
