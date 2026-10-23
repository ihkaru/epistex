# Upstream Engine Release & Maintenance Protocol (RELEASING.md)

> [!IMPORTANT]
> **Upstream Maintainer Scope Notice**:
> This document governs the versioning, testing, and publication lifecycle of the **Epistex Core Engine** (`src/`, `bin/gx`, `config/`).
> It applies **strictly to upstream maintainers** of the Epistex starter kit (`IS_STARTER_KIT = True`).
> When Epistex is specialized for downstream enterprise production (via `gx init`), this file is automatically pruned to prevent agent prompt poisoning.

---

## 1. Cadence & Release Model (Laravel-Inspired)

Epistex follows the **Laravel Release & Branching Architecture**:
- **Trunk (`main`)**: Canonical production-ready code.
- **Series Maintenance Branch (`1.x`)**: Active maintenance branch for the 1.x major series. All patch and minor enhancements target `1.x` and merge into `main`.
- **Git Tags**: Annotated tags formatted as `vMAJOR.MINOR.PATCH`.

```text
  [1.x / Active Series] ────► v1.1.0 ────► v1.1.1 (Patches: bugfixes & zero breaking changes)
          ▲                      │
          │                      ▼
  [feat/* or fix/*]      [GitHub Release]
```

---

## 2. Deterministic Release Trigger Matrix (State Machine)

To eliminate agent guesswork, releases are governed by objective file-path and commit-type conditions:

| Change Category | Target Files Affected | Trigger Condition | SemVer Action | Agent Role |
| :--- | :--- | :--- | :--- | :--- |
| **Content & Knowledge** | `knowledge/**`, operational docs | Any changes exclusively in `knowledge/` | **NO-OP (No release)** | Commit & push normally. Engine version remains untouched. |
| **Engine Bugfix / Perf** | `src/**`, `bin/gx`, `tests/**` | Commit prefix `fix:` or `perf:` | **PATCH (`v1.1.x`)** | Execute Pre-Flight Gauntlet $\rightarrow$ Bump Patch $\rightarrow$ Release. |
| **New Feature / Additive** | `src/**`, `bin/gx`, `config/**` | Commit prefix `feat:` (e.g. new CLI command or flag) | **MINOR (`v1.x.0`)** | Execute Pre-Flight Gauntlet $\rightarrow$ Bump Minor $\rightarrow$ Release. |
| **Breaking Shift** | Public interfaces, schemas | Commit message contains `BREAKING CHANGE:` or `feat!:` | **MAJOR (`v2.0.0`)** | **Halt**: Requires explicit user / architectural approval. |

---

## 3. Automated Readiness Detection (`gx doctor --check-release`)

Coding agents can verify release readiness deterministically:
```bash
./bin/gx doctor --check-release --json
```

When unreleased code changes exist in `src/` or `bin/`, the CLI returns:
```json
{
  "release_readiness": {
    "release_required": true,
    "mode": "upstream_starter_kit",
    "current_version": "1.1.0",
    "latest_tag": "v1.1.0",
    "unreleased_commits_count": 2,
    "recommended_bump": "minor",
    "code_changes_detected": true,
    "reason": "Detected 2 unreleased commit(s) touching engine code since v1.1.0."
  }
}
```

If changes are content-only (`knowledge/`), `release_required` is `false`.
In downstream mode (`IS_STARTER_KIT = False`), release checks are completely suppressed.

---

## 4. Pre-Flight Release Gauntlet

Every release must pass all 4 automated gates with zero warnings:

```bash
# 1. Parallel Hermetic Test Suite
python3 -m unittest discover -s tests -v

# 2. Deterministic Static SRP & Abstraction Analyzer
python3 ~/.gemini/config/skills/craftsman-coder/scripts/static_srp_analyzer.py . --strict

# 3. Zero-Mock & Silent Mock Static Detector
detect-mocks .

# 4. End-to-End Repository Doctor Check
./bin/gx doctor --check-assets --check-release --json
```

---

## 5. Automated Release Execution (`scripts/release.sh`)

To eliminate human error and ensure that git tagging, branch synchronization, and **GitHub Release publication** occur atomically, maintainers should use the release automation script:

```bash
# 1. Preview release without touching files or git:
./scripts/release.sh --dry-run

# 2. Execute automated release (patch, minor, or major):
./scripts/release.sh patch   # or minor / major
```

The script automatically executes:
1. Scope validation (`IS_STARTER_KIT == True`) and working tree cleanliness checks.
2. Automated bump recommendation via `gx doctor --check-release`.
3. The 4-gate pre-flight gauntlet (unit tests, SRP static analyzer, zero-mock detector, `gx doctor`).
4. Version bumping in `config/app.py` and `pyproject.toml`.
5. Release notes extraction from `CHANGELOG.md`.
6. Committing the release bump to `main`.
7. Fast-forwarding the active series branch `1.x` to `main`.
8. Creating the annotated Git tag `vMAJOR.MINOR.PATCH`.
9. Pushing `main`, `1.x`, and tags to GitHub.
10. Creating or updating the official **GitHub Release** via `gh release create`.

---

## 6. Manual Release Sequence (Reference)

If executing manually:

1. **Bump Version**:
   - `config/app.py`: Update `APP_VERSION`.
   - `pyproject.toml`: Update `version`.
2. **Document Changes**:
   - Add entry in `CHANGELOG.md` following Keep a Changelog standard.
3. **Commit & Align Branches**:
   ```bash
   git add config/app.py pyproject.toml CHANGELOG.md
   git commit -m "chore(release): bump version to vMAJOR.MINOR.PATCH"
   git branch -f 1.x main
   ```
4. **Tag & Publish to GitHub**:
   ```bash
   git tag -a vMAJOR.MINOR.PATCH -m "Release vMAJOR.MINOR.PATCH: <summary>"
   git push origin main 1.x --tags
   gh release create vMAJOR.MINOR.PATCH --title "vMAJOR.MINOR.PATCH: <summary>" --notes-file <notes>
   ```
