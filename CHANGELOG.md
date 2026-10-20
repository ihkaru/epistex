# Changelog

All notable changes to **Gnosidex** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) following the [Laravel Release Model](https://laravel.com/docs/releases).

## [v1.1.0] - 2026-10-20

### Added
- **`gx init` Specialization Installer**: Added autonomous, non-interactive CLI command (`gx init`) enabling coding agents to specialize the repository for an organization, update metadata in `config/app.py`, prune sample starter documents, and generate `.env` from template.
- **Unified CLI Executable (`gx`)**: Established `gx` as the canonical 2-character CLI executable (`bin/gx`), eliminating naming redundancy while maintaining backward-compatible symlinks (`gnosidex -> gx` and `kb -> gx`).
- **Comprehensive Agent Versioning Protocol**: Formulated and documented Laravel-inspired series maintenance (`1.x`), SemVer 2.0.0 release gates, and downstream upstream merge safety in `AGENTS.md` and `README.md`.
- **Environment Template (`.env.example`)**: Added comprehensive configuration template for Infisical Vault integration and S3-compatible cloud storage.

### Changed
- Refactored CLI commands, error envelopes, doctor `fix_hint` attributes, companion generation, and test suites to adopt `gx` as the primary executable.
- Aligned `pyproject.toml` console scripts with `gx = "bin.gx:main"`.

---

## [v1.0.0] - 2026-10-18

### Added
- Initial release of **Gnosidex**: Enterprise Git-Based Knowledge Base Starter Kit.
- Pure Python 3.10+ standard library core with zero external runtime dependencies.
- SOLID & Interface-First architecture (DIP) with abstract contracts in `src/contracts/`.
- Event-Driven Architecture (EDA) with typed domain events and priority listener bus.
- Fast pruned directory scanner ($O(V)$) and streaming frontmatter reader ($O(K)$).
- Bounded min-heap schedule extractor ($O(M \log k)$) and single-pass inverted link index ($O(N + R)$).
- Hermetic code runner with in-memory secret injection supporting Infisical Universal Auth.
- Tiered companion markdown pattern for cloud asset offloading (S3 SigV4) preventing Git bloat.
- Dual-audience CLI with strict machine-pure JSON STDOUT, STDERR diagnostics, and POSIX BSD sysexits (`sysexits.h`).
