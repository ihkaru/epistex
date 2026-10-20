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

## 4. Operational Scope & Anti-Poisoning Doctrine

To guarantee that coding agents remain strictly aligned with the operational context and never confuse **Downstream Content Maintenance** with **Upstream Framework Releasing**, agents **MUST** respect the repository mode defined in `config/app.py`:

### A. Downstream Operational Mode (`IS_STARTER_KIT = False`)
When Gnosidex has been specialized for an organization (e.g. via `gx init`):
1. **Content-Only Scope**: The agent's responsibility is exclusively authoring, updating, and auditing knowledge documents (`knowledge/`), running hermetic tasks (`gx run`), and verifying health (`gx doctor`).
2. **Zero-Release Invariant**: Autonomous agents **MUST NOT** bump engine versions, create git release tags, or generate engine release notes for content updates. Engine release triggers are completely deactivated.
3. **Upstream Synchronization**: Downstream repositories pull framework and CLI enhancements from upstream without touching internal documents:
   ```bash
   git remote add upstream https://github.com/ihkaru/gnosidex.git
   git fetch upstream 1.x
   git merge --no-commit upstream/1.x
   ```

### B. Upstream Starter Kit Mode (`IS_STARTER_KIT = True`)
When maintaining the open-source Gnosidex engine (`src/`, `bin/gx`, `config/`):
1. **Automated Release Verification**: Run `./bin/gx doctor --check-release --json` to detect whether unreleased code commits warrant a Patch or Minor release.
2. **Release Governance**: Follow the comprehensive state machine and pre-flight gates documented strictly in [`docs/RELEASING.md`](docs/RELEASING.md).
3. **Anti-Poisoning Pruning**: When `gx init` is executed, [`docs/RELEASING.md`](docs/RELEASING.md) is automatically pruned so downstream agents never encounter engine release instructions.

---

## 5. Agent Infrastructure Directory (`.agents/`)

The `.agents/` directory provides the on-demand skill library and stop-hook gate for coding agents:

```text
.agents/
├── hooks.json                          # AGY stop-hook configuration (auto-runs pre_stop.sh)
├── hooks/
│   └── pre_stop.sh                     # 4-gate gauntlet executed before agent may stop
└── skills/
    ├── gnosidex-doctor/
    │   └── SKILL.md                    # gx doctor audit, exit code interpretation & repair loop
    ├── gnosidex-knowledge-author/
    │   └── SKILL.md                    # Frontmatter schema, naming conventions, link integrity
    └── gnosidex-downstream-setup/
        └── SKILL.md                    # Downstream specialization, upstream sync, anti-poisoning
```

### When to Load Each Skill

| Situation | Skill to Load |
|---|---|
| Verifying repository health / resolving errors | `gnosidex-doctor` |
| Authoring, scaffolding, or auditing knowledge documents | `gnosidex-knowledge-author` |
| Onboarding a new downstream organization | `gnosidex-downstream-setup` |

### Adding Downstream-Specific Skills

After `gx init` specializes the repository, **downstream agents** may add their own skills under `.agents/skills/`:

```bash
mkdir -p .agents/skills/my-domain-skill
# Write .agents/skills/my-domain-skill/SKILL.md with YAML frontmatter:
# ---
# name: my-domain-skill
# description: "What this skill does and when to activate it."
# ---
```

Skills are **never merged back upstream** — they belong exclusively to the downstream knowledge base.

---

## 6. The Verification Gauntlet (Evidence-First Doctrine)

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


