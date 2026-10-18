# Agent-First Tool Contract & Operational Protocol (AGENTS.md)

## 1. Dual-Audience CLI Design
The `kb` CLI provides strict stream separation between machine payload, runtime diagnostics, and visual display:

```text
               ┌────────────────────────────────────────────────────────┐
               │                     kb <subcommand>                    │
               └───────────────────────────┬────────────────────────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
             [Flag --json / CI pipe]                   [TTY / Terminal]
                        │                                     │
           ┌────────────┴────────────┐                        │
           ▼                         ▼                        ▼
     STDOUT (Pure Data)      STDERR (Diagnostics)       STDOUT (Visual)
   • Machine-parseable      • Progress status         • Rich ASCII tables
   • Strict JSON schema     • Non-fatal warnings      • ANSI color codes
   • Zero ANSI escapes      • Telemetry logs          • Interactive prompts
```

### A. Stream Purity & I/O Channels
- **STDOUT Reserved for Pure Data**: When `--json` is active (or when STDOUT is piped), STDOUT outputs **ONLY** valid JSON. Zero ANSI escapes, zero banners, zero progress chatter.
- **STDERR Reserved for Diagnostics**: Benchmarks, telemetry, and warnings are routed strictly to `sys.stderr`.
- **Deterministic POSIX/BSD Exit Codes (`sysexits.h`)**:
  | Exit Code | POSIX Constant | Agent Meaning | Actionable Agent Response |
  |---|---|---|---|
  | `0` | `EX_OK` | Execution successful. | Proceed to next task. |
  | `2` | `EX_USAGE` | Invalid CLI arguments/flags. | Read `--help` and correct invocation syntax. |
  | `65` | `EX_DATAERR` | Frontmatter/schema validation error. | Enter repair loop using `fix_hint`. |
  | `66` | `EX_NOINPUT` | Target document not found. | Verify path or scaffold using `kb create`. |
  | `70` | `EX_SOFTWARE` | Internal runner or script exception. | Inspect STDERR stack trace. |
  | `78` | `EX_CONFIG` | Secret provider / vault error. | Check credentials or use fallback. |

### B. Structured Self-Correction Envelope
When a command fails with `--json`, it returns an actionable envelope enabling self-healing loops:
```json
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

## 2. Key Operational Patterns
- **Machine-First Degradation**: Automatically checks `sys.stdout.isatty()`. In headless subshells, ANSI styling is disabled automatically.
- **Atomic Writes via Rename (`os.replace`)**: All mutations write to a temporary file first, then atomically replace the target to prevent file corruption.
- **Idempotency & Safe Mutation**: Running `kb create` multiple times will not overwrite files unless `--force` is specified.
- **Token-Budget Preserving Invocations**:
  - `kb map --depth 2 --compact`: Summarizes repository layout in < 150 tokens.
  - `kb schedule --limit 5`: Queries nearest deadlines in < 100 tokens.
- **Hermetic Code Execution**:
  - `kb run -- <cmd>` executes commands in a stripped environment, injecting secrets in-memory from Infisical (or fallback).
  - Supports `--dry-run` to preview commands and injected keys without executing.
- **Cloud Asset Offloading & Tiered Hydration**:
  - Offload binary files: `kb asset push <file> --key <key> --companion <path.md>` to keep Git lightweight.
  - Check existence without downloading: `kb asset check <key>`.
  - Hydrate / download binary on-demand: `kb asset pull <key> --target <path>`.
  - Discover assets: `kb asset list --tier local|cloud|all`.
  - Verify asset integrity during health check: `kb doctor --check-assets --json`.

