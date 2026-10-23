---
name: epistex-knowledge-author
description: |
  Guides agents in authoring, validating, and organizing knowledge documents
  within an Epistex knowledge base. Covers frontmatter schema, document
  categories, naming conventions, link integrity, and schedule management.
  Activate whenever creating, editing, or auditing knowledge documents.
---

# Epistex Knowledge Authoring Skill

## Document Structure & Frontmatter

Every document in `knowledge/` **must** begin with a valid YAML frontmatter block:

```markdown
---
title: "Short, clear title"
status: "active"          # active | draft | deprecated | archived
category: "runbook"       # architecture-decision | runbook | playbook | rfc | activity | guideline
owner: "@team-handle"
tags:
  - "tag-one"
  - "tag-two"
deadlines:
  - label: "Review Deadline"
    date: "2026-12-31"
---
```

### Allowed Values per Field

| Field | Allowed Values |
|---|---|
| `status` | `active`, `draft`, `deprecated`, `archived` |
| `category` | `architecture-decision`, `runbook`, `playbook`, `rfc`, `activity`, `guideline` |
| `owner` | Any `@handle` string |
| `tags` | Any lowercase hyphenated strings |
| `deadlines[].date` | ISO 8601 format: `YYYY-MM-DD` |

> Always run `./bin/gx doctor --json` after authoring to catch schema errors before committing.

## Naming Conventions

### Architecture Decision Records (ADR)

```
knowledge/engineering/adr/ADR-{NNN}-{kebab-title}.md
```
Example: `ADR-002-event-sourcing-for-audit-trail.md`

### Runbooks

```
knowledge/engineering/runbooks/RUN-{NNN}-{kebab-topic}.md
```
Example: `RUN-002-database-backup-and-restore.md`

### Playbooks

```
knowledge/operations/playbooks/PLAY-{NNN}-{kebab-scenario}.md
```
Example: `PLAY-002-disaster-recovery-failover.md`

### Activities

```
knowledge/activities/{activity-type}/{year}/README.md
```
Example: `knowledge/activities/quarterly-audit/2027-Q1/README.md`

## Scaffolding New Documents

Use the CLI to scaffold with valid frontmatter:

```bash
# Create a new runbook
./bin/gx create knowledge/engineering/runbooks/RUN-002-new-runbook.md \
  --category runbook \
  --owner "@ops-team"

# Create a new ADR
./bin/gx create knowledge/engineering/adr/ADR-002-new-decision.md \
  --category architecture-decision \
  --owner "@platform-eng"
```

Always pass `--json` for machine-readable output in agentic pipelines.

## Link Integrity

- Use **relative paths** for all internal document links: `[ADR-001](../adr/ADR-001-event-driven-architecture.md)`
- Never use absolute filesystem paths in documents
- Run `./bin/gx doctor --json` to validate all relative links in one pass

## Schedule & Deadline Tracking

To list upcoming deadlines across all knowledge documents:

```bash
./bin/gx schedule --limit 10 --json
```

To filter by tag or category:

```bash
./bin/gx schedule --limit 5 --json | python3 -c "
import sys, json
data = json.load(sys.stdin)
for item in data.get('upcoming', []):
    print(f\"{item['date']} | {item['label']} | {item['file']}\")
"
```

## Repository Map

To get a compact token-budget-safe summary of the repository layout:

```bash
./bin/gx map --depth 2 --compact --json
```

This returns the directory tree in under 150 tokens — safe for agent context windows.
