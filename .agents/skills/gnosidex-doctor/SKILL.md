---
name: gnosidex-doctor
description: |
  Runs the full Gnosidex repository health audit (gx doctor), interprets the JSON
  output, reports all detected issues with actionable fix hints, and guides the
  agent toward remediation. Use whenever the repository state needs to be verified
  before committing or completing a task.
---

# Gnosidex Doctor Skill

This skill governs how coding agents interact with the `gx doctor` health audit
command. It provides interpretation rules and remediation workflows.

## When to Activate

Activate this skill whenever:
- A task modifies knowledge documents, schemas, or frontmatter
- An agent is about to commit or push changes
- The user asks about repository health or link integrity
- Any `gx` command returns a non-zero exit code

## Execution Protocol

### Step 1 — Run Full Audit

```bash
./bin/gx doctor --check-assets --json 2>/dev/null
```

Parse the JSON response. A healthy repository returns:

```json
{
  "status": "healthy",
  "checked_files": 42,
  "issues": []
}
```

### Step 2 — Interpret Exit Codes

| Exit Code | Meaning | Agent Action |
|---|---|---|
| `0` | All checks pass | Proceed to next task |
| `65` | Frontmatter / schema validation error | Enter repair loop using `fix_hint` |
| `66` | Document not found | Verify path or scaffold via `gx create` |
| `70` | Internal runner error | Inspect STDERR stack trace |
| `78` | Vault / secret config error | Run `gx secrets` to diagnose |

### Step 3 — Repair Loop (on validation errors)

If `status == "error"` and `exit_code == 65`:

1. Read the `file`, `line`, `field`, `received`, and `fix_hint` fields.
2. Open the flagged file and apply the fix from `fix_hint`.
3. Re-run `gx doctor --json` to confirm resolution.
4. Repeat until `status == "healthy"`.

```python
# Error envelope shape (exit code 65)
{
  "status": "error",
  "exit_code": 65,
  "error_type": "SCHEMA_VALIDATION_ERROR",
  "file": "knowledge/activities/quarterly-audit/2026-Q4/README.md",
  "line": 4,
  "field": "category",
  "received": "routine-check",
  "allowed": ["architecture-decision", "runbook", "playbook", "rfc", "activity", "guideline"],
  "fix_hint": "Change 'category: routine-check' to one of: architecture-decision, runbook, playbook, rfc, activity, guideline"
}
```

### Step 4 — Asset Verification (optional, requires cloud)

If the repository uses cloud asset offloading:

```bash
./bin/gx doctor --check-assets --json
```

If an asset returns `"remote_exists": false`, upload the binary:

```bash
./bin/gx asset push <local_file> --key <key> --companion <companion.md>
```
