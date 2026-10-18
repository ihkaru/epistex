---
title: "Quarterly Knowledge Base and Security Audit (2026-Q4)"
status: "active"
category: "activity"
owner: "@sec-ops"
routine: "quarterly"
deadlines:
  - milestone: "Schema and Link Sanity Check"
    due: "2026-10-25"
  - milestone: "Universal Auth Key Rotation"
    due: "2026-11-01"
  - milestone: "Hermetic Runner Penetration Test"
    due: "2026-11-10"
  - milestone: "Final Audit Signoff"
    due: "2026-11-20"
---

# Quarterly Knowledge Base and Security Audit (2026-Q4)

## Overview
Quarterly routine to audit document integrity, link freshness, secret hygiene, and hermetic execution safety across the knowledge repository.

## Audit Steps
1. Run automated doctor checks:
   ```bash
   ./bin/kb doctor
   ```
2. Validate upcoming deadlines:
   ```bash
   ./bin/kb schedule --limit 5
   ```
3. Test Infisical secret injection in dry-run mode:
   ```bash
   ./bin/kb run --dry-run -- python3 --version
   ```
