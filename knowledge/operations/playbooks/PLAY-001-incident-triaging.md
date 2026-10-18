---
title: "PLAY-001: Operational Incident Triaging and Blast Radius Containment"
status: "active"
category: "playbook"
owner: "@incident-commander"
tags:
  - "incident"
  - "triage"
  - "ops"
---

# PLAY-001: Operational Incident Triaging and Blast Radius Containment

## Scope & Trigger Conditions
This playbook triggers when an unexpected production anomaly or data integrity issue occurs in critical knowledge services.

## Immediate Action Checklist
1. **Declare Incident Level**:
   - P1: Total outage or continuous data loss.
   - P2: Partial degradation or failed secret injection.
   - P3: Minor UI or formatting regression.
2. **Execute Diagnostic Doctor**:
   ```bash
   ./bin/kb doctor --json
   ```
3. **Verify Links & References**:
   Refer to operational runbooks in [RUN-001](../../engineering/runbooks/RUN-001-secret-injection-infisical.md).
