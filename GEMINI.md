# Gnosidex Architecture & Governance Guide (GEMINI.md)

## 1. Overview & Core Philosophy
**Gnosidex** is an enterprise-grade, plug-and-play, high-performance Git-based Knowledge Base starter kit. It provides:
- **Zero External Runtime Dependencies**: Standard Python 3.10+ execution out of the box.
- **Convention-Over-Configuration**: Predictable Laravel-inspired folder layout (`bin/`, `config/`, `knowledge/`, `src/`, `storage/`).
- **SOLID & Interface-First Design**: Strict Dependency Inversion via abstract contracts (`src/contracts/`).
- **Event-Driven Architecture (EDA)**: Extensible pub/sub dispatcher and lifecycle hooks (`src/events/`).
- **Hermetic Code Execution**: Memory-only secret injection with first-party Infisical support and fallback to process environment.
- **Dual-Audience CLI (`gnosidex` / `kb`)**: Agent-first tool contract with pure machine-readable STDOUT on `--json` and POSIX sysexits.

## 2. Directory Taxonomy & Conventions
```text
.
├── bin/
│   ├── gnosidex                     # Primary executable symlink (chmod +x)
│   └── kb                           # Executable CLI entrypoint (chmod +x)
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
6. **Cloud Asset Offloading & Auth Modes (Git Bloat Prevention)**: Binary files (PDFs, images, archives) must not be committed directly to Git. Use `kb asset push` to offload to cloud storage with a Git-native companion markdown pointer. Cloud connectivity is strictly opt-in (`local` by default) with three configurable auth postures (`--cloud-auth` / `KB_CLOUD_AUTH`): `hermetic` (memory-only secret injection via `SecretProviderInterface`), `env` (environment variables), or `auto`.

## 4. Verification & Testing Commands
Run all automated verification gates:
```bash
# 1. Run unit and integration tests
python3 -m unittest discover -s tests -v

# 2. Run repository doctor audit (with optional asset verification)
./bin/kb doctor --check-assets --json

# 3. Test hermetic dry-run execution
./bin/kb run --dry-run -- python3 --version
```

