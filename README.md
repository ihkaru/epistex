# Enterprise Git-Based Knowledge Base Starter Kit

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Zero-Dependency Core](https://img.shields.io/badge/dependencies-zero_runtime-success.svg)]()
[![Code Architecture](https://img.shields.io/badge/architecture-SOLID%20%7C%20EDA%20%7C%20DIP-purple.svg)]()

A high-performance, enterprise-ready, plug-and-play **Git-based Knowledge Base Starter Kit** engineered with an **Agent-First Tool Contract**, **Event-Driven Architecture (EDA)**, **Interface-First Design (SOLID)**, and **Hermetic Code Execution with Runtime Secret Injection** (first-party support for Infisical and zero vendor lock-in).

---

## Key Highlights

- **Zero External Runtime Dependencies**: Powered entirely by the Python 3.10+ Standard Library. Clone and run immediately on Linux, macOS, or Windows without running `pip install`.
- **Agent-First Tool Contract**:
  - **Stream Purity**: Pure machine-parseable JSON on STDOUT when `--json` is active or piped; human progress and diagnostic benchmarks sent strictly to STDERR.
  - **Deterministic POSIX/BSD Exit Codes**: `EX_OK (0)`, `EX_USAGE (2)`, `EX_DATAERR (65)`, `EX_NOINPUT (66)`, `EX_SOFTWARE (70)`, `EX_CONFIG (78)`.
  - **Self-Correction Envelopes**: Structured error responses with actionable `fix_hint` and field diagnostics for automated agent self-healing loops.
  - **Machine-First Degradation**: Automatically disables ANSI colors when TTY is not attached.
- **Hermetic Code Runner & Secret Injection**:
  - Memory-only secret injection directly into target child processes over TLS. Secrets are never written to disk (`.env` or temporary files).
  - Sanitized host environment: child processes inherit only a safe allowlist (`PATH`, `TERM`, `LANG`, etc.), preventing host variable leaks.
  - First-party support for **Infisical** (Universal Auth & CLI export) with zero vendor lock-in (seamless fallback to `EnvSecretProvider`).
- **Convention-Over-Configuration**:
  - Laravel-inspired directory structure: `bin/`, `config/`, `knowledge/`, `src/`, `storage/`.
  - Predictable semantic prefixes: `[ADR-NNN]` (Architecture Decision Records), `[RUN-NNN]` (Runbooks), `[PLAY-NNN]` (Playbooks).
- **Algorithmic Big-O Optimizations**:
  - **Filesystem Traversal**: $O(V)$ pruned `os.scandir` iterator skipping `.git`, `node_modules`, and `storage` at the iterator level.
  - **Frontmatter Reader**: $O(K)$ streaming line reader with early exit at the second `---` marker ($O(1)$ memory).
  - **Deadline & Schedule Query**: $O(M \log k)$ bounded min-heap (`heapq`) for top-$k$ nearest milestones.
  - **Link Integrity Audit**: $O(N + R)$ single-pass hash inverted index for $O(1)$ relative link verification without disk stat storms.
  - **Repository Map**: Token-budget bounded depth traversal (< 150-300 tokens) for instant agent orientation.
- **Event-Driven Architecture (EDA)**:
  - Pub/Sub event dispatcher with listener priority ordering and pipeline pattern.
  - Typed domain events: `DocumentCreatedEvent`, `FrontmatterParsedEvent`, `PreRunExecutionEvent`, `PostRunExecutionEvent`, `SecretInjectedEvent`, `HealthCheckCompletedEvent`.
  - Append-only audit logging to `storage/logs/audit.jsonl`.
- **SOLID & Interface-First Design**:
  - Abstract contracts (`src/contracts/`) decouple high-level CLI commands from secret backends and execution runners.
  - Strict Single Responsibility Principle: all classes $\le 180$ lines, all functions $\le 50$ lines.

---

## Directory Taxonomy

```text
kb-starter-kit/
├── bin/
│   └── kb                           # Executable CLI runner (chmod +x)
├── config/                          # Convention-over-configuration settings
│   ├── app.py                       # App metadata, paths, POSIX exit codes
│   ├── schema.py                    # Frontmatter schema rules & templates
│   └── vault.py                     # Secret provider & hermetic runner config
├── knowledge/                       # Domain-driven knowledge base documents
│   ├── engineering/
│   │   ├── adr/                     # Architecture Decision Records ([ADR-001]-...)
│   │   └── runbooks/                # Operational Runbooks ([RUN-001]-...)
│   ├── operations/
│   │   └── playbooks/               # Incident & triage playbooks ([PLAY-001]-...)
│   └── activities/                  # Structured operational activities & milestones
│       └── quarterly-audit/2026-Q4/
├── src/                             # SOLID, Interface-First Python package
│   ├── contracts/                   # Abstract interfaces (Events, Secrets, Runners, Validator)
│   ├── core/                        # High-performance zero-dep algorithmic core
│   │   ├── errors.py                # Domain exceptions & POSIX sysexits envelopes
│   │   ├── io_stream.py             # Atomic writes (os.replace) & streaming reader
│   │   ├── scanner.py               # Pruned scandir iterator & inverted index
│   │   ├── yaml_parser.py           # Safe restricted YAML parser
│   │   └── schema_validator.py      # Frontmatter schema validator
│   ├── events/                      # Event dispatcher & typed domain events
│   ├── providers/                   # Concrete provider implementations (DI ready)
│   │   ├── secrets/                 # InfisicalProvider, EnvSecretProvider, MemorySecretProvider
│   │   └── runner/                  # HermeticCodeRunner, DryCodeRunner
│   ├── listeners/                   # AuditEventListener, TelemetryEventListener
│   └── commands/                    # CLI commands (doctor, map, create, schedule, run, secrets)
├── storage/                         # Local storage & ephemeral artifacts
│   ├── cache/
│   └── logs/                        # Structured JSONL audit logs
├── tests/                           # Complete test suite (23 tests, zero mock leakage)
├── AGENTS.md                        # Agent-First Tool Contract & operational protocols
├── DESIGN.md                        # Architecture, SOLID principles & Big-O analysis
├── GEMINI.md                        # Self-contained repository governance manual
└── README.md                        # Root manifest and quickstart guide
```

---

## Quickstart & CLI Commands

All commands can be invoked directly using `./bin/kb` without installation:

### 1. Repository Health Audit (`kb doctor`)
Validates frontmatter schema compliance, relative link integrity, line limit caps, and secret leak sentinels:
```bash
./bin/kb doctor --json
```
Output (STDOUT pure data):
```json
{
  "status": "ok",
  "exit_code": 0,
  "scanned_files": 4,
  "total_issues": 0,
  "schema_issues": [],
  "dead_links": [],
  "secret_leaks": []
}
```

### 2. Token-Efficient Repository Map (`kb map`)
Produces a bounded, token-efficient structural overview of all domains:
```bash
./bin/kb map --depth 2 --compact --json
```

### 3. Query Upcoming Schedules (`kb schedule`)
Uses a bounded min-heap ($O(M \log k)$) to extract nearest deadlines:
```bash
./bin/kb schedule --limit 5 --json
```

### 4. Hermetic Execution with Secret Injection (`kb run`)
Executes a command in an isolated environment with secrets injected directly into process memory:
```bash
# Preview execution in dry-run mode
./bin/kb run --dry-run -- python3 -c "import os; print(os.environ)"

# Execute hermetically with Infisical secrets
./bin/kb run -- python3 -c "import os; print('Injected keys:', len(os.environ))"
```

### 5. Inspect Secret Provider Status (`kb secrets`)
Inspects active secret provider connectivity and masks keys for safe diagnostics:
```bash
./bin/kb secrets --json
```

### 6. Scaffold New Documents Atomically (`kb create`)
Scaffolds documents from standard templates (`adr`, `runbook`, `activity`) using atomic writes:
```bash
./bin/kb create adr engineering/adr/ADR-002-distributed-tracing.md --title "Distributed Tracing"
```

---

## Running Verification & Tests

Execute the parallel hermetic test suite:
```bash
python3 -m unittest discover -s tests -v
```

Run static SRP analysis to verify class and function line caps:
```bash
python3 ~/.gemini/config/skills/craftsman-coder/scripts/static_srp_analyzer.py . --strict
```

Verify zero-mock compliance in production code:
```bash
detect-mocks .
```

---

## License

This project is licensed under the permissive **MIT License**.
