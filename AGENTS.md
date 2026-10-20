# Agent-First Tool Contract & Operational Protocol (AGENTS.md)

## 1. Dual-Audience CLI Design
The `gx` CLI (Gnosidex) provides strict stream separation between machine payload, runtime diagnostics, and visual display:

```text
               ┌────────────────────────────────────────────────────────┐
               │                     gx <subcommand>                    │
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
  | `66` | `EX_NOINPUT` | Target document not found. | Verify path or scaffold using `gx create`. |
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
- **Idempotency & Safe Mutation**: Running `gx create` multiple times will not overwrite files unless `--force` is specified.
- **Token-Budget Preserving Invocations**:
  - `gx map --depth 2 --compact`: Summarizes repository layout in < 150 tokens.
  - `gx schedule --limit 5`: Queries nearest deadlines in < 100 tokens.
- **Hermetic Code Execution**:
  - `gx run -- <cmd>` executes commands in a stripped environment, injecting secrets in-memory from Infisical (or fallback).
  - Supports `--dry-run` to preview commands and injected keys without executing.
- **Cloud Asset Offloading & Tiered Hydration**:
  - Offload binary files: `gx asset push <file> --key <key> --companion <path.md>` to keep Git lightweight.
  - Check existence without downloading: `gx asset check <key>`.
  - Hydrate / download binary on-demand: `gx asset pull <key> --target <path>`.
  - Discover assets: `gx asset list --tier local|cloud|all`.
  - Verify asset integrity during health check: `gx doctor --check-assets --json`.

---

## 3. Autonomous Repository Specialization (`gx init`)

When a coding agent is instructed to adopt, initialize, or specialize Gnosidex for a company or project, the agent **MUST** invoke the initialization installer non-interactively:

```bash
./bin/gx init \
  --name "Project / Org Name" \
  --description "Accurate project description" \
  --owner "@team-or-handle" \
  --clean-samples \
  --yes \
  --json
```

### Agent Invariants during Specialization:
1. **Zero-Interactivity**: Always supply `--yes` or `-y` along with `--json` to prevent blocking on interactive stdin prompts.
2. **Boilerplate Pruning**: Pass `--clean-samples` to purge development-only sample documents (`knowledge/engineering/adr/` and `knowledge/activities/`).
3. **Automated Documentation Clean-up**: `gx init` automatically converts the starter-kit alert and checklist in `README.md` into an active organization knowledge base header.
4. **Environment Initialization**: Generates `.env` from `.env.example` if absent, allowing subsequent secret vault configuration.

---

## 4. Agent Versioning & Git Lifecycle Protocol (Laravel Model)

Coding agents modifying or contributing to Gnosidex or its downstream instances **MUST** adhere to the following Laravel-inspired version control protocol:

```text
  [1.x Branch] ────────► Target for bugfixes, non-breaking features, and patch PRs
       ▲
       │
  [feat/* or fix/*] ───► Short-lived branches created from 1.x
```

### A. Branching Doctrine
- **Active Series Branch (`1.x`)**: All maintenance, bugfixes, and backward-compatible additive features **MUST** target the `1.x` branch.
- **Production Baseline (`main`)**: Serves as the stable release trunk. Merges to `main` occur upon validated release tagging.
- **Branch Naming Conventions**:
  - `feat/<short-description>` for new capabilities (e.g. `feat/sqlite-audit-sink`).
  - `fix/<short-description>` for defect corrections (e.g. `fix/scandir-symlink-loop`).
  - `chore/<short-description>` for dependency or governance updates.

### B. Strict Semantic Versioning 2.0.0 (`vMAJOR.MINOR.PATCH`)
- **`PATCH` (`1.0.x`)**:
  - Bug fixes, Big-O algorithmic optimizations, documentation corrections.
  - **Hard Invariant**: 100% zero breaking changes to existing frontmatter schemas or CLI flags.
- **`MINOR` (`1.x.0`)**:
  - Additive CLI commands, new document templates in `config/schema.py`, new storage/secret providers.
  - **Hard Invariant**: Backward-compatible with existing companion documents and configuration files.
- **`MAJOR` (`2.0.0`)**:
  - Fundamental architectural shifts or deprecation cleanups.
  - **Agent Rule**: Autonomous agents **MUST NOT** perform major version bumps without explicit user instruction.

### C. Downstream Upstream Synchronization
When working in a downstream specialized repository, agents can pull core engine updates from upstream Gnosidex safely:
```bash
git fetch upstream 1.x
git merge --no-commit upstream/1.x
```
Because custom business documents reside in `knowledge/` and core engine components reside in `src/`, upgrades merge cleanly.

---

## 5. The Verification Gauntlet (Evidence-First Doctrine)

Before declaring any coding task complete or committing changes, coding agents **MUST** execute and review concrete evidence from the 4 automated gates:

```bash
# 1. Parallel Unit & Integration Test Suite (Zero failures allowed)
python3 -m unittest discover -s tests -v

# 2. Deterministic Static SRP & Abstraction Analyzer
python3 ~/.gemini/config/skills/craftsman-coder/scripts/static_srp_analyzer.py . --strict

# 3. Zero-Mock & Silent Mock Static Detector
detect-mocks .

# 4. End-to-End Repository Health Audit
./bin/gx doctor --check-assets --json
```

Agents must never conclude a task without terminal output evidence validating all four gates.


