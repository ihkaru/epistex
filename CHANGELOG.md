# Changelog

All notable changes to **Epistex** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) following the [Laravel Release Model](https://laravel.com/docs/releases).

## [v1.2.0] - 2026-10-20

### Added
- **Agent Infrastructure Directory (`.agents/`)**: Introduced on-demand skill library and stop-hook gate for coding agents:
  - `.agents/hooks.json` — AGY stop-hook configuration wiring `pre_stop.sh` before agent may stop.
  - `.agents/hooks/pre_stop.sh` — 4-gate verification gauntlet (unit tests + SRP analyzer + zero-mock detector + `ep doctor`) executed automatically before any agent turn completes.
  - `.agents/skills/epistex-doctor/SKILL.md` — Health audit workflow with exit code interpretation, self-healing repair loop, and asset verification protocol.
  - `.agents/skills/epistex-knowledge-author/SKILL.md` — Frontmatter schema, naming conventions, link integrity rules, and `ep create` scaffold patterns.
  - `.agents/skills/epistex-downstream-setup/SKILL.md` — Complete downstream onboarding guide: `ep init` flow, GEMINI.md domain SOP template, upstream sync protocol, and anti-poisoning invariants.
- **Pre-Commit Hook (`.githooks/pre-commit`)**: Enforces Python 300-line SRP limit and blocks `RELEASING.md` commits in downstream repos (anti-poisoning guard). Auto-activated via `git config core.hooksPath .githooks` on `ep init`.
- **Downstream GEMINI.md Template (§7 in `GEMINI.md`)**: Documents required sections for downstream organizations to fill after `ep init` — Identity SOP, Domain Business Logic, Tooling Stack Mandates, Anti-Assumption Rules, Content-Only Scope declaration.

### Changed
- **`AGENTS.md` §5** (new): Agent infrastructure routing table documenting when to load each skill.
- **`GEMINI.md` §5–7** (new): `.agents/` directory reference, `IS_STARTER_KIT` mode comparison table, and downstream GEMINI.md template.
- **`cmd_init.py`**: Added `_activate_githooks()` — auto-wires `.githooks/` as `core.hooksPath` on `ep init`; adds `githooks_activated` field to JSON payload.
- **`test_init_command.py`**: Added assertion for `githooks_activated` key in init payload.

---

## [v1.1.0] - 2026-10-20

### Added
- **`ep init` Specialization Installer**: Added autonomous, non-interactive CLI command (`ep init`) enabling coding agents to specialize the repository for an organization, update metadata in `config/app.py`, prune sample starter documents, and generate `.env` from template.
- **Unified CLI Executables (`ep` / `epistex`)**: Established `ep` and `epistex` as the canonical CLI executables (`bin/ep`, `bin/epistex`).
- **Agent-First Governance & Versioning Protocol**: Formulated and documented Laravel-inspired series maintenance (`1.x`), SemVer 2.0.0 release gates, and downstream upstream merge safety in `AGENTS.md` and `README.md`.
- **Environment Template (`.env.example`)**: Added comprehensive configuration template for Infisical Vault integration and S3-compatible cloud storage.

### Changed
- Refactored CLI commands, error envelopes, doctor `fix_hint` attributes, companion generation, and test suites to adopt canonical executables.
- Aligned `pyproject.toml` console scripts with `ep = "bin.ep:main"` and `epistex = "bin.ep:main"`.

---

## [v1.0.0] - 2026-10-18

### Added
- Initial release of **Epistex**: Enterprise Git-Based Knowledge Base Starter Kit.
- Pure Python 3.10+ standard library core with zero external runtime dependencies.
- SOLID & Interface-First architecture (DIP) with abstract contracts in `src/contracts/`.
- Event-Driven Architecture (EDA) with typed domain events and priority listener bus.
- Fast pruned directory scanner ($O(V)$) and streaming frontmatter reader ($O(K)$).
- Bounded min-heap schedule extractor ($O(M \log k)$) and single-pass inverted link index ($O(N + R)$).
- Hermetic code runner with in-memory secret injection supporting Infisical Universal Auth.
- Tiered companion markdown pattern for cloud asset offloading (S3 SigV4) preventing Git bloat.
- Dual-audience CLI with strict machine-pure JSON STDOUT, STDERR diagnostics, and POSIX BSD sysexits (`sysexits.h`).
