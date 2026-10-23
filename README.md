<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/brand/epistex-wordmark-light.svg">
    <img src="docs/images/brand/epistex-wordmark.svg" alt="Epistex" height="64">
  </picture>
</p>

<p align="center">
  <strong>Zero Syntax for Humans. Zero Ambiguity for AI Agents.</strong><br>
  <em>The Enterprise Git-Based Knowledge Base Starter Kit with Hermetic Secret Injection and Pure Machine Contracts.</em>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/dependencies-zero_runtime-success.svg" alt="Zero-Dependency Core">
  <img src="https://img.shields.io/badge/architecture-SOLID%20%7C%20EDA%20%7C%20DIP-purple.svg" alt="Code Architecture">
  <a href="https://github.com/ihkaru/epistex/releases"><img src="https://img.shields.io/badge/release-v1.2.0%20(Laravel%20Model)-blue.svg" alt="Latest Release"></a>
</p>

---

## 🧠 The Agent-Mediated Experience

> [!TIP]
> **No CLI Syntax to Memorize**: You never need to remember complex commands, flags, or configuration paths. Simply speak to your AI coding agent (Antigravity, Claude Code, Cursor, Codex) in natural language. The agent consults its embedded skills in `.agents/skills/` and translates your intent into deterministic `gx` CLI calls behind the scenes.

| What You Say to Your AI Agent (Natural Intent) | What The Agent Runs Under the Hood | Outcome Delivered to You |
|:---|:---|:---|
| *"Specialize this repository for our team and prune sample docs"* | `./bin/gx init --name "MyOrg" --clean-samples -y --json` | Repositories specialized, metadata configured, starter-kit release triggers deactivated. |
| *"Audit our knowledge base for broken links, missing frontmatter, or secret leaks"* | `./bin/gx doctor --check-assets --json` | Complete health audit in < 50ms; agent summarizes findings and self-heals broken links. |
| *"What upcoming deadlines and milestones are approaching?"* | `./bin/gx schedule --limit 10 --json` | Nearest milestones queried via $O(M \log k)$ bounded min-heap in < 100 tokens. |
| *"Draft a new Architecture Decision Record for our PostgreSQL migration"* | `./bin/gx create knowledge/engineering/adr/ADR-002-postgres.md --category architecture-decision --json` | Scaffolds standard document with valid YAML frontmatter and atomic writes (`os.replace`). |
| *"Run our data sync script hermetically without saving credentials to disk"* | `./bin/gx run -- python3 scripts/sync.py` | Injects in-memory secrets directly from Infisical vault; zero disk leaks, zero process contamination. |

---

> [!IMPORTANT]
> **Starter Kit Specialization Notice (Replace Once Adopted)**:
> This repository is a generic, zero-vendor-lock-in **starter template**. When adopting this repository for your organization or team, follow the [Specialization Checklist](#-starter-kit-specialization-checklist-replace-once-adopted) to configure identity metadata, document governance schemas, secret vaults, and cloud storage. Once customized, feel free to replace or remove that section to document your specific organization's knowledge base.

---

## 🚀 Starter Kit Specialization Checklist (Replace Once Adopted)

When tailoring this starter kit to your organization's specific requirements, execute the following specialization sequence:

### 1. Identity & Metadata Customization
- **[`config/app.py`](config/app.py)**: Update `APP_NAME`, `APP_DESCRIPTION`, and `APP_VERSION` to reflect your team or organizational identity.
- **[`README.md`](README.md)**: Replace the root title and introductory charter with your organization's specific mission and guidelines.

### 2. Schema & Governance Rules
- **[`config/schema.py`](config/schema.py)**:
  - Customize `ALLOWED_STATUSES` (e.g., `["draft", "in-review", "approved", "deprecated"]`).
  - Customize `ALLOWED_CATEGORIES` (e.g., adding `sop`, `data-dictionary`, `postmortem`, `rfc`).
  - Adjust `REQUIRED_FRONTMATTER_FIELDS` to enforce internal team governance.
  - Tailor `DEFAULT_TEMPLATES` for your automated document scaffolding via `gx create`.

### 3. Secret Vault & Cloud Storage Integration
- **Environment Template**: Copy [`.env.example`](.env.example) to `.env` (`cp .env.example .env`).
- **Secret Vault ([`config/vault.py`](config/vault.py))**:
  - Point `INFISICAL_API_URL` and `INFISICAL_PROJECT_ID` to your organization's Infisical instance.
  - Inject Machine Identity credentials (`INFISICAL_CLIENT_ID`, `INFISICAL_CLIENT_SECRET`) or use `KB_VAULT_BACKEND=env` for standard CI runners.
- **Cloud Storage ([`config/cloud.py`](config/cloud.py))**:
  - Configure `S3_ENDPOINT_URL`, `S3_BUCKET_NAME`, and `S3_REGION` (compatible with AWS S3, Cloudflare R2, MinIO, Coolify S3, Backblaze).
  - Select your cloud authentication mode: `KB_CLOUD_AUTH=hermetic` (zero disk secrets) or `env`.

### 4. Knowledge Domain Organization
- **Prune Sample Documents**: Remove or replace initial boilerplate examples in [`knowledge/engineering/adr/`](knowledge/engineering/adr/) and [`knowledge/activities/`](knowledge/activities/).
- **Establish Business Domains**: Create domain directories that map to your team's real operational boundaries (e.g. `knowledge/data-platform/`, `knowledge/governance/`, `knowledge/infrastructure/`).
- **Scaffold New Documents**: Use `./bin/gx create <template> <path>` to generate new standard documents with atomic writes.

### 5. Final Verification & Documentation Cleanup
- Run the full verification gauntlet to confirm compliance with your customized schemas:
  ```bash
  ./bin/gx doctor --check-assets --json
  ```
- Once verified, remove or replace this **Specialization Checklist** section in `README.md` with your team's operational manual.

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
epistex/
├── .agents/                         # On-demand skill library & AGY stop-hook
│   ├── hooks.json                   # Automated pre-stop verification hook
│   ├── hooks/pre_stop.sh            # 4-gate gauntlet (tests + SRP + mocks + doctor)
│   └── skills/                      # Doctor, Knowledge-Author, Downstream-Setup
├── .githooks/                       # Git lifecycle hooks
│   └── pre-commit                   # 300-line SRP guard & anti-poisoning check
├── bin/
│   ├── ep                           # Short canonical CLI entrypoint (chmod +x)
│   ├── epistex                      # Full canonical alias symlink (chmod +x)
│   ├── gx                           # Backward-compatible symlink (chmod +x)
│   └── kb                           # Legacy transition symlink (chmod +x)
├── config/                          # Convention-over-configuration settings
│   ├── app.py                       # App metadata, paths, IS_STARTER_KIT flag
│   ├── schema.py                    # Frontmatter schema rules & templates
│   ├── vault.py                     # Secret provider & hermetic runner config
│   └── cloud.py                     # S3 asset storage & auth posture config
├── knowledge/                       # Domain-driven knowledge base documents
│   ├── engineering/
│   │   ├── adr/                     # Architecture Decision Records ([ADR-001]-...)
│   │   └── runbooks/                # Operational Runbooks ([RUN-001]-...)
│   ├── operations/
│   │   └── playbooks/               # Incident & triage playbooks ([PLAY-001]-...)
│   └── activities/                  # Structured operational activities & milestones
│       └── quarterly-audit/2026-Q4/
├── scripts/
│   └── release.sh                   # 1-step deterministic release automation engine
├── src/                             # SOLID, Interface-First Python package
│   ├── contracts/                   # Abstract interfaces (Events, Secrets, Runners, Validator)
│   ├── core/                        # High-performance zero-dep algorithmic core
│   │   ├── errors.py                # Domain exceptions & POSIX sysexits envelopes
│   │   ├── io_stream.py             # Atomic writes (os.replace) & streaming reader
│   │   ├── scanner.py               # Pruned scandir iterator & inverted index
│   │   ├── yaml_parser.py           # Safe restricted YAML parser
│   │   ├── release_checker.py       # Deterministic SemVer release-readiness probe
│   │   └── schema_validator.py      # Frontmatter schema validator
│   ├── events/                      # Event dispatcher & typed domain events
│   ├── providers/                   # Concrete provider implementations (DI ready)
│   │   ├── secrets/                 # InfisicalProvider, EnvSecretProvider, MemorySecretProvider
│   │   ├── storage/                 # LocalAssetStorageProvider, S3AssetStorageProvider
│   │   └── runner/                  # HermeticCodeRunner, DryCodeRunner
│   ├── listeners/                   # AuditEventListener, TelemetryEventListener
│   └── commands/                    # CLI commands (doctor, map, create, schedule, run, asset, init)
├── storage/                         # Local storage & ephemeral artifacts
│   ├── cache/
│   └── logs/                        # Structured JSONL audit logs
├── tests/                           # Complete test suite (41 tests, zero mock leakage)
├── AGENTS.md                        # Agent-First Tool Contract & operational protocols
├── CONTRIBUTING.md                  # Laravel-aligned open-source contribution guidelines
├── DESIGN.md                        # Architecture, SOLID principles & Big-O analysis
├── GEMINI.md                        # Self-contained repository governance manual
├── SECURITY.md                      # Responsible vulnerability disclosure policy
└── README.md                        # Root manifest and quickstart guide
```

---

## Quickstart & CLI Commands

All commands can be invoked directly using `./bin/ep` or `./bin/gx` (or the `epistex` alias) without installation:

### 1. Repository Health Audit (`gx doctor`)
Validates frontmatter schema compliance, relative link integrity, line limit caps, and secret leak sentinels:
```bash
./bin/gx doctor --json
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

### 2. Token-Efficient Repository Map (`gx map`)
Produces a bounded, token-efficient structural overview of all domains:
```bash
./bin/gx map --depth 2 --compact --json
```

### 3. Query Upcoming Schedules (`gx schedule`)
Uses a bounded min-heap ($O(M \log k)$) to extract nearest deadlines:
```bash
./bin/gx schedule --limit 5 --json
```

### 4. Hermetic Execution with Secret Injection (`gx run`)
Executes a command in an isolated environment with secrets injected directly into process memory:
```bash
# Preview execution in dry-run mode
./bin/gx run --dry-run -- python3 -c "import os; print(os.environ)"

# Execute hermetically with Infisical secrets
./bin/gx run -- python3 -c "import os; print('Injected keys:', len(os.environ))"
```

### 5. Inspect Secret Provider Status (`gx secrets`)
Inspects active secret provider connectivity and masks keys for safe diagnostics:
```bash
./bin/gx secrets --json
```

### 6. Scaffold New Documents Atomically (`gx create`)
Scaffolds documents from standard templates (`adr`, `runbook`, `activity`) using atomic writes:
```bash
./bin/gx create adr engineering/adr/ADR-002-distributed-tracing.md --title "Distributed Tracing"
```

### 7. Cloud Asset Offloading & Tiered Hydration (`gx asset`)

Prevent Git repository bloat by storing heavy binary assets (PDFs, images, datasets) in cloud/local storage while keeping lightweight companion markdown pointers in Git:

```bash
# 1. Offload binary asset and generate Git companion markdown atomically
./bin/gx asset push path/to/spec.pdf --key specs/network-topology.pdf --companion engineering/assets/network.md --title "Network Topology"

# 2. Check remote asset existence without downloading full blob
./bin/gx asset check specs/network-topology.pdf --json

# 3. Discover assets across local and cloud tiers
./bin/gx asset list --tier all --json

# 4. Download / hydrate asset on-demand and verify SHA-256
./bin/gx asset pull specs/network-topology.pdf --target /tmp/restored-spec.pdf --json

# 5. Audit cloud assets in doctor
./bin/gx doctor --check-assets --json
```

#### Opt-In Cloud Storage & Flexible Authentication Modes
Cloud storage is **strictly opt-in** (`local` by default). When using an S3-compatible backend (`--backend s3` or `KB_CLOUD_STORAGE=s3`), credentials can be resolved via three security postures:
1. **Hermetic Injection (`--cloud-auth hermetic` or `KB_CLOUD_AUTH=hermetic`)**:
   Credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, etc.) are resolved strictly in-memory from the configured `SecretProviderInterface` (e.g. Infisical). Host `os.environ` is bypassed and no credentials ever touch disk.
2. **Environment Only (`--cloud-auth env` or `KB_CLOUD_AUTH=env`)**:
   Credentials are read strictly from host `os.environ` / `.env`.
3. **Auto Detection (`--cloud-auth auto` or `KB_CLOUD_AUTH=auto`)**:
   Checks secret provider first, then falls back to ambient environment.

Example hermetic upload with Infisical secrets:
```bash
./bin/gx asset push report.pdf --key reports/q4.pdf --backend s3 --cloud-auth hermetic
```

---

## 🏷️ Version Control & Branching Strategy (Laravel Model)

Epistex adopts the **Laravel Release & Branching Architecture** to balance rapid open-source innovation with rock-solid enterprise stability:

```text
  [1.x / Stable Series] ─────► v1.0.0 ──► v1.0.1 (Patches: bugfixes & zero breaking changes)
          ▲
          │ Non-breaking PRs & additive features
  [Feature Branches]    ─────► feat/* or bugfix/*
          ▲
  [Main / Canonical]    ─────► Production-ready stable release baseline
```

1. **Major Series Branches (`1.x`, `2.x`)**:
   - Modeled after Laravel's release branches (e.g. `11.x`), the `1.x` branch serves as the active maintenance line for the 1.x major series.
   - Bugfixes, minor non-breaking enhancements, and routine maintenance PRs target `1.x`.
2. **Canonical Trunk (`main`)**:
   - Represents production-ready, verified code.
   - Every merge to `main` must pass the automated Gauntlet (32 unit tests, static SRP analysis, zero-mock detector).
3. **Semantic Versioning 2.0.0 (`vMAJOR.MINOR.PATCH`)**:
   - **`PATCH` (e.g. `v1.0.1`)**: Backward-compatible bugfixes and performance optimizations.
   - **`MINOR` (e.g. `v1.1.0`)**: New CLI commands, additional templates, non-breaking schema additions.
   - **`MAJOR` (e.g. `v2.0.0`)**: Scheduled breaking architectural shifts or deprecation cleanups.
4. **Starter Kit Downstream Upgrades**:
   - When downstream organizations adopt Epistex as their internal knowledge base, they can track upstream improvements without conflict by adding Epistex as an upstream remote:
     ```bash
     git remote add upstream https://github.com/ihkaru/epistex.git
     git fetch upstream 1.x
     git merge --no-commit upstream/1.x
     ```
   - Because organizational documents live in `knowledge/` and the core engine lives in `src/`, upstream engine upgrades merge cleanly without colliding with internal documentation.

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
