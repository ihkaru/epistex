# Contributing to Gnosidex

Thank you for considering contributing to Gnosidex! The contribution model is modeled directly after the **Laravel Open Source Framework**.

---

## 1. Branching Strategy

To keep releases predictable and zero-regression:

| Contribution Type | Target Branch | Notes |
|---|---|---|
| **Bug Fixes** | `1.x` | Bug fixes that do not break backward compatibility. |
| **New Features** | `1.x` | Additive features, new CLI commands/flags that are backward-compatible. |
| **Breaking Changes** | `main` (or dedicated future major branch) | Major interface modifications requiring SemVer major bumps. |

> All changes merged into `1.x` are regularly synchronized into `main`.

---

## 2. Pull Request Guidelines

1. **Evidence-First Development**:
   - Every new feature or bugfix **must include automated tests** in `tests/`.
   - Run the test suite before submitting:
     ```bash
     python3 -m unittest discover -s tests -v
     ```
2. **Quality & Architecture Invariants**:
   - **SRP Limits**: Classes $\le 180$ lines, functions $\le 50$ lines.
   - **Zero External Dependencies**: Gnosidex core must remain 100% standard library Python 3.10+.
   - **Zero-Mock Production Paths**: No mock leaks or dummy simulators outside `tests/`.
   - **Stream Purity**: CLI commands must output pure JSON to STDOUT when `--json` is passed.
3. **Pre-Stop Gate**:
   - Verify repository health:
     ```bash
     ./bin/gx doctor --check-assets --json
     ```

---

## 3. Upstream vs Downstream Contribution

- **Upstream Scope (`IS_STARTER_KIT = True`)**: This repository (`ihkaru/gnosidex`) is the upstream starter kit engine. Maintainer releases, SemVer bumping, and engine development happen here.
- **Downstream Specialization (`IS_STARTER_KIT = False`)**: If you cloned Gnosidex for your private organization, specialize it with `./bin/gx init`. Do not submit organization-specific documents or credentials upstream.
