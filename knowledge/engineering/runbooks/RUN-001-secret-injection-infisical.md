---
title: "RUN-001: Hermetic Code Execution and Infisical Secret Injection"
status: "active"
category: "runbook"
owner: "@sec-ops"
tags:
  - "infisical"
  - "secrets"
  - "security"
  - "runbook"
---

# RUN-001: Hermetic Code Execution and Infisical Secret Injection

## Objective
Run scripts, migrations, and diagnostic commands securely without persisting credentials to `.env` files or committing secrets to git.

## Execution Flow
1. Verify Infisical CLI authentication or configure Universal Auth:
   ```bash
   infisical login --domain https://secrets.dvlpid.my.id/api \
     --method=universal-auth \
     --client-id="$INFISICAL_CLIENT_ID" \
     --client-secret="$INFISICAL_CLIENT_SECRET"
   ```
2. Verify available secrets in memory:
   ```bash
   ./bin/ep secrets
   ```
3. Execute target command hermetically:
   ```bash
   ./bin/ep run -- python3 -c "import os; print('Injected keys:', len(os.environ))"
   ```

## Troubleshooting
- If Infisical is unreachable, the system automatically falls back to `EnvSecretProvider`.
- Check [ADR-001](../adr/ADR-001-event-driven-architecture.md) for architectural invariants.
