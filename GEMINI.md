# Gnosidex Architecture & Governance Guide (GEMINI.md)

## 1. Overview & Core Philosophy
**Gnosidex** is an enterprise-grade, plug-and-play, high-performance Git-based Knowledge Base starter kit. It provides:
- **Zero External Runtime Dependencies**: Standard Python 3.10+ execution out of the box.
- **Convention-Over-Configuration**: Predictable Laravel-inspired folder layout (`bin/`, `config/`, `knowledge/`, `src/`, `storage/`).
- **SOLID & Interface-First Design**: Strict Dependency Inversion via abstract contracts (`src/contracts/`).
- **Event-Driven Architecture (EDA)**: Extensible pub/sub dispatcher and lifecycle hooks (`src/events/`).
- **Hermetic Code Execution**: Memory-only secret injection with first-party Infisical support and fallback to process environment.
- **Dual-Audience CLI (`gx` / `gnosidex`)**: Agent-first tool contract with pure machine-readable STDOUT on `--json` and POSIX sysexits.

## 2. Directory Taxonomy & Conventions
```text
.
├── bin/
│   ├── gx                           # Primary executable CLI entrypoint (chmod +x)
│   ├── gnosidex                     # Canonical alias symlink (chmod +x)
│   └── kb                           # Legacy transition symlink (chmod +x)
├── config/                          # Centralized convention configuration
│   ├── app.py                       # App metadata, defaults, exit code mappings
│   ├── schema.py                    # Frontmatter schemas & allowed statuses
│   └── vault.py                     # Secret provider configuration
├── knowledge/                       # Domain-driven knowledge base documents
│   ├── engineering/
│   │   ├── adr/                     # Architecture Decision Records (e.g. ADR-001-...)
│   │   └── runbooks/                # Operational Runbooks (e.g. RUN-001-...)
│   ├── operations/
│   │   └── playbooks/               # Playbooks & incident guides
│   └── activities/                  # Structured operational activities & milestones
├── src/                             # SOLID, Interface-First Python package
│   ├── contracts/                   # Abstract base interfaces (DIP)
│   ├── core/                        # High-performance zero-dep algorithmic core
│   ├── events/                      # Event dispatcher & typed domain events
│   ├── providers/                   # Secret backends & hermetic execution runners
│   ├── listeners/                   # Built-in audit & telemetry listeners
│   └── commands/                    # CLI commands (doctor, map, create, schedule, run, secrets)
├── storage/                         # Local cache and ephemeral logs
│   ├── cache/
│   └── logs/
└── tests/                           # Hermetic unit & integration test suite
```

## 3. Strict Algorithmic & Quality Invariants
1. **Directory Traversal ($O(V)$)**: Filesystem scanning uses pruned `os.scandir()`. Never traverse `.git`, `node_modules`, or `storage`.
2. **Frontmatter Extraction ($O(K)$)**: Streaming line generator with early exit at the second `---` delimiter. Never buffer full markdown bodies to memory.
3. **Schedule Query ($O(M \log k)$)**: Query upcoming deadlines using a bounded min-heap (`heapq`).
4. **Link Integrity Audit ($O(N + R)$)**: Single-pass hash inverted index for $O(1)$ relative link lookups.
5. **Class & Function Length Caps**: Classes must not exceed 180 lines; functions must not exceed 50 lines.
6. **Cloud Asset Offloading & Auth Modes (Git Bloat Prevention)**: Binary files (PDFs, images, archives) must not be committed directly to Git. Use `gx asset push` to offload to cloud storage with a Git-native companion markdown pointer. Cloud connectivity is strictly opt-in (`local` by default) with three configurable auth postures (`--cloud-auth` / `KB_CLOUD_AUTH`): `hermetic` (memory-only secret injection via `SecretProviderInterface`), `env` (environment variables), or `auto`.

## 4. Verification & Testing Commands
Run all automated verification gates:
```bash
# 1. Run unit and integration tests
python3 -m unittest discover -s tests -v

# 2. Run repository doctor audit (with optional asset verification)
./bin/gx doctor --check-assets --json

# 3. Test hermetic dry-run execution
./bin/gx run --dry-run -- python3 --version
```

---

## 5. Agent Infrastructure Directory (`.agents/`)

On-demand skill library and stop-hook gate for coding agents:

```text
.agents/
├── hooks.json                    # AGY stop-hook: runs pre_stop.sh before agent stops
├── hooks/pre_stop.sh             # 4-gate verification gauntlet (tests + SRP + mocks + doctor)
└── skills/
    ├── gnosidex-doctor/          # gx doctor audit workflow & repair loop
    ├── gnosidex-knowledge-author/ # Frontmatter schema, naming conventions, link integrity
    └── gnosidex-downstream-setup/ # Downstream specialization & upstream sync protocol
```

Read the relevant `SKILL.md` before performing specialized tasks:
- Health audits & error repair → `.agents/skills/gnosidex-doctor/SKILL.md`
- Authoring knowledge documents → `.agents/skills/gnosidex-knowledge-author/SKILL.md`
- Onboarding a downstream organization → `.agents/skills/gnosidex-downstream-setup/SKILL.md`

---

## 6. Operational Mode (`IS_STARTER_KIT`)

`config/app.py` carries a flag that governs agent behavior:

| Flag Value | Context | Agent Scope |
|---|---|---|
| `IS_STARTER_KIT = True` | **Upstream** (this repo) | Engine maintenance, release checks active (`gx doctor --check-release`) |
| `IS_STARTER_KIT = False` | **Downstream** (after `gx init`) | Content-only; engine releases, git tags, and `docs/RELEASING.md` suppressed |

Downstream agents **MUST NOT** bump engine versions or create git release tags.
All downstream changes are content-only (`knowledge/`, domain docs, GEMINI.md).

---

## 7. Downstream GEMINI.md Template

After running `gx init`, downstream organizations **MUST** enrich `GEMINI.md` with
domain-specific sections. Minimum required sections:

```markdown
## Identity & User Detection SOP
How agents detect the active user at session start.

## Domain Business Logic
Core formulas, thresholds, and rules specific to this organization.
Reference authoritative data sources — never guess relational structure.

## Tooling Stack Mandates
- Document engine (e.g., Typst for print, Markdown for web)
- Automation engine (e.g., Windmill for scheduled ETL)
- Forbidden alternatives and why

## Anti-Assumption Rules
Explicit prohibitions. What requires user confirmation before generating output.

## Content-Only Scope
Confirmation that IS_STARTER_KIT = False is active and release mechanics are suppressed.
Upstream sync protocol: git fetch upstream main && git merge --no-commit upstream/main
```

> See `.agents/skills/gnosidex-downstream-setup/SKILL.md` for the full onboarding workflow.


