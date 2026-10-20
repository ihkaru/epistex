---
name: gnosidex-downstream-setup
description: |
  Step-by-step onboarding guide for coding agents tasked with specializing a
  freshly cloned Gnosidex starter kit into a production knowledge base for a
  specific organization. Covers gx init, upstream sync wiring, domain SOP
  authoring, and the anti-poisoning invariants that protect downstream agents.
---

# Gnosidex Downstream Specialization Skill

## Overview

This skill governs the transition from **upstream starter kit** (`IS_STARTER_KIT = True`)
to **downstream production knowledge base** (`IS_STARTER_KIT = False`).

After running `gx init`, a Gnosidex repository transforms into an organization-specific
knowledge base. This skill ensures that transition is complete, safe, and well-documented.

---

## Step 1 — Clone & Initialize

```bash
git clone https://github.com/ihkaru/gnosidex.git my-org-kb
cd my-org-kb

# Wire the upstream remote for future engine updates
git remote rename origin upstream
git remote add origin https://github.com/YOUR_ORG/YOUR_REPO.git

# Specialize the repository (non-interactive, agent-safe)
./bin/gx init \
  --name "Organization Knowledge Base" \
  --description "Accurate description of the organization and scope" \
  --owner "@your-team-handle" \
  --clean-samples \
  --yes \
  --json
```

After `gx init` completes:
- `config/app.py` → `IS_STARTER_KIT = False` (release checks deactivated)
- `docs/RELEASING.md` → **deleted** (anti-poisoning: downstream agents never see engine release instructions)
- Sample ADR and activity docs → removed (if `--clean-samples` was passed)

---

## Step 2 — Enrich GEMINI.md with Domain SOP

After init, the agent **MUST** populate `GEMINI.md` with organization-specific rules.
Open `GEMINI.md` and add the following sections (adapt to your domain):

### Required Sections for Downstream GEMINI.md

```markdown
## Identity & User Detection SOP
- How agents should detect the active user (e.g., `python scripts/kb.py whoami`)
- Cascade: env variable → git config → interactive prompt

## Domain Business Logic
- Core formulas, thresholds, and classification rules specific to this organization
- Reference the authoritative data source (never guess relational structure)

## Tooling Stack Mandates
- Document generation engine (e.g., Typst for print, HTML for web)
- Automation pipeline engine (e.g., Windmill for scheduled ETL)
- Forbidden alternatives (e.g., no raw cron daemons, no Puppeteer for PDFs)

## Anti-Assumption Rules
- Explicit prohibitions against hardcoding or assuming domain-specific values
- When to confirm with the user before generating outputs

## Content-Only Scope (IS_STARTER_KIT = False)
- Engine version bumps, git release tags, and engine release notes are FORBIDDEN
- All changes are content-only: knowledge/, docs/, kegiatan/, etc.
- To receive engine updates from upstream Gnosidex:
  git fetch upstream main
  git merge --no-commit upstream/main
```

---

## Step 3 — Wire `.githooks/pre-commit` (Optional but Recommended)

Enforce file length limits and schema validity on every commit:

```bash
mkdir -p .githooks
cat > .githooks/pre-commit << 'EOF'
#!/usr/bin/env bash
# Pre-commit: Block commits with Python files exceeding 300 lines
set -euo pipefail
LIMIT=300
ERRORS=0
while IFS= read -r -d '' file; do
  lines=$(wc -l < "$file")
  if [ "$lines" -gt "$LIMIT" ]; then
    echo "[FAIL] $file: $lines lines exceeds $LIMIT-line limit. Decompose before committing."
    ERRORS=$((ERRORS + 1))
  fi
done < <(git diff --cached --name-only -z | grep -z '\.py$' || true)
if [ "$ERRORS" -gt 0 ]; then
  exit 1
fi
EOF
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
echo "Pre-commit hook installed."
```

---

## Step 4 — Upstream Engine Sync Protocol

When new features or fixes are released in upstream Gnosidex:

```bash
# Fetch upstream changes (engine only)
git fetch upstream main

# Preview what will merge (inspect before accepting)
git diff HEAD upstream/main -- src/ bin/ config/ tests/

# Merge engine updates without auto-commit (review first)
git merge --no-commit upstream/main

# Verify no breakage
python3 -m unittest discover -s tests -v

# If tests pass, complete the merge
git commit -m "chore(upstream): sync engine from gnosidex vX.Y.Z"
```

> Never merge upstream changes to `knowledge/`, `docs/` (your domain docs), or
> `GEMINI.md` — those are owned by the downstream organization.

---

## Anti-Poisoning Invariants (Enforced by IS_STARTER_KIT = False)

| Forbidden Action | Why |
|---|---|
| Bumping `APP_VERSION` in `config/app.py` | Engine versioning is upstream's concern only |
| Creating `git tag vX.Y.Z` | Downstream releases are content deployments, not engine releases |
| Running `gx doctor --check-release` | This flag is suppressed in downstream mode |
| Pushing to `upstream` remote | Downstream agents write only to `origin` |
